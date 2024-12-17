import pandas as pd
import streamlit as st
from calc import generate_report

st.title('Analysis')
if "reports" not in st.session_state:
    st.session_state.reports = pd.DataFrame()
if "calc_completed" not in st.session_state:
    st.session_state.calc_completed = 0


def run_analysis(**kargs):
    st.session_state.reports = generate_report(**kargs)
    st.session_state.calc_completed = 1


# Sidebars
st.sidebar.subheader("Params")
ticker = st.sidebar.text_input("Ticker", placeholder="AAPL").upper()
start_date = st.sidebar.date_input("Start Date", format="MM/DD/YYYY")
end_date = st.sidebar.date_input("End Date", format="MM/DD/YYYY")
volume_breakout_threshold = st.sidebar.number_input("Volume Breakout Threshold(%)", value=200.0, step=10.0)
price_change_threshold = st.sidebar.number_input("Price Change Threshold(%)", value=2.0, step=0.5)
holding_period = st.sidebar.number_input("Number of day holding", value=10, format="%d", step=1)
st.sidebar.button("Calculate", on_click=lambda: run_analysis(
    ticker=ticker,
    start_date=start_date,
    end_date=end_date,
    volume_threshold=volume_breakout_threshold,
    price_threshold=price_change_threshold,
    holding_period=holding_period
))

if st.session_state.calc_completed:
    # df = pd.DataFrame(
    #     [
    #         {"command": "st.selectbox", "rating": 4, "is_widget": True},
    #         {"command": "st.balloons", "rating": 5, "is_widget": False},
    #         {"command": "st.time_input", "rating": 3, "is_widget": True},
    #     ]
    # )
    if not st.session_state.reports.empty:
        print('Report Generated')
        st.dataframe(st.session_state.reports)
    else:
        st.write("No Report Generated")
