# AI Financial Auditor

A FastAPI project scaffold for an AI-powered financial auditor service.

## Features
- FastAPI REST API
- PostgreSQL database with SQLAlchemy models
- Transaction reconciliation service
- Anomaly detection and flagging
- LLM-based audit engine integration
- File upload and processing
- Environment-based configuration
- Database migrations with Alembic
- Comprehensive test scaffold

## Database Models
- **User**: User management and authentication
- **Transaction**: Financial transactions with categories and verification
- **File**: Uploaded financial files with processing status
- **Anomaly**: Detected financial irregularities with severity levels
- **TaxRecord**: Tax calculations and filing information

## API Endpoints
- `GET /health` - Health check
- `POST /upload` - File upload
- `POST /api/v1/audit` - AI-powered financial audit
- `POST /api/v1/reconcile` - Bank transaction reconciliation
- `GET /api/v1/reconciliation-report` - Reconciliation status report

## Getting Started

1. Create a virtual environment:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

2. Install dependencies:

```powershell
pip install -r requirements.txt
```

3. Set up the database:

```powershell
# Update DATABASE_URL in .env file
# Run migrations
alembic upgrade head
```

4. Copy `.env.example` to `.env` and configure:

```powershell
copy .env.example .env
# Edit .env with your OpenAI API key and database URL
```

5. Run the application:

```powershell
uvicorn app.main:app --reload
```

6. Open Swagger UI:

`http://127.0.0.1:8000/docs`
