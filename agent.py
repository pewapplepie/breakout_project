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


