# tests/test_openrouter.py
import asyncio
import os
import json
from pathlib import Path
import pytest
from tqa.llm.openrouter import OpenRouterClient, encode_image_base64
from config.settings import settings
from config.schemas import MasterAnalystOutput

# Set up dummy chart paths for testing
DUMMY_CHART_DIR = Path("data/charts")
DUMMY_DAILY = DUMMY_CHART_DIR / "TEST_daily.png"
DUMMY_WEEKLY = DUMMY_CHART_DIR / "TEST_weekly.png"

def create_dummy_charts():
    """Creates empty files to act as dummy charts if they don't exist."""
    DUMMY_CHART_DIR.mkdir(parents=True, exist_ok=True)
    if not DUMMY_DAILY.exists():
        with open(DUMMY_DAILY, "wb") as f:
            f.write(b"dummy daily chart content")
    if not DUMMY_WEEKLY.exists():
        with open(DUMMY_WEEKLY, "wb") as f:
            f.write(b"dummy weekly chart content")

@pytest.mark.asyncio
async def test_encode_image_base64():
    create_dummy_charts()
    encoded = await encode_image_base64(str(DUMMY_DAILY))
    assert isinstance(encoded, str)
    assert len(encoded) > 0

@pytest.mark.asyncio
async def test_openrouter_client_init():
    client = OpenRouterClient(api_key="test_key")
    assert client.api_key == "test_key"
    assert "system_prompts" in client.prompts_config
    assert "user_prompts" in client.prompts_config

@pytest.mark.asyncio
async def test_analyze_ticker_mock(monkeypatch):
    """
    Tests the analyze_ticker method with a mocked aiohttp response.
    """
    create_dummy_charts()
    
    mock_response_data = {
        "choices": [{
            "message": {
                "content": json.dumps({
                    "ticker": "AAPL",
                    "primary_pattern": "Cup and Handle",
                    "fundamental_catalyst": "Strong iPhone sales",
                    "suggested_entry_pivot": 150.0,
                    "suggested_stop_loss": 140.0,
                    "confidence_score": 8,
                    "bull_case": "Growth is accelerating",
                    "bear_case_risks": "Supply chain issues"
                })
            }
        }]
    }

    class MockResponse:
        def __init__(self):
            self.status = 200
        async def json(self):
            return mock_response_data
        async def __aenter__(self):
            return self
        async def __aexit__(self, exc_type, exc_val, exc_tb):
            pass

    class MockSession:
        def post(self, *args, **kwargs):
            return MockResponse()
        async def __aenter__(self):
            return self
        async def __aexit__(self, exc_type, exc_val, exc_tb):
            pass

    monkeypatch.setattr("aiohttp.ClientSession", lambda: MockSession())

    client = OpenRouterClient(api_key="test_key")
    result, prompt = await client.analyze_ticker(
        ticker="AAPL",
        fundamentals={"some": "data"},
        chart_paths={"daily": str(DUMMY_DAILY), "weekly": str(DUMMY_WEEKLY)}
    )

    assert isinstance(result, MasterAnalystOutput)
    assert result.ticker == "AAPL"
    assert result.confidence_score == 8
    assert isinstance(prompt, str)

if __name__ == "__main__":
    # Simple manual run
    async def main():
        print("Running manual test...")
        try:
            await test_analyze_ticker_mock(None) # This won't work easily with monkeypatch manually
            print("Mock test passed!")
        except Exception as e:
            print(f"Test failed: {e}")

    # asyncio.run(main())
