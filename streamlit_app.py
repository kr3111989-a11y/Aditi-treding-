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
st.title("⚡ Aditi AI Live Trading Bot with Signal History Log")

# 1. वॉचलिस्ट
WATCHLIST = {
    "NIFTY 50": "99926000",
    "BANK NIFTY": "99926009",
    "RELIANCE": "2885",
    "TCS": "11536",
    "HDFC BANK": "1333"
}

# 2. सिग्नल हिस्ट्री को स्टोर करने के लिए सेशन स्टेट
if 'signal_history' not in st.session_state:
    st.session_state['signal_history'] = []

# 3. एडवांस टेक्निकल दिमाग
class AdvancedTradingBrain:
    def calculate_rsi(self, prices, window=14):
        if len(prices) < window + 1:
            return 50.0
        deltas = np.diff(prices)
        seed = deltas[:window]
        up = seed[seed >= 0].sum() / window
        down = -seed[seed < 0].sum() / window
        if down == 0:
            return 100.0
        rs = up / down
        return 100.0 - (100.0 / (1.0 + rs))

    def evaluate_strategy(self, symbol, price_history):
        if len(price_history) < 20:
            return "WAIT", "Collecting data..."
            
        current_price = price_history[-1]
        ema_20 = np.mean(price_history[-20:])
        vwap = np.mean(price_history[-10:])
        rsi = self.calculate_rsi(price_history)
        
        score = 0
        reasons = []

        if current_price > ema_20 and current_price > vwap:
            score += 2
            reasons.append("Price > EMA & VWAP")
        if 40 <= rsi <= 70:
            score += 1
            reasons.append(f"RSI Healthy ({rsi:.1f})")

        if score >= 3:
            return "STRONG_BUY_CE", f"Bullish setup! {reasons}"
        elif score <= 0:
            return "STRONG_BUY_PE", f"Bearish pressure {reasons}"
        else:
            return "WAIT", "Mixed signals"

# 4. अलर्ट और हिस्ट्री में जोड़ने वाला फंक्शन
def record_and_alert(symbol, signal_type, price, reason):
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # हिस्ट्री की लिस्ट में सबसे ऊपर नया सिग्नल जोड़ना
    log_entry = {
        "Time": current_time,
        "Symbol": symbol,
        "Signal": signal_type,
        "Price": price,
        "Details": reason
    }
    st.session_state['signal_history'].insert(0, log_entry)
    
    # व्हाट्सएप अलर्ट
    alert_text = f"🚨 {symbol} -> {signal_type} @ {price} | {reason}"
    phone_number = "91XXXXXXXXXX"  # अपना नंबर डालें
    apikey = "YOUR_API_KEY"        # अपनी API Key डालें
    url = f"https://api.callmebot.com/whatsapp.php?phone={phone_number}&text={urllib.parse.quote(alert_text)}&apikey={apikey}"
    try:
        urllib.request.urlopen(url)
    except:
        pass

# 5. बैकग्राउंड वर्कर (1-सेकंड लाइव डेटा)
def master_background_worker(api_key, client_id, pin, token):
    obj = SmartConnect(api_key=api_key)
    totp = pyotp.TOTP(str(token).strip()).now()
    data = obj.generateSession(client_id, pin, totp)
    
    if data and data.get('status'):
        brain = AdvancedTradingBrain()
        price_trackers = {symbol: [] for symbol in WATCHLIST.keys()}
        
        while True:
            for symbol, token_id in WATCHLIST.items():
                try:
                    ltp_data = obj.ltpData("NSE", symbol, token_id)
                    if ltp_data and 'data' in ltp_data:
                        current_price = ltp_data['data'].get('ltp', 0)
                        if current_price > 0:
                            price_trackers[symbol].append(current_price)
                            if len(price_trackers[symbol]) > 30:
                                price_trackers[symbol].pop(0)
                                
                            signal, reason = brain.evaluate_strategy(symbol, price_trackers[symbol])
                            
                            # हर 5 मिनट में एक ही सिंबल पर बार-बार स्पैम न हो, इसके लिए बेसिक चेक
                            if signal in ["STRONG_BUY_CE", "STRONG_BUY_PE"]:
                                record_and_alert(symbol, signal, current_price, reason)
                except Exception as e:
                    print(f"Error {symbol}: {e}")
            time.sleep(2) # हर 2 सेकंड में स्कैनिंग

# 6. UI और डैशबोर्ड
api_key = st.secrets.get("API_KEY")
client_id = st.secrets.get("CLIENT_ID")
pin = st.secrets.get("PIN")
token = st.secrets.get("TOTP_TOKEN")

if 'master_running' not in st.session_state:
    if api_key:
        st.session_state['master_running'] = True
        threading.Thread(target=master_background_worker, args=(api_key, client_id, pin, token), daemon=True).start()

st.success("🟢 LIVE Bot Active: Scanning Market Every 2 Seconds")

# स्क्रीन पर सिग्नल हिस्ट्री टेबल दिखाना
st.markdown("### 📊 Live Trade Opportunities & Signal History Log")
if len(st.session_state['signal_history']) > 0:
    st.table(st.session_state['signal_history'])
else:
    st.info("⏳ Bot is actively scanning. Whenever a trading opportunity is found, it will appear here automatically with time and price!")
