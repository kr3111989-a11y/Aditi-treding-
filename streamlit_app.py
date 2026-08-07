import streamlit as st
from SmartApi import SmartConnect
import pyotp
import requests
import pandas as pd

st.title("Aditi Trading Dashboard - Market")

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
                user_input = st.text_input("Enter Symbol / Option (e.g. RELIANCE-EQ, NIFTY, 24650CE):", "").strip().upper()
                
                if st.button("Get Live Price"):
                    if user_input:
                        # सामान्य शॉर्टकट और ऑप्शन फॉर्मेट ठीक करना
                        if user_input in ["NIFTY 50", "NIFTY50"]:
                            user_input = "NIFTY"
                        elif user_input in ["BANK NIFTY", "BANKNIFTY"]:
                            user_input = "BANKNIFTY"
                        
                        # अगर यूजर ने स्ट्राइक प्राइस या CE/PE लिखा हो (जैसे NIFTY 24650 CE)
                        # तो स्पेस हटाकर NIFTY से जोड़ देना
                        if "CE" in user_input or "PE" in user_input:
                            user_input = user_input.replace(" ", "")
                            if not user_input.startswith("NIFTY") and not user_input.startswith("BANKNIFTY"):
                                user_input = "NIFTY" + user_input
                        
                        # डेटाबेस में खोजना
                        matched = df[df['symbol'] == user_input]
                        if matched.empty:
                            matched = df[df['symbol'].str.contains(user_input, na=False)]
                        
                        if not matched.empty:
                            exchange = matched.iloc[0]['exch_seg']
                            token_id = matched.iloc[0]['token']
                            exact_symbol = matched.iloc[0]['symbol']
                            
                            st.write(f"Found: {exact_symbol} (Exchange: {exchange})")
                            
                            try:
                                ltp_data = obj.ltpData(exchange, exact_symbol, token_id)
                                st.success("Live Price Fetched Successfully!")
                                st.json(ltp_data)
                            except Exception as err:
                                st.error(f"Error fetching price: {err}")
                        else:
                            st.warning("Symbol not found in database. Try writing like 'NIFTY24650CE'.")
                    else:
                        st.warning("Please enter a valid symbol.")
            else:
                st.error("Could not load Scrip Master database.")
        else:
            st.error(f"Login Failed: {data.get('message', 'Unknown error')}")
            
    except Exception as e:
        st.error(f"Error: {e}")
else:
    st.warning("Please configure API_KEY, CLIENT_ID, PIN, and TOTP_TOKEN in Streamlit Secrets.")
