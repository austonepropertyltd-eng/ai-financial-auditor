import pandas as pd


def normalize_columns(df):
    df.columns = [col.strip().lower() for col in df.columns]
    return df


def detect_amount_column(df):
    possible_names = [
        "amount", "amt", "value", "total",
        "transaction_amount", "balance"
    ]

    for col in df.columns:
        if col in possible_names:
            return col

    for col in df.columns:
        for name in possible_names:
            if name in col:
                return col

    raise Exception("No amount column detected")


def detect_date_column(df):
    possible_names = ["date", "transaction_date", "time"]

    for col in df.columns:
        if col in possible_names:
            return col

    for col in df.columns:
        for name in possible_names:
            if name in col:
                return col

    return None


def process_excel(file_path):
    df = pd.read_excel(file_path)

    df = normalize_columns(df)

    amount_col = detect_amount_column(df)
    date_col = detect_date_column(df)

    df.rename(columns={amount_col: "amount"}, inplace=True)

    df["amount"] = pd.to_numeric(df["amount"], errors="coerce")
    df = df.dropna(subset=["amount"])

    return df