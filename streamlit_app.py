import streamlit as st
from SmartApi import SmartConnect
import pyotp
import numpy as np
from datetime import datetime

st.set_page_config(layout="wide")
st.title("⚡ Aditi AI: Direct Live Scanner")

# क्रेडेंशियल्स
api_key = st.secrets.get("API_KEY")
client_id = st.secrets.get("CLIENT_ID")
pin = st.secrets.get("PIN")
token = st.secrets.get("TOTP_TOKEN")

if 'signal_history' not in st.session_state:
    st.session_state['signal_history'] = []

st.info("👆 नीचे दिए गए बटन पर क्लिक करके लाइव मार्केट चेक करें:")

if st.button("🚀 Scan Market Now", type="primary"):
    try:
        obj = SmartConnect(api_key=api_key)
        totp = pyotp.TOTP(str(token).strip()).now()
        data = obj.generateSession(client_id, pin, totp)
        
        if data and data.get('status'):
            symbols = {"NIFTY 50": "99926000", "BANK NIFTY": "99926009", "RELIANCE": "2885"}
            
            for name, tid in symbols.items():
                ltp_data = obj.ltpData("NSE", name, tid)
                if ltp_data and 'data' in ltp_data:
                    price = ltp_data['data']['ltp']
                    
                    # एंट्री लॉग जोड़ना
                    log = {
                        "Time": datetime.now().strftime("%H:%M:%S"),
                        "Symbol": name,
                        "Action": "BUY 1 LOT",
                        "Price": price
                    }
                    st.session_state['signal_history'].insert(0, log)
            
            st.success("✅ स्कैन सफल! ताजा भाव नीचे टेबल में आ गया है:")
        else:
            st.error("❌ ब्रोकर सेशन फेल हो गया है। कृपया अपने API Key / PIN / TOTP चेक करें।")
    except Exception as e:
        st.error(f"⚠️ एरर आया: {e}")

# टेबल दिखाना
st.markdown("### 📊 Live Scanned Data & Signals")
if len(st.session_state['signal_history']) > 0:
    st.table(st.session_state['signal_history'])
else:
    st.warning("अभी टेबल खाली है। ऊपर दिए गए नीले बटन पर क्लिक करें।")
