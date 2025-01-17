import streamlit as st
import pandas as pd

# Preprocessing function
@st.cache_data
def preprocess_data():
    # Load datasets
    ba_reviews = pd.read_csv('ba_reviews.csv')  # Replace with actual file path
    countries = pd.read_csv('countries.csv')   # Replace with actual file path

    # Step 1: Handle Missing Values in Countries Dataset
    countries.loc[countries['Country'] == 'Sark', 'Code'] = 'SRK'

    # Step 2: Handle Missing Values in BA Reviews Dataset
    most_frequent_type = ba_reviews['traveller_type'].mode()[0]
    ba_reviews['traveller_type'].fillna(most_frequent_type, inplace=True)

    # Step 3: Format Columns
    ba_reviews['date'] = pd.to_datetime(ba_reviews['date'], errors='coerce', dayfirst=True)
    ba_reviews['date_flown'] = pd.to_datetime(ba_reviews['date_flown'], errors='coerce', dayfirst=True)
    ba_reviews['place_cleaned'] = ba_reviews['place'].str.strip().str.title()

    # Step 4: Merge BA Reviews and Countries Dataset
    countries['Country'] = countries['Country'].str.strip()
    merged_data = pd.merge(
        ba_reviews,
        countries,
        left_on='place_cleaned',
        right_on='Country',
        how='left'
    )

    # Step 5: Return the cleaned dataset
    return merged_data

# Load and preprocess data
st.title("British Airways Data Preprocessing")
st.write("Loading and cleaning datasets...")

with st.spinner("Preprocessing data..."):
    cleaned_data = preprocess_data()
    st.success("Data preprocessing completed!")

# Display a sample of the cleaned data
st.write("### Sample of Preprocessed Data")
st.dataframe(cleaned_data.head())

