import streamlit as st
import pandas as pd
import numpy as np

st.title('Home and leisure injuries')


# Load data

@st.cache_data
def load_data():
    df = pd.read_csv("data/mds dashboard.csv", low_memory=False)

    # filter out unneeded rows and columns
    cols = [
        'RecordingCountry',
        'AgeCategoryOfPatient',
        'SexOfPatient',
       'CountryOfPermanentResidence',
       'MonthOfAttendance',
       'YearOfAttendance',
       'TreatmentAndFollowUp',
       'TypeOfInjury1',
       'TypeOfInjury2',
       'PartOfTheBodyInjured1',
       'PartOfTheBodyInjured2',
       'Intent',
       'PlaceOfOccurrence',
       'MechanismOfInjury',
       'ActivityWhenInjured'
    ]
    df = df.loc[df["HomeLeisure"] == 1, cols]

    # convert all columns to categories to increase performance
    for c in df.columns:

        if c in ["YearOfAttendance"]:
            df[c] = df[c].astype(int, errors="raise")
            continue
        
        df[c] = pd.Categorical(df[c], categories=sorted(df[c].unique().astype(str)), ordered=True)

    return df

@st.cache_data
def convert_to_csv(df):
   return df.to_csv(index=False).encode('utf-8')

df = load_data()


# Line graph

st.write("## Injuries by time")

col_opts = list(df.columns)
col_opts.remove("YearOfAttendance")
opt = st.selectbox("Category", col_opts, key="selextbox-linegraph")  # it has the first option in the list selected, so consider ensuring that "RecordingCountry" is the first item

# this is the calculation of injury numbers
p = df.groupby(["YearOfAttendance", opt]) \
    .size().unstack()

st.line_chart(p)


# Bar chart

st.write("## Injuries by category")

col_opts = list(df.columns)
col_opts.remove("YearOfAttendance")
opt = st.selectbox("Category", col_opts, key="selectbox-barchart")  # it has the first option in the list selected, so consider ensuring that "RecordingCountry" is the first item

p = df.groupby(["YearOfAttendance", opt]) \
    .size().unstack().mean()

st.bar_chart(p)


# Display column selector

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
