from fastapi import APIRouter

router = APIRouter()

@router.get("/partner/dashboard")
def partner_dashboard():
    return {
        "total_reports": 10,
        "total_value": 12000000,
        "total_tax": 1500000,
        "clients": 5,
        "revenue": 300000
    }