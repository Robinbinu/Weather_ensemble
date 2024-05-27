import streamlit as st
import pandas as pd
import numpy as np
from sklearn.preprocessing import MinMaxScaler, StandardScaler
import pickle
from tensorflow.keras.models import load_model

st.set_page_config(page_title="Feature based weather prediction", page_icon="🌡️")
st.markdown("# Feature based weather prediction")
st.sidebar.header("Feature based weather prediction")

# Load the LSTM model and scalers
loaded_lstm_model = load_model('models/lstm_weather_model.h5')

with open('models/lstm_model.pkl', 'rb') as f:
    lstm_scalers = pickle.load(f)
    lstm_scaler_features = lstm_scalers['scaler_features']
    lstm_scaler_target = lstm_scalers['scaler_target']

# Load the XGBoost model
with open('models/xgboost_model.pkl', 'rb') as f:
    loaded_xgboost_model = pickle.load(f)

# Load the Ridge Regression model and scaler
with open('models/ridge_regression_model.pkl', 'rb') as f:
    ridge_data = pickle.load(f)
    loaded_ridge_model = ridge_data['model']
    ridge_scaler = ridge_data['scaler']

# Column names for features
feature_names = ['tmin', 'tmean', 'atmax', 'atmin', 'atmean', 'sun_dur', 'prec_sum',
                 'prec_hrs', 'wsmax', 'wgmax', 'wdirdom', 'radsum', 'evapotrans']

def preprocess_data(data, scaler_features):
    data_df = pd.DataFrame(data, columns=feature_names)
    scaled_data = scaler_features.transform(data_df)
    return scaled_data

def postprocess_data(data, scaler_target):
    return scaler_target.inverse_transform(data)

# Function to make predictions for all models
def predict_all_models(data):
    predictions = {}

    # LSTM
    scaled_input_lstm = preprocess_data(data, lstm_scaler_features)
    prediction_lstm = loaded_lstm_model.predict(scaled_input_lstm.reshape(1, scaled_input_lstm.shape[0], scaled_input_lstm.shape[1]))
    prediction_lstm = postprocess_data(prediction_lstm, lstm_scaler_target)
    predictions['LSTM'] = prediction_lstm[0][0]

    # XGBoost
    scaled_input_xgb = preprocess_data(data, lstm_scaler_features)
    prediction_xgb = loaded_xgboost_model.predict(scaled_input_xgb)
    predictions['XGBoost'] = prediction_xgb[0]

    # Ridge Regression
    scaled_input_ridge = ridge_scaler.transform(data)
    prediction_ridge = loaded_ridge_model.predict(scaled_input_ridge)
    predictions['Ridge Regression'] = prediction_ridge[0]

    return predictions

st.title('Weather Prediction')

# Sidebar inputs for features with synchronized number_input and slider
st.sidebar.header('Input Features')

inputs = []
for name in feature_names:
    # Initialize session state for the synchronized value
    if f'{name}_value' not in st.session_state:
        st.session_state[f'{name}_value'] = 30.0

    # Sidebar number input with custom step value
    number_input_value = st.sidebar.number_input(
        f'{name.capitalize()} (Number Input):',
        min_value=0.0,
        max_value=100.0,
        value=st.session_state[f'{name}_value'],
        step=1.0,
        key=f'{name}_number_input'
    )

    # Sidebar slider with synchronized value
    slider_value = st.sidebar.slider(
        f'{name.capitalize()} (Slider):',
        min_value=0.0,
        max_value=100.0,
        value=st.session_state[f'{name}_value'],
        step=1.0,
        key=f'{name}_slider'
    )

    # Update the session state to synchronize both inputs
    if number_input_value != st.session_state[f'{name}_value']:
        st.session_state[f'{name}_value'] = number_input_value
    if slider_value != st.session_state[f'{name}_value']:
        st.session_state[f'{name}_value'] = slider_value

    inputs.append(st.session_state[f'{name}_value'])

input_df = pd.DataFrame([inputs], columns=feature_names)

# Display user inputs
st.subheader('User Input Features')
st.write(input_df)

# Make predictions for all models
predictions = predict_all_models(input_df.values)

# Display the predictions
st.subheader('Predictions')
for model_name, prediction in predictions.items():
    st.write(f'{model_name} Predicted tmax: {prediction:.2f}')
