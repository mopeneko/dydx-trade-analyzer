from datetime import datetime, time
import pytz
import streamlit as st
import pandas as pd
from matplotlib import pyplot as plt
import seaborn as sns


def get_timestamp(d, tz: str, end=False) -> int:
    native_dt = datetime.combine(d, time())
    if end:
        native_dt = native_dt.replace(hour=23, minute=59, second=59)
    dt = pytz.timezone(tz).localize(native_dt)
    return int(dt.timestamp() * 1000)


st.set_page_config(page_title="dYdX Trade Analyzer")
st.title("dYdX Trade Analyzer")

uploaded_file = st.file_uploader("Upload a CSV file")

today = datetime.today()
begging_of_month = datetime(today.year, today.month, 1)
d = st.date_input(
    "Select duration",
    (begging_of_month, today),
    begging_of_month,
    today,
)

timezone = st.selectbox(
    "Select timezone",
    ("UTC", "JST"),
)

if uploaded_file is not None and len(d) == 2:
    df = pd.read_csv(uploaded_file)

    tz = "UTC"
    match timezone:
        case "JST":
            tz = "Asia/Tokyo"

    start_timestamp = get_timestamp(d[0], tz)
    end_timestamp = get_timestamp(d[1], tz, end=True)

    df = df.where(df["Opened"] >= start_timestamp)
    df = df.where(df["Opened"] <= end_timestamp)

    st.write("PnL(sum):", df['PnL'].sum(), "USD")
    st.write("PnL(mean):", df['PnL'].mean(), "USD")

    df_long = df.where(df["Type"] == "Long")
    df_short = df.where(df["Type"] == "Short")

    st.write("Long PnL(mean):", df_long['PnL'].mean(), "USD")
    st.write("Short PnL(mean):", df_short['PnL'].mean(), "USD")

    plot = sns.catplot(x="Type", y="PnL", data=df, kind="box")
    st.pyplot(plot.fig)

    plot = sns.catplot(x="Market", y="PnL", data=df, kind="box", hue="Type")
    st.pyplot(plot.fig)
