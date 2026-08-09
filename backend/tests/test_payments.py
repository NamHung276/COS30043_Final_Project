import pytest
from unittest.mock import patch, AsyncMock
from fastapi.testclient import TestClient
from main import app
from app.utils.dependencies import get_current_user
from app.models.user import UserContext

client = TestClient(app)

def mock_get_current_user():
    return UserContext(uid="test_user", email="test@example.com")

app.dependency_overrides[get_current_user] = mock_get_current_user

@pytest.fixture
def mock_payment_service():
    with patch("app.routers.payments.payment_service", autospec=True) as mock:
        yield mock

@pytest.fixture
def mock_crypto_service():
    with patch("app.routers.payments.crypto_service", autospec=True) as mock:
        yield mock

@pytest.fixture
def mock_get_game_detail():
    with patch("app.routers.payments.get_game_detail", autospec=True) as mock:
        yield mock

@patch("app.routers.payments.get_game_detail")
@patch("app.routers.payments.payment_service")
def test_create_paypal_order_success(mock_payment_service, mock_get_game_detail):
    # Setup mock
    mock_payment_service.create_order = AsyncMock(return_value={"id": "ORDER123", "status": "CREATED"})
    mock_get_game_detail.return_value = {"price": {"final": 25.50}, "title": "Test Game"}
    
    # Test request
    response = client.post(
        "/api/payments/paypal/create-order",
        json={"items": ["steam-123"], "currency": "USD", "description": "Test Game Purchase"}
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
    assert data["success"] == True
    assert data["transaction_id"] == "ORDER123"
    
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
