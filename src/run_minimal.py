import argparse
from pathlib import Path
import pandas as pd
import numpy as np

PRIMARY_FILE = "All-matched-datas.xlsx"
ALT_PATH = Path("data/raw/All-matched-datas.xlsx")
OUTPUT_DIR = Path("output")
OUTPUT_FILE = OUTPUT_DIR / "processed_minimal.csv"

def find_data_file() -> Path | None:
    root_path = Path(PRIMARY_FILE)
    if root_path.exists():
        return root_path
    if ALT_PATH.exists():
        return ALT_PATH
    return None

def check_and_parse_dates(df: pd.DataFrame) -> pd.DataFrame:
    if "Date" not in df.columns:
        print("Uyarı: 'Date' sütunu yok.")
        return df
    try:
        df["Date"] = pd.to_datetime(df["Date"], errors="raise")
    except Exception:
        print("Tarih parse edilemedi. Örnek ilk 5 değer:")
        print(df["Date"].head())
        df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
    return df

def rebase_cpi(df: pd.DataFrame, contract_month: int = 1) -> pd.DataFrame:
    if "CPI_2015_100" not in df.columns:
        raise ValueError("CPI_2015_100 sütunu bulunamadı.")
    if "Country" not in df.columns:
        raise ValueError("Country sütunu bulunamadı.")
    df = df.sort_values(["Country", "Date"])
    rebased_frames = []
    for country, g in df.groupby("Country", group_keys=False):
        g = g.copy()
        g["month"] = g["Date"].dt.month
        current_base = np.nan
        cpi_rebased = []
        for _, row in g.iterrows():
            if row["month"] == contract_month:
                current_base = row["CPI_2015_100"]
            if pd.isna(current_base):
                cpi_rebased.append(np.nan)
            else:
                cpi_rebased.append(row["CPI_2015_100"] / current_base)
        g["cpi_rebased"] = cpi_rebased
        rebased_frames.append(g.drop(columns=["month"]))
    out = pd.concat(rebased_frames).sort_values(["Country", "Date"])
    return out

def compute_real_and_erosion(df: pd.DataFrame) -> pd.DataFrame:
    if "MonthlyWage" not in df.columns:
        raise ValueError("MonthlyWage sütunu yok.")
    if "cpi_rebased" not in df.columns:
        raise ValueError("cpi_rebased hesaplanmamış.")
    df = df.copy()
    df["real_wage"] = df["MonthlyWage"] / df["cpi_rebased"]
    df["erosion_gap"] = 1 - df["real_wage"]
    return df

def add_inflation_and_volatility(df: pd.DataFrame) -> pd.DataFrame:
    if "CPI_2015_100" not in df.columns:
        return df
    df = df.sort_values(["Country", "Date"])
    df["inflation_yoy"] = df.groupby("Country")["CPI_2015_100"].pct_change(12)
    df["volatility_12m"] = (
        df.groupby("Country")["inflation_yoy"]
        .rolling(12)
        .std()
        .reset_index(level=0, drop=True)
    )
    return df

def main(contract_month: int):
    data_path = find_data_file()
    if not data_path:
        print("Veri dosyası bulunamadı. All-matched-datas.xlsx ekleyin.")
        return
    df = pd.read_excel(data_path, sheet_name=0)
    if "CPI_2015_100" not in df.columns:
        try:
            df2 = pd.read_excel(data_path, sheet_name="Sheet2")
            if "CPI_2015_100" in df2.columns:
                df = df2
        except Exception:
            pass
    df = check_and_parse_dates(df)

    required = ["Country", "Date", "CPI_2015_100", "MonthlyWage"]
    missing = [c for c in required if c not in df.columns]
    if missing:
        print(f"Eksik zorunlu sütun(lar): {missing}")
        return

    df = rebase_cpi(df, contract_month=contract_month)
    df = compute_real_and_erosion(df)
    df = add_inflation_and_volatility(df)

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    df.to_csv(OUTPUT_FILE, index=False)
    print(f"Kaydedildi: {OUTPUT_FILE}")
    print(df.head())

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Minimal real wage erosion hesaplama")
    parser.add_argument("--contract-month", type=int, default=1, help="Kontrat başlangıç ayı (1,4 veya 7)")
    args = parser.parse_args()
    main(contract_month=args.contract_month)
