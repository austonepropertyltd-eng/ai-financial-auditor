from typing import Any
from app.core.config import settings


def build_audit_prompt(company_name: str, period: str, financials: dict[str, Any]) -> str:
    return (
        f"You are an expert financial auditor. Analyze the financial data below and produce a concise audit summary, key findings, "
        f"and recommendations for internal controls or risk areas.\n\n"
        f"Company: {company_name}\n"
        f"Period: {period}\n"
        f"Financial data: {financials}\n"
    )


async def query_llm(prompt: str) -> str:
    import openai

    openai.api_key = settings.OPENAI_API_KEY
    response = await openai.ChatCompletion.acreate(
        model=settings.MODEL_NAME,
        messages=[
            {"role": "system", "content": "You are an experienced financial auditor."},
            {"role": "user", "content": prompt},
        ],
        temperature=0.2,
    )
    return response.choices[0].message["content"].strip()
