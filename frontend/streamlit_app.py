import os
import streamlit as st
import requests

API_URL = os.getenv("API_URL", "http://localhost:8000")

st.set_page_config(
    page_title="Sun Life Insurance Quoting",
    page_icon="🌞",
    layout="centered")

st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Source+Sans+3:wght@400;600;700&display=swap');
        html, body, [class*="css"] {
            font-family: 'Source Sans 3', sans-serif;
            background-color: #f5f5f5 !important;
        }
        .stApp {
            background-color: #f5f5f5 !important;
        }
        label {
            color: #1a3c4d !important;
        }
        .header {
            background-color: #F5A800;
            padding: 2rem;
            border-radius: 8px;
            margin-bottom: 2rem;
        }
        .header h1 {
            color: #1a3c4d;
            font-size: 2rem;
            font-weight: 700;
            margin: 0 0 0.3rem 0;
        }
        .header p {
            color: #1a3c4d;
            font-weight: 600;
            margin: 0 0 0.3rem 0;
        }
        .header small {
            color: #1a3c4d;
            font-size: 0.85rem;
        }
        .section-title {
            text-align: center;
            font-size: 1.4rem;
            font-weight: 700;
            color: #1a3c4d;
            margin-bottom: 1.5rem;
        }
        div.stButton > button {
            background-color: #1a3c4d;
            color: white;
            border: none;
            border-radius: 6px;
            padding: 0.6rem 2rem;
            font-size: 1rem;
            font-weight: 600;
            width: 100%;
        }
        div.stButton > button:hover {
            background-color: #14303f;
        }
        .quote-box {
            background-color: white;
            border-radius: 8px;
            padding: 2rem;
            text-align: center;
            border-top: 6px solid #F5A800;
            margin-top: 1.5rem;
        }
        .quote-amount {
            font-size: 3.5rem;
            font-weight: 700;
            color: #1a3c4d;
        }
        .bmi-badge {
            background-color: #F5A800;
            color: #1a3c4d;
            border-radius: 20px;
            padding: 0.3rem 1.2rem;
            font-size: 1rem;
            font-weight: 700;
            display: inline-block;
            margin-bottom: 1rem;
        }
        .reason-text {
            color: #555;
            font-size: 0.95rem;
            margin-top: 0.8rem;
        }
    </style>
""", unsafe_allow_html=True)

st.markdown("""
    <div class="header">
        <h1>Health Insurance Calculator</h1>
        <p>Secure and protect your family's future.</p>
    </div>
""", unsafe_allow_html=True)

st.markdown(
    '<div class="section-title">Tell us about yourself</div>',
    unsafe_allow_html=True)

col1, col2 = st.columns(2)
with col1:
    gender = st.selectbox("Your gender", ["Male", "Female"])
with col2:
    age = st.number_input("Your age", min_value=18, max_value=120, value=30)

col3, col4 = st.columns(2)
with col3:
    height = st.number_input(
        "Height (cm)",
        min_value=140.0,
        max_value=210.0,
        value=170.0)
with col4:
    weight = st.number_input(
        "Weight (kg)",
        min_value=45.0,
        max_value=200.0,
        value=70.0)

if st.button("Get My Quote →"):
    with st.spinner("Calculating your quote..."):
        try:
            response = requests.post(f"{API_URL}/predict", json={
                "gender": gender,
                "age": age,
                "height": height,
                "weight": weight
            })
            data = response.json()
            st.markdown(f"""
                <div class="quote-box">
                    <div class="bmi-badge">BMI: {data['bmi']}</div>
                    <div class="quote-amount">${data['quote']:.2f}</div>
                    <div class="reason-text">{data['reason']}</div>
                </div>
            """, unsafe_allow_html=True)
        except Exception:
            st.error(
                "Could not connect to the API. Make sure the FastAPI server is running.")