# forecast_plugin.py
import pandas as pd
from statsmodels.tsa.arima.model import ARIMA

def generate_forecast() -> pd.DataFrame:
    # Load data
    df_demand_data = pd.read_csv('updated_mock_sku_demand_data.csv')

    # Convert 'Date' column to datetime and set as index
    df_demand_data["Date"] = pd.to_datetime(df_demand_data["Date"])
    df_demand_data.set_index("Date", inplace=True)

    # Ensure data is sorted by date
    df_demand_data.sort_index(inplace=True)

    # Forecast periods (e.g., next 1 week)
    forecast_periods = 1

    # Function to train ARIMA model and forecast demand for a single SKU
    def forecast_demand(df: pd.DataFrame, sku_id: str) -> pd.Series:
        df_sku = df[df["SKU ID"] == sku_id]["Demand Quantity"]
        if len(df_sku) < 10:
            raise ValueError(f"Not enough data to train ARIMA for SKU: {sku_id}")
        model = ARIMA(df_sku, order=(2, 1, 2))
        model_fit = model.fit()
        forecast = model_fit.forecast(steps=forecast_periods)
        return forecast

    # Forecast for both SKUs
    try:
        forecast_pepsi = forecast_demand(df_demand_data, "PEP-ORG-330C")
        forecast_mountain_dew = forecast_demand(df_demand_data, "MD-ORG-600B")
    except Exception as e:
        raise RuntimeError(f"Forecasting failed: {e}")

    # Generate forecast dates
    last_date = df_demand_data.index.max()
    forecast_dates = pd.date_range(start=last_date, periods=forecast_periods + 1, freq='W-MON')[1:]
    forecast_dates_str = forecast_dates.strftime('%Y-%m-%d').tolist()

    # Create forecast DataFrame
    df_forecast = pd.DataFrame({
        "Date": forecast_dates_str * 2,
        "SKU ID": ["PEP-ORG-330C"] * forecast_periods + ["MD-ORG-600B"] * forecast_periods,
        "SKU Name": ["Pepsi Original 330ml Can"] * forecast_periods + ["Mountain Dew 600ml Bottle"] * forecast_periods,
        "Forecasted Demand": list(forecast_pepsi.round().astype(int)) + list(forecast_mountain_dew.round().astype(int))
    })

    return df_forecast
