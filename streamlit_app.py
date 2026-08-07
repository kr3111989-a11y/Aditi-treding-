import streamlit as st
from SmartApi import SmartConnect
import pyotp
from datetime import datetime

st.set_page_config(layout="wide")
st.title("⚡ Aditi AI: Session-Fixed Dashboard")

api_key = st.secrets.get("API_KEY")
client_id = st.secrets.get("CLIENT_ID")
pin = st.secrets.get("PIN")
token = st.secrets.get("TOTP_TOKEN")

if 'signal_history' not in st.session_state:
    st.session_state['signal_history'] = []

# सेशन को एक ही बार कनेक्ट करने का फंक्शन ताकि बार-बार एरर न आए
@st.cache_resource
def get_smart_connection():
    obj = SmartConnect(api_key=api_key)
    totp = pyotp.TOTP(str(token).strip()).now()
    session = obj.generateSession(client_id, pin, totp)
    if session and session.get('status'):
        return obj
    return None

st.info("👆 अब सेशन फिक्स कर दिया गया है। किसी भी इंडेक्स पर क्लिक करें, तुरंत भाव मिलेगा:")

col1, col2 = st.columns(2)

with col1:
    if st.button("📊 Get Nifty 50 Price", type="primary"):
        try:
            obj = get_smart_connection()
            if obj:
                ltp = obj.ltpData("NSE", "NIFTY 50", "99926000")['data']['ltp']
                st.session_state['signal_history'].insert(0, {"Time": datetime.now().strftime("%H:%M:%S"), "Index": "NIFTY 50", "Price": ltp})
                st.success("Nifty 50 Fetched!")
            else:
                st.error("Connection Failed")
        except Exception as e:
            st.error(f"Error: {e}")

    if st.button("📊 Get Fin Nifty Price"):
        try:
            obj = get_smart_connection()
            if obj:
                ltp = obj.ltpData("NSE", "FIN NIFTY", "99926037")['data']['ltp']
                st.session_state['signal_history'].insert(0, {"Time": datetime.now().strftime("%H:%M:%S"), "Index": "FIN NIFTY", "Price": ltp})
                st.success("Fin Nifty Fetched!")
            else:
                st.error("Connection Failed")
        except Exception as e:
            st.error(f"Error: {e}")

with col2:
    if st.button("📊 Get Bank Nifty Price", type="primary"):
        try:
            obj = get_smart_connection()
            if obj:
                ltp = obj.ltpData("NSE", "BANK NIFTY", "99926009")['data']['ltp']
                st.session_state['signal_history'].insert(0, {"Time": datetime.now().strftime("%H:%M:%S"), "Index": "BANK NIFTY", "Price": ltp})
                st.success("Bank Nifty Fetched!")
            else:
                st.error("Connection Failed")
        except Exception as e:
            st.error(f"Error: {e}")

    if st.button("📊 Get Midcp Nifty Price"):
        try:
            obj = get_smart_connection()
            if obj:
                ltp = obj.ltpData("NSE", "MIDCP NIFTY", "99926074")['data']['ltp']
                st.session_state['signal_history'].insert(0, {"Time": datetime.now().strftime("%H:%M:%S"), "Index": "MIDCP NIFTY", "Price": ltp})
                st.success("Midcap Nifty Fetched!")
            else:
                st.error("Connection Failed")
        except Exception as e:
            st.error(f"Error: {e}")

st.markdown("### 📊 Live Indices Price Log")
if st.session_state['signal_history']:
    st.table(st.session_state['signal_history'])
else:
    st.warning("टेबल खाली है। ऊपर दिए गए किसी भी बटन पर क्लिक करें।")
