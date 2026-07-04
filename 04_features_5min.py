import pandas as pd

df = pd.read_csv("energy_resampled_5min.csv", parse_dates=["datetime"])
df = df.sort_values("datetime").reset_index(drop=True)

# drop leftover columns from previous runs to avoid conflicts
for col in ["hourly_avg", "is_gap_filled", "gap_minutes_filled",
            "time_decimal", "shift_datetime", "status",
            "hour", "minute", "day_of_week", "month", "is_weekend",
            "shift", "shift_date", "date", "is_gap_filled"]:
    if col in df.columns:
        df = df.drop(columns=[col])

# ── Time features ──
df["hour"]        = df["datetime"].dt.hour
df["minute"]      = df["datetime"].dt.minute
df["day_of_week"] = df["datetime"].dt.dayofweek
df["month"]       = df["datetime"].dt.month
df["is_weekend"]  = df["day_of_week"].isin([5, 6]).astype(int)

# ── Shift classification ──
df["time_decimal"] = df["hour"] + df["minute"] / 60
df["shift"] = "Shift C"
df.loc[(df["time_decimal"] >= 6)  & (df["time_decimal"] < 14), "shift"] = "Shift A"
df.loc[(df["time_decimal"] >= 14) & (df["time_decimal"] < 22), "shift"] = "Shift B"

# ── Shift date — business day starts at 06:00 ──
df["shift_datetime"] = df["datetime"] - pd.Timedelta(hours=6)
df["shift_date"]     = df["shift_datetime"].dt.date
df["date"]           = df["datetime"].dt.date

# ── Recalculate connectivity flags using two-condition Qlik logic ──

# condition 1: slot was interpolated AND original gap was > 9 minutes
df["is_gap_filled"] = (
    (df["is_interpolated"] == True) & (df["gap_block_minutes"] > 9)
)

# condition 2: hourly average consumption from real readings only
hourly_avg = (
    df[df["is_interpolated"] == False]
    .groupby("hour")["consumption_kwh"]
    .mean()
    .rename("hourly_avg")
)
df = df.merge(hourly_avg, on="hour", how="left")

# apply two-condition logic
df["status"] = "normal"
df.loc[
    (df["is_gap_filled"] == True) &
    (df["consumption_kwh"] >= 0.51 * df["hourly_avg"]),
    "status"
] = "connectivity_issue"

# ── Save enriched 5-min file ──
df.to_csv("energy_resampled_5min.csv", index=False)
print("Saved: energy_resampled_5min.csv")

# ── Calendar day aggregation ──
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

# ── Shift daily aggregation ──
shift_daily = df.groupby(["shift_date", "shift"]).agg(
    total_kwh          = ("consumption_kwh", "sum"),
    avg_power_kw       = ("power_kw", "mean"),
    connectivity_slots = ("status", lambda x: (x == "connectivity_issue").sum()),
    total_slots        = ("status", "count")
).reset_index()

shift_daily["gap_pct"] = (
    shift_daily["connectivity_slots"] / shift_daily["total_slots"] * 100
).round(2)
shift_daily["day_quality"] = shift_daily["gap_pct"].apply(
    lambda x: "poor" if x > 20 else ("moderate" if x > 5 else "good")
)

# ── Sanity checks ──
print("\nConnectivity flag breakdown:")
print(df["status"].value_counts())

print("\nDay quality breakdown:")
print(daily["day_quality"].value_counts())

print("\nDate range:", daily["date"].min(), "→", daily["date"].max())
print("Total days:", len(daily))
print("Avg daily consumption:", daily["total_kwh"].mean().round(2))
print("Max daily consumption:", daily["total_kwh"].max().round(2))

# ── June validation ──
june = daily[
    (pd.to_datetime(daily["date"]).dt.month == 6) &
    (pd.to_datetime(daily["date"]).dt.year == 2026)
].copy()

print("\n── June Daily Validation ──")
print(june[["date", "total_kwh", "gap_pct", "day_quality"]].to_string())
print("\nJune total:", june["total_kwh"].sum().round(2))

# ── Shift sample ──
print("\nShift daily sample:")
print(shift_daily.head(9).to_string())

daily.to_csv("energy_daily_5min.csv", index=False)
shift_daily.to_csv("energy_shift_daily.csv", index=False)
print("\nSaved: energy_daily_5min.csv and energy_shift_daily.csv")