import streamlit as st
import pandas as pd
import numpy as np

st.title('Dashboard template')


# Load data

@st.cache_data
def load_data():
    df = pd.read_csv("data/MDS 2018-2022 stable countries.csv")

    # convert all columns to categories to increase performance
    for c in df.columns:

        # this is the only pure number column
        if c == "YearOfAttendance":
            df[c] = df[c].astype(int, errors="raise")
            continue

        df[c] = pd.Categorical(df[c], categories=sorted(df[c].unique().astype(str)), ordered=True)

    return df

@st.cache_data
def convert_to_csv(df):
   return df.to_csv(index=False).encode('utf-8')

df = load_data()

# Display column selector


st.write("## Incidence rate by year")

st.write("Placeholder for line graph.")

p = df.groupby(["YearOfAttendance", "RecordingCountry"]) \
    .size().unstack()

st.line_chart(p)

st.write("## Incidence rate by other variable")

st.write("Placeholder for bar graph.")


st.write("## Pivot table")

col_opts = df.columns
ColOptsFilter = st.multiselect("Select display columns", col_opts, default=["RecordingCountry", "SexOfPatient", "AgeCategoryOfPatient"], max_selections=4)

if len(ColOptsFilter) == 0:
    st.warning("### No columns have been selected")
    st.stop()

# Build popover for filters

with st.popover("Open filters"):

    # make dropdown with sorted list of values
    for c in ColOptsFilter:
        c_opt = sorted(df[c].unique().astype(str))

        # filter categorical columns by selected values
        if df[c].dtype == "category":
            v = st.multiselect(c, c_opt, default=c_opt)
            df = df.loc[df[c].isin(v), :]
            df[c] = df[c].cat.remove_unused_categories()

        # filter numerical columns (year) by range (min-max, both inclusive)
        if df[c].dtype == "int64":
            c_opt = [int(x) for x in c_opt]
            v = st.select_slider(c, c_opt, value=(np.min(c_opt), np.max(c_opt)))
            df = df.loc[df[c] >= np.min(v), :]
            df = df.loc[df[c] <= np.max(v), :]

# summarise/count groups, remove groups with zero cases
df = df.groupby(ColOptsFilter).size().reset_index(name='Count')
df = df.loc[df["Count"] > 0, :]

st.dataframe(df)

st.download_button(
    "Download",
    convert_to_csv(df),
    "file.csv",
    "text/csv",
    key='download-csv'
)
