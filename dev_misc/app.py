import streamlit as st
import subprocess
import webbrowser

command = 'streamlit run 1_🌦️Global_weather_forecast.py --server.port 8502'
process = subprocess.Popen(command, stdout=subprocess.PIPE, shell=True)
output, error = process.communicate()
print(output.decode())

def main():
    st.title("Weather App")

    if st.button("Weather Forecast"):
        # Open weather forecast page in browser
        webbrowser.open_new_tab("http://localhost:8502")

    if st.button("Weather Predict"):
        # Open weather predict page in browser
        webbrowser.open_new_tab("http://localhost:8501/predict")

if __name__ == "__main__":
    main()