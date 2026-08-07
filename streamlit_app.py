import streamlit as st

st.title("Aditi Trading Dashboard")
st.write("Welcome to your private trading automation panel.")

# Streamlit secrets से सुरक्षित रूप से API Key चेक करना
api_key = st.secrets.get("API_KEY", "Not Set")

if api_key != "Not Set":
    st.success("API Key loaded securely!")
    
    # ट्रेडिंग डैशबोर्ड का मेन इंटरफ़ेस
    st.info("Your dashboard is connected and ready for live trading automation.")
    
    # यहाँ हम लाइव मार्केट इंडेक्स या ट्रेडिंग का स्टेटस जोड़ेंगे
    col1, col2 = st.columns(2)
    with col1:
        st.metric(label="Nifty 50 Status", value="Connected", delta="Live")
    with col2:
        st.metric(label="Bank Nifty Status", value="Connected", delta="Live")
        
    if st.button("Fetch Market Data"):
        st.write("Fetching live feed from Angel One API...")
        # यहाँ आगे चलकर लाइव आर्डर और पोजीशन का डेटा दिखेगा
else:
    st.warning("Please configure your API_KEY in Streamlit Secrets.")

