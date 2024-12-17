import numpy as np
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots


def build_breakout_trades(data, vol_thresh=200, price_thresh=2, hold_days=10):
    print("Building breakout report...")
    data = data[["v", "vw", "t"]].copy()
    data["t"] = pd.to_datetime(data["t"], unit="ms")
    data["avg_vol"] = data["v"].rolling(20, min_periods=1).mean().shift(1)
    data["vol_ratio"] = data["v"] / data["avg_vol"]
    data["price_change"] = data["vw"].pct_change() * 100

    # Find breakout days
    breakouts = data[
        (data["vol_ratio"] > vol_thresh / 100) & (data["price_change"] > price_thresh)
    ].copy()

    exit_indices = np.clip(breakouts.index + hold_days, 0, len(data) - 1)
    exit_indices = exit_indices

    # Extract exit prices and calculate returns
    breakouts["Exit Price"] = data.loc[exit_indices, "vw"].values
    breakouts["Exit Date"] = data.loc[exit_indices, "t"].values
    breakouts["Return %"] = (
        (breakouts["Exit Price"] - breakouts["vw"]) / breakouts["vw"] * 100
    )
    breakouts["Date"] = pd.to_datetime(breakouts["t"], unit="ms").dt.strftime(
        "%Y-%m-%d"
    )
    breakouts["Exit Date"] = pd.to_datetime(
        breakouts["Exit Date"], unit="ms"
    ).dt.strftime("%Y-%m-%d")

    # Select relevant columns
    return breakouts[["Date", "vw", "Exit Price", "Exit Date", "Return %"]].rename(
        columns={"vw": "Entry Price"}
    )


def build_breakout_report(data):
    wintrades = sum(data["Return %"] >= 0)
    losstrades = sum(data["Return %"] < 0)
    avg_return = np.mean(data["Return %"])
    max_return = np.max(data["Return %"])
    min_return = np.min(data["Return %"])
    total_trades = wintrades + losstrades
    return pd.DataFrame(
        {
            "Total Trades": total_trades,
            "Wining Trades": wintrades,
            "Losing Trades": losstrades,
            "Avg Return": avg_return,
            "Max Return": max_return,
            "Min Return": min_return,
        },
        index=["Performance Metrics"],
    )


def build_graph(data, reports):
    data["t"] = pd.to_datetime(data["t"], unit="ms")
    data["20_Volume_Mean"] = data["v"].rolling(20, min_periods=1).mean().shift(1)
    data["vol_ratio"] = data["v"] / data["20_Volume_Mean"]
    data["price_change"] = data["vw"].pct_change() * 100
    # Create a subplot figure
    fig = make_subplots(
        rows=2,
        cols=1,
        shared_xaxes=True,
        row_heights=[0.6, 0.4],
        vertical_spacing=0.1,
        specs=[[{"secondary_y": False}], [{"secondary_y": True}]],
        subplot_titles=("Breakout Performance", "Breakout Metrics"),
    )

    # Add the closing prices line
    fig.add_trace(
        go.Scatter(
            x=data["t"],
            y=data["vw"],
            mode="lines",
            name="Volume Weighted Average Price",
            line=dict(color="blue"),
        ),
        # secondary_y=Fals,
        row=1,
        col=1,
    )
    # Add Entry Price markers
    fig.add_trace(
        go.Scatter(
            x=pd.to_datetime(reports["Date"]),
            y=reports["Entry Price"],
            mode="markers",
            name="Entry Price",
            marker=dict(color="green", size=10, symbol="triangle-up"),
        ),
        # secondary_y=False,
        row=1,
        col=1,
    )

    # Add Exit Price markers
    fig.add_trace(
        go.Scatter(
            x=pd.to_datetime(reports["Date"]),
            y=reports["Exit Price"],
            mode="markers",
            name="Exit Price",
            marker=dict(color="red", size=10, symbol="triangle-down"),
        ),
        # secondary_y=False,
        row=1,
        col=1,
    )
    # Second subplot: Volume Metrics
    # Add Volume Histogram
    fig.add_trace(
        go.Bar(
            x=data["t"],
            y=data["v"],
            name="Volume",
            marker=dict(color="lightgray"),
            opacity=0.5,
        ),
        row=2,
        col=1,
        secondary_y=False,
    )

    # Add 20-day Volume Mean line
    fig.add_trace(
        go.Scatter(
            x=data["t"],
            y=data["20_Volume_Mean"],
            mode="lines",
            name="20-Day Volume Mean",
            line=dict(color="orange", dash="dot"),
        ),
        row=2,
        col=1,
        secondary_y=False,
    )

    # # Add vol_ratio line on secondary y-axis
    # fig.add_trace(
    #     go.Scatter(
    #         x=data["t"],
    #         y=data["vol_ratio"],
    #         mode="markers",
    #         name="Volume Ratio",
    #         marker=dict(
    #             size=data["vol_ratio"].fillna(0),
    #             color="cyan",
    #             opacity=np.clip(data["vol_ratio"].fillna(0), 0, 1),
    #             symbol="circle",
    #         ),
    #     ),
    #     row=2,
    #     col=1,
    #     secondary_y=True,
    # )

    # Add price_change as scatter bubbles
    fig.add_trace(
        go.Scatter(
            x=data["t"],
            y=data["price_change"],
            mode="markers",
            name="Price Change (%)",
            marker=dict(
                size=np.where(
                    data["price_change"] > 2,
                    np.clip(data["price_change"].fillna(0), 5, 10),  # Scale up size
                    2,  # Default size for < 2%
                ),
                color="cyan",
                opacity=np.where(
                    data["price_change"] > 2,
                    np.clip(
                        data["price_change"].fillna(0) / 5, 0.7, 0.9
                    ),  # Increase opacity
                    0.2,  # Default opacity for < 2%
                ),
                symbol="circle",
            ),
        ),
        row=2,
        col=1,
        secondary_y=True,
    )
    # Add custom legend entries
    fig.add_trace(
        go.Scatter(
            x=[None],
            y=[None],
            mode="markers",
            name="High Price Change (>2%)",
            marker=dict(size=30, color="cyan", opacity=0.9, symbol="circle"),
        )
    )
    # Customize layout
    fig.update_layout(
        title="Stock Prices, Trades, and Volume Metrics",
        xaxis_title="Date",
        # yaxis_title="Price (USD)",
        # yaxis2_title="Volume",
        # yaxis3_title="Volume Metrics",
        # yaxis4_title="Vol Ratio / Price Change (%)",
        width=1920,  # Width of the chart
        height=800,  # Height of the chart
        legend_title="Legend",
        template="plotly_white",
        bargap=0.2,
    )
    return fig
