import streamlit as st
from SmartApi import SmartConnect
import pyotp
import urllib.parse
import urllib.request
import threading
import time
import numpy as np
from datetime import datetime

st.set_page_config(layout="wide")
st.title("⚡ Aditi AI: Live 1-Second Multi-Indicator Engine")

# 1. सिग्नल हिस्ट्री
if 'signal_history' not in st.session_state:
    st.session_state['signal_history'] = []

# 2. एडवांस ट्रेडिंग दिमाग (बिना किसी बजट लिमिट के)
class AdvancedTradingBrain:
    def calculate_rsi(self, prices):
        if len(prices) < 15: return 50.0
        deltas = np.diff(prices[-15:])
        up = deltas[deltas > 0].sum() / 14
        down = -deltas[deltas < 0].sum() / 14
        if down == 0: return 100.0
        rs = up / down
        return 100.0 - (100.0 / (1.0 + rs))

    def evaluate_strategy(self, symbol, price_history):
        if len(price_history) < 20: return "WAIT", "Collecting..."
        
        current_price = price_history[-1]
        ema_20 = np.mean(price_history[-20:])
        rsi = self.calculate_rsi(price_history)
        
        # 1-लॉट ट्रेड सिग्नल लॉजिक
        if current_price > ema_20 and 40 < rsi < 70:
            return "BUY_1_LOT", f"Trend Bullish, RSI: {rsi:.1f}"
        return "WAIT", "Neutral"

# 3. मास्टर वर्कर (लाइव 1-सेकंड डेटा)
def master_background_worker():
    api_key = st.secrets.get("API_KEY")
    client_id = st.secrets.get("CLIENT_ID")
    pin = st.secrets.get("PIN")
    token = st.secrets.get("TOTP_TOKEN")
    
    obj = SmartConnect(api_key=api_key)
    totp = pyotp.TOTP(str(token).strip()).now()
    obj.generateSession(client_id, pin, totp)
    
    # इंडेक्स और शेयर्स (लाइव टोकन के साथ)
    symbols = {"NIFTY 50": "99926000", "BANK NIFTY": "99926009", "RELIANCE": "2885"}
    trackers = {s: [] for s in symbols}
    
    while True:
        for name, tid in symbols.items():
            try:
                # सीधे ब्रोकर से लाइव LTP
                data = obj.ltpData("NSE", name, tid)
                price = data['data']['ltp']
                
                trackers[name].append(price)
                if len(trackers[name]) > 30: trackers[name].pop(0)
                
                signal, reason = AdvancedTradingBrain().evaluate_strategy(name, trackers[name])
                
                if signal == "BUY_1_LOT":
                    # व्हाट्सएप अलर्ट
                    log = {"Time": datetime.now().strftime("%H:%M:%S"), "Symbol": name, "Action": "BUY 1 LOT", "Price": price}
                    if not st.session_state['signal_history'] or st.session_state['signal_history'][0]['Time'] != log['Time']:
                        st.session_state['signal_history'].insert(0, log)
            except: pass
        time.sleep(1) # हर 1 सेकंड में स्कैनिंग

# 4. थ्रेडिंग और UI
if 'started' not in st.session_state:
    threading.Thread(target=master_background_worker, daemon=True).start()
    st.session_state['started'] = True

st.success("🟢 BOT ACTIVE: LIVE Scanning Every 1 Second | Logic: 1 LOT ONLY")
st.table(st.session_state['signal_history'])
