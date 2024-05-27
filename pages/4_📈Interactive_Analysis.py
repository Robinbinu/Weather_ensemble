import streamlit as st
import pandas as pd
import plotly.express as px

# Load the dataset
@st.cache_data
def load_data():
    data = pd.read_csv("dataset/data.csv", parse_dates=["date"], index_col="date")
        # Extract month and year from the 'date' column
    data['year'] = data.index.year
    data['month'] = data.index.month

    # Define a list of weather descriptions that indicate rain
    rain_descriptions = ["Light Drizzle", "Drizzle", "Heavy Drizzle", "Light Rain", "Rain", "Heavy Rain"]

    # Filter the DataFrame for rows where the weather description indicates rain
    rain_df = data[data['weather_code'].isin(rain_descriptions)]

    # # Group by year and month to see which months had rain
    # rain_months = rain_df.groupby(['month']).size().reset_index(name='days_with_rain').sort_values(by='days_with_rain',ascending=False)
    # Group by year and month
    rain_months = rain_df.groupby(['year', 'month']).size().reset_index(name='days_with_rain')


# Display the months with rain
    rain_months.head(24)
    return data.drop(columns=['weather_code']),rain_df,rain_months # Remove 'weather_code' column

data,rain_df,rain_months = load_data()

# Title and introduction
st.title("Interactive Analysis")

# Sidebar for user selection
analysis_option = st.sidebar.selectbox(
    "Select an analysis option:",
    ("Temperature Distribution", "Correlation Heatmap", "Summary Statistics", "Time Series Plots", "Compare Distribution","Seasonal Analysis")
)

# Temperature Distribution Analysis
if analysis_option == "Temperature Distribution":
    st.subheader("Temperature Distribution Analysis")
    st.write("This section displays the distribution of temperature variables over the entire dataset.")
    temperature_option = st.sidebar.radio(
        "Select a temperature variable:",
        ("tmax", "tmin", "tmean")
    )
    st.write(f"Distribution of {temperature_option.capitalize()} Temperature:")
    fig_temp_dist = px.histogram(data, x=temperature_option, title=f"Distribution of {temperature_option.capitalize()} Temperature")
    st.plotly_chart(fig_temp_dist)

# Correlation Heatmap Analysis
elif analysis_option == "Correlation Heatmap":
    st.subheader("Correlation Heatmap Analysis")
    st.write("This section visualizes the correlation between different weather variables using a heatmap.")
    corr_matrix = data.corr()
    st.write("Correlation Matrix:")
    st.write(corr_matrix)
    fig_corr_heatmap = px.imshow(corr_matrix, title="Correlation Heatmap")
    st.plotly_chart(fig_corr_heatmap)

# Summary Statistics Analysis
elif analysis_option == "Summary Statistics":
    st.subheader("Summary Statistics Analysis")
    st.write("This section provides basic statistical summary for numerical columns in the dataset.")
    st.write("Basic statistics for numerical columns:")
    st.write(data.describe())

# Time Series Plots Analysis
elif analysis_option == "Time Series Plots":
    st.subheader("Time Series Plots Analysis")
    st.write("This section displays the trends of weather variables over time using line plots.")
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

# Compare Distribution Analysis
elif analysis_option == "Compare Distribution":
    st.subheader("Compare Distribution Analysis")
    st.write("This section allows you to compare the distribution of weather variables across different time periods or categories.")
    compare_option = st.sidebar.radio(
        "Select an option to compare:",
        ("Temperature by Month", "Temperature by Year", "Precipitation by Month", "Precipitation by Year")
    )

    if compare_option == "Temperature by Month":
        st.write("Compare Temperature Distribution by Month:")
        fig_temp_month = px.box(data.reset_index(), x=data.index.month, y=["tmax", "tmin", "tmean"], points="all",
                                title="Temperature Distribution by Month")
        st.plotly_chart(fig_temp_month)

    elif compare_option == "Temperature by Year":
        st.write("Compare Temperature Distribution by Year:")
        fig_temp_year = px.box(data.reset_index(), x=data.index.year, y=["tmax", "tmin", "tmean"], points="all",
                               title="Temperature Distribution by Year")
        st.plotly_chart(fig_temp_year)

    elif compare_option == "Precipitation by Month":
        st.write("Compare Precipitation Distribution by Month:")
        fig_precip_month = px.box(data.reset_index(), x=data.index.month, y=["prec_sum", "prec_hrs"], points="all",
                                  title="Precipitation Distribution by Month")
        st.plotly_chart(fig_precip_month)

    elif compare_option == "Precipitation by Year":
        st.write("Compare Precipitation Distribution by Year:")
        fig_precip_year = px.box(data.reset_index(), x=data.index.year, y=["prec_sum", "prec_hrs"], points="all",
                                 title="Precipitation Distribution by Year")
        st.plotly_chart(fig_precip_year)
