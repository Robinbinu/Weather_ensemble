import streamlit as st

st.set_page_config(
    page_title="WeatherWave",
    page_icon="🌊",
)

st.write("# Welcome to WeatherWave! 🌊")

st.sidebar.success("Ride the Wave with WeatherWave")

st.markdown(
    """
    ### Discover the Future of Weather Forecasting with WeatherWave 🌦️

    WeatherWave is your ultimate destination for state-of-the-art weather forecasting and insightful data analysis. Whether you're a weather enthusiast, a data scientist, or just someone who wants to know if they should carry an umbrella tomorrow, WeatherWave has got you covered!

    **👈 Select an option from the sidebar** to dive into the powerful features of WeatherWave!

    ### 🌟 Features at a Glance:
    - **Real-time Weather Data:** Access the latest weather information from around the globe, all in one place.
    - **Advanced Forecast Models:** Utilize cutting-edge machine learning models to predict weather patterns with high accuracy.
    - **Interactive Visualizations:** Explore weather data through stunning and interactive charts and maps.
    - **Personalized Insights:** Get tailored weather updates and alerts based on your location and preferences.

    ### 📚 Want to Learn More?
    - Check out our comprehensive [documentation](https://github.com/Robinbinu/Weather_ensemble/blob/main/documentation/Tomorrow's%20Weather%20Predictive%20Analytics.pdf).
    - Join our [community forums](https://github.com/Robinbinu/Weather_ensemble) to ask questions and share feedback.

    WeatherWave is more than just weather – it's your gateway to understanding the world through data. Join us on this exciting journey and ride the wave of innovation!
    """
)
