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
st.title("⚡ Aditi AI: Live 1-Second Multi-Indicator Engine")

# हर 1 सेकंड में स्क्रीन रिफ्रेश होगी
st_autorefresh(interval=1000, key="datarefresh")

if 'signal_history' not in st.session_state:
    st.session_state['signal_history'] = []

class AdvancedTradingBrain:
    def evaluate_strategy(self, symbol, price_history):
        if len(price_history) < 20: return "WAIT", "Collecting..."
        current_price = price_history[-1]
        ema_20 = np.mean(price_history[-20:])
        if current_price > ema_20:
            return "BUY_1_LOT", "Trend Bullish"
        return "WAIT", "Neutral"

def master_background_worker():
    api_key = st.secrets.get("API_KEY")
    client_id = st.secrets.get("CLIENT_ID")
    pin = st.secrets.get("PIN")
    token = st.secrets.get("TOTP_TOKEN")
    
    obj = SmartConnect(api_key=api_key)
    totp = pyotp.TOTP(str(token).strip()).now()
    obj.generateSession(client_id, pin, totp)
    
    symbols = {"NIFTY 50": "99926000", "BANK NIFTY": "99926009", "RELIANCE": "2885"}
    trackers = {s: [] for s in symbols}
    
    while True:
        for name, tid in symbols.items():
            try:
                data = obj.ltpData("NSE", name, tid)
                price = data['data']['ltp']
                trackers[name].append(price)
                if len(trackers[name]) > 30: trackers[name].pop(0)
                
                signal, reason = AdvancedTradingBrain().evaluate_strategy(name, trackers[name])
                if signal == "BUY_1_LOT":
                    log = {"Time": datetime.now().strftime("%H:%M:%S"), "Symbol": name, "Action": "BUY 1 LOT", "Price": price}
                    if not st.session_state['signal_history'] or st.session_state['signal_history'][0]['Time'] != log['Time']:
                        st.session_state['signal_history'].insert(0, log)
            except: pass
        time.sleep(1)

if 'started' not in st.session_state:
    threading.Thread(target=master_background_worker, daemon=True).start()
    st.session_state['started'] = True

st.success("🟢 BOT ACTIVE: Live Scanning & Auto-Refreshing Every 1 Second")
st.table(st.session_state['signal_history'])
