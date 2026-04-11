import pandas as pd

def analyze_financial_data(file_path):
    df = pd.read_excel(file_path)

    df.columns = [c.lower() for c in df.columns]

    if "amount" not in df.columns:
        return {"monthly": {}, "anomalies": []}

    df["amount"] = pd.to_numeric(df["amount"], errors="coerce")
    df = df.dropna(subset=["amount"])

    mean = df["amount"].mean()
    std = df["amount"].std()

    df["anomaly"] = abs(df["amount"] - mean) > (2 * std)

    anomalies = df[df["anomaly"]].to_dict(orient="records")

    monthly = df.groupby(df.index)["amount"].sum().to_dict()

    return {
        "monthly": monthly,
        "anomalies": anomalies
    }