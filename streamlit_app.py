import streamlit as st
from SmartApi import SmartConnect
import pyotp
import time
from datetime import datetime

st.set_page_config(layout="wide")
st.title("⚡ Aditi AI: All Indices Live Scanner")

api_key = st.secrets.get("API_KEY")
client_id = st.secrets.get("CLIENT_ID")
pin = st.secrets.get("PIN")
token = st.secrets.get("TOTP_TOKEN")

if 'signal_history' not in st.session_state:
    st.session_state['signal_history'] = []

# भारत के सभी प्रमुख इंडेक्स और उनके सही टोकन आईडी
ALL_INDICES = {
    "NIFTY 50": "99926000",
    "BANK NIFTY": "99926009",
    "FIN NIFTY": "99926037",
    "MIDCP NIFTY": "99926074",
    "NIFTY NEXT 50": "99926059",
    "SENSEX": "99919000"
}

st.info("👆 बटन दबाते ही यह सभी मुख्य इंडेक्स का ताजा लाइव भाव ले आएगा:")

if st.button("🚀 Scan All Indices Now", type="primary"):
    try:
        obj = SmartConnect(api_key=api_key)
        totp = pyotp.TOTP(str(token).strip()).now()
        session = obj.generateSession(client_id, pin, totp)
        
        if session and session.get('status'):
            for name, tid in ALL_INDICES.items():
                # सर्वर पर लोड न पड़े इसलिए छोटा सा सुरक्षित गैप
                time.sleep(0.5) 
                ltp_data = obj.ltpData("NSE", name, tid) if "SENSEX" not in name else obj.ltpData("BSE", name, tid)
                
                if ltp_data and 'data' in ltp_data:
                    price = ltp_data['data']['ltp']
                    log = {
                        "Time": datetime.now().strftime("%H:%M:%S"),
                        "Index Name": name,
                        "Status": "ACTIVE",
                        "Live Price": price
                    }
                    st.session_state['signal_history'].insert(0, log)
            st.success("✅ सभी इंडेक्स सफलतापूर्वक स्कैन हो गए हैं!")
        else:
            st.error("❌ लॉगिन फेल। कृपया अपने क्रेडेंशियल्स चेक करें।")
    except Exception as e:
        st.error(f"⚠️ एरर: {e}")

st.markdown("### 📊 Live Indices Dashboard")
if st.session_state['signal_history']:
    st.table(st.session_state['signal_history'])
else:
    st.warning("टेबल अभी खाली है। ऊपर दिए गए बटन पर क्लिक करें।")
