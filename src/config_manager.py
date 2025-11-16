"""
Configuration management for ElevenLabs Music MCP Server
"""

import os
from pathlib import Path
from dataclasses import dataclass, field
from typing import Optional
import json


@dataclass
class Config:
    """Configuration for Music MCP Server."""
    
    # API Configuration
    api_key: str
    api_base_url: str = "https://api.elevenlabs.io/v1"
    api_timeout: int = 30
    
    # Output Directories
    music_output_dir: Path = Path.home() / "Music" / "ElevenLabs" / "generated"
    journal_output_dir: Path = Path.home() / "Music" / "ElevenLabs" / "journal"
    preference_storage_path: Path = Path.home() / "Music" / "ElevenLabs" / "preferences"
    
    # Generation Defaults
    default_output_format: str = "mp3_44100_128"
    default_duration_ms: int = 60000
    max_duration_ms: int = 300000
    min_duration_ms: int = 10000
    
    # Features
    enable_preference_learning: bool = True
    enable_journal_integration: bool = False  # Phase 3
    
    # Logging
    log_level: str = "INFO"
    log_file: Optional[Path] = None
    
    def __post_init__(self):
        """Ensure directories exist."""
        self.music_output_dir.mkdir(parents=True, exist_ok=True)
        self.journal_output_dir.mkdir(parents=True, exist_ok=True)
        self.preference_storage_path.mkdir(parents=True, exist_ok=True)
    
    @classmethod
    def from_env(cls) -> 'Config':
        """Load configuration from environment variables."""
        api_key = os.getenv("ELEVENLABS_API_KEY")
        if not api_key:
            raise ValueError("ELEVENLABS_API_KEY environment variable not set")
        
        return cls(
            api_key=api_key,
            api_base_url=os.getenv("ELEVENLABS_API_URL", cls.api_base_url),
            music_output_dir=Path(os.getenv(
                "MUSIC_OUTPUT_DIR",
                cls.music_output_dir
            )),
            journal_output_dir=Path(os.getenv(
                "JOURNAL_OUTPUT_DIR",
                cls.journal_output_dir
            )),
            enable_preference_learning=os.getenv(
                "ENABLE_PREFERENCE_LEARNING",
                "true"
            ).lower() == "true",
            log_level=os.getenv("LOG_LEVEL", "INFO")
        )
    
    @classmethod
    def from_file(cls, path: Path) -> 'Config':
        """Load configuration from JSON file."""
        with open(path) as f:
            data = json.load(f)
        
        # TODO: Implement full deserialization
        return cls(**data)
    
    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "api_base_url": self.api_base_url,
            "music_output_dir": str(self.music_output_dir),
            "journal_output_dir": str(self.journal_output_dir),
            "default_duration_ms": self.default_duration_ms,
            "enable_preference_learning": self.enable_preference_learning
        }


if __name__ == "__main__":
    # Test configuration loading
    try:
        config = Config.from_env()
        print("✅ Configuration loaded successfully")
        print(f"Output directory: {config.music_output_dir}")
    except Exception as e:
        print(f"❌ Configuration error: {e}")
