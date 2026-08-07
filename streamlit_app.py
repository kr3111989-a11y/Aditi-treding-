import streamlit as st
from SmartApi import SmartConnect
import pyotp

st.title("Aditi Trading Dashboard - Full Market")

api_key = st.secrets.get("API_KEY")
client_id = st.secrets.get("CLIENT_ID")
pin = st.secrets.get("PIN")
token = st.secrets.get("TOTP_TOKEN")

if api_key and client_id and pin and token:
    try:
        obj = SmartConnect(api_key=api_key)
        totp = pyotp.TOTP(token).now()
        data = obj.generateSession(client_id, pin, totp)
        
        if data and data.get('status'):
            st.success("Connected to Angel One Successfully!")
            
            symbol = st.text_input("Enter Symbol (e.g. SBIN-EQ, NIFTY):", "").upper()
            
            if st.button("Get Live Price"):
                if symbol:
                    st.write(f"Fetching live price for {symbol}...")
                    try:
                        # सामान्य शेयरों या इंडेक्स के लिए ltpData कॉल करना
                        # (नोट: इसके लिए सही एक्सचेंज और टोकन या सिंबल फॉर्मेट की जरूरत होती है)
                        ltp_data = obj.ltpData("NSE", symbol, "EXACT_SYMBOL_OR_TOKEN")
                        st.write(ltp_data)
                    except Exception as err:
                        st.error(f"Could not fetch price: {err}")
                else:
                    st.warning("Please enter a valid symbol.")
        else:
            st.error(f"Login Failed: {data.get('message', 'Unknown error')}")
            
    except Exception as e:
        st.error(f"Error: {e}")
else:
    st.warning("Please configure API_KEY, CLIENT_ID, PIN, and TOTP_TOKEN in Streamlit Secrets.")
