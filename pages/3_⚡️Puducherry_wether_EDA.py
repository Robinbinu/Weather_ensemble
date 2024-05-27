import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.figure_factory as ff
import warnings

# Load the dataset
@st.cache_data
def load_data():
    data = pd.read_csv("dataset/data.csv", parse_dates=["date"], index_col="date")
    return data.drop(columns=['weather_code'])  # Remove 'weather_code' column

# Suppress warnings
warnings.filterwarnings("ignore")

data = load_data()

# Title and introduction
st.title("Exploratory Data Analysis (EDA) - Pondicherry Weather Data")
st.write("This page presents an exploratory analysis of the historical weather data for Pondicherry.")

# Display basic information about the dataset
st.header("Dataset Overview")
st.write("Shape of the dataset:", data.shape)
st.write("Column names:", data.columns.tolist())
st.write("Preview of the dataset:")
st.write(data.head())

# Display summary statistics
st.header("Summary Statistics")
st.write("Basic statistics for numerical columns:")
st.write(data.describe())

# Display missing values
st.header("Missing Values")
missing_values = data.isnull().sum()
st.write("Number of missing values in each column:")
st.write(missing_values)

# Display data distribution
st.header("Data Distribution")
st.write("Distribution of weather variables:")
st.write("Temperature (Max, Min, Mean):")
st.write(data[["tmax", "tmin", "tmean"]].describe())
st.write("Other weather variables:")
st.write(data[["atmax", "atmin", "atmean", "sun_dur", "prec_sum", "prec_hrs", "wsmax", "wgmax", "radsum", "evapotrans"]].describe())

# Display time series plots
st.header("Time Series Analysis")
st.write("Temperature Over Time:")
fig_temp = px.line(data.reset_index(), x='date', y=["tmax", "tmin", "tmean"], title="Temperature Over Time")
st.plotly_chart(fig_temp)

st.write("Precipitation Over Time:")
fig_precip = px.line(data.reset_index(), x='date', y=["prec_sum", "prec_hrs"], title="Precipitation Over Time")
st.plotly_chart(fig_precip)

st.write("Wind Speed Over Time:")
fig_wind = px.line(data.reset_index(), x='date', y=["wsmax", "wgmax"], title="Wind Speed Over Time")
st.plotly_chart(fig_wind)

st.write("Solar Radiation Over Time:")
fig_rad = px.line(data.reset_index(), x='date', y="radsum", title="Solar Radiation Over Time")
st.plotly_chart(fig_rad)
