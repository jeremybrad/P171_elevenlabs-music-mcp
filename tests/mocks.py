# Mock responses for testing

class MockAPIResponse:
    """Mock successful API response"""
    def __init__(self, audio_data: bytes = b"fake audio data"):
        self.status_code = 200
        self.content = audio_data
        self._json = {
            "composition_plan": {
                "style": "lo-fi hip hop",
                "tempo": 70,
                "key": "C minor"
            },
            "metadata": {
                "duration_ms": 30000,
                "format": "mp3_44100_128"
            }
        }
    
    def json(self):
        return self._json

class MockCopyrightError:
    """Mock copyright error response"""
    def __init__(self):
        self.status_code = 400
        self._json = {
            "error": {
                "type": "bad_prompt",
                "message": "Prompt contains copyrighted material",
                "suggested_prompt": "gentle piano in the style of classical music"
            }
        }
    
    def json(self):
        return self._json

# Pytest fixtures for mocks
import pytest

@pytest.fixture
def mock_successful_response():
    return MockAPIResponse()

@pytest.fixture
def mock_copyright_error():
    return MockCopyrightError()
