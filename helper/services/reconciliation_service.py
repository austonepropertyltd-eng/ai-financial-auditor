from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_, func
from difflib import SequenceMatcher
import re

from app.models.transaction import Transaction
from app.models.anomaly import Anomaly
from app.models.file import File
from app.utils.logger import get_logger

logger = get_logger(__name__)


class ReconciliationService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def reconcile_bank_transactions(
        self,
        bank_transactions: List[Dict[str, Any]],
        user_id: int,
        file_id: Optional[int] = None,
        tolerance_days: int = 3,
        amount_tolerance: float = 0.01
    ) -> Dict[str, Any]:
        """
        Reconcile bank transactions against existing transactions in the database.

        Args:
            bank_transactions: List of bank transaction dicts with keys: date, amount, description
            user_id: User ID for filtering transactions
            file_id: Optional file ID for tracking
            tolerance_days: Days tolerance for date matching
            amount_tolerance: Amount tolerance for matching (as percentage)

        Returns:
            Dict with matched, unmatched, and flagged transactions
        """
        matched = []
        unmatched = []
        flagged = []

        for bank_tx in bank_transactions:
            match_result = await self._find_transaction_match(
                bank_tx, user_id, tolerance_days, amount_tolerance
            )

            if match_result["matched"]:
                matched.append({
                    "bank_transaction": bank_tx,
                    "internal_transaction": match_result["transaction"],
                    "match_score": match_result["score"],
                    "match_type": match_result["match_type"]
                })
            else:
                unmatched.append(bank_tx)
                # Create anomaly for unmatched transaction
                anomaly = await self._create_unmatched_anomaly(bank_tx, user_id, file_id)
                flagged.append({
                    "transaction": bank_tx,
                    "anomaly": anomaly
                })

        return {
            "matched": matched,
            "unmatched": unmatched,
            "flagged": flagged,
            "summary": {
                "total_bank_transactions": len(bank_transactions),
                "matched_count": len(matched),
                "unmatched_count": len(unmatched),
                "match_rate": len(matched) / len(bank_transactions) if bank_transactions else 0
            }
        }

    async def _find_transaction_match(
        self,
        bank_tx: Dict[str, Any],
        user_id: int,
        tolerance_days: int,
        amount_tolerance: float
    ) -> Dict[str, Any]:
        """
        Find matching internal transaction for a bank transaction.
        """
        bank_date = bank_tx["date"]
        bank_amount = bank_tx["amount"]
        bank_description = bank_tx.get("description", "").lower()

        # Date range for matching
        date_from = bank_date - timedelta(days=tolerance_days)
        date_to = bank_date + timedelta(days=tolerance_days)

        # Amount range for matching
        amount_min = bank_amount * (1 - amount_tolerance)
        amount_max = bank_amount * (1 + amount_tolerance)

        # Query for potential matches
        stmt = select(Transaction).where(
            and_(
                Transaction.user_id == user_id,
                Transaction.transaction_date >= date_from,
                Transaction.transaction_date <= date_to,
                Transaction.amount >= amount_min,
                Transaction.amount <= amount_max,
                Transaction.is_verified == False  # Only match unverified transactions
            )
        )

        result = await self.db.execute(stmt)
        candidates = result.scalars().all()

        if not candidates:
            return {"matched": False, "transaction": None, "score": 0, "match_type": None}

        # Score candidates based on multiple factors
        scored_candidates = []
        for candidate in candidates:
            score = self._calculate_match_score(bank_tx, candidate)
            scored_candidates.append((candidate, score))

        # Sort by score (highest first)
        scored_candidates.sort(key=lambda x: x[1], reverse=True)
        best_match, best_score = scored_candidates[0]

        # Consider it a match if score is above threshold
        match_threshold = 0.7
        if best_score >= match_threshold:
            return {
                "matched": True,
                "transaction": best_match,
                "score": best_score,
                "match_type": self._determine_match_type(best_score)
            }

        return {"matched": False, "transaction": None, "score": best_score, "match_type": None}

    def _calculate_match_score(self, bank_tx: Dict[str, Any], internal_tx: Transaction) -> float:
        """
        Calculate match score between bank and internal transaction.
        """
        score = 0.0
        total_weight = 0.0

        # Amount match (40% weight)
        bank_amount = abs(bank_tx["amount"])
        internal_amount = abs(float(internal_tx.amount))
        if bank_amount == internal_amount:
            score += 0.4
        elif abs(bank_amount - internal_amount) / max(bank_amount, internal_amount) < 0.05:
            score += 0.3
        total_weight += 0.4

        # Date match (30% weight)
        bank_date = bank_tx["date"]
        internal_date = internal_tx.transaction_date.replace(tzinfo=None)
        days_diff = abs((bank_date - internal_date).days)
        if days_diff == 0:
            score += 0.3
        elif days_diff <= 1:
            score += 0.25
        elif days_diff <= 3:
            score += 0.2
        total_weight += 0.3

        # Description similarity (30% weight)
        bank_desc = bank_tx.get("description", "").lower()
        internal_desc = (internal_tx.description or "").lower()

        if bank_desc and internal_desc:
            # Clean descriptions for better matching
            bank_clean = self._clean_description(bank_desc)
            internal_clean = self._clean_description(internal_desc)

            similarity = SequenceMatcher(None, bank_clean, internal_clean).ratio()
            score += similarity * 0.3
            total_weight += 0.3
        else:
            total_weight += 0.3  # Still count the weight even if no description

        return score / total_weight if total_weight > 0 else 0.0

    def _clean_description(self, description: str) -> str:
        """
        Clean transaction description for better matching.
        """
        # Remove common noise words and characters
        noise_words = ['debit', 'credit', 'payment', 'transfer', 'withdrawal', 'deposit']
        desc = description.lower()

        # Remove special characters and extra spaces
        desc = re.sub(r'[^\w\s]', ' ', desc)
        desc = re.sub(r'\s+', ' ', desc).strip()

        # Remove noise words
        words = desc.split()
        filtered_words = [word for word in words if word not in noise_words]
        return ' '.join(filtered_words)

    def _determine_match_type(self, score: float) -> str:
        """
        Determine match type based on score.
        """
        if score >= 0.9:
            return "exact"
        elif score >= 0.8:
            return "high_confidence"
        elif score >= 0.7:
            return "medium_confidence"
        else:
            return "low_confidence"

    async def _create_unmatched_anomaly(
        self,
        bank_tx: Dict[str, Any],
        user_id: int,
        file_id: Optional[int]
    ) -> Anomaly:
        """
        Create an anomaly for unmatched bank transaction.
        """
        anomaly = Anomaly(
            file_id=file_id,
            anomaly_type="unmatched_bank_transaction",
            severity="medium",
            description=f"Unmatched bank transaction: {bank_tx.get('description', 'No description')} - Amount: ${bank_tx['amount']:.2f} on {bank_tx['date'].strftime('%Y-%m-%d')}",
            confidence_score=0.8,
            detected_data={
                "bank_transaction": {
                    "date": bank_tx["date"].isoformat(),
                    "amount": bank_tx["amount"],
                    "description": bank_tx.get("description", "")
                }
            },
            ai_analysis="This bank transaction could not be matched with any internal records. This may indicate missing transaction recording, timing differences, or potential fraudulent activity.",
            status="detected"
        )

        self.db.add(anomaly)
        await self.db.commit()
        await self.db.refresh(anomaly)

        logger.info(f"Created anomaly for unmatched bank transaction: {bank_tx}")
        return anomaly

    async def get_reconciliation_report(self, user_id: int, days_back: int = 30) -> Dict[str, Any]:
        """
        Generate a reconciliation report for recent transactions.
        """
        cutoff_date = datetime.now() - timedelta(days=days_back)

        # Get recent anomalies
        stmt = select(Anomaly).where(
            and_(
                Anomaly.anomaly_type == "unmatched_bank_transaction",
                Anomaly.created_at >= cutoff_date
            )
        ).order_by(Anomaly.created_at.desc())

        result = await self.db.execute(stmt)
        recent_anomalies = result.scalars().all()

        # Get transaction statistics
        stmt = select(
            func.count(Transaction.id).label("total_transactions"),
            func.sum(Transaction.amount).label("total_amount"),
            func.count(Transaction.id).filter(Transaction.is_verified == True).label("verified_count")
        ).where(
            and_(
                Transaction.user_id == user_id,
                Transaction.created_at >= cutoff_date
            )
        )

        result = await self.db.execute(stmt)
        stats = result.first()

        return {
            "period_days": days_back,
            "statistics": {
                "total_transactions": stats.total_transactions or 0,
                "verified_transactions": stats.verified_count or 0,
                "unverified_transactions": (stats.total_transactions or 0) - (stats.verified_count or 0),
                "total_amount": float(stats.total_amount or 0)
            },
            "anomalies": [
                {
                    "id": anomaly.id,
                    "description": anomaly.description,
                    "severity": anomaly.severity,
                    "status": anomaly.status,
                    "created_at": anomaly.created_at.isoformat()
                }
                for anomaly in recent_anomalies
            ]
        }