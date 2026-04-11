from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from helper.database import SessionLocal
from helper.core.deps import get_current_user
from helper.models.report import Report

router = APIRouter()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get("/my-reports")
def get_reports(user=Depends(get_current_user), db: Session = Depends(get_db)):
    reports = db.query(Report).filter(Report.user_email == user["sub"]).all()
    return reports