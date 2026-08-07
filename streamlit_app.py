import streamlit as st
from SmartApi import SmartConnect
import pyotp
import time
from datetime import datetime

st.set_page_config(layout="wide")
st.title("⚡ Aditi AI: All Indices Safe Scanner")

api_key = st.secrets.get("API_KEY")
client_id = st.secrets.get("CLIENT_ID")
pin = st.secrets.get("PIN")
token = st.secrets.get("TOTP_TOKEN")

if 'signal_history' not in st.session_state:
    st.session_state['signal_history'] = []

# सभी मुख्य इंडेक्स
ALL_INDICES = {
    "NIFTY 50": ("99926000", "NSE"),
    "BANK NIFTY": ("99926009", "NSE"),
    "FIN NIFTY": ("99926037", "NSE"),
    "MIDCP NIFTY": ("99926074", "NSE")
}

st.info("👆 बटन दबाते ही सभी इंडेक्स का लाइव भाव सुरक्षित तरीके से लोड हो जाएगा:")

if st.button("🚀 Get All Indices Live Price", type="primary"):
    try:
        obj = SmartConnect(api_key=api_key)
        totp = pyotp.TOTP(str(token).strip()).now()
        session = obj.generateSession(client_id, pin, totp)
        
        if session and session.get('status'):
            for name, (tid, exchange) in ALL_INDICES.items():
                # सर्वर पर लोड और 'Access Rate' एरर से बचने के लिए छोटा सा गैप
                time.sleep(0.7)
                ltp_data = obj.ltpData(exchange, name, tid)
                
                if ltp_data and 'data' in ltp_data:
                    price = ltp_data['data']['ltp']
                    log = {
                        "Time": datetime.now().strftime("%H:%M:%S"),
                        "Index": name,
                        "Live Price": price,
                        "Status": "SUCCESS"
                    }
                    st.session_state['signal_history'].insert(0, log)
            
            st.success("✅ सभी इंडेक्स का लाइव भाव सफलताપूर्वक आ गया है!")
        else:
            st.error("❌ लॉगिन फेल। कृपया अपने क्रेडेंशियल्स चेक करें।")
    except Exception as e:
        st.error(f"⚠️ एरर: {e}")

st.markdown("### 📊 All Indices Live Dashboard")
if st.session_state['signal_history']:
    st.table(st.session_state['signal_history'])
else:
    st.warning("टेबल खाली है। ऊपर दिए गए बटन पर क्लिक करें।")
