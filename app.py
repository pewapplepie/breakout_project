import pandas as pd
import streamlit as st
from agent import Agent
from calc import build_graph, build_breakout_report
import datetime

st.set_page_config(page_title="Volume Breakout Analysis", layout="wide")

st.title("Volume Breakout Analysis")
if "report" not in st.session_state:
    st.session_state.report = pd.DataFrame()
if "calc_completed" not in st.session_state:
    st.session_state.calc_completed = 0
if "raw_data" not in st.session_state:
    st.session_state.raw_data = pd.DataFrame()


@st.cache_data(ttl=600)
def fetch_data(ticker, start_date, end_date):
    print("agenting to fetch data...")
    agent = Agent()
    data = agent.get_dataframe(ticker, start_date, end_date)
    if data.empty:
        print("no data available")
    return data


@st.cache_data(ttl=600)
def run_analysis(**kwargs):
    print("Fetching data...")
    data = fetch_data(
        ticker, start_date=kwargs["start_date"], end_date=kwargs["end_date"]
    )
    print("Running analysis...")
    report = build_breakout_report(
        data,
        vol_thresh=kwargs["volume_threshold"],
        price_thresh=kwargs["price_threshold"],
        hold_days=kwargs["holding_period"],
    )

    st.session_state.report = report
    st.session_state.raw_data = data
    st.session_state.calc_completed = 1
    print("Completed analysis")


today = datetime.datetime.today()
min_date = today - datetime.timedelta(weeks=104)
# Sidebars
st.sidebar.subheader("Params")
ticker = st.sidebar.text_input("Ticker", placeholder="AAPL").upper()
st.sidebar.subheader("Date Range")
end_date = st.sidebar.date_input("To", format="MM/DD/YYYY", value=today)
start_date = st.sidebar.date_input(
    "From (Max window size is two year)", format="MM/DD/YYYY", value=min_date
)

volume_breakout_threshold = st.sidebar.number_input(
    "Volume Breakout Threshold(%)", value=200.0, step=10.0
)
price_change_threshold = st.sidebar.number_input(
    "Price Change Threshold(%)", value=2.0, step=0.5
)
holding_period = st.sidebar.number_input(
    "Number of day holding", value=10, format="%d", step=1
)
st.sidebar.button(
    "Calculate",
    on_click=lambda: run_analysis(
        ticker=ticker,
        start_date=start_date,
        end_date=end_date,
        volume_threshold=volume_breakout_threshold,
        price_threshold=price_change_threshold,
        holding_period=holding_period,
    ),
)

if st.session_state.calc_completed:

    if not st.session_state.report.empty:
        print("Report Generated")
        st.dataframe(st.session_state.report)

        fig = build_graph(st.session_state.raw_data, st.session_state.report)
        st.plotly_chart(fig, use_container_width=True)

    else:
        st.write("No Breakout")
