import streamlit as st
import pandas as pd

#st.set_page_config(page_title="EU Injury Dashboard", layout="wide")

@st.cache_data
def load_data_summary():
    #df = pd.read_csv("data/mds dashboard.csv", low_memory=False)
    df = pd.read_csv("data/mds dashboard random.csv")

    cols = ["YearOfAttendance", "HomeLeisure", "RoadTraffic", "Fall", "Sports", "PaidWork", "SelfHarm", "Assault"]
    summary = df.loc[:, cols]
    summary["n"] = 1

    return summary.groupby("YearOfAttendance").sum()

@st.cache_data
def load_reference_population():
    return pd.read_csv("data/reference population.csv")

summary = load_data_summary()
refpop = load_reference_population()

st.write("# Welcome to the European Injury Database")

st.warning('This dashboard shows random data to showcase the functionality of the dashboard. The *actual* MDS will be available in the near future.', icon="⚠️")

st.write("Incidence of injuries in the IDB-MDS per year, only includes selected stable countries and years.")

# calculate incidence for each year
refpop_year = refpop.groupby("YearOfAttendance").sum()
incidence = pd.concat([summary["n"], refpop_year], axis=1)
incidence["IncidencePer1000"] = incidence["n"] / incidence["ReferencePopulation"] * 1000

st.line_chart(
    incidence["IncidencePer1000"],
    x_label = "Year",
    y_label = "Incidence per 1000 citizens"
)

st.write("Average annual injuries according to type.")

st.bar_chart(
    summary.loc[:, summary.columns != "n"].sum() / refpop["ReferencePopulation"].sum() * 1000,
    x_label = "Type of injury",
    y_label = "Incidence per 1000 citizens"
)


# print number of injuries per year and distribution by category