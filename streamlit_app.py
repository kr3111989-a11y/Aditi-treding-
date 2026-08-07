import streamlit as st
from SmartApi import SmartConnect
import pyotp
from datetime import datetime

st.set_page_config(layout="wide")
st.title("⚡ Aditi AI: All Indices Combined Scanner")

api_key = st.secrets.get("API_KEY")
client_id = st.secrets.get("CLIENT_ID")
pin = st.secrets.get("PIN")
token = st.secrets.get("TOTP_TOKEN")

if 'signal_history' not in st.session_state:
    st.session_state['signal_history'] = []

st.info("👆 यह एक ही बार में सभी प्रमुख इंडेक्स का लाइव भाव सुरक्षित तरीके से लाएगा:")

if st.button("🚀 Get All Indices Live Price", type="primary"):
    try:
        obj = SmartConnect(api_key=api_key)
        totp = pyotp.TOTP(str(token).strip()).now()
        session = obj.generateSession(client_id, pin, totp)
        
        if session and session.get('status'):
            # सभी इंडेक्स के लिए एक साथ कंबाइंड रिक्वेस्ट भेजने की लिस्ट
            exchange_tokens = {
                "NSE": ["99926000", "99926009", "99926037", "99926074"], # Nifty, BankNifty, FinNifty, MidcpNifty
                "BSE": ["99919000"] # Sensex
            }
            
            # एक साथ डेटा फेच करना (Rate Limit से बचने के लिए कंबाइंड तरीका)
            for exchange, tokens in exchange_tokens.items():
                response = obj.marketData("FULL", {exchange: tokens})
                if response and 'data' in response and 'fetched' in response['data']:
                    for item in response['data']['fetched']:
                        symbol_name = item.get('tradingSymbol', 'Index')
                        price = item.get('ltp', 0)
                        
                        log = {
                            "Time": datetime.now().strftime("%H:%M:%S"),
                            "Index": symbol_name,
                            "Live Price": price,
                            "Status": "SUCCESS"
                        }
                        st.session_state['signal_history'].insert(0, log)
                        
            st.success("✅ सभी इंडेक्स का लाइव भाव एक साथ मिल गया है!")
        else:
            st.error("❌ लॉगिन फेल। क्रेडेंशियल्स चेक करें।")
    except Exception as e:
        st.error(f"⚠️ एरर: {e}")

st.markdown("### 📊 All Indices Live Dashboard")
if st.session_state['signal_history']:
    st.table(st.session_state['signal_history'])
else:
    st.warning("टेबल खाली है। ऊपर दिए गए बटन पर क्लिक करें।")

