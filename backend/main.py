from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd
from datetime import date

app = FastAPI(title="Energy Monitoring API")

# allow React (running on different port) to call this API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# load all CSVs once at startup — no need to reload on every request
daily    = pd.read_csv("data/energy_daily_business.csv", parse_dates=["shift_date"])
shifts   = pd.read_csv("data/energy_shift_daily.csv", parse_dates=["shift_date"])
forecast = pd.read_csv("data/energy_forecast.csv", parse_dates=["date"])
raw      = pd.read_csv("data/energy_resampled_5min.csv", parse_dates=["datetime"])

@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/summary")
def summary():
    return {
        "total_kwh":        round(daily["total_kwh"].sum(), 2),
        "avg_daily_kwh":    round(daily["total_kwh"].mean(), 2),
        "peak_day":         str(daily.loc[daily["total_kwh"].idxmax(), "shift_date"].date()),
        "peak_kwh":         round(daily["total_kwh"].max(), 2),
        "total_days":       len(daily),
        "good_days":        int((daily["day_quality"] == "good").sum()),
        "poor_days":        int((daily["day_quality"] == "poor").sum()),
        "data_start":       str(daily["shift_date"].min().date()),
        "data_end":         str(daily["shift_date"].max().date()),
    }

@app.get("/daily")
def get_daily(start: str = None, end: str = None):
    df = daily.copy()
    if start:
        df = df[df["shift_date"] >= pd.to_datetime(start)]
    if end:
        df = df[df["shift_date"] <= pd.to_datetime(end)]
    df["shift_date"] = df["shift_date"].dt.strftime("%Y-%m-%d")
    return df[["shift_date", "total_kwh", "peak_kwh", "gap_pct", "day_quality"]].to_dict(orient="records")

@app.get("/forecast")
def get_forecast():
    df = forecast.copy()
    df["date"] = df["date"].dt.strftime("%Y-%m-%d")
    return df[["date", "predicted_kwh", "lower_bound", "upper_bound"]].to_dict(orient="records")

@app.get("/shifts")
def get_shifts(start: str = None, end: str = None):
    df = shifts.copy()
    if start:
        df = df[df["shift_date"] >= pd.to_datetime(start)]
    if end:
        df = df[df["shift_date"] <= pd.to_datetime(end)]
    df["shift_date"] = df["shift_date"].dt.strftime("%Y-%m-%d")
    return df[["shift_date", "shift", "total_kwh", "gap_pct", "day_quality"]].to_dict(orient="records")

@app.get("/hourly")
def get_hourly(date: str = None):
    df = raw.copy()
    df["date"] = df["datetime"].dt.date.astype(str)
    if date:
        df = df[df["date"] == date]
    df["hour"] = df["datetime"].dt.hour
    hourly = df.groupby("hour")["consumption_kwh"].sum().reset_index()
    hourly.columns = ["hour", "total_kwh"]
    hourly["total_kwh"] = hourly["total_kwh"].round(2)
    return hourly.to_dict(orient="records")