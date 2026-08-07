import streamlit as st
from SmartApi import SmartConnect
import pyotp
import urllib.parse
import urllib.request
import threading
import time
import numpy as np
from datetime import datetime
from streamlit_autorefresh import st_autorefresh

st.set_page_config(layout="wide")
st.title("⚡ Aditi AI: Ultra-Active Live Engine")

# हर 1 सेकंड में रिफ्रेश
st_autorefresh(interval=1000, key="datarefresh")

if 'signal_history' not in st.session_state:
    st.session_state['signal_history'] = []

class FlexibleTradingBrain:
    def evaluate_strategy(self, symbol, price_history):
        if len(price_history) < 5: return "WAIT", "Loading..."
        
        # बहुत ही हल्का और लचीला लॉजिक
        current_price = price_history[-1]
        prev_price = price_history[-2]
        
        # अगर सिर्फ पिछले भाव से भाव बढ़ गया, तो सिग्नल दे दो (Ultra-Fast)
        if current_price > prev_price:
            return "BUY_1_LOT", f"Price Up: {current_price}"
        elif current_price < prev_price:
            return "SELL_1_LOT", f"Price Down: {current_price}"
        return "WAIT", "Neutral"

def master_background_worker():
    api_key = st.secrets.get("API_KEY")
    client_id = st.secrets.get("CLIENT_ID")
    pin = st.secrets.get("PIN")
    token = st.secrets.get("TOTP_TOKEN")
    
    obj = SmartConnect(api_key=api_key)
    totp = pyotp.TOTP(str(token).strip()).now()
    obj.generateSession(client_id, pin, totp)
    
    symbols = {"NIFTY 50": "99926000", "BANK NIFTY": "99926009"}
    trackers = {s: [] for s in symbols}
    
    while True:
        for name, tid in symbols.items():
            try:
                data = obj.ltpData("NSE", name, tid)
                price = data['data']['ltp']
                trackers[name].append(price)
                if len(trackers[name]) > 10: trackers[name].pop(0)
                
                signal, reason = FlexibleTradingBrain().evaluate_strategy(name, trackers[name])
                
                # अब यह हर छोटे मूवमेंट पर एंट्री करेगा
                if signal != "WAIT":
                    log = {"Time": datetime.now().strftime("%H:%M:%S"), "Symbol": name, "Action": signal, "Price": price}
                    if not st.session_state['signal_history'] or st.session_state['signal_history'][0]['Time'] != log['Time']:
                        st.session_state['signal_history'].insert(0, log)
            except: pass
        time.sleep(1)

if 'started' not in st.session_state:
    threading.Thread(target=master_background_worker, daemon=True).start()
    st.session_state['started'] = True

st.success("🟢 ULTRA-ACTIVE MODE: Scanning every small tick...")
st.table(st.session_state['signal_history'])
