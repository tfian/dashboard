import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from io import BytesIO

st.set_page_config(page_title="WHO Road Traffic Dashboard", layout="wide")

# Load data
@st.cache_data
def load_data():
    file_path = "WHO_Road_Traffic_Injuries_Europe.xlsx"
    df = pd.read_excel(file_path, sheet_name="Tabelle1")
    df = df[df['Number'].notna()]  # Remove rows with missing values in Number
    return df

df = load_data()

# Sidebar filters
st.sidebar.header("Filters")
countries = df['Country Name'].unique()
selected_countries = st.sidebar.multiselect("Select countries", countries, default=['Austria', 'Germany', 'Sweden'])
years = sorted(df['Year'].unique())
selected_years = st.sidebar.slider("Select year range", int(min(years)), int(max(years)), (2000, 2020))

sexes = df['Sex'].unique()
selected_sex = st.sidebar.selectbox("Sex", sexes)

# Filtered DataFrame
filtered_df = df[(df['Country Name'].isin(selected_countries)) &
                 (df['Year'].between(*selected_years)) &
                 (df['Sex'] == selected_sex)]

st.title("\U0001F6E3 WHO Road Traffic Injury Dashboard")
st.markdown("Data from the WHO Mortality Database – Deaths from Road Traffic Accidents in Europe")

# KPIs
col1, col2, col3 = st.columns(3)
total_deaths = int(filtered_df['Number'].sum())
avg_death_rate = filtered_df['Death rate per 100 000 population'].mean()
highest_year = filtered_df.groupby('Year')['Number'].sum().idxmax()

col1.metric("\U0001F480 Total Deaths", f"{total_deaths:,}")
col2.metric("\U0001F4CA Avg. Death Rate / 100,000", f"{avg_death_rate:.2f}")
col3.metric("\U0001F5F3 Year with Most Deaths", f"{highest_year}")

# 1. Trend analysis
st.subheader("\U0001F4C8 Deaths Over Time")
fig1, ax1 = plt.subplots()
trend_data = filtered_df.groupby(['Year', 'Country Name'])['Number'].sum().unstack()
trend_data.plot(ax=ax1, marker='o')
ax1.set_ylabel("Number of Deaths")
ax1.set_xlabel("Year")
ax1.set_title("Road Traffic Deaths Over Time")
st.pyplot(fig1)

# 2. Country comparison
st.subheader("\U0001F30E Country Comparison (Death Rate in Latest Year)")
latest_year = max(selected_years)
latest_df = filtered_df[filtered_df['Year'] == latest_year]
bar_data = latest_df.groupby('Country Name')['Death rate per 100 000 population'].mean().sort_values()
fig2, ax2 = plt.subplots()
bar_data.plot(kind='barh', ax=ax2, color='steelblue')
ax2.set_xlabel("Death Rate per 100,000")
ax2.set_title(f"Death Rate in {latest_year}")
st.pyplot(fig2)

# 3. Age distribution by country
st.subheader("\U0001F9D3 Age Distribution of Deaths by Country")
age_df = filtered_df.copy()
age_summary = age_df.groupby(['Country Name', 'Age Group'])['Number'].sum().unstack().fillna(0)
fig3, ax3 = plt.subplots(figsize=(10, 6))
if len(age_summary) == 1:
    age_summary.T.plot(kind='bar', ax=ax3, legend=False)
    ax3.set_title(f"Deaths by Age Group in {age_summary.index[0]}")
else:
    age_summary.T.plot(kind='bar', ax=ax3)
    ax3.set_title("Deaths by Age Group and Country")
ax3.set_ylabel("Number of Deaths")
ax3.set_xlabel("Age Group")
ax3.legend(title="Country")
st.pyplot(fig3)

# 4. Raw data view
st.subheader("\U0001F4C3 Filtered Raw Data")
st.dataframe(filtered_df.reset_index(drop=True))

# Export functions
st.subheader("\U0001F4BE Export")

def convert_df_to_csv(df):
    return df.to_csv(index=False).encode('utf-8')

csv_data = convert_df_to_csv(filtered_df)
st.download_button(label="Download CSV of filtered data",
                   data=csv_data,
                   file_name='filtered_road_traffic_data.csv',
                   mime='text/csv')

buffer = BytesIO()
fig3.savefig(buffer, format="pdf")
buffer.seek(0)
st.download_button(label="Download age distribution chart (PDF)",
                   data=buffer,
                   file_name="age_distribution_by_country.pdf",
                   mime="application/pdf")

st.caption("Source: WHO Mortality Database")
