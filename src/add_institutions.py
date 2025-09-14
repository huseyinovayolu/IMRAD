import pandas as pd
from pathlib import Path

WAGE_FILE = Path("output/processed_minimal.csv")
ICTWSS_FILE_ROOT = Path("Raw-ICTWSS.xlsx")
ICTWSS_FILE_ALT = Path("data/raw/Raw-ICTWSS.xlsx")
OUTPUT_FILE = Path("output/processed_with_inst.csv")

def find_ictwss() -> Path | None:
    if ICTWSS_FILE_ROOT.exists():
        return ICTWSS_FILE_ROOT
    if ICTWSS_FILE_ALT.exists():
        return ICTWSS_FILE_ALT
    return None

def load_institutional():
    path = find_ictwss()
    if not path:
        print("Kurumsal veri dosyası bulunamadı: Raw-ICTWSS.xlsx")
        return pd.DataFrame()
    try:
        df = pd.read_excel(path, sheet_name=0)
    except Exception:
        print("ICTWSS dosyası okunamadı.")
        return pd.DataFrame()
    return df

def standardize_country_code(s: pd.Series) -> pd.Series:
    return s.astype(str).str.upper().str.strip()

def main():
    if not WAGE_FILE.exists():
        print("Önce run_minimal.py çalıştırılmalı (output/processed_minimal.csv yok).")
        return
    wages = pd.read_csv(WAGE_FILE, parse_dates=["Date"])
    inst = load_institutional()
    if inst.empty:
        print("Kurumsal veri boş, birleşim atlandı.")
        return

    wages["year"] = wages["Date"].dt.year

    candidate_country_cols = [c for c in inst.columns if c.lower() in ("country", "code", "iso", "country_code")]
    candidate_year_cols = [c for c in inst.columns if c.lower() in ("year", "yr")]

    if not candidate_country_cols or not candidate_year_cols:
        print("Kurumsal veri sütunları tespit edilemedi. Sütun listesi:")
        print(list(inst.columns))
        return

    country_col = candidate_country_cols[0]
    year_col = candidate_year_cols[0]

    inst = inst.copy()
    inst["country_merge"] = standardize_country_code(inst[country_col])
    wages["country_merge"] = standardize_country_code(wages["Country"])

    target_vars = ["union_density", "coordination", "bargaining_coverage"]
    for tv in target_vars:
        if tv not in inst.columns:
            inst[tv] = None

    merged = wages.merge(
        inst[["country_merge", year_col] + target_vars],
        left_on=["country_merge", "year"],
        right_on=["country_merge", year_col],
        how="left",
        suffixes=("", "_inst"),
    ).drop(columns=[year_col])

    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    merged.to_csv(OUTPUT_FILE, index=False)
    print(f"Kurumsal birleşim tamamlandı: {OUTPUT_FILE}")
    print(merged[target_vars].head())

if __name__ == "__main__":
    main()
