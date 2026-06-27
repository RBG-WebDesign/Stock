# tests/test_orchestrator.py
import asyncio
import json
from pathlib import Path
import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from src.tqa.llm.orchestrator import AnalysisOrchestrator
from src.tqa.llm.openrouter import OpenRouterClient
from config.schemas import MasterAnalystOutput

@pytest.mark.asyncio
async def test_orchestrator_parallel_analysis():
    # 1. Setup mocks
    mock_analysis = MasterAnalystOutput(
        ticker="AAPL",
        primary_pattern="Cup and Handle",
        fundamental_catalyst="Strong earnings",
        suggested_entry_pivot=150.0,
        suggested_stop_loss=140.0,
        confidence_score=8,
        bull_case="Growth",
        bear_case_risks="Inflation"
    )

    tickers_data = [
        {"ticker": "AAPL", "chart_paths": {"daily": "d1", "weekly": "w1"}},
        {"ticker": "MSFT", "chart_paths": {"daily": "d2", "weekly": "w2"}},
    ]

    # Mock OpenRouterClient
    with patch("src.tqa.llm.orchestrator.OpenRouterClient") as MockClient:
        mock_instance = MockClient.return_value
        mock_instance.__aenter__.return_value = mock_instance
        mock_instance.analyze_ticker = AsyncMock(return_value=(mock_analysis, "mock_prompt"))
        
        # Mock _save_report to avoid file I/O
        with patch.object(AnalysisOrchestrator, "_save_report", new_callable=AsyncMock) as mock_save:
            orchestrator = AnalysisOrchestrator(semaphore_limit=2)
            results = await orchestrator.analyze_multiple(tickers_data)

            # 2. Assertions
            assert len(results) == 2
            assert results[0]["analysis"] == mock_analysis
            assert results[1]["analysis"] == mock_analysis
            assert mock_instance.analyze_ticker.call_count == 2
            assert mock_save.call_count == 2

@pytest.mark.asyncio
async def test_openrouter_client_context_manager():
    with patch("aiohttp.ClientSession") as MockSession:
        mock_session_instance = MockSession.return_value
        mock_session_instance.close = AsyncMock()
        
        async with OpenRouterClient() as client:
            assert client._session is not None
        
        assert client._session is None
        mock_session_instance.close.assert_called()

@pytest.mark.asyncio
async def test_robust_parsing():
    client = OpenRouterClient()
    
    # Test with markdown blocks
    content = "```json\n{\"ticker\": \"AAPL\", \"primary_pattern\": \"Pattern\", \"fundamental_catalyst\": \"Catalyst\", \"suggested_entry_pivot\": 100, \"suggested_stop_loss\": 90, \"confidence_score\": 7, \"bull_case\": \"Bull\", \"bear_case_risks\": \"Bear\"}\n```"
    result = await client._parse_and_validate(content, "AAPL", MasterAnalystOutput)
    assert result is not None
    assert result.ticker == "AAPL"

    # Test with plain JSON
    content = "{\"ticker\": \"MSFT\", \"primary_pattern\": \"Pattern\", \"fundamental_catalyst\": \"Catalyst\", \"suggested_entry_pivot\": 100, \"suggested_stop_loss\": 90, \"confidence_score\": 7, \"bull_case\": \"Bull\", \"bear_case_risks\": \"Bear\"}"
    result = await client._parse_and_validate(content, "MSFT", MasterAnalystOutput)
    assert result is not None
    assert result.ticker == "MSFT"

    # Test with malformed JSON
    content = "invalid json"
    result = await client._parse_and_validate(content, "INVALID", MasterAnalystOutput)
    assert result is None
