import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from io import BytesIO

st.set_page_config(page_title="EU Injury Dashboard", layout="wide")

# Load data for all injury categories
@st.cache_data
def load_data():
    # Road Traffic Accidents
    traffic_file_path = "WHO_Road_Traffic_Injuries_Europe.xlsx"
    traffic_df = pd.read_excel(traffic_file_path, sheet_name="Tabelle1")
    traffic_df = traffic_df[traffic_df['Number'].notna()]

    # Poisonings
    poisoning_file_path = "WHO_Poisonings_Europe.xlsx"
    poisoning_df = pd.read_excel(poisoning_file_path, sheet_name="Tabelle1")
    poisoning_df = poisoning_df[poisoning_df['Number'].notna()]

    # Falls
    falls_file_path = "WHO_Falls_Europe.xlsx"
    falls_df = pd.read_excel(falls_file_path, sheet_name="Tabelle1")
    falls_df = falls_df[falls_df['Number'].notna()]

    # Fires
    fires_file_path = "WHO_Fires_Europe.xlsx"
    fires_df = pd.read_excel(fires_file_path, sheet_name="Tabelle1")
    fires_df = fires_df[fires_df['Number'].notna()]

    # Drownings
    drownings_file_path = "WHO_Drownings_Europe.xlsx"
    drownings_df = pd.read_excel(drownings_file_path, sheet_name="Tabelle1")
    drownings_df = drownings_df[drownings_df['Number'].notna()]

    # Mechanical Forces
    mechanical_file_path = "WHO_Mechanical_Forces_Europe.xlsx"
    mechanical_df = pd.read_excel(mechanical_file_path, sheet_name="Tabelle1")
    mechanical_df = mechanical_df[mechanical_df['Number'].notna()]

    # Natural Disasters
    disasters_file_path = "WHO_Natural_Disasters_Europe.xlsx"
    disasters_df = pd.read_excel(disasters_file_path, sheet_name="Tabelle1")
    disasters_df = disasters_df[disasters_df['Number'].notna()]

    # Other Unintentional Injuries
    other_file_path = "WHO_Other_Unintentional_Injuries_Europe.xlsx"
    other_df = pd.read_excel(other_file_path, sheet_name="Tabelle1")
    other_df = other_df[other_df['Number'].notna()]

    return {
        "Road Traffic Accidents": traffic_df,
        "Poisonings": poisoning_df,
        "Falls": falls_df,
        "Fires": fires_df,
        "Drownings": drownings_df,
        "Mechanical Forces": mechanical_df,
        "Natural Disasters": disasters_df,
        "Other Unintentional Injuries": other_df,
    }

# Load all datasets
data_dict = load_data()

# Sidebar for menu selection
st.sidebar.header("Select Statistic Type")
statistic_type = st.sidebar.selectbox("Choose a statistic", list(data_dict.keys()))

# Select the appropriate dataset based on the selection
df = data_dict[statistic_type]

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
ax1.set_title(f"{statistic_type} Deaths Over Time")
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
    ax3.set_title(f"Deaths by Age Group and Country")
ax3.set_ylabel("Number of Deaths")
ax3.set_xlabel("Age Group")
ax3.legend(title="Country")
st.pyplot(fig3)


st.caption("Source: WHO Mortality Database")
