import streamlit as st
import pandas as pd

#st.set_page_config(page_title="EU Injury Dashboard", layout="wide")

@st.cache_data
def load_data_summary():
    df = pd.read_csv("data/mds dashboard.csv")

    cols = ["YearOfAttendance", "HomeLeisure", "RoadTraffic", "Fall", "Sports", "PaidWork", "SelfHarm", "Assault"]
    summary = df.loc[:, cols]
    summary["n"] = 1

    return summary.groupby("YearOfAttendance").sum()

summary = load_data_summary()

st.write("# Welcome to the European Injury Database")

st.write("Injuries in the IDB-MDS per year, only includes selected stable countries and years.")

st.line_chart(summary["n"])

st.write("Injury distribution according to type.")

st.bar_chart(summary.loc[:, summary.columns != "n"].sum())


# print number of injuries per year and distribution by category