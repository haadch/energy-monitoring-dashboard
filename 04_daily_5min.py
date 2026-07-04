import pandas as pd

df = pd.read_csv("energy_resampled_5min.csv", parse_dates=["datetime"])

df["date"] = df["datetime"].dt.date

daily = df.groupby("date").agg(
    total_kwh          = ("consumption_kwh", "sum"),
    peak_kwh           = ("consumption_kwh", "max"),
    avg_power_kw       = ("power_kw", "mean"),
    connectivity_slots = ("status", lambda x: (x == "connectivity_issue").sum()),
    total_slots        = ("status", "count")
).reset_index()

daily["gap_pct"]     = (daily["connectivity_slots"] / daily["total_slots"] * 100).round(2)
daily["day_quality"] = daily["gap_pct"].apply(
    lambda x: "poor" if x > 20 else ("moderate" if x > 5 else "good")
)

# ── Sanity checks ──
print("Total days:", len(daily))
print("Date range:", daily["date"].min(), "→", daily["date"].max())
print("Max daily consumption:", daily["total_kwh"].max().round(2))
print("Min daily consumption:", daily["total_kwh"].min().round(2))
print("Avg daily consumption:", daily["total_kwh"].mean().round(2))
print("\nDay quality breakdown:")
print(daily["day_quality"].value_counts())

# ── June validation ──
june = daily[
    (pd.to_datetime(daily["date"]).dt.month == 6) &
    (pd.to_datetime(daily["date"]).dt.year == 2026)
].copy()

print("\n── June Daily Validation ──")
print(june[["date", "total_kwh", "gap_pct", "day_quality"]].to_string())
print("\nJune total:", june["total_kwh"].sum().round(2))

daily.to_csv("energy_daily_5min.csv", index=False)
print("\nSaved: energy_daily_5min.csv")