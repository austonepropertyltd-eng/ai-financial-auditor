import pandas as pd

def analyze_financial_data(df: pd.DataFrame):

    if "amount" not in df.columns:
        return {"monthly": {}, "anomalies": [], "insight": "No financial data found."}

    df["amount"] = pd.to_numeric(df["amount"], errors="coerce")
    df = df.dropna(subset=["amount"])

    # Monthly grouping
    if "date" in df.columns:
        df["date"] = pd.to_datetime(df["date"], errors="coerce")
        df = df.dropna(subset=["date"])
        df["month"] = df["date"].dt.strftime("%Y-%m")
        monthly = df.groupby("month")["amount"].sum().to_dict()
    else:
        monthly = {"Total": df["amount"].sum()}

    # Stats
    total = df["amount"].sum()
    avg = df["amount"].mean()

    # Anomalies
    mean = df["amount"].mean()
    std = df["amount"].std()

    df["anomaly"] = abs(df["amount"] - mean) > (2 * std)
    anomalies = df[df["anomaly"] == True].to_dict(orient="records")

    # 🔥 AI INSIGHT
    insight = f"""
    Total transaction volume is {total:.2f}.
    Average transaction is {avg:.2f}.
    Detected {len(anomalies)} unusual transactions.
    """

    return {
        "monthly": monthly,
        "anomalies": anomalies,
        "insight": insight
    }