#!/usr/bin/env python3
"""
ElevenLabs Music MCP Server
Exposes music generation tools through the Model Context Protocol

Author: Jeremy Bradford
Date: 2025-11-16
Project: P171_elevenlabs-music-mcp
"""

import asyncio
import json
import sys
import os
import logging
import traceback
from typing import Any, Dict, List, Optional
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv

# MCP imports
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent

# Local imports
from music_generator import MusicGenerator
from file_manager import FileManager
from config_manager import Config

# Phase 2+ imports (not yet implemented)
# from composition_planner import CompositionPlanner
# from context_analyzer import ContextAnalyzer
# from preference_learner import PreferenceLearner

# Load environment variables
load_dotenv()

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    stream=sys.stderr
)


class MusicMCPServer:
    """
    Main MCP server for music generation.
    Exposes tools for AI agents to generate, manage, and learn from music.
    """

    def __init__(self):
        """Initialize the MCP server and all components."""
        self.server = Server("elevenlabs-music")

        # Load configuration
        try:
            self.config = Config.from_env()
            logging.info("Configuration loaded successfully")
        except Exception as e:
            logging.error(f"Failed to load configuration: {e}")
            raise

        # Initialize core components
        self.generator = MusicGenerator(
            api_key=self.config.api_key,
            base_url=self.config.api_base_url,
            timeout=self.config.api_timeout,
            max_retries=self.config.max_retries
        )
        self.file_manager = FileManager(self.config.music_output_dir)

        # Phase 2+ components (not yet implemented)
        # self.planner = CompositionPlanner()
        # self.context_analyzer = ContextAnalyzer()
        # self.preference_learner = PreferenceLearner(self.config.preference_storage_path)

        logging.info("All components initialized")

        # Register all MCP tools
        self.register_tools()
        
    def register_tools(self):
        """Register all available MCP tools."""

        # Tool 1: Simple music generation
        @self.server.tool()
        async def generate_music_simple(
            prompt: str,
            duration_ms: int = None,
            output_format: str = "mp3_44100_128",
            metadata: dict = None
        ) -> dict:
            """
            Generate music from a simple text prompt using ElevenLabs.

            This tool generates music based on natural language descriptions.
            It handles API communication, file storage, and metadata management.

            Args:
                prompt: Natural language description of desired music
                    Examples:
                    - "lo-fi hip hop beats for coding, 90 BPM"
                    - "calming ambient piano, gentle, 2 minutes"
                    - "energizing workout music with bass"
                duration_ms: Optional duration in milliseconds (3000-300000)
                    Default: 60000 (1 minute)
                output_format: Audio format (default: mp3_44100_128)
                metadata: Optional metadata tags to include

            Returns:
                dict with:
                - success: bool
                - audio_path: str (if successful)
                - metadata: dict with composition details
                - error: str (if failed)
                - suggested_prompt: str (if copyright issue)
            """
            try:
                logging.info(f"Received music generation request: '{prompt[:50]}...'")

                # Validate duration
                if duration_ms is not None:
                    if duration_ms < self.config.min_duration_ms:
                        return {
                            "success": False,
                            "error": f"Duration must be at least {self.config.min_duration_ms}ms (3 seconds)"
                        }
                    if duration_ms > self.config.max_duration_ms:
                        return {
                            "success": False,
                            "error": f"Duration cannot exceed {self.config.max_duration_ms}ms (5 minutes)"
                        }

                # Initialize generator session if not exists
                if not self.generator.session:
                    await self.generator.__aenter__()

                # Generate music
                result = await self.generator.generate_simple(
                    prompt=prompt,
                    duration_ms=duration_ms or self.config.default_duration_ms,
                    output_format=output_format
                )

                # Check for errors
                if not result.success:
                    response = {
                        "success": False,
                        "error": result.error
                    }
                    if result.suggested_prompt:
                        response["suggested_prompt"] = result.suggested_prompt
                        response["message"] = (
                            f"Copyright issue detected. Try this instead: '{result.suggested_prompt}'"
                        )
                    return response

                # Save to filesystem
                file_metadata = metadata or {}
                file_metadata.update({
                    "prompt": prompt,
                    "duration_ms": duration_ms or self.config.default_duration_ms,
                    "composition_plan": result.composition_plan,
                    "output_format": output_format,
                    "generated_at": datetime.now().isoformat()
                })

                audio_path, metadata_path = self.file_manager.save_music(
                    audio_data=result.audio_data,
                    metadata=file_metadata,
                    prompt=prompt
                )

                logging.info(f"Music saved successfully: {audio_path}")

                # Build response
                return {
                    "success": True,
                    "audio_path": str(audio_path),
                    "metadata_path": str(metadata_path),
                    "file_size_bytes": len(result.audio_data),
                    "composition_plan": result.composition_plan or {},
                    "prompt": prompt,
                    "duration_ms": duration_ms or self.config.default_duration_ms,
                    "message": f"Successfully generated music: {audio_path.name}"
                }

            except Exception as e:
                logging.error(f"Music generation failed: {e}", exc_info=True)
                return {
                    "success": False,
                    "error": str(e),
                    "traceback": traceback.format_exc()
                }
        
        # Tool 2: Create composition plan
        @self.server.tool()
        async def create_composition_plan(
            prompt: str,
            total_duration_ms: int,
            sections: list = None,
            mood_progression: str = None
        ) -> dict:
            """
            Generate a structured composition plan before creating music.
            
            Args:
                prompt: High-level description
                total_duration_ms: Total length desired
                sections: Optional pre-defined sections
                mood_progression: Optional mood flow (e.g., "calm to energetic")
                
            Returns:
                dict with composition_plan structure
            """
            try:
                # TODO: Implement
                return {
                    "success": False,
                    "error": "Not implemented yet"
                }
            except Exception as e:
                return {
                    "success": False,
                    "error": str(e)
                }
        
        # Tool 3: Generate from composition plan
        @self.server.tool()
        async def generate_music_structured(
            composition_plan: dict,
            strict_duration: bool = False,
            metadata: dict = None
        ) -> dict:
            """
            Generate music from a detailed composition plan.
            
            Args:
                composition_plan: Structured plan from create_composition_plan
                strict_duration: Enforce exact section durations
                metadata: Optional metadata tags
                
            Returns:
                dict with audio_path and generation details
            """
            try:
                # TODO: Implement
                return {
                    "success": False,
                    "error": "Not implemented yet"
                }
            except Exception as e:
                return {
                    "success": False,
                    "error": str(e)
                }
        
        # Tool 4: Analyze mood for music suggestion
        @self.server.tool()
        async def analyze_mood_for_music(
            context: str,
            activity: str = None,
            time_of_day: str = None,
            recent_music: list = None
        ) -> dict:
            """
            Analyze context and suggest appropriate music parameters.
            
            Args:
                context: Text to analyze for mood
                activity: Optional activity type (e.g., "coding", "writing")
                time_of_day: Optional time context (e.g., "morning", "evening")
                recent_music: Optional list of recently generated tracks
                
            Returns:
                dict with suggested_prompt, duration, mood_analysis, reasoning
            """
            try:
                # TODO: Implement
                return {
                    "success": False,
                    "error": "Not implemented yet"
                }
            except Exception as e:
                return {
                    "success": False,
                    "error": str(e)
                }
        
        # Tool 5: Journal entry with music (Phase 3)
        @self.server.tool()
        async def generate_journal_entry_with_music(
            conversation_history: list = None,
            date: str = None,
            mood_override: str = None,
            music_duration_ms: int = 60000
        ) -> dict:
            """
            Create a daily journal entry with matching soundtrack.
            
            Args:
                conversation_history: Recent conversations to analyze
                date: ISO date string (default: today)
                mood_override: Optional forced mood
                music_duration_ms: Length of soundtrack
                
            Returns:
                dict with journal_entry, music details, combined_path
            """
            try:
                # TODO: Implement (Phase 3)
                return {
                    "success": False,
                    "error": "Phase 3 feature - not yet implemented"
                }
            except Exception as e:
                return {
                    "success": False,
                    "error": str(e)
                }


        logging.info("✅ Registered MCP tools (Phase 1: generate_music_simple, Phase 2+: other tools)")
    
    async def run(self):
        """Start the MCP server with stdio transport."""
        async with stdio_server() as (read_stream, write_stream):
            await self.server.run(
                read_stream,
                write_stream,
                self.server.create_initialization_options()
            )


async def main():
    """Main entry point for the MCP server."""
    print("🎵 Starting ElevenLabs Music MCP Server...", file=sys.stderr)
    
    # Check for API key
    api_key = os.getenv("ELEVENLABS_API_KEY")
    if not api_key:
        print("❌ ERROR: ELEVENLABS_API_KEY not set", file=sys.stderr)
        print("   Set it with: export ELEVENLABS_API_KEY='your-key'", file=sys.stderr)
        sys.exit(1)
    
    print(f"✅ API key found", file=sys.stderr)
    
    # Create and run server
    server = MusicMCPServer()
    await server.run()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 Shutting down gracefully...", file=sys.stderr)
    except Exception as e:
        print(f"\n❌ Fatal error: {e}", file=sys.stderr)
        traceback.print_exc()
        sys.exit(1)
