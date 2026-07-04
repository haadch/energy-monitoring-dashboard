import pandas as pd

df = pd.read_csv("energy_clean.csv", parse_dates=["datetime"])
df = df.sort_values("datetime").reset_index(drop=True)

df["gap_minutes"] = df["datetime"].diff().dt.total_seconds() / 60

# ── Full 5-minute grid ──
grid_start = df["datetime"].min().floor("5min")
grid_end   = df["datetime"].max().ceil("5min")
full_grid  = pd.date_range(start=grid_start, end=grid_end, freq="5min")
grid_df    = pd.DataFrame({"datetime": full_grid})

# ── Snap to nearest 5-min slot ──
df["datetime"] = df["datetime"].dt.round("5min")

# ── Aggregate slots that collide after snapping ──
df_snapped = df.groupby("datetime").agg(
    branch          = ("branch", "first"),
    total_register  = ("total_register", "mean"),
    mf              = ("mf", "first"),
    power_kw        = ("power_kw", "mean"),
    power_factor    = ("power_factor", "mean"),
    consumption_kwh = ("consumption_kwh", "sum"),
    gap_minutes     = ("gap_minutes", "max")
).reset_index()

# ── Merge onto full grid ──
merged = pd.merge(grid_df, df_snapped, on="datetime", how="left")
merged["branch"] = merged["branch"].ffill()
merged["mf"]     = merged["mf"].ffill().fillna(160)

# ── Fill gaps, assign status, store gap_block_minutes on every slot ──
def fill_gap_block(df):
    df = df.copy()
    i = 0
    while i < len(df):
        if pd.isna(df.loc[i, "consumption_kwh"]):
            gap_start = i
            while i < len(df) and pd.isna(df.loc[i, "consumption_kwh"]):
                i += 1
            gap_end = i

            if gap_end < len(df):
                n_slots              = (gap_end - gap_start) + 1
                total_consumption    = df.loc[gap_end, "consumption_kwh"]
                distributed          = total_consumption / n_slots
                gap_duration_minutes = (gap_end - gap_start) * 5
                gap_duration_hours   = gap_duration_minutes / 60

                flag = "connectivity_issue" if gap_duration_hours >= 1.5 else "normal"

                for j in range(gap_start, gap_end + 1):
                    df.loc[j, "consumption_kwh"]    = distributed
                    df.loc[j, "status"]             = flag
                    df.loc[j, "gap_block_minutes"]  = gap_duration_minutes
                    df.loc[j, "is_interpolated"]    = True
        else:
            df.loc[i, "status"]            = "normal"
            df.loc[i, "gap_block_minutes"] = 0
            df.loc[i, "is_interpolated"]   = False
            i += 1
    return df

merged = fill_gap_block(merged)

# ── Final cleanup ──
merged["status"]          = merged["status"].fillna("normal")
merged["consumption_kwh"] = merged["consumption_kwh"].fillna(0)
merged["gap_block_minutes"] = merged["gap_block_minutes"].fillna(0)
merged["is_interpolated"]   = merged["is_interpolated"].fillna(False)

# ── Sanity checks ──
total        = len(merged)
normal       = (merged["status"] == "normal").sum()
connectivity = (merged["status"] == "connectivity_issue").sum()

print("Total 5-min slots:", total)
print("Normal slots:", normal)
print("Connectivity issue slots:", connectivity)
print("Gap filled %:", round(connectivity / total * 100, 2))
print("Interpolated slots:", merged["is_interpolated"].sum())
print("\nDate range:", merged["datetime"].min(), "→", merged["datetime"].max())
print("Max consumption per slot:", merged["consumption_kwh"].max().round(2))
print("Avg consumption per slot:", merged["consumption_kwh"].mean().round(4))
print("\nSample:\n", merged.head(5).to_string())

merged.to_csv("energy_resampled_5min.csv", index=False)
print("\nSaved: energy_resampled_5min.csv")