import streamlit as st
from SmartApi import SmartConnect

st.title("Aditi Trading Dashboard - Full Market")

api_key = st.secrets.get("API_KEY")
client_id = st.secrets.get("CLIENT_ID")
pin = st.secrets.get("PIN")

if api_key and client_id and pin:
    try:
        obj = SmartConnect(api_key=api_key)
        data = obj.generateSession(client_id, pin)
        st.success("Connected to Angel One!")

        # स्टॉक सर्च करने के लिए इनपुट बॉक्स
        symbol = st.text_input("Enter Stock Symbol (e.g. SBIN, RELIANCE):", "").upper()
        
        if st.button("Get Live Price"):
            if symbol:
                # यहाँ हम NSE का सिंबल डालकर प्राइस फेच करते हैं
                # नोट: इसके लिए 'symboltoken' की जरूरत होती है
                st.write(f"Fetching live price for {symbol}...")
                # भविष्य में यहाँ हम टोकन मैप का इस्तेमाल करेंगे
            else:
                st.warning("Please enter a valid stock symbol.")
                
    except Exception as e:
        st.error(f"Login Failed: {e}")
else:
    st.warning("Please configure API_KEY, CLIENT_ID, and PIN in Secrets.")
    
