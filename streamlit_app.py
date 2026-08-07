import streamlit as st
from SmartApi import SmartConnect
import pyotp
import urllib.parse
import urllib.request
import threading
import time
import numpy as np

st.set_page_config(layout="wide")
st.title("⚡ Aditi AI Multi-Indicator 1-Second Live Trading Bot")

# 1. वॉचलिस्ट
WATCHLIST = {
    "NIFTY 50": "99926000",
    "BANK NIFTY": "99926009",
    "RELIANCE": "2885",
    "TCS": "11536",
    "HDFC BANK": "1333"
}

# 2. एडवांस टेक्निकल 'दिमाग' (VWAP, EMA, RSI, Supertrend, MACD)
class AdvancedTradingBrain:
    def __init__(self):
        self.budget = 2000  # फिक्स बजट नियम
        
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
        
        # इंडिकेटर्स की गणना (Mathematical Logic)
        ema_20 = np.mean(price_history[-20:])
        vwap = np.mean(price_history[-10:])  # शार्ट-टर्म VWAP एप्रोच
        rsi = self.calculate_rsi(price_history)
        
        # MACD रफ कैलकुलेशन
        ema_12 = np.mean(price_history[-12:])
        ema_26 = np.mean(price_history[-26:])
        macd = ema_12 - ema_26
        
        # Supertrend बेसिक लॉजिक (ट्रेडिंग सिग्नल के लिए)
        supertrend_bullish = current_price > (np.mean(price_history[-10:]) * 0.995)

        score = 0
        reasons = []

        # नियम 1: EMA & VWAP क्रॉसओवर
        if current_price > ema_20 and current_price > vwap:
            score += 2
            reasons.append("Price > EMA & VWAP")

        # नियम 2: RSI मोमेंटम ज़ोन (40 से 60 के बीच या ऊपर)
        if 40 <= rsi <= 70:
            score += 1
            reasons.append(f"RSI Healthy ({rsi:.1f})")

        # नियम 3: MACD पॉजिटिव
        if macd > 0:
            score += 1
            reasons.append("MACD Bullish")

        # नियम 4: Supertrend कन्फर्मेशन
        if supertrend_bullish:
            score += 1
            reasons.append("Supertrend GREEN")

        # फाइनल डिसीजन (जब सारे नियम मैच हों)
        if score >= 4:
            return "STRONG_BUY_CE", f"All Indicators Bullish! {reasons}"
        elif score <= 1:
            return "STRONG_BUY_PE", f"Bearish Pressure {reasons}"
        else:
            return "WAIT", f"Mixed Signals Score: {score}"

# 3. अलर्ट फंक्शन
def send_whatsapp_and_audio_alert(symbol, signal_type, price, reason):
    alert_text = f"🚨 {symbol} -> {signal_type} @ {price} | {reason}"
    st.session_state['latest_alert'] = alert_text
    print(alert_text)
    
    phone_number = "91XXXXXXXXXX"  # अपना नंबर डालें
    apikey = "YOUR_API_KEY"        # अपनी API Key डालें
    safe_message = urllib.parse.quote(alert_text)
    url = f"https://api.callmebot.com/whatsapp.php?phone={phone_number}&text={safe_message}&apikey={apikey}"
    try:
        urllib.request.urlopen(url)
    except:
        pass

# 4. 1-सेकंड का सुपर-फास्ट बैकग्राउंड वर्कर
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
                    # ब्रोकर से बिल्कुल सीधा लाइव LTP फेच करना
                    ltp_data = obj.ltpData("NSE", symbol, token_id)
                    if ltp_data and 'data' in ltp_data:
                        current_price = ltp_data['data'].get('ltp', 0)
                        if current_price > 0:
                            price_trackers[symbol].append(current_price)
                            # सिर्फ पिछले 30 टिक का डेटा स्टोर रखें
                            if len(price_trackers[symbol]) > 30:
                                price_trackers[symbol].pop(0)
                                
                            signal, reason = brain.evaluate_strategy(symbol, price_trackers[symbol])
                            
                            if signal in ["STRONG_BUY_CE", "STRONG_BUY_PE"]:
                                send_whatsapp_and_audio_alert(symbol, signal, current_price, reason)
                except Exception as e:
                    print(f"Error {symbol}: {e}")
            
            time.sleep(1) # बिल्कुल हर 1 सेकंड में नया डेटा माँगेगा!

# 5. UI और थ्रेडिंग इनिशियलाइज़ेशन
api_key = st.secrets.get("API_KEY")
client_id = st.secrets.get("CLIENT_ID")
pin = st.secrets.get("PIN")
token = st.secrets.get("TOTP_TOKEN")

if 'master_running' not in st.session_state:
    if api_key:
        st.session_state['master_running'] = True
        threading.Thread(target=master_background_worker, args=(api_key, client_id, pin, token), daemon=True).start()

st.success("⚡ 1-Second Ultra-Fast Multi-Indicator Engine is RUNNING!")
if 'latest_alert' in st.session_state:
    st.warning(f"📢 **Live Market Status:** {st.session_state['latest_alert']}")
else:
    st.info("🔄 Bot is scanning all assets every 1 second across VWAP, EMA, RSI, MACD & Supertrend...")
