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

# Phase 2+ imports
from composition_planner import CompositionPlanner
from context_analyzer import ContextAnalyzer
from preference_learner import PreferenceLearner

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

        # Phase 2 components
        self.planner = CompositionPlanner()
        self.context_analyzer = ContextAnalyzer()
        self.preference_learner = PreferenceLearner(self.config.preference_storage_path)

        logging.info("All components initialized (including Phase 2 features)")

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

                # Record preference for learning (Phase 2)
                if self.config.enable_preference_learning:
                    try:
                        self.preference_learner.record_generation(
                            prompt=prompt,
                            metadata=file_metadata,
                            result_path=audio_path
                        )
                        logging.debug("Preference recorded for learning")
                    except Exception as e:
                        # Don't fail the request if preference recording fails
                        logging.warning(f"Failed to record preference: {e}")

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
            total_duration_ms: int = 60000,
            sections: int = None,
            mood_progression: str = None
        ) -> dict:
            """
            Generate a structured composition plan before creating music.

            Creates an intelligent multi-section plan that can be used with
            generate_music_structured for sophisticated compositions.

            Args:
                prompt: High-level description (e.g., "focus music for coding")
                total_duration_ms: Total length desired (default: 60000 = 1 minute)
                sections: Optional number of sections (default: auto-detect)
                mood_progression: Optional mood flow (e.g., "calm to energetic")

            Returns:
                dict with:
                - success: bool
                - composition_plan: Structured plan with sections
                - template_used: str (if template matched)
                - reasoning: str explaining the plan
            """
            try:
                logging.info(f"Creating composition plan: '{prompt[:50]}...'")

                # If mood progression specified, use progressive plan
                if mood_progression:
                    # Parse mood progression
                    parts = mood_progression.lower().split(" to ")
                    if len(parts) == 2:
                        start_mood, end_mood = parts
                        plan = self.planner.create_progressive_plan(
                            start_mood=start_mood.strip(),
                            end_mood=end_mood.strip(),
                            duration_ms=total_duration_ms,
                            num_sections=sections or 3
                        )

                        from dataclasses import asdict
                        return {
                            "success": True,
                            "composition_plan": asdict(plan) if hasattr(plan, '__dataclass_fields__') else plan,
                            "mood_progression": mood_progression,
                            "reasoning": f"Created progressive plan from {start_mood} to {end_mood}"
                        }

                # Otherwise create from prompt (may use template)
                plan = self.planner.create_plan_from_prompt(
                    prompt=prompt,
                    total_duration_ms=total_duration_ms,
                    num_sections=sections
                )

                # Check if a template was used
                template_used = None
                for template_name in ["focus_work", "energetic_workout", "calming_meditation",
                                     "creative_flow", "dramatic_build"]:
                    if template_name.replace("_", " ") in prompt.lower():
                        template_used = template_name
                        break

                from dataclasses import asdict
                plan_dict = asdict(plan) if hasattr(plan, '__dataclass_fields__') else plan

                return {
                    "success": True,
                    "composition_plan": plan_dict,
                    "template_used": template_used,
                    "total_duration_ms": total_duration_ms,
                    "sections_count": len(plan.sections) if hasattr(plan, 'sections') else len(plan_dict.get("sections", [])),
                    "reasoning": self._explain_plan(plan_dict if isinstance(plan_dict, dict) else plan, template_used)
                }

            except Exception as e:
                logging.error(f"Composition plan creation failed: {e}", exc_info=True)
                return {
                    "success": False,
                    "error": str(e),
                    "traceback": traceback.format_exc()
                }

        def _explain_plan(self, plan, template: str = None) -> str:
            """Generate human-readable explanation of composition plan."""
            # Handle both dict and dataclass formats
            if isinstance(plan, dict):
                sections = plan.get("sections", [])
            else:
                sections = plan.sections if hasattr(plan, 'sections') else []

            if not sections:
                return "Created basic plan"

            if template:
                return f"Used '{template}' template with {len(sections)} sections"

            # Describe the progression
            if len(sections) <= 1:
                first_section = sections[0]
                if isinstance(first_section, dict):
                    prompt = first_section.get('style', first_section.get('prompt', 'unknown'))
                else:
                    prompt = first_section.style if hasattr(first_section, 'style') else 'unknown'
                return f"Single section: {prompt}"

            # Get prompts from sections
            def get_prompt(section):
                if isinstance(section, dict):
                    return section.get('style', section.get('prompt', ''))
                return section.style if hasattr(section, 'style') else ''

            first = get_prompt(sections[0])
            last = get_prompt(sections[-1])
            return f"Created {len(sections)}-section plan progressing from '{first[:30]}...' to '{last[:30]}...'"
        
        # Tool 3: Generate from composition plan
        @self.server.tool()
        async def generate_music_structured(
            composition_plan: dict,
            strict_duration: bool = False,
            metadata: dict = None
        ) -> dict:
            """
            Generate music from a detailed composition plan.

            Uses a structured multi-section composition plan to create
            sophisticated music with mood progressions and transitions.

            Args:
                composition_plan: Structured plan from create_composition_plan
                    Must contain "sections" list with prompts and durations
                strict_duration: Enforce exact section durations (default: False)
                metadata: Optional metadata tags to include

            Returns:
                dict with:
                - success: bool
                - audio_path: str (if successful)
                - metadata: dict with composition details
                - sections_generated: int
                - total_duration_ms: int
                - error: str (if failed)
            """
            try:
                logging.info("Generating structured music from composition plan")

                # Validate composition plan
                if not composition_plan or "sections" not in composition_plan:
                    return {
                        "success": False,
                        "error": "Invalid composition_plan: must contain 'sections' list"
                    }

                sections = composition_plan.get("sections", [])
                if not sections:
                    return {
                        "success": False,
                        "error": "Composition plan has no sections"
                    }

                # Initialize generator session if needed
                if not self.generator.session:
                    await self.generator.__aenter__()

                # Generate music using structured method
                result = await self.generator.generate_structured(
                    composition_plan=composition_plan,
                    strict_duration=strict_duration
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
                            f"Copyright issue detected. Adjust your composition plan."
                        )
                    return response

                # Build comprehensive metadata
                file_metadata = metadata or {}
                file_metadata.update({
                    "composition_plan": composition_plan,
                    "sections_count": len(sections),
                    "total_duration_ms": sum(s.get("duration_ms", 0) for s in sections),
                    "strict_duration": strict_duration,
                    "generated_at": datetime.now().isoformat(),
                    "generation_type": "structured"
                })

                # Create descriptive prompt for filename
                first_section = sections[0].get("prompt", "structured_music")
                filename_prompt = f"{first_section} (structured)"

                # Save to filesystem
                audio_path, metadata_path = self.file_manager.save_music(
                    audio_data=result.audio_data,
                    metadata=file_metadata,
                    prompt=filename_prompt
                )

                logging.info(f"Structured music saved: {audio_path}")

                # Record preference for learning (Phase 2)
                if self.config.enable_preference_learning:
                    try:
                        self.preference_learner.record_generation(
                            prompt=filename_prompt,
                            metadata=file_metadata,
                            result_path=audio_path
                        )
                        logging.debug("Preference recorded for structured generation")
                    except Exception as e:
                        logging.warning(f"Failed to record preference: {e}")

                # Build response
                return {
                    "success": True,
                    "audio_path": str(audio_path),
                    "metadata_path": str(metadata_path),
                    "file_size_bytes": len(result.audio_data),
                    "sections_generated": len(sections),
                    "total_duration_ms": file_metadata["total_duration_ms"],
                    "composition_plan": composition_plan,
                    "message": f"Successfully generated {len(sections)}-section composition: {audio_path.name}"
                }

            except Exception as e:
                logging.error(f"Structured music generation failed: {e}", exc_info=True)
                return {
                    "success": False,
                    "error": str(e),
                    "traceback": traceback.format_exc()
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

            This is the "magic" tool that enables AI agents like Betty to
            automatically suggest music based on conversation context, user
            mood, and activity. Perfect for proactive music suggestions.

            Args:
                context: Text to analyze for mood (e.g., conversation snippet,
                    user message, journal entry)
                activity: Optional explicit activity (e.g., "coding", "writing")
                    If not provided, will attempt to infer from context
                time_of_day: Optional time context (e.g., "morning", "evening")
                recent_music: Optional list of recently generated prompts
                    Used to avoid repetition

            Returns:
                dict with:
                - success: bool
                - suggested_prompt: str (music prompt to use)
                - suggested_duration_ms: int
                - mood_detected: str
                - activity_detected: str
                - confidence: float (0.0-1.0)
                - reasoning: str (explanation of suggestion)
                - alternative_prompts: list (other options)
            """
            try:
                logging.info(f"Analyzing mood from context: '{context[:50]}...'")

                # Detect mood from context
                mood_result = self.context_analyzer.detect_mood(context)
                detected_mood = mood_result["mood"]
                mood_confidence = mood_result["confidence"]

                # Detect or use provided activity
                if activity:
                    detected_activity = activity
                    activity_confidence = 1.0
                else:
                    activity_result = self.context_analyzer.detect_activity(context)
                    detected_activity = activity_result["activity"]
                    activity_confidence = activity_result["confidence"]

                logging.info(f"Detected: mood={detected_mood} ({mood_confidence:.2f}), "
                           f"activity={detected_activity} ({activity_confidence:.2f})")

                # Get music suggestion based on detected context
                suggested_prompt = self.context_analyzer.suggest_music_for_context(
                    activity=detected_activity,
                    mood=detected_mood,
                    duration_ms=60000,  # Default duration
                    time_of_day=time_of_day
                )

                # Check preference learner for personalized recommendations
                recommendations = []
                if self.config.enable_preference_learning:
                    recommendations = self.preference_learner.get_recommendations(
                        activity=detected_activity,
                        mood=detected_mood,
                        limit=3
                    )

                # Generate alternative prompts
                alternatives = []
                if recommendations:
                    # Include user's past preferences
                    alternatives.extend(recommendations[:2])

                # Determine appropriate duration based on activity
                duration_map = {
                    "coding": 120000,      # 2 minutes
                    "writing": 90000,      # 1.5 minutes
                    "studying": 120000,    # 2 minutes
                    "exercising": 180000,  # 3 minutes
                    "relaxing": 120000,    # 2 minutes
                    "meeting": 60000,      # 1 minute
                }
                suggested_duration = duration_map.get(detected_activity, 60000)

                # Build reasoning explanation
                reasoning = self._build_reasoning(
                    detected_mood,
                    detected_activity,
                    mood_confidence,
                    activity_confidence,
                    time_of_day,
                    len(recommendations) > 0
                )

                # Calculate overall confidence
                overall_confidence = (mood_confidence + activity_confidence) / 2

                return {
                    "success": True,
                    "suggested_prompt": suggested_prompt,
                    "suggested_duration_ms": suggested_duration,
                    "mood_detected": detected_mood,
                    "activity_detected": detected_activity,
                    "mood_confidence": mood_confidence,
                    "activity_confidence": activity_confidence,
                    "overall_confidence": overall_confidence,
                    "reasoning": reasoning,
                    "alternative_prompts": alternatives,
                    "personalized": len(recommendations) > 0,
                    "time_of_day": time_of_day
                }

            except Exception as e:
                logging.error(f"Mood analysis failed: {e}", exc_info=True)
                return {
                    "success": False,
                    "error": str(e),
                    "traceback": traceback.format_exc()
                }

        def _build_reasoning(
            self,
            mood: str,
            activity: str,
            mood_conf: float,
            activity_conf: float,
            time_of_day: str = None,
            personalized: bool = False
        ) -> str:
            """Build human-readable reasoning for music suggestion."""
            parts = []

            # Mood reasoning
            if mood_conf > 0.7:
                parts.append(f"Detected strong {mood} mood")
            elif mood_conf > 0.4:
                parts.append(f"Detected {mood} mood")
            else:
                parts.append(f"Uncertain mood (guessing {mood})")

            # Activity reasoning
            if activity_conf > 0.7:
                parts.append(f"clearly doing {activity}")
            elif activity_conf > 0.4:
                parts.append(f"possibly {activity}")
            else:
                parts.append(f"activity unclear (guessing {activity})")

            # Time of day
            if time_of_day:
                parts.append(f"during {time_of_day}")

            # Personalization
            if personalized:
                parts.append("considering your past preferences")

            return "; ".join(parts) + "."
        
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


        logging.info("✅ Registered all MCP tools (Phase 1+2: music generation with composition planning, mood analysis, and preference learning)")
    
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
