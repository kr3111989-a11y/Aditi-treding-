import streamlit as st
from SmartApi import SmartConnect
import pyotp
import urllib.parse
import urllib.request
import threading
import time

st.set_page_config(layout="wide")
st.title("⚡ Aditi AI Ultimate Trading Bot & Multi-Scanner with Voice Alert")

# 1. सभी इंडेक्स और प्रमुख शेयरों की वॉचलिस्ट
WATCHLIST = {
    "NIFTY 50": "99926000",
    "BANK NIFTY": "99926009",
    "SENSEX": "99919000",
    "RELIANCE": "2885",
    "TCS": "11536",
    "HDFC BANK": "1333"
}

# 2. बॉट का 'दिमाग' और स्कैनिंग इंजन
class UltimateTradingBrain:
    def __init__(self):
        self.budget = 2000  # फिक्स बजट नियम
        
    def analyze_market_conditions(self, symbol, market_data):
        score = 0
        reasons = []

        if market_data.get('price_breakout') == 'High_Broken':
            score += 2
            reasons.append(f"{symbol}: High broken.")

        if market_data.get('price', 0) > market_data.get('vwap', 0):
            score += 1
            reasons.append("Price is above VWAP.")

        if 40 <= market_data.get('rsi', 50) <= 60:
            score += 1
            reasons.append("Healthy momentum zone.")

        if score >= 3:
            return "BULLISH_SIGNAL", reasons
        elif score <= -2:
            return "BEARISH_SIGNAL", reasons
        else:
            return "WAIT", []

# 3. व्हाट्सएप, साउंड और वॉइस अलर्ट भेजने का मास्टर फंक्शन
def send_whatsapp_and_audio_alert(symbol, signal_type, price):
    alert_text = f"ALERT: {symbol} -> {signal_type} at Price {price}"
    print(f"🚨 {alert_text}")
    
    # [A] फोन के ब्राउज़र में बोलकर अलर्ट देने वाला वॉइस कोड (Text-to-Speech)
    st.markdown(f"""
        <script>
            var msg = new SpeechSynthesisUtterance("{alert_text}");
            window.speechSynthesis.speak(msg);
        </script>
    """, unsafe_allow_html=True)
    
    # [B] व्हाट्सएप पर लाइव मैसेज भेजने का कोड
    phone_number = "919067177695"  # यहाँ अपना 10 अंकों का मोबाइल नंबर लिखें (आगे 91 लगाकर)
    apikey = "YOUR_API_KEY"        # यहाँ CallMeBot से मिली हुई API Key लिखें
    
    safe_message = urllib.parse.quote(f"🚨 ADITI BOT: {symbol} -> {signal_type} @ {price}")
    whatsapp_url = f"https://api.callmebot.com/whatsapp.php?phone={phone_number}&text={safe_message}&apikey={apikey}"
    
    try:
        urllib.request.urlopen(whatsapp_url)
    except Exception as e:
        print(f"WhatsApp Error: {e}")

# 4. क्रेडेंशियल्स लोड करना (Streamlit Secrets से)
api_key = st.secrets.get("API_KEY")
client_id = st.secrets.get("CLIENT_ID")
pin = st.secrets.get("PIN")
token = st.secrets.get("TOTP_TOKEN")

# 5. बैकग्राउंड मास्टर वर्कर (जो ब्रोकर से जुड़कर सबको स्कैन करेगा)
def master_background_worker(api_key, client_id, pin, token):
    try:
        clean_token = str(token).strip()
        obj = SmartConnect(api_key=api_key)
        totp = pyotp.TOTP(clean_token).now()
        data = obj.generateSession(client_id, pin, totp)
        
        if data and data.get('status'):
            print("🟢 Master Background Worker Running Successfully!")
            brain = UltimateTradingBrain()
            
            while True:
                try:
                    for symbol, token_id in WATCHLIST.items():
                        simulated_price = 25000.0  # लाइव LTP यहाँ प्रोसेस होगा
                        
                        feed = {
                            'price_breakout': 'High_Broken',
                            'price': simulated_price,
                            'vwap': simulated_price - 10,
                            'rsi': 52
                        }
                        
                        signal, reasons = brain.analyze_market_conditions(symbol, feed)
                        
                        if signal in ["BULLISH_SIGNAL", "BEARISH_SIGNAL"]:
                            send_whatsapp_and_audio_alert(symbol, signal, simulated_price)
                            
                    time.sleep(10)
                except Exception as loop_err:
                    print(f"Loop Error: {loop_err}")
                    time.sleep(5)
        else:
            print("❌ Authentication Failed.")
    except Exception as e:
        print(f"Worker Error: {e}")

# 6. बैकग्राउंड थ्रेड को चालू करना
if 'master_running' not in st.session_state:
    if api_key and client_id and pin and token:
        st.session_state['master_running'] = True
        t = threading.Thread(target=master_background_worker, args=(api_key, client_id, pin, token))
        t.daemon = True
        t.start()

# 7. यूजर इंटरफेस (फ्रंटएंड डैशबोर्ड)
if api_key and client_id and pin and token:
    st.success("🟢 Ultimate Bot Status: ACTIVE & MONITORING ALL ASSETS WITH VOICE ALERTS")
    st.info("🚀 बॉट बैकग्राउंड में सभी इंडेक्स और शेयरों की स्कैनिंग कर रहा है। जब ऐप खुली होगी तो यह बोलकर भी अलर्ट देगा और व्हाट्सएप पर भी भेजेगा!")
    
    if st.button("📡 Test Voice & WhatsApp Alert Now"):
        send_whatsapp_and_audio_alert("NIFTY 50", "BULLISH_SIGNAL (TEST)", 25000.0)
        st.success("टेस्ट वॉइस और व्हाट्सएप अलर्ट ट्रिगर कर दिया गया है!")
else:
    st.warning("Please configure your API credentials in Streamlit Secrets.")
