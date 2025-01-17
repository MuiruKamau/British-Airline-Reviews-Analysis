import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime
import matplotlib.pyplot as plt

# Preprocessing function
@st.cache_data
def preprocess_data():
    ba_reviews = pd.read_csv('ba_reviews.csv')  # Replace with actual file path
    countries = pd.read_csv('countries.csv')   # Replace with actual file path

    # Handle missing values
    countries.loc[countries['Country'] == 'Sark', 'Code'] = 'SRK'
    most_frequent_type = ba_reviews['traveller_type'].mode()[0]
    ba_reviews['traveller_type'].fillna(most_frequent_type, inplace=True)

    # Format columns
    ba_reviews['date'] = pd.to_datetime(ba_reviews['date'], errors='coerce', dayfirst=True)
    ba_reviews['date_flown'] = pd.to_datetime(ba_reviews['date_flown'], errors='coerce', dayfirst=True)
    ba_reviews['place_cleaned'] = ba_reviews['place'].str.strip().str.title()

    # Merge datasets
    countries['Country'] = countries['Country'].str.strip()
    merged_data = pd.merge(
        ba_reviews,
        countries,
        left_on='place_cleaned',
        right_on='Country',
        how='left'
    )

    # Add Top 10 Aircraft Grouping
    top_aircraft = merged_data['aircraft'].value_counts().head(10).index.tolist()
    merged_data['aircraft_grouped'] = merged_data['aircraft'].apply(lambda x: x if x in top_aircraft else "Others")

    return merged_data

# Load and preprocess data
cleaned_data = preprocess_data()

# Streamlit App Layout
st.title("British Airways Dashboard")

# Sidebar Filters
st.sidebar.header("Filters")

# Date Range Filter with Year → Month → Day Hierarchical Selection
st.sidebar.subheader("Select Date Range")
available_years = sorted(cleaned_data['date_flown'].dropna().dt.year.unique())
selected_year = st.sidebar.selectbox("Select Year", ["All"] + available_years)

if selected_year != "All":
    available_months = sorted(cleaned_data[cleaned_data['date_flown'].dt.year == selected_year]['date_flown'].dt.month.unique())
    month_names = [datetime(1900, month, 1).strftime("%B") for month in available_months]
    month_map = {name: month for name, month in zip(month_names, available_months)}
    selected_month_name = st.sidebar.selectbox("Select Month", ["All"] + month_names)
    selected_month = month_map.get(selected_month_name, "All")
else:
    selected_month = "All"

if selected_year != "All" and selected_month != "All":
    available_days = sorted(cleaned_data[
        (cleaned_data['date_flown'].dt.year == selected_year) &
        (cleaned_data['date_flown'].dt.month == selected_month)
    ]['date_flown'].dt.day.unique())
    selected_day = st.sidebar.selectbox("Select Day", ["All"] + available_days)
else:
    selected_day = "All"

# Apply the hierarchical date filter
filtered_data = cleaned_data.copy()

if selected_year != "All":
    filtered_data = filtered_data[filtered_data['date_flown'].dt.year == selected_year]

if selected_month != "All":
    filtered_data = filtered_data[filtered_data['date_flown'].dt.month == selected_month]

if selected_day != "All":
    filtered_data = filtered_data[filtered_data['date_flown'].dt.day == selected_day]

# Traveller Type Filter
traveller_types = ["All"] + list(cleaned_data['traveller_type'].unique())
selected_traveller_types = st.sidebar.multiselect(
    "Select Traveller Type",
    traveller_types,
    default="All"
)

if "All" in selected_traveller_types and len(selected_traveller_types) > 1:
    selected_traveller_types.remove("All")
elif len(selected_traveller_types) == 0:
    selected_traveller_types = ["All"]

if "All" not in selected_traveller_types:
    filtered_data = filtered_data[filtered_data['traveller_type'].isin(selected_traveller_types)]

# Recommended Filter
recommendation_options = ["All"] + list(cleaned_data['recommended'].unique())
selected_recommendations = st.sidebar.multiselect(
    "Select Recommendation Status",
    recommendation_options,
    default="All"
)

if "All" in selected_recommendations and len(selected_recommendations) > 1:
    selected_recommendations.remove("All")
elif len(selected_recommendations) == 0:
    selected_recommendations = ["All"]

if "All" not in selected_recommendations:
    filtered_data = filtered_data[filtered_data['recommended'].isin(selected_recommendations)]

# Aircraft Type Filter
aircraft_types = ["All"] + list(cleaned_data['aircraft_grouped'].unique())
selected_aircraft = st.sidebar.multiselect(
    "Select Aircraft Type",
    aircraft_types,
    default="All"
)

if "All" in selected_aircraft and len(selected_aircraft) > 1:
    selected_aircraft.remove("All")
elif len(selected_aircraft) == 0:
    selected_aircraft = ["All"]

if "All" not in selected_aircraft:
    filtered_data = filtered_data[filtered_data['aircraft_grouped'].isin(selected_aircraft)]

# Country Filter
continent_groups = cleaned_data.groupby('Continent')['place_cleaned'].unique().to_dict()
selected_continent = st.sidebar.selectbox("Select Continent", options=["All"] + list(continent_groups.keys()))

if selected_continent == "All":
    available_countries = ["All"] + list(cleaned_data['place_cleaned'].unique())
else:
    available_countries = ["All"] + list(continent_groups[selected_continent])

selected_countries = st.sidebar.multiselect(
    "Select Countries",
    available_countries,
    default="All"
)

if "All" in selected_countries and len(selected_countries) > 1:
    selected_countries.remove("All")
elif len(selected_countries) == 0:
    selected_countries = ["All"]

if "All" not in selected_countries:
    filtered_data = filtered_data[filtered_data['place_cleaned'].isin(selected_countries)]

# Tabs for Visualizations
tab1, tab2 = st.tabs(["Filtered Data Sample", "Visualizations"])

with tab1:
    st.write("### Filtered Data Sample")
    st.dataframe(filtered_data)

with tab2:
    st.write("### Reviews Per Country (Based on Filters)")
    # Count the number of reviews per selected country
    flights_per_country = filtered_data['place_cleaned'].value_counts().reset_index()
    flights_per_country.columns = ['Country', 'Number of Flights']

    # Plot the bar chart
    fig, ax = plt.subplots(figsize=(12, 6))
    bars = ax.bar(
        flights_per_country['Country'],
        flights_per_country['Number of Flights'],
        color='skyblue'
    )
    for bar in bars:
        height = bar.get_height()
        ax.text(
            bar.get_x() + bar.get_width() / 2,  # x-coordinate
            height + 0.5,                      # y-coordinate
            f'{int(height)}',                  # Label
            ha='center',                       # Alignment
            va='bottom',                       # Position
            fontsize=10                        # Font size
        )

    ax.set_title('Reviews Per Country (Filtered)', fontsize=16)
    ax.set_xlabel('Country', fontsize=14)
    ax.set_ylabel('Number of Flights', fontsize=14)
    plt.xticks(rotation=45, ha='right', fontsize=12)
    st.pyplot(fig)

