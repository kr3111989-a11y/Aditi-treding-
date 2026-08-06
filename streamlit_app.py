import streamlit as st

st.title("Aditi Trading Dashboard")
st.write("Welcome to your private trading automation panel.")

api_key = st.secrets.get("API_KEY", "Not Set")
if api_key != "Not Set":
    st.success("API Key loaded securely!")
else:
    st.warning("Please configure your API_KEY in Streamlit Secrets.")


