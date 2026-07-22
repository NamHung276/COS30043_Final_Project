import pytest
from unittest.mock import patch, AsyncMock
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

@pytest.fixture
def mock_payment_service():
    with patch("app.routers.payments.payment_service", autospec=True) as mock:
        yield mock

@pytest.fixture
def mock_crypto_service():
    with patch("app.routers.payments.crypto_service", autospec=True) as mock:
        yield mock

def test_create_paypal_order_success(mock_payment_service):
    # Setup mock
    mock_payment_service.create_order = AsyncMock(return_value={"id": "ORDER123", "status": "CREATED"})
    
    # Test request
    response = client.post(
        "/api/payments/paypal/create-order",
        json={"amount": 25.50, "currency": "USD", "description": "Test Game Purchase"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["order_id"] == "ORDER123"
    assert data["status"] == "CREATED"
    
    mock_payment_service.create_order.assert_called_once_with(
        amount=25.50, currency="USD", description="Test Game Purchase"
    )

def test_capture_paypal_order_success(mock_payment_service):
    mock_payment_service.capture_order = AsyncMock(return_value={"id": "ORDER123", "status": "COMPLETED"})
    
    response = client.post(
        "/api/payments/paypal/capture-order",
        json={"order_id": "ORDER123"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "COMPLETED"
    
    mock_payment_service.capture_order.assert_called_once_with(order_id="ORDER123")

def test_get_crypto_rates_success(mock_crypto_service):
    mock_crypto_service.get_exchange_rates = AsyncMock(return_value={
        "bitcoin": {"usd": 50000},
        "ethereum": {"usd": 3000}
    })
    
    response = client.get("/api/payments/crypto-rates?currency=usd")
    
    assert response.status_code == 200
    data = response.json()
    assert "rates" in data
    assert data["rates"]["bitcoin"]["usd"] == 50000
    assert data["rates"]["ethereum"]["usd"] == 3000
    
    mock_crypto_service.get_exchange_rates.assert_called_once_with(vs_currency="usd")
