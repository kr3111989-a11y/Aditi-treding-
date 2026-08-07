import streamlit as st
from SmartApi import SmartConnect
import pyotp
import requests
import pandas as pd

st.set_page_config(layout="wide")
st.title("Aditi Trading Dashboard - Smart Option Chain")

api_key = st.secrets.get("API_KEY")
client_id = st.secrets.get("CLIENT_ID")
pin = st.secrets.get("PIN")
token = st.secrets.get("TOTP_TOKEN")

@st.cache_data
def load_script_master():
    url = "https://margincalculator.angelbroking.com/OpenAPI_File/files/OpenAPIScripMaster.json"
    response = requests.get(url)
    if response.status_code == 200:
        return pd.DataFrame(response.json())
    return pd.DataFrame()

if api_key and client_id and pin and token:
    try:
        obj = SmartConnect(api_key=api_key)
        totp = pyotp.TOTP(token).now()
        data = obj.generateSession(client_id, pin, totp)
        
        if data and data.get('status'):
            st.success("Connected to Angel One Successfully!")
            
            with st.spinner("Loading Market Database..."):
                df = load_script_master()
                
            if not df.empty:
                # सभी उपलब्ध इंडेक्स की लिस्ट निकालना
                all_indices = sorted(df[df['exch_seg'] == 'NFO']['name'].dropna().unique())
                default_idx = all_indices.index("NIFTY") if "NIFTY" in all_indices else 0
                
                col1, col2 = st.columns(2)
                with col1:
                    index_choice = st.selectbox("Select Index:", all_indices, index=default_idx)
                
                # उस इंडेक्स की उपलब्ध एक्सपायरी डेट्स निकालना
                index_options = df[(df['name'] == index_choice) & (df['exch_seg'] == 'NFO')]
                if not index_options.empty:
                    expiries = sorted(index_options['expiry'].dropna().unique())
                    with col2:
                        expiry_choice = st.selectbox("Select Expiry:", expiries)
                    
                    if st.button("Load Option Chain View"):
                        with st.spinner("Formatting Option Chain..."):
                            # चुनी गई एक्सपायरी और इंडेक्स के कॉन्ट्रैक्ट्स
                            filtered = index_options[index_options['expiry'] == expiry_choice]
                            
                            # स्ट्राइक प्राइस को सही फॉर्मेट में बदलना
                            filtered['strike'] = pd.to_numeric(filtered['strike'], errors='coerce') / 100.0
                            
                            # CE और PE को अलग करना
                            ce_df = filtered[filtered['symbol'].str.endswith('CE', na=False)]
                            pe_df = filtered[filtered['symbol'].str.endswith('PE', na=False)]
                            
                            # स्ट्राइक के हिसाब से मर्ज करना ताकि ऐप जैसा व्यू मिले
                            merged = pd.merge(
                                ce_df[['strike', 'symbol', 'token']].rename(columns={'symbol': 'CE_Symbol', 'token': 'CE_Token'}),
                                pe_df[['strike', 'symbol', 'token']].rename(columns={'symbol': 'PE_Symbol', 'token': 'PE_Token'}),
                                on='strike',
                                how='inner'
                            ).sort_values('strike')
                            
                            if not merged.empty:
                                st.write(f"### Option Chain for {index_choice} (Expiry: {expiry_choice})")
                                st.dataframe(merged.reset_index(drop=True), use_container_width=True)
                                st.info("यह ऑप्शन चेन व्यू अब स्ट्राइक प्राइस के हिसाब से व्यवस्थित है।")
                            else:
                                st.warning("No matching CE/PE data found for this expiry.")
                else:
                    st.warning("No options data available for this index.")
            else:
                st.error("Could not load Scrip Master database.")
        else:
            st.error(f"Login Failed: {data.get('message', 'Unknown error')}")
            
    except Exception as e:
        st.error(f"Error: {e}")
else:
    st.warning("Please configure API_KEY, CLIENT_ID, PIN, and TOTP_TOKEN in Streamlit Secrets.")
