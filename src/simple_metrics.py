import pandas as pd
from pathlib import Path

INPUT = Path("output/processed_with_inst.csv")
FALLBACK = Path("output/processed_minimal.csv")
OUTPUT = Path("output/erosion_metrics.csv")

def compute_metrics(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["year"] = df["Date"].dt.year
    rows = []
    for (country, year), g in df.groupby(["Country", "year"]):
        g = g.sort_values("Date")
        mean_erosion = g["erosion_gap"].mean()
        peak_erosion = g["erosion_gap"].max()
        rec_idx = g.index[g["erosion_gap"] <= 0].tolist()
        if rec_idx:
            first_rec_pos = g.index.get_loc(rec_idx[0]) + 1
        else:
            first_rec_pos = None
        rows.append(
            {
                "Country": country,
                "year": year,
                "mean_erosion": mean_erosion,
                "peak_erosion": peak_erosion,
                "months_to_recovery": first_rec_pos,
            }
        )
    return pd.DataFrame(rows)

def main():
    if INPUT.exists():
        df = pd.read_csv(INPUT, parse_dates=["Date"])
    elif FALLBACK.exists():
        df = pd.read_csv(FALLBACK, parse_dates=["Date"])
    else:
        print("Önce run_minimal.py (ve isteğe bağlı add_institutions.py) çalıştırılmalı.")
        return

    required = {"Date", "Country", "erosion_gap"}
    if not required.issubset(df.columns):
        print("Gerekli sütunlar eksik:", required - set(df.columns))
        return

    metrics = compute_metrics(df)
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    metrics.to_csv(OUTPUT, index=False)
    print(f"Erosion metrikleri kaydedildi: {OUTPUT}")
    print(metrics.head())

if __name__ == "__main__":
    main()
