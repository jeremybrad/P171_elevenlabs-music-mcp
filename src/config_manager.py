"""
Configuration management for ElevenLabs Music MCP Server
"""

import os
import logging
import sys
from pathlib import Path
from dataclasses import dataclass, field
from typing import Optional
import json


def setup_logging(log_level: str = "INFO", log_file: Optional[Path] = None):
    """
    Configure logging for the application.

    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR)
        log_file: Optional file path for logging
    """
    # Convert string level to logging constant
    numeric_level = getattr(logging, log_level.upper(), logging.INFO)

    # Configure basic format
    log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    date_format = '%Y-%m-%d %H:%M:%S'

    # Set up handlers
    handlers = [logging.StreamHandler(sys.stderr)]

    if log_file:
        log_file = Path(log_file)
        log_file.parent.mkdir(parents=True, exist_ok=True)
        handlers.append(logging.FileHandler(log_file))

    # Configure root logger
    logging.basicConfig(
        level=numeric_level,
        format=log_format,
        datefmt=date_format,
        handlers=handlers,
        force=True  # Override any existing configuration
    )

    # Reduce noise from third-party libraries
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)
    logging.getLogger("aiohttp").setLevel(logging.WARNING)

    logging.info(f"Logging initialized at {log_level} level")


@dataclass
class Config:
    """Configuration for Music MCP Server."""

    # API Configuration
    api_key: str
    api_base_url: str = "https://api.elevenlabs.io/v1"
    api_timeout: int = 30
    max_retries: int = 3

    # Output Directories
    music_output_dir: Path = Path.home() / "Music" / "ElevenLabs" / "generated"
    journal_output_dir: Path = Path.home() / "Music" / "ElevenLabs" / "journal"
    preference_storage_path: Path = Path.home() / "Music" / "ElevenLabs" / "preferences"

    # Generation Defaults
    default_output_format: str = "mp3_44100_128"
    default_duration_ms: int = 60000
    max_duration_ms: int = 300000
    min_duration_ms: int = 3000

    # Features
    enable_preference_learning: bool = True
    enable_journal_integration: bool = False  # Phase 3
    enable_mood_analysis: bool = False  # Phase 2

    # Logging
    log_level: str = "INFO"
    log_file: Optional[Path] = None

    # Development
    debug_mode: bool = False
    use_mock_api: bool = False

    def __post_init__(self):
        """Ensure directories exist and validate configuration."""
        # Expand user paths
        if isinstance(self.music_output_dir, str):
            self.music_output_dir = Path(self.music_output_dir).expanduser()
        if isinstance(self.journal_output_dir, str):
            self.journal_output_dir = Path(self.journal_output_dir).expanduser()
        if isinstance(self.preference_storage_path, str):
            self.preference_storage_path = Path(self.preference_storage_path).expanduser()
        if self.log_file and isinstance(self.log_file, str):
            self.log_file = Path(self.log_file).expanduser()

        # Create directories
        self.music_output_dir.mkdir(parents=True, exist_ok=True)
        self.journal_output_dir.mkdir(parents=True, exist_ok=True)
        self.preference_storage_path.mkdir(parents=True, exist_ok=True)

        # Validate configuration
        self.validate()

        # Set up logging
        setup_logging(self.log_level, self.log_file)

    def validate(self):
        """
        Validate configuration values.

        Raises:
            ValueError: If configuration is invalid
        """
        if not self.api_key:
            raise ValueError("ELEVENLABS_API_KEY is required")

        if not self.use_mock_api and not self.api_key.startswith("sk_"):
            raise ValueError(
                f"Invalid API key format. ElevenLabs API keys should start with 'sk_', "
                f"got: {self.api_key[:10]}..."
            )

        if self.min_duration_ms < 3000:
            raise ValueError("min_duration_ms must be at least 3000ms (3 seconds)")

        if self.max_duration_ms > 300000:
            raise ValueError("max_duration_ms cannot exceed 300000ms (5 minutes)")

        if self.min_duration_ms >= self.max_duration_ms:
            raise ValueError("min_duration_ms must be less than max_duration_ms")

        if self.api_timeout < 10:
            raise ValueError("api_timeout must be at least 10 seconds")

        return True
    
    @classmethod
    def from_env(cls) -> 'Config':
        """
        Load configuration from environment variables.

        Returns:
            Config instance with values from environment

        Raises:
            ValueError: If required environment variables are missing
        """
        # Load .env file if python-dotenv is available
        try:
            from dotenv import load_dotenv
            load_dotenv()
        except ImportError:
            # python-dotenv not installed, that's okay in test environments
            pass

        api_key = os.getenv("ELEVENLABS_API_KEY", "")
        if not api_key:
            raise ValueError(
                "ELEVENLABS_API_KEY environment variable not set. "
                "Please set it in your .env file or environment."
            )

        # Helper to parse boolean env vars
        def parse_bool(value: str, default: bool = False) -> bool:
            if value == "":
                return default
            return value.lower() in ("true", "1", "yes", "on")

        return cls(
            api_key=api_key,
            api_base_url=os.getenv("ELEVENLABS_API_URL", "https://api.elevenlabs.io/v1"),
            api_timeout=int(os.getenv("API_TIMEOUT_SECONDS", "30")),
            max_retries=int(os.getenv("MAX_RETRIES", "3")),
            music_output_dir=Path(os.getenv("MUSIC_OUTPUT_DIR", "~/Music/ElevenLabs/generated")).expanduser(),
            journal_output_dir=Path(os.getenv("JOURNAL_OUTPUT_DIR", "~/Music/ElevenLabs/journal")).expanduser(),
            preference_storage_path=Path(os.getenv("PREFERENCE_STORAGE_PATH", "~/Music/ElevenLabs/preferences")).expanduser(),
            default_output_format=os.getenv("DEFAULT_OUTPUT_FORMAT", "mp3_44100_128"),
            default_duration_ms=int(os.getenv("DEFAULT_DURATION_MS", "60000")),
            enable_preference_learning=parse_bool(os.getenv("ENABLE_PREFERENCE_LEARNING", "true")),
            enable_journal_integration=parse_bool(os.getenv("ENABLE_JOURNAL_INTEGRATION", "false")),
            enable_mood_analysis=parse_bool(os.getenv("ENABLE_MOOD_ANALYSIS", "false")),
            log_level=os.getenv("LOG_LEVEL", "INFO"),
            log_file=Path(os.getenv("LOG_FILE", "")).expanduser() if os.getenv("LOG_FILE") else None,
            debug_mode=parse_bool(os.getenv("DEBUG_MODE", "false")),
            use_mock_api=parse_bool(os.getenv("USE_MOCK_API", "false")),
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
