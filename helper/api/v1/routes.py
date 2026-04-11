from fastapi import APIRouter, HTTPException, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Dict, Any, Optional
from app.schemas.audit import AuditRequest, AuditResponse
from app.schemas.reconciliation import ReconciliationRequest, ReconciliationResponse, ReconciliationReport
from app.services.audit_service import run_financial_audit
from app.services.reconciliation_service import ReconciliationService
from app.core.database import get_db

router = APIRouter(tags=["audit"])

@router.post("/audit", response_model=AuditResponse)
async def audit_financial_report(request: AuditRequest):
    try:
        return await run_financial_audit(request)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))

@router.post("/reconcile", response_model=ReconciliationResponse)
async def reconcile_bank_transactions(
    request: ReconciliationRequest,
    db: AsyncSession = Depends(get_db)
):
    try:
        service = ReconciliationService(db)
        result = await service.reconcile_bank_transactions(
            bank_transactions=request.bank_transactions,
            user_id=request.user_id,
            file_id=request.file_id,
            tolerance_days=request.tolerance_days,
            amount_tolerance=request.amount_tolerance
        )
        return ReconciliationResponse(**result)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))

@router.get("/reconciliation-report", response_model=ReconciliationReport)
async def get_reconciliation_report(
    user_id: int = Query(..., description="User ID"),
    days_back: int = Query(30, description="Days to look back"),
    db: AsyncSession = Depends(get_db)
):
    try:
        service = ReconciliationService(db)
        report = await service.get_reconciliation_report(user_id, days_back)
        return ReconciliationReport(**report)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))
