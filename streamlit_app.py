import streamlit as st
from SmartApi import SmartConnect
import pyotp
import requests
import pandas as pd

st.title("Aditi Trading Dashboard - Option Chain Analysis")

api_key = st.secrets.get("API_KEY")
client_id = st.secrets.get("CLIENT_ID")
pin = st.secrets.get("PIN")
token = st.secrets.get("TOTP_TOKEN")

@st.cache_data
def load_script_master():
    url = "https://margincalculator.angelbroking.com/OpenAPI_File/files/OpenAPIScripMaster.json"
    response = requests.get(url)
    if response.status_code == 200:
        return pd.DataFrame(response.json())
    return pd.DataFrame()

if api_key and client_id and pin and token:
    try:
        obj = SmartConnect(api_key=api_key)
        totp = pyotp.TOTP(token).now()
        data = obj.generateSession(client_id, pin, totp)
        
        if data and data.get('status'):
            st.success("Connected to Angel One Successfully!")
            
            with st.spinner("Loading Market Database..."):
                df = load_script_master()
                
            if not df.empty:
                # इंडेक्स चुनने के लिए ऑप्शन
                index_choice = st.selectbox("Select Index for Option Chain:", ["NIFTY", "BANKNIFTY"])
                
                if st.button("Get Option Chain"):
                    with st.spinner(f"Fetching Option Chain for {index_choice}..."):
                        # NFO सेगमेंट से उस इंडेक्स के ऑप्शंस को फिल्टर करना
                        option_df = df[(df['name'] == index_choice) & (df['exch_seg'] == 'NFO')]
                        
                        if not option_df.empty:
                            # शुरुआती कुछ स्ट्राइक्स या डेटा दिखाने के लिए टेबल तैयार करना
                            st.write(f"Total Option Contracts found for {index_choice}: {len(option_df)}")
                            
                            # यूजर को आसानी से देखने के लिए मुख्य कॉलम दिखाना
                            display_cols = ['symbol', 'strike', 'instrumenttype', 'expiry', 'token']
                            available_cols = [col for col in display_cols if col in option_df.columns]
                            
                            st.dataframe(option_df[available_cols].head(50))
                            st.info("ऊपर दिए गए सिंबल या टोकन का उपयोग करके आप लाइव एलटीपी (LTP) ट्रैक कर सकते हैं।")
                        else:
                            st.warning("Option chain data not found.")
            else:
                st.error("Could not load Scrip Master database.")
        else:
            st.error(f"Login Failed: {data.get('message', 'Unknown error')}")
            
    except Exception as e:
        st.error(f"Error: {e}")
else:
    st.warning("Please configure API_KEY, CLIENT_ID, PIN, and TOTP_TOKEN in Streamlit Secrets.")
