import pandas as pd
from fastapi import FastAPI, Form
from fastapi.responses import FileResponse
from agent import Agent, analyze_breakouts

app = FastAPI()
agent = Agent()


@app.post("/generate_report")
def generate_report(
    ticker: str = Form(...),
    start_date: str = Form(...),
    end_date: str = Form(...),
    volume_threshold: float = Form(...),
    price_threshold: float = Form(...),
    holding_period: int = Form(...),
):
    data = agent.get_dataframe(ticker, start_date, end_date)
    report = analyze_breakouts(data, volume_threshold, price_threshold, holding_period)
    csv_file = f"{ticker}_report.csv"
    report.to_csv(csv_file, index=False)
    return FileResponse(csv_file, media_type="text/csv", filename=csv_file)
