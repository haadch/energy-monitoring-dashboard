import pandas as pd

df = pd.read_csv("energy_resampled.csv", parse_dates=["datetime"])

# time features
df["hour"]       = df["datetime"].dt.hour
df["day_of_week"] = df["datetime"].dt.dayofweek    # 0=Monday, 6=Sunday
df["month"]      = df["datetime"].dt.month
df["date"]       = df["datetime"].dt.date
df["is_weekend"] = df["day_of_week"].isin([5, 6]).astype(int)

# save enriched 15-min file
df.to_csv("energy_resampled.csv", index=False)
print("15-min file updated with time features")

# daily aggregation
daily = df.groupby("date").agg(
    total_kwh         = ("consumption_kwh", "sum"),
    avg_kwh_per_slot  = ("consumption_kwh", "mean"),
    peak_kwh          = ("consumption_kwh", "max"),
    avg_power_kw      = ("power_kw", "mean"),
    connectivity_slots = ("status", lambda x: (x == "connectivity_issue").sum()),
    total_slots       = ("status", "count")
).reset_index()

# flag days where more than 20% of slots are connectivity issues
daily["gap_pct"] = (daily["connectivity_slots"] / daily["total_slots"] * 100).round(2)
daily["day_quality"] = daily["gap_pct"].apply(
    lambda x: "poor" if x > 20 else ("moderate" if x > 5 else "good")
)

print("\nDaily aggregation sample:")
print(daily.head(7))
print("\nDay quality breakdown:")
print(daily["day_quality"].value_counts())
print("\nDate range:", daily["date"].min(), "→", daily["date"].max())
print("Total days:", len(daily))
print("Max daily consumption:", daily["total_kwh"].max().round(2))
print("Min daily consumption:", daily["total_kwh"].min().round(2))
print("Average daily consumption:", daily["total_kwh"].mean().round(2))

daily.to_csv("energy_daily.csv", index=False)
print("\nSaved: energy_daily.csv")