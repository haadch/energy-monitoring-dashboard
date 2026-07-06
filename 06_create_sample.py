import pandas as pd
import os

# create sample folder inside backend/data
os.makedirs("backend/data/sample", exist_ok=True)

# load full files
daily    = pd.read_csv("backend/data/energy_daily_business.csv")
shifts   = pd.read_csv("backend/data/energy_shift_daily.csv")
forecast = pd.read_csv("backend/data/energy_forecast.csv")
raw      = pd.read_csv("backend/data/energy_resampled_5min.csv")

# take last 30 days from each
daily_sample    = daily.tail(30).copy()
shifts_sample   = shifts.tail(90).copy()
forecast_sample = forecast.copy()
raw_sample      = raw.tail(30 * 288).copy()

# save to sample folder — originals untouched
daily_sample.to_csv("backend/data/sample/energy_daily_business.csv",   index=False)
shifts_sample.to_csv("backend/data/sample/energy_shift_daily.csv",     index=False)
forecast_sample.to_csv("backend/data/sample/energy_forecast.csv",      index=False)
raw_sample.to_csv("backend/data/sample/energy_resampled_5min.csv",     index=False)

print("Daily rows:",    len(daily_sample))
print("Shift rows:",    len(shifts_sample))
print("Forecast rows:", len(forecast_sample))
print("Raw rows:",      len(raw_sample))
print("\nSample files saved to backend/data/sample/")
print("Original files untouched.")