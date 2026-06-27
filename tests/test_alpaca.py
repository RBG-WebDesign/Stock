# tests/test_alpaca.py
import pytest
from unittest.mock import AsyncMock, patch
from src.tqa.execution.alpaca import AlpacaClient

@pytest.mark.asyncio
async def test_alpaca_client_init():
    client = AlpacaClient(key_id="test_key", secret_key="test_secret")
    assert client.key_id == "test_key"
    assert client.secret_key == "test_secret"
    assert "APCA-API-KEY-ID" in client.headers

@pytest.mark.asyncio
async def test_get_account_info_mock(monkeypatch):
    mock_account_data = {
        "id": "account_id_123",
        "buying_power": "400000.00",
        "cash": "100000.00"
    }

    class MockResponse:
        def __init__(self):
            self.status = 200
        async def json(self):
            return mock_account_data
        async def __aenter__(self):
            return self
        async def __aexit__(self, exc_type, exc_val, exc_tb):
            pass

    class MockSession:
        def get(self, *args, **kwargs):
            return MockResponse()
        async def close(self):
            pass

    client = AlpacaClient(key_id="test_key", secret_key="test_secret")
    client._session = MockSession()

    res = await client.get_account_info()
    assert res is not None
    assert res["id"] == "account_id_123"
    assert res["buying_power"] == "400000.00"

@pytest.mark.asyncio
async def test_submit_bracket_order_mock(monkeypatch):
    mock_order_data = {
        "id": "order_id_456",
        "symbol": "MITK",
        "qty": "10",
        "side": "buy",
        "type": "limit",
        "limit_price": "19.67"
    }

    class MockResponse:
        def __init__(self):
            self.status = 201
        async def json(self):
            return mock_order_data
        async def __aenter__(self):
            return self
        async def __aexit__(self, exc_type, exc_val, exc_tb):
            pass

    class MockSession:
        def post(self, url, json=None, **kwargs):
            # Assert payload structure is correct
            assert json is not None
            assert json["symbol"] == "MITK"
            assert json["qty"] == "10"
            assert json["order_class"] == "bracket"
            assert json["take_profit"]["limit_price"] == "23.60"
            assert json["stop_loss"]["stop_price"] == "18.10"
            return MockResponse()
        async def close(self):
            pass

    client = AlpacaClient(key_id="test_key", secret_key="test_secret")
    client._session = MockSession()

    res = await client.submit_bracket_order(
        symbol="MITK",
        entry_price=19.67,
        stop_loss=18.10,
        take_profit=23.60,
        qty=10
    )
    
    assert res is not None
    assert res["id"] == "order_id_456"
