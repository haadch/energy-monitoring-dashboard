import pandas as pd
import numpy as np

df = pd.read_csv("energy_clean.csv", parse_dates=["datetime"])
df = df.sort_values("datetime").reset_index(drop=True)

# ── Step 1: Calculate time gap between each row and the previous one ──
df["gap_minutes"] = df["datetime"].diff().dt.total_seconds() / 60

# ── Step 2: Build the full 15-minute grid from start to end ──
grid_start = df["datetime"].min().floor("15min")
grid_end   = df["datetime"].max().ceil("15min")
full_grid  = pd.date_range(start=grid_start, end=grid_end, freq="15min")
grid_df    = pd.DataFrame({"datetime": full_grid})

# ── Step 3: Snap actual readings to nearest 15-min slot ──
df["datetime"] = df["datetime"].dt.round("15min")

# ── Step 4: Where multiple readings land on same slot, average them ──
df_snapped = df.groupby("datetime").agg(
    branch          = ("branch", "first"),
    register        = ("total_register", "mean"),
    mf              = ("mf", "first"),
    power_kw        = ("power_kw", "mean"),
    power_factor    = ("power_factor", "mean"),
    consumption_kwh = ("consumption_kwh", "sum"),
    gap_minutes     = ("gap_minutes", "max")
).reset_index()

# ── Step 5: Merge snapped data onto full grid ──
merged = pd.merge(grid_df, df_snapped, on="datetime", how="left")
merged["branch"] = merged["branch"].ffill()
merged["mf"]     = merged["mf"].ffill().fillna(160)

# ── Step 6: Identify gap blocks ──
# a gap block = a stretch of NaN rows sitting between two real readings
# for each gap block we distribute the next known consumption evenly

def fill_gap_block(df):
    df = df.copy()
    i = 0
    while i < len(df):
        if pd.isna(df.loc[i, "consumption_kwh"]):
            # find the start and end of this gap block
            gap_start = i
            while i < len(df) and pd.isna(df.loc[i, "consumption_kwh"]):
                i += 1
            gap_end = i  # first real row after the gap

            if gap_end < len(df):
                # how many slots to fill including the real row after gap
                n_slots = (gap_end - gap_start) + 1
                total_consumption = df.loc[gap_end, "consumption_kwh"]
                distributed = total_consumption / n_slots

                # gap duration in hours
                gap_duration_hours = (gap_end - gap_start) * 15 / 60

                # assign flag based on your rule
                flag = "connectivity_issue" if gap_duration_hours >= 1.5 else "normal"

                # fill each missing slot
                for j in range(gap_start, gap_end + 1):
                    df.loc[j, "consumption_kwh"] = distributed
                    df.loc[j, "status"] = flag
        else:
            df.loc[i, "status"] = "normal"
            i += 1
    return df

merged = fill_gap_block(merged)

# ── Step 7: Final cleanup ──
merged["status"] = merged["status"].fillna("normal")
merged["consumption_kwh"] = merged["consumption_kwh"].fillna(0)

# ── Step 8: Sanity checks ──
total_slots        = len(merged)
normal_slots       = (merged["status"] == "normal").sum()
connectivity_slots = (merged["status"] == "connectivity_issue").sum()

print("Total 15-min slots:", total_slots)
print("Normal slots:", normal_slots)
print("Connectivity issue slots:", connectivity_slots)
print("Gap filled %:", round(connectivity_slots / total_slots * 100, 2))
print("\nDate range:", merged["datetime"].min(), "→", merged["datetime"].max())
print("Max consumption in a slot:", merged["consumption_kwh"].max().round(2))
print("Average consumption per slot:", merged["consumption_kwh"].mean().round(4))
print("\nSample normal rows:")
print(merged[merged["status"] == "normal"].head(3))
print("\nSample connectivity issue rows:")
print(merged[merged["status"] == "connectivity_issue"].head(3))

merged.to_csv("energy_resampled.csv", index=False)
print("\nSaved: energy_resampled.csv")