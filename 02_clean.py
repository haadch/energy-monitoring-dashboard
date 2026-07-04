import pandas as pd

df = pd.read_csv("energy_raw.csv")

# build proper datetime from Date + Times columns
df["datetime"] = pd.to_datetime(
    df["Date"].astype(str) + " " + df["Times"].str.strip(),
    format="%Y%m%d %I:%M:%S %p"
)

# keep both registers before doing any calculation
df = df[["datetime", "SiteID", "bd_zy", "bd_sy", "Multiplying Factor", "p", "cs"]].copy()
df.columns = ["datetime", "branch", "total_register", "solar_register", "mf", "power_kw", "power_factor"]

# sort chronologically — critical before delta calculation
df = df.sort_values("datetime").reset_index(drop=True)

# subtract solar from total to get net grid import register
df["import_register"] = df["total_register"] - df["solar_register"]

# delta on import register only
df["register_delta"]  = df["import_register"].diff()
df["consumption_kwh"] = df["register_delta"] * df["mf"]

# remove negative deltas — meter resets or day boundary issues
df.loc[df["consumption_kwh"] < 0, "consumption_kwh"] = None

# drop rows where consumption couldn't be calculated
df = df.dropna(subset=["consumption_kwh"])

# sanity checks
print("Date range:", df["datetime"].min(), "→", df["datetime"].max())
print("Total clean rows:", len(df))
print("Nulls remaining:\n", df.isnull().sum())
print("Min consumption:", df["consumption_kwh"].min())
print("Max consumption:", df["consumption_kwh"].max())
print("Average consumption per interval:", df["consumption_kwh"].mean().round(4))
print("\nSample:\n", df.head(5))

df.to_csv("energy_clean.csv", index=False)
print("\nSaved: energy_clean.csv")