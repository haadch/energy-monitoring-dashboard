import pandas as pd

# ── 1. Load ──────────────────────────────────────────────
df = pd.read_csv("energy_raw.csv")

print("Shape:", df.shape)
print("\nColumns:\n", df.columns.tolist())
print("\nFirst 3 rows:\n", df.head(3))
print("\nData types:\n", df.dtypes)
print("\nNull counts:\n", df.isnull().sum())