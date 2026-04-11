import pytest
from datetime import datetime, timedelta
from unittest.mock import AsyncMock, MagicMock
from app.services.reconciliation_service import ReconciliationService


@pytest.fixture
def mock_db():
    return AsyncMock()


@pytest.fixture
def reconciliation_service(mock_db):
    return ReconciliationService(mock_db)


@pytest.mark.asyncio
async def test_reconcile_bank_transactions(reconciliation_service, mock_db):
    # Mock bank transactions
    bank_transactions = [
        {
            "date": datetime(2024, 1, 15),
            "amount": -100.00,
            "description": "Grocery Store Purchase"
        },
        {
            "date": datetime(2024, 1, 16),
            "amount": 500.00,
            "description": "Salary Deposit"
        }
    ]

    # Mock internal transactions
    mock_transaction = MagicMock()
    mock_transaction.id = 1
    mock_transaction.amount = -100.00
    mock_transaction.transaction_date = datetime(2024, 1, 15)
    mock_transaction.description = "Grocery Store"
    mock_transaction.is_verified = False

    # Mock database query result
    mock_result = MagicMock()
    mock_result.scalars.return_value.all.return_value = [mock_transaction]
    mock_db.execute.return_value = mock_result

    # Mock anomaly creation
    mock_anomaly = MagicMock()
    mock_anomaly.id = 1
    mock_anomaly.description = "Unmatched bank transaction"
    mock_db.add.return_value = None
    mock_db.commit.return_value = None
    mock_db.refresh.return_value = None

    result = await reconciliation_service.reconcile_bank_transactions(
        bank_transactions=bank_transactions,
        user_id=1,
        tolerance_days=3,
        amount_tolerance=0.01
    )

    assert "matched" in result
    assert "unmatched" in result
    assert "flagged" in result
    assert "summary" in result
    assert result["summary"]["total_bank_transactions"] == 2


def test_calculate_match_score(reconciliation_service):
    bank_tx = {
        "date": datetime(2024, 1, 15),
        "amount": -100.00,
        "description": "Grocery Store Purchase"
    }

    # Create mock internal transaction
    mock_internal_tx = MagicMock()
    mock_internal_tx.amount = -100.00
    mock_internal_tx.transaction_date = datetime(2024, 1, 15)
    mock_internal_tx.description = "Grocery Store"

    score = reconciliation_service._calculate_match_score(bank_tx, mock_internal_tx)

    # Should be high score for exact matches
    assert score > 0.9


def test_clean_description(reconciliation_service):
    dirty_desc = "DEBIT PURCHASE - GROCERY STORE #123"
    clean_desc = reconciliation_service._clean_description(dirty_desc)

    assert "debit" not in clean_desc.lower()
    assert "purchase" not in clean_desc.lower()
    assert "grocery" in clean_desc.lower()
    assert "store" in clean_desc.lower()


def test_determine_match_type(reconciliation_service):
    assert reconciliation_service._determine_match_type(0.95) == "exact"
    assert reconciliation_service._determine_match_type(0.85) == "high_confidence"
    assert reconciliation_service._determine_match_type(0.75) == "medium_confidence"
    assert reconciliation_service._determine_match_type(0.65) == "low_confidence"