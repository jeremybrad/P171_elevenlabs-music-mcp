"""
File Manager - Organize and save generated music files
"""

from pathlib import Path
from typing import Optional, Dict, Any, Tuple
from datetime import datetime
import json
import re
import logging
import tempfile

logger = logging.getLogger(__name__)


class FileManager:
    """
    Manage music file organization and metadata.

    Features:
    - Date-based directory structure (YYYY-MM)
    - Descriptive filenames with slugs from prompts
    - Atomic file writes using temp files
    - Metadata storage as JSON
    - Counter to avoid duplicate names
    """

    def __init__(self, base_dir: Path):
        self.base_dir = Path(base_dir).expanduser()
        self.base_dir.mkdir(parents=True, exist_ok=True)
        logger.info(f"FileManager initialized with base directory: {self.base_dir}")

    def _create_slug(self, text: str, max_length: int = 30) -> str:
        """
        Create a filesystem-safe slug from text.

        Args:
            text: Input text (e.g., prompt)
            max_length: Maximum slug length

        Returns:
            Filesystem-safe slug

        Examples:
            "Lo-fi Hip Hop Beats" -> "lo_fi_hip_hop_beats"
            "Calm Piano (2 min)" -> "calm_piano_2_min"
        """
        if not text:
            return "music"

        # Convert to lowercase
        slug = text.lower()

        # Remove special characters, keep alphanumeric and spaces
        slug = re.sub(r'[^a-z0-9\s_-]', '', slug)

        # Replace spaces and multiple separators with single underscore
        slug = re.sub(r'[\s_-]+', '_', slug)

        # Remove leading/trailing underscores
        slug = slug.strip('_')

        # Truncate to max length
        if len(slug) > max_length:
            slug = slug[:max_length].rstrip('_')

        # Fallback if slug is empty
        return slug if slug else "music"

    def _get_next_counter(self, directory: Path, date_str: str, slug: str) -> int:
        """
        Get the next available counter for a filename.

        Args:
            directory: Directory to search
            date_str: Date string (e.g., "2025-11-16")
            slug: File slug

        Returns:
            Next available counter (1-999)
        """
        pattern = f"{date_str}_{slug}_*.mp3"
        existing_files = list(directory.glob(pattern))

        if not existing_files:
            return 1

        # Extract counters from existing files
        counters = []
        for file_path in existing_files:
            match = re.search(r'_(\d{3})\.mp3$', file_path.name)
            if match:
                counters.append(int(match.group(1)))

        return max(counters, default=0) + 1

    def _atomic_write(self, path: Path, data: bytes):
        """
        Write file atomically using a temporary file.

        Args:
            path: Target file path
            data: Data to write

        Raises:
            IOError: If write fails
        """
        # Create temp file in same directory for atomic rename
        temp_fd, temp_path = tempfile.mkstemp(
            dir=path.parent,
            suffix='.tmp',
            prefix='.elevenlabs_'
        )

        try:
            # Write data to temp file
            with open(temp_fd, 'wb') as f:
                f.write(data)

            # Atomic rename (on POSIX systems)
            Path(temp_path).rename(path)
            logger.debug(f"Atomically wrote {len(data)} bytes to {path}")

        except Exception as e:
            # Clean up temp file on error
            try:
                Path(temp_path).unlink(missing_ok=True)
            except:
                pass
            raise IOError(f"Failed to write file {path}: {e}")

    def save_music(
        self,
        audio_data: bytes,
        metadata: dict,
        prompt: Optional[str] = None
    ) -> Tuple[Path, Path]:
        """
        Save music audio and metadata with organized naming.

        Args:
            audio_data: Audio file bytes
            metadata: Metadata dictionary (must include 'prompt')
            prompt: Optional prompt override (uses metadata['prompt'] if not provided)

        Returns:
            Tuple of (audio_path, metadata_path)

        Examples:
            audio_path: ~/Music/ElevenLabs/generated/2025-11/2025-11-16_lo_fi_beats_001.mp3
            metadata_path: ~/Music/ElevenLabs/generated/2025-11/2025-11-16_lo_fi_beats_001.json
        """
        # Extract prompt
        prompt_text = prompt or metadata.get('prompt', 'music')

        # Create date-based directory
        now = datetime.now()
        date_dir = self.base_dir / now.strftime("%Y-%m")
        date_dir.mkdir(parents=True, exist_ok=True)

        # Generate filename components
        date_str = now.strftime("%Y-%m-%d_%H-%M-%S")
        slug = self._create_slug(prompt_text)
        counter = self._get_next_counter(date_dir, now.strftime("%Y-%m-%d"), slug)

        # Build filename
        filename_base = f"{now.strftime('%Y-%m-%d')}_{slug}_{counter:03d}"
        audio_path = date_dir / f"{filename_base}.mp3"
        metadata_path = date_dir / f"{filename_base}.json"

        # Save audio file atomically
        logger.info(f"Saving music to {audio_path}")
        self._atomic_write(audio_path, audio_data)

        # Save metadata file
        metadata_with_paths = {
            **metadata,
            "audio_path": str(audio_path),
            "saved_at": datetime.now().isoformat(),
            "file_size_bytes": len(audio_data)
        }

        metadata_json = json.dumps(metadata_with_paths, indent=2).encode('utf-8')
        self._atomic_write(metadata_path, metadata_json)

        logger.info(f"Saved music: {audio_path.name} ({len(audio_data)} bytes)")

        return audio_path, metadata_path

    def get_output_path(
        self,
        prefix: str = "generated",
        extension: str = "mp3",
        metadata: Optional[dict] = None
    ) -> Path:
        """
        Generate organized file path (legacy method).

        Args:
            prefix: Filename prefix
            extension: File extension
            metadata: Optional metadata

        Returns:
            Path object for new file
        """
        now = datetime.now()
        date_dir = self.base_dir / f"{now.year}-{now.month:02d}"
        date_dir.mkdir(parents=True, exist_ok=True)

        slug = prefix
        if metadata and 'prompt' in metadata:
            slug = self._create_slug(metadata['prompt'])

        counter = self._get_next_counter(date_dir, now.strftime("%Y-%m-%d"), slug)
        filename = f"{now.strftime('%Y-%m-%d')}_{slug}_{counter:03d}.{extension}"

        return date_dir / filename

    def save_audio(
        self,
        audio_data: bytes,
        metadata: Optional[dict] = None,
        prefix: str = "generated"
    ) -> Path:
        """
        Save audio file with metadata (legacy method).

        Args:
            audio_data: Audio bytes
            metadata: Optional metadata
            prefix: Filename prefix

        Returns:
            Path to saved audio file
        """
        if metadata:
            audio_path, _ = self.save_music(audio_data, metadata)
            return audio_path
        else:
            path = self.get_output_path(prefix=prefix)
            self._atomic_write(path, audio_data)
            return path

    def save_metadata(self, audio_path: Path, metadata: dict):
        """
        Save metadata JSON alongside audio file.

        Args:
            audio_path: Path to audio file
            metadata: Metadata dictionary
        """
        metadata_path = audio_path.with_suffix('.json')
        metadata_json = json.dumps(metadata, indent=2).encode('utf-8')
        self._atomic_write(metadata_path, metadata_json)


if __name__ == "__main__":
    # Test file manager
    import tempfile
    with tempfile.TemporaryDirectory() as tmpdir:
        fm = FileManager(Path(tmpdir))
        path = fm.get_output_path(prefix="test")
        print(f"✅ Generated path: {path}")
