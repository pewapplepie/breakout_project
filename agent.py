from datetime import datetime
import requests
import pandas as pd
from dotenv import load_dotenv
import os

load_dotenv()

API_KEY = os.getenv("api_key")


class Agent:
    def __init__(self):
        self.base_url: str = "https://api.polygon.io/v2"
        self.header = {"Authorization": f"Bearer {API_KEY}"}
        self.data = None

    def get_historical_data(self, ticker, start_date, end_date):
        ticker = ticker.upper()
        url = f"{self.base_url}/aggs/ticker/{ticker}/range/1/day/{start_date}/{end_date}?adjusted=true&sort=asc"

        data = []
        next_url = url

        while next_url:
            response = requests.get(next_url, headers=self.header)
            if response.status_code == 200:
                json_data = response.json()
                results = json_data.get("results", [])
                data.extend(results)
                next_url = json_data.get("next_url")  # Handle pagination
            else:
                print(f"Error {response.status_code}: {response.text}")
                break
        self.data = data
        return data

    def get_dataframe(self, ticker, start_dt, end_dt):
        data = self.get_historical_data(ticker, start_dt, end_dt)
        df = pd.DataFrame(data)
        return df


def analyze_breakouts(data, vol_thresh=200, price_thresh=2, hold_days=10):
    data = data[["v", "c", "t"]].copy()
    data["t"] = pd.to_datetime(data["t"], unit="ms")
    data["avg_vol"] = data["v"].rolling(20, min_periods=1).mean().shift(1)
    data["vol_ratio"] = data["v"] / data["avg_vol"]
    data["price_change"] = data["c"].pct_change() * 100

    # Find breakout days
    breakouts = data[
        (data["vol_ratio"] > vol_thresh / 100) & (data["price_change"] > price_thresh)
    ].copy()

    exit_indices = breakouts.index + hold_days
    exit_indices = [exit_i for exit_i in exit_indices if exit_i < len(data)]

    # Extract exit prices and calculate returns
    breakouts["Exit Price"] = data.loc[exit_indices, "c"].values
    breakouts["Return %"] = (
        (breakouts["Exit Price"] - breakouts["c"]) / breakouts["c"] * 100
    )
    breakouts["Date"] = pd.to_datetime(breakouts["t"], unit="ms").dt.strftime(
        "%Y-%m-%d"
    )

    # Select relevant columns
    return breakouts[["Date", "c", "Exit Price", "Return %"]].rename(
        columns={"c": "Entry Price"}
    )
