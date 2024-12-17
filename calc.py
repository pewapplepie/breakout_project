import pandas as pd
from agent import Agent

agent = Agent()


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


def generate_report(
        ticker: str,
        start_date: str,
        end_date: str,
        volume_threshold: float,
        price_threshold: float,
        holding_period: int
):
    data = agent.get_dataframe(ticker, start_date, end_date)
    report = analyze_breakouts(data, volume_threshold, price_threshold, holding_period)
    print("Report Generated")
    return report
