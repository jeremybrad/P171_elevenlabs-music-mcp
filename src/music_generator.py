"""
Music Generator - Interface with ElevenLabs Music API
"""

import aiohttp
import logging
import asyncio
from typing import Optional, Dict, Any
from dataclasses import dataclass
from pathlib import Path

logger = logging.getLogger(__name__)


@dataclass
class MusicResult:
    """Result from music generation."""
    success: bool
    audio_path: Optional[Path] = None
    audio_data: Optional[bytes] = None
    composition_plan: Optional[dict] = None
    duration_ms: Optional[int] = None
    error: Optional[str] = None
    suggested_prompt: Optional[str] = None


class MusicGenerationError(Exception):
    """Base exception for music generation errors."""
    pass


class CopyrightError(MusicGenerationError):
    """Copyrighted content detected in prompt."""
    def __init__(self, message: str, suggestion: str = None):
        super().__init__(message)
        self.suggestion = suggestion


class RateLimitError(MusicGenerationError):
    """API rate limit exceeded."""
    pass


class APIError(MusicGenerationError):
    """General API error."""
    def __init__(self, message: str, status_code: int = None):
        super().__init__(message)
        self.status_code = status_code


class MusicGenerator:
    """
    Generate music using ElevenLabs API.
    """

    def __init__(
        self,
        api_key: str,
        base_url: str = "https://api.elevenlabs.io/v1",
        timeout: int = 30,
        max_retries: int = 3
    ):
        self.api_key = api_key
        self.base_url = base_url
        self.timeout = aiohttp.ClientTimeout(total=timeout)
        self.max_retries = max_retries
        self.session: Optional[aiohttp.ClientSession] = None

    async def __aenter__(self):
        """Async context manager entry."""
        self.session = aiohttp.ClientSession(timeout=self.timeout)
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        if self.session:
            await self.session.close()

    def _get_headers(self) -> dict:
        """Get API request headers."""
        return {
            "xi-api-key": self.api_key,
            "Content-Type": "application/json"
        }

    async def _make_request_with_retry(
        self,
        method: str,
        url: str,
        **kwargs
    ) -> aiohttp.ClientResponse:
        """
        Make HTTP request with exponential backoff retry.

        Args:
            method: HTTP method (GET, POST, etc.)
            url: Full URL to request
            **kwargs: Additional arguments to pass to aiohttp

        Returns:
            Response object

        Raises:
            RateLimitError: If rate limit is exceeded
            APIError: For other API errors
        """
        last_exception = None

        for attempt in range(self.max_retries):
            try:
                if not self.session:
                    self.session = aiohttp.ClientSession(timeout=self.timeout)

                async with self.session.request(method, url, **kwargs) as response:
                    # Success
                    if response.status == 200:
                        return response

                    # Rate limit - retry with backoff
                    if response.status == 429:
                        retry_after = int(response.headers.get('Retry-After', 2 ** attempt))
                        logger.warning(f"Rate limited. Waiting {retry_after}s before retry {attempt + 1}/{self.max_retries}")
                        if attempt < self.max_retries - 1:
                            await asyncio.sleep(retry_after)
                            continue
                        raise RateLimitError("API rate limit exceeded. Please try again later.")

                    # Bad request - check for copyright error
                    if response.status == 400:
                        error_data = await response.json()
                        error_info = error_data.get('error', {})

                        if error_info.get('type') == 'bad_prompt':
                            suggested = error_info.get('suggested_prompt', '')
                            raise CopyrightError(
                                error_info.get('message', 'Copyrighted content detected'),
                                suggestion=suggested
                            )

                        raise APIError(error_info.get('message', 'Bad request'), status_code=400)

                    # Unauthorized
                    if response.status == 401:
                        raise APIError("Invalid API key", status_code=401)

                    # Other errors
                    error_text = await response.text()
                    raise APIError(
                        f"API error: {error_text}",
                        status_code=response.status
                    )

            except (aiohttp.ClientError, asyncio.TimeoutError) as e:
                last_exception = e
                logger.warning(f"Request failed (attempt {attempt + 1}/{self.max_retries}): {e}")
                if attempt < self.max_retries - 1:
                    await asyncio.sleep(2 ** attempt)  # Exponential backoff
                    continue

        raise APIError(f"Request failed after {self.max_retries} attempts: {last_exception}")

    async def generate_simple(
        self,
        prompt: str,
        duration_ms: Optional[int] = None,
        output_format: str = "mp3_44100_128"
    ) -> MusicResult:
        """
        Generate music from a simple text prompt.

        Args:
            prompt: Natural language description of desired music
            duration_ms: Optional duration in milliseconds (3000-300000)
            output_format: Audio format (default: mp3_44100_128)

        Returns:
            MusicResult with audio data and metadata

        Raises:
            CopyrightError: If prompt contains copyrighted content
            RateLimitError: If rate limit is exceeded
            APIError: For other API errors
        """
        try:
            logger.info(f"Generating music: '{prompt[:50]}...' (duration: {duration_ms}ms)")

            # Build request payload
            payload = {
                "prompt": prompt,
                "output_format": output_format
            }

            if duration_ms is not None:
                payload["duration_ms"] = duration_ms

            # Make API request
            url = f"{self.base_url}/music/compose"
            headers = self._get_headers()

            async with self.session.post(url, json=payload, headers=headers) as response:
                if response.status == 200:
                    # Get audio data
                    audio_data = await response.read()

                    # Try to extract composition plan from headers or response
                    composition_plan = {}
                    if 'x-composition-plan' in response.headers:
                        import json
                        composition_plan = json.loads(response.headers['x-composition-plan'])

                    logger.info(f"Successfully generated {len(audio_data)} bytes of audio")

                    return MusicResult(
                        success=True,
                        audio_data=audio_data,
                        composition_plan=composition_plan,
                        duration_ms=duration_ms
                    )

                # Handle errors
                elif response.status == 400:
                    error_data = await response.json()
                    error_info = error_data.get('error', {})

                    if error_info.get('type') == 'bad_prompt':
                        suggested = error_info.get('suggested_prompt', '')
                        return MusicResult(
                            success=False,
                            error=f"Copyright detected: {error_info.get('message')}",
                            suggested_prompt=suggested
                        )

                    return MusicResult(
                        success=False,
                        error=error_info.get('message', 'Bad request')
                    )

                elif response.status == 429:
                    return MusicResult(
                        success=False,
                        error="Rate limit exceeded. Please try again in a moment."
                    )

                elif response.status == 401:
                    return MusicResult(
                        success=False,
                        error="Invalid API key. Please check your ELEVENLABS_API_KEY."
                    )

                else:
                    error_text = await response.text()
                    return MusicResult(
                        success=False,
                        error=f"API error ({response.status}): {error_text}"
                    )

        except CopyrightError as e:
            logger.warning(f"Copyright error: {e}")
            return MusicResult(
                success=False,
                error=str(e),
                suggested_prompt=e.suggestion
            )

        except RateLimitError as e:
            logger.warning(f"Rate limit error: {e}")
            return MusicResult(
                success=False,
                error=str(e)
            )

        except Exception as e:
            logger.error(f"Generation failed: {e}", exc_info=True)
            return MusicResult(
                success=False,
                error=f"Unexpected error: {str(e)}"
            )

    async def generate_structured(
        self,
        composition_plan: dict,
        strict_duration: bool = False,
        output_format: str = "mp3_44100_128"
    ) -> MusicResult:
        """
        Generate music from a detailed composition plan.

        Args:
            composition_plan: Structured plan with sections, mood, etc.
            strict_duration: Enforce exact section durations
            output_format: Audio format (default: mp3_44100_128)

        Returns:
            MusicResult with audio data and metadata
        """
        try:
            logger.info(f"Generating structured music from plan")

            # Build request payload
            payload = {
                "composition_plan": composition_plan,
                "output_format": output_format,
                "strict_duration": strict_duration
            }

            # Make API request
            url = f"{self.base_url}/music/compose"
            headers = self._get_headers()

            async with self.session.post(url, json=payload, headers=headers) as response:
                if response.status == 200:
                    audio_data = await response.read()

                    logger.info(f"Successfully generated structured music ({len(audio_data)} bytes)")

                    return MusicResult(
                        success=True,
                        audio_data=audio_data,
                        composition_plan=composition_plan
                    )

                # Handle errors (same as generate_simple)
                elif response.status == 400:
                    error_data = await response.json()
                    error_info = error_data.get('error', {})
                    return MusicResult(
                        success=False,
                        error=error_info.get('message', 'Bad request')
                    )

                else:
                    error_text = await response.text()
                    return MusicResult(
                        success=False,
                        error=f"API error ({response.status}): {error_text}"
                    )

        except Exception as e:
            logger.error(f"Structured generation failed: {e}", exc_info=True)
            return MusicResult(
                success=False,
                error=f"Unexpected error: {str(e)}"
            )


# Example usage for testing
async def test_generator():
    """Test the music generator."""
    import os
    api_key = os.getenv("ELEVENLABS_API_KEY")
    if not api_key:
        print("❌ API key not set")
        return
    
    async with MusicGenerator(api_key) as generator:
        result = await generator.generate_simple(
            prompt="lo-fi beats for coding",
            duration_ms=30000
        )
        print(f"Result: {result}")


if __name__ == "__main__":
    import asyncio
    asyncio.run(test_generator())
