import pandas as pd
import matplotlib.pyplot as plt
from prophet import Prophet
from sklearn.metrics import mean_absolute_error

df = pd.read_csv("energy_daily_business.csv", parse_dates=["shift_date"])
df = df.rename(columns={"shift_date": "ds", "total_kwh": "y"})

# remove known shutdown days
shutdown_dates = pd.to_datetime([
    "2025-09-06",
    "2026-02-05",
    "2026-03-20", "2026-03-21", "2026-03-22", "2026-03-23",
    "2026-05-01",
    "2026-05-27", "2026-05-28", "2026-05-29",
])
df_clean = df[~df["ds"].isin(shutdown_dates)].copy()

# ── Option A — Evaluate accuracy on February 2026 ──
print("=" * 50)
print("OPTION A — Accuracy evaluation on February 2026")
print("=" * 50)

feb_holdout = df_clean[
    (df_clean["ds"].dt.month == 2) &
    (df_clean["ds"].dt.year == 2026)
].copy()

train_a = df_clean[
    ~((df_clean["ds"].dt.month == 2) & (df_clean["ds"].dt.year == 2026))
].copy()

print(f"Training rows:   {len(train_a)}")
print(f"Holdout rows:    {len(feb_holdout)} (February 2026)")

model_a = Prophet(
    yearly_seasonality      = True,
    weekly_seasonality      = True,
    daily_seasonality       = False,
    seasonality_mode        = "additive",
    changepoint_prior_scale = 0.05
)
model_a.fit(train_a)
print("Model A trained")

# pass February dates directly to Prophet
future_a   = pd.DataFrame({"ds": feb_holdout["ds"].values})
forecast_a = model_a.predict(future_a)
forecast_a["yhat"]       = forecast_a["yhat"].clip(lower=0)
forecast_a["yhat_lower"] = forecast_a["yhat_lower"].clip(lower=0)

eval_a = feb_holdout[["ds", "y"]].merge(
    forecast_a[["ds", "yhat", "yhat_lower", "yhat_upper"]],
    on="ds", how="inner"
)
eval_a["error_pct"] = (
    (eval_a["y"] - eval_a["yhat"]).abs() / eval_a["y"] * 100
).round(2)

mae_a  = mean_absolute_error(eval_a["y"], eval_a["yhat"])
mape_a = eval_a["error_pct"].mean()

print(f"\nMAE:      {mae_a:.2f} kWh")
print(f"MAPE:     {mape_a:.2f}%")
print(f"Accuracy: {100 - mape_a:.2f}%")
print(f"\nDay by Day:")
print(eval_a[["ds", "y", "yhat", "error_pct"]].to_string())

# plot A
fig1, ax1 = plt.subplots(figsize=(14, 5))
ax1.plot(eval_a["ds"], eval_a["y"],
         color="steelblue", linewidth=2, label="Actual")
ax1.plot(eval_a["ds"], eval_a["yhat"],
         color="darkorange", linewidth=2, linestyle="--", label="Predicted")
ax1.fill_between(
    eval_a["ds"], eval_a["yhat_lower"], eval_a["yhat_upper"],
    alpha=0.2, color="darkorange", label="Confidence interval"
)
ax1.set_title("February 2026 — Actual vs Predicted (Model Accuracy Test)")
ax1.set_xlabel("Date")
ax1.set_ylabel("Daily kWh")
ax1.legend()
plt.tight_layout()
plt.savefig("forecast_accuracy_feb.png", dpi=150)
plt.show()
print("Saved: forecast_accuracy_feb.png")

# ── Option B — Train on all data, forecast 60 days forward ──
print("\n" + "=" * 50)
print("OPTION B — Future forecast: July 2026 onwards")
print("=" * 50)

model_b = Prophet(
    yearly_seasonality      = False,  # turn off — we don't have a full year
    weekly_seasonality      = True,   # this we know well
    daily_seasonality       = False,
    seasonality_mode        = "additive",
    changepoint_prior_scale = 0.001,  # extremely flat trend
    changepoint_range       = 0.7
)
model_b.fit(df_clean)

future_b   = model_b.make_future_dataframe(periods=14, freq="D")
forecast_b = model_b.predict(future_b)
forecast_b["yhat"]       = forecast_b["yhat"].clip(lower=0)
forecast_b["yhat_lower"] = forecast_b["yhat_lower"].clip(lower=0)

# export future only
last_date    = df_clean["ds"].max()
forecast_out = forecast_b[forecast_b["ds"] > last_date][
    ["ds", "yhat", "yhat_lower", "yhat_upper"]
].copy()
forecast_out.columns = ["date", "predicted_kwh", "lower_bound", "upper_bound"]
forecast_out["date"] = forecast_out["date"].dt.date
forecast_out = forecast_out.round(2)
forecast_out.to_csv("energy_forecast.csv", index=False)
print("\nForecast sample (next 10 days):")
print(forecast_out.head(10).to_string())
print(f"\nSaved: energy_forecast.csv ({len(forecast_out)} days)")

# plot B1 — full history + future forecast
fig2, ax2 = plt.subplots(figsize=(14, 5))
ax2.plot(df["ds"], df["y"],
         color="steelblue", linewidth=1, label="Actual")
ax2.plot(forecast_b["ds"], forecast_b["yhat"],
         color="darkorange", linewidth=1.5, label="Forecast")
ax2.fill_between(
    forecast_b["ds"], forecast_b["yhat_lower"], forecast_b["yhat_upper"],
    alpha=0.2, color="darkorange", label="Confidence interval"
)
ax2.axvline(x=last_date, color="gray", linestyle="--",
            linewidth=1, label="Forecast start")
ax2.set_title("Energy Consumption — Full History + 60-Day Forecast")
ax2.set_xlabel("Date")
ax2.set_ylabel("Daily kWh")
ax2.legend()
plt.tight_layout()
plt.savefig("forecast_future.png", dpi=150)
plt.show()
print("Saved: forecast_future.png")

# plot B2 — July forecast zoomed
fig3, ax3 = plt.subplots(figsize=(14, 5))
future_only = forecast_b[forecast_b["ds"] > last_date]
ax3.plot(future_only["ds"], future_only["yhat"],
         color="darkorange", linewidth=2, label="Predicted")
ax3.fill_between(
    future_only["ds"], future_only["yhat_lower"], future_only["yhat_upper"],
    alpha=0.2, color="darkorange", label="Confidence interval"
)
ax3.set_title("60-Day Forecast — July 2026 Onwards")
ax3.set_xlabel("Date")
ax3.set_ylabel("Daily kWh")
ax3.legend()
plt.tight_layout()
plt.savefig("forecast_july.png", dpi=150)
plt.show()
print("Saved: forecast_july.png")