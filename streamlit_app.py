import streamlit as st
from SmartApi import SmartConnect
import pyotp
from datetime import datetime

st.set_page_config(layout="wide")
st.title("⚡ Aditi AI: Safe Multi-Index Dashboard")

api_key = st.secrets.get("API_KEY")
client_id = st.secrets.get("CLIENT_ID")
pin = st.secrets.get("PIN")
token = st.secrets.get("TOTP_TOKEN")

if 'signal_history' not in st.session_state:
    st.session_state['signal_history'] = []

st.info("👆 नीचे अलग-अलग इंडेक्स के बटन दिए गए हैं। किसी भी बटन पर क्लिक करके उसका लाइव भाव बिना किसी एरर के देखें:")

# अलग-अलग सुरक्षित बटन
col1, col2 = st.columns(2)

with col1:
    if st.button("📊 Get Nifty 50 Price", type="primary"):
        try:
            obj = SmartConnect(api_key=api_key)
            totp = pyotp.TOTP(str(token).strip()).now()
            if obj.generateSession(client_id, pin, totp).get('status'):
                ltp = obj.ltpData("NSE", "NIFTY 50", "99926000")['data']['ltp']
                st.session_state['signal_history'].insert(0, {"Time": datetime.now().strftime("%H:%M:%S"), "Index": "NIFTY 50", "Price": ltp})
                st.success("Nifty 50 Updated!")
        except Exception as e:
            st.error(f"Error: {e}")

    if st.button("📊 Get Fin Nifty Price"):
        try:
            obj = SmartConnect(api_key=api_key)
            totp = pyotp.TOTP(str(token).strip()).now()
            if obj.generateSession(client_id, pin, totp).get('status'):
                ltp = obj.ltpData("NSE", "FIN NIFTY", "99926037")['data']['ltp']
                st.session_state['signal_history'].insert(0, {"Time": datetime.now().strftime("%H:%M:%S"), "Index": "FIN NIFTY", "Price": ltp})
                st.success("Fin Nifty Updated!")
        except Exception as e:
            st.error(f"Error: {e}")

with col2:
    if st.button("📊 Get Bank Nifty Price", type="primary"):
        try:
            obj = SmartConnect(api_key=api_key)
            totp = pyotp.TOTP(str(token).strip()).now()
            if obj.generateSession(client_id, pin, totp).get('status'):
                ltp = obj.ltpData("NSE", "BANK NIFTY", "99926009")['data']['ltp']
                st.session_state['signal_history'].insert(0, {"Time": datetime.now().strftime("%H:%M:%S"), "Index": "BANK NIFTY", "Price": ltp})
                st.success("Bank Nifty Updated!")
        except Exception as e:
            st.error(f"Error: {e}")

    if st.button("📊 Get Midcp Nifty Price"):
        try:
            obj = SmartConnect(api_key=api_key)
            totp = pyotp.TOTP(str(token).strip()).now()
            if obj.generateSession(client_id, pin, totp).get('status'):
                ltp = obj.ltpData("NSE", "MIDCP NIFTY", "99926074")['data']['ltp']
                st.session_state['signal_history'].insert(0, {"Time": datetime.now().strftime("%H:%M:%S"), "Index": "MIDCP NIFTY", "Price": ltp})
                st.success("Midcap Nifty Updated!")
        except Exception as e:
            st.error(f"Error: {e}")

st.markdown("### 📊 Live Indices Price Log")
if st.session_state['signal_history']:
    st.table(st.session_state['signal_history'])
else:
    st.warning("टेबल खाली है। ऊपर दिए गए किसी भी बटन पर क्लिक करें।")
