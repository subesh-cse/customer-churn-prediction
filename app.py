import streamlit as st
import pandas as pd
import numpy as np
import joblib

# -----------------------------
# Load trained model and scaler
# -----------------------------
model = joblib.load("models/churn_model.pkl")
scaler = joblib.load("models/scaler.pkl")

# -----------------------------
# Load dataset to rebuild feature structure
# -----------------------------
df = pd.read_csv("data/WA_Fn-UseC_-Telco-Customer-Churn.csv")

# Same preprocessing as training
df['TotalCharges'] = pd.to_numeric(df['TotalCharges'], errors='coerce')
df['TotalCharges'] = df['TotalCharges'].fillna(0)
df = df.drop('customerID', axis=1)
df['Churn'] = df['Churn'].map({'No': 0, 'Yes': 1})

# Recreate encoded feature structure
df_encoded = pd.get_dummies(df, drop_first=True)
feature_columns = df_encoded.drop("Churn", axis=1).columns

# -----------------------------
# Streamlit UI
# -----------------------------
st.title("Customer Churn Prediction")

st.write("Enter customer details to predict churn.")

# User Inputs
tenure = st.slider("Tenure (months)", 0, 72, 12)

monthly_charges = st.number_input(
    "Monthly Charges",
    min_value=0.0,
    max_value=200.0,
    value=70.0
)

total_charges = st.number_input(
    "Total Charges",
    min_value=0.0,
    max_value=10000.0,
    value=1000.0
)

# -----------------------------
# Prepare input
# -----------------------------
input_df = pd.DataFrame(np.zeros((1, len(feature_columns))), columns=feature_columns)

input_df["tenure"] = tenure
input_df["MonthlyCharges"] = monthly_charges
input_df["TotalCharges"] = total_charges

# Scale input
input_scaled = scaler.transform(input_df)

# -----------------------------
# Prediction
# -----------------------------
if st.button("Predict Churn"):

    prediction = model.predict(input_scaled)[0]
    probability = model.predict_proba(input_scaled)[0][1]

    st.subheader("Prediction Confidence")

    if prediction == 1:
        st.error("Customer likely to churn")
        st.metric("Churn Probability", f"{probability:.2f}")
        st.progress(float(probability))
    else:
        stay_prob = 1 - probability
        st.success("Customer likely to stay")
        st.metric("Stay Probability", f"{stay_prob:.2f}")
        st.progress(float(stay_prob))