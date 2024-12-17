import pandas as pd
import streamlit as st
from agent import Agent
from calc import *
import datetime

st.set_page_config(page_title="Volume Breakout Analysis", layout="wide")

st.title("Volume Breakout Analysis")
if "data" not in st.session_state:
    st.session_state.data = None
if "trades" not in st.session_state:
    st.session_state.trades = None
if "report" not in st.session_state:
    st.session_state.report = None
if "calc_completed" not in st.session_state:
    st.session_state.calc_completed = 0
if "custome_api" not in st.session_state:
    st.session_state.custome_api = ""

agent = Agent(st.session_state.custome_api)


@st.cache_data(ttl=60)
def fetch_data(ticker, start_date, end_date):
    print("calling agent to fetch data...")
    data = agent.get_dataframe(ticker, start_date, end_date)
    if data.empty:
        print("no data available")
    return data


# @st.cache_data(ttl=60)
def run_analysis(**kwargs):
    print("Fetching data...")
    data = fetch_data(
        ticker, start_date=kwargs["start_date"], end_date=kwargs["end_date"]
    )
    print("Running analysis...")
    trades = build_breakout_trades(
        data,
        vol_thresh=kwargs["volume_threshold"],
        price_thresh=kwargs["price_threshold"],
        hold_days=kwargs["holding_period"],
    )

    report = build_breakout_report(trades)
    st.session_state.data = data
    st.session_state.trades = trades
    st.session_state.report = report
    print("Analysis completed")
    print(st.session_state.report)
    print("Completed analysis")
    st.session_state.calc_completed = 1
    # return data, trades, report


today = datetime.datetime.today()
min_date = today - datetime.timedelta(weeks=104)
# Sidebars
st.sidebar.subheader("Params")
ticker = st.sidebar.text_input("Ticker", placeholder="AAPL").upper()
st.sidebar.subheader("Date Range")

start_date = st.sidebar.date_input(
    "Start Date ",
    format="MM/DD/YYYY",
    value=min_date,
)
st.sidebar.caption(
    f"Max window size is two year lookback from current date for free api version, min start date: *{min_date.strftime('%Y-%m-%d')}*"
)
end_date = st.sidebar.date_input("End Date", format="MM/DD/YYYY", value=today)
volume_breakout_threshold = st.sidebar.number_input(
    "Volume Breakout Threshold(%)", value=200.0, step=10.0
)
price_change_threshold = st.sidebar.number_input(
    "Price Change Threshold(%)", value=2.0, step=0.5
)
holding_period = st.sidebar.number_input(
    "Number of day holding", value=10, format="%d", step=1, min_value=1
)

if st.sidebar.button(
    "Calculate",
    on_click=lambda: run_analysis(
        ticker=ticker,
        start_date=start_date,
        end_date=end_date,
        volume_threshold=volume_breakout_threshold,
        price_threshold=price_change_threshold,
        holding_period=holding_period,
    ),
):
    st.session_state.calc_completed = 1
    st.rerun()
st.sidebar.divider()
st.sidebar.subheader("Custome API")
st.sidebar.write("If you wish to use a custom API, please provide your Polygon API key")
st.session_state.custome_api = st.sidebar.text_input(
    "Polygon API Key", placeholder="your_api_key"
)
if st.sidebar.button("Validate API Key"):
    if agent.is_api_key_valid(st.session_state.custome_api):
        st.success("API Key is valid!")
        agent = Agent(st.session_state.custome_api)
    else:
        st.error("Invalid API Key. Please check and try again.")
        st.session_state.custome_api = ""


if st.session_state.calc_completed:

    if st.session_state.report is not None:
        print("Report Generated")
        st.write("The app use vwap for all calculation to account for look-ahead bias")
        st.subheader("Breakout Performance Report")
        st.dataframe(st.session_state.report)

        fig = build_graph(st.session_state.data, st.session_state.trades)
        st.plotly_chart(fig, use_container_width=True)

        st.write("Trades Report")
        st.dataframe(st.session_state.trades)

    else:
        st.write("No Breakout")
