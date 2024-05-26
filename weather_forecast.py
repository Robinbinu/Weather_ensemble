import streamlit as st
import requests_cache
import pandas as pd
from openmeteo_requests import Client
from openmeteo_sdk.Variable import Variable
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from retry_requests import retry
import folium
from streamlit_folium import st_folium
from geopy.geocoders import Nominatim
from datetime import datetime, timedelta
import weather_code_decoder as wcd

# Function to setup retry mechanism
def setup_retry(session, retries, backoff_factor):
    retry_strategy = Retry(
        total=retries,
        backoff_factor=backoff_factor,
        status_forcelist=[429, 500, 502, 503, 504],
        allowed_methods=["HEAD", "GET", "OPTIONS"]
    )
    adapter = HTTPAdapter(max_retries=retry_strategy)
    session.mount("http://", adapter)
    session.mount("https://", adapter)
    return session

# Function to get location name from coordinates
def get_location_name(latitude, longitude):
    geolocator = Nominatim(user_agent="weather_app")
    location = geolocator.reverse((latitude, longitude), exactly_one=True)
    if location:
        return location.address
    else:
        return None
    
# Function to get coordinates from a location name
def get_coordinates(location_name):
    geolocator = Nominatim(user_agent="weather_app")
    location = geolocator.geocode(location_name)
    if location:
        return location.latitude, location.longitude
    else:
        return None, None

# Streamlit App
def main():
    st.title("Weather Forecast Module")

    # Input for location search
    location_name = st.text_input("Enter a location name:")

    # Get coordinates from location name
    if location_name:
        lat, lon = get_coordinates(location_name)
        if lat and lon:
            st.success(f"Coordinates for {location_name}: Latitude {lat}, Longitude {lon}")
        else:
            st.error(f"Could not find coordinates for {location_name}. Please try another location.")
            lat, lon = 11.9338, 79.8298  # Default coordinates
    else:
        lat, lon = 11.9338, 79.8298  # Default coordinates

    # Folium map for selecting location
    m = folium.Map(location=[lat, lon], zoom_start=5)
    marker = folium.Marker(location=[lat, lon], draggable=True)
    m.add_child(marker)

    # Render Folium map in Streamlit
    map_data = st_folium(m, width=700, height=500)

    if map_data['last_clicked']:
        lat = map_data['last_clicked']['lat']
        lon = map_data['last_clicked']['lng']

    st.write(f"Selected Coordinates: Latitude {lat}, Longitude {lon}")

    # Fetch weather data
    if st.button("Get Weather Data"):
        cache_session = requests_cache.CachedSession('.cache', expire_after=3600)
        retry_session = setup_retry(cache_session, retries=5, backoff_factor=0.2)
        openmeteo = Client(session=retry_session)
        
        url = "https://ensemble-api.open-meteo.com/v1/ensemble"
        params = {
            "latitude": lat,
            "longitude": lon,
            "hourly": ["temperature_2m", "weather_code", "relative_humidity_2m", "wind_speed_10m"],  # Add extra weather variables here
            "forecast_days": 7,
            # "models": ["icon_seamless", "icon_global", "icon_eu", "icon_d2", "gfs_seamless", "gfs025", "gfs05", "ecmwf_ifs04", "ecmwf_ifs025", "gem_global", "bom_access_global_ensemble"]
            "models":"icon_seamless"
        }
        responses = openmeteo.weather_api(url, params=params)
        
        response = responses[0]
        st.write(f"Coordinates: {response.Latitude()}°N, {response.Longitude()}°E")
        st.write(f"Elevation: {response.Elevation()} m asl")
        
        # Process hourly data
        hourly = response.Hourly()
        hourly_data = {
            "date": pd.date_range(
                start=pd.to_datetime(hourly.Time(), unit="s", utc=True),
                end=pd.to_datetime(hourly.TimeEnd(), unit="s", utc=True),
                freq=pd.Timedelta(seconds=hourly.Interval()),
                inclusive="left"
            )
        }
        
        for i in range(hourly.VariablesLength()):
            variable = hourly.Variables(i)
            member = variable.EnsembleMember()
            values = variable.ValuesAsNumpy()
            if variable.Variable() == Variable.temperature and variable.Altitude() == 2:
                hourly_data[f"temperature_2m_member{member}"] = values
            elif variable.Variable() == Variable.weather_code:
                hourly_data[f"weather_code_member{member}"] = values
            elif variable.Variable() == Variable.relative_humidity and variable.Altitude() == 2:  # Add extra conditions for additional weather variables
                hourly_data[f"relative_humidity_2m_member{member}"] = values
            elif variable.Variable() == Variable.wind_speed and variable.Altitude() == 10:  # Assuming wind speed is measured at 10m height
                hourly_data[f"wind_speed_10m_member{member}"] = values
                 # Add more conditions for other weather variables as needed

        df = pd.DataFrame(data=hourly_data)
        df.set_index('date', inplace=True)

        # Create columns for max_temp, max_weather_code, max_relative_humidity, max_wind_speed
        df['max_temp'] = df[[col for col in df.columns if 'temperature_2m' in col]].max(axis=1)
        df['max_weather_code'] = df[[col for col in df.columns if 'weather_code' in col]].max(axis=1)
        df['max_relative_humidity'] = df[[col for col in df.columns if 'relative_humidity_2m' in col]].max(axis=1)
        df['max_wind_speed'] = df[[col for col in df.columns if 'wind_speed_10m' in col]].max(axis=1)

        # Calculate daily mean
        daily_mean = df.resample('D').mean()
        daily_mean = daily_mean.dropna()  # Drop rows with NaN values
        
        # Calculate daily max
        daily_max = df.resample('D').max()
        daily_max = daily_max.dropna() 

        # Remove time component from index
        daily_mean.index = daily_max.index.date
        daily_max.index = daily_max.index.date
        
        df['max_weather_code'] = df[[col for col in df.columns if 'weather_code' in col]].max(axis=1)
        
        df['weather_desc'] = df['max_weather_code'].map(wcd.map_weather_codes)
        daily_max['weather_desc'] = daily_max['max_weather_code'].map(wcd.map_weather_codes)

        # Display DataFrame
         # Display DataFrame
        st.write("Daily Data:")
        st.dataframe(daily_max[['max_temp', 'max_weather_code', 'max_relative_humidity', 'max_wind_speed','weather_desc']])
        
        st.write("Daily Mean Data:")
        st.dataframe(daily_mean[['max_temp', 'max_weather_code', 'max_relative_humidity', 'max_wind_speed']])

        # Display Location Name
        if lat and lon:
            location_name = get_location_name(lat, lon)
            if location_name:
                st.write(f"Current Location: {location_name}")
            else:
                st.write("Location Name Not Available")

        # Print Tomorrow's Temperature
        tomorrow_date = datetime.utcnow().date() + timedelta(days=1)
        if tomorrow_date in daily_mean.index:
            tomorrow_temp = daily_mean.loc[tomorrow_date, 'max_temp']
            tomorrow_type= wcd.map_weather_codes(daily_max.loc[tomorrow_date, 'max_weather_code'].round())
            st.write(f"Tomorrow's Temperature: {tomorrow_temp.round()}°C")
            st.write(f"Tomorrow's probable weather: {tomorrow_type}")
            
        else:
            st.write("Tomorrow's Temperature Not Available")

        # Display DataFrame
        st.write("Overall Weather Data:")
        st.dataframe(df.head())
        
        # st.write(df.max_weather_code.value_counts())

        # Display Temperature Over Time
        st.subheader("Temperature Chart")
        st.line_chart(df['max_temp'])

        # Display Code Over Time
        st.subheader("Weather Code Chart")
        st.line_chart(df['max_weather_code'])
        
         # Display Code Over Time
        st.subheader("Weather Type Chart")
        st.scatter_chart(df['weather_desc'])

        # Display Relative Humidity Over Time
        st.subheader("Relative Humidity Chart")
        st.line_chart(df['max_relative_humidity'])

        # Display Wind Speed Over Time
        st.subheader("Wind Speed Chart")
        st.line_chart(df['max_wind_speed'])


if __name__ == '__main__':
    main()

