import streamlit as st
from SmartApi import SmartConnect
from SmartApi.smartWebSocketV2 import SmartWebSocketV2
import pyotp
import requests
import pandas as pd
import threading

st.set_page_config(layout="wide")
st.title("⚡ Aditi Angel One - Live WebSocket Option Chain")

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
            st.success("🟢 Connected to Angel One & Ready for WebSocket Stream!")
            
            feed_token = data['data'].get('feedToken')
            
            with st.spinner("Loading Market Database..."):
                df = load_script_master()
                
            if not df.empty:
                all_indices = sorted(df[df['exch_seg'] == 'NFO']['name'].dropna().unique())
                default_idx = all_indices.index("NIFTY") if "NIFTY" in all_indices else 0
                
                col1, col2 = st.columns(2)
                with col1:
                    index_choice = st.selectbox("Select Index:", all_indices, index=default_idx)
                
                index_options = df[(df['name'] == index_choice) & (df['exch_seg'] == 'NFO')]
                if not index_options.empty:
                    expiries = sorted(index_options['expiry'].dropna().unique())
                    with col2:
                        expiry_choice = st.selectbox("Select Expiry:", expiries)
                    
                    if st.button("🚀 Initialize Live WebSocket Stream"):
                        filtered = index_options[index_options['expiry'] == expiry_choice]
                        filtered['strike'] = pd.to_numeric(filtered['strike'], errors='coerce') / 100.0
                        
                        ce_df = filtered[filtered['symbol'].str.endswith('CE', na=False)]
                        pe_df = filtered[filtered['symbol'].str.endswith('PE', na=False)]
                        
                        merged = pd.merge(
                            ce_df[['strike', 'symbol', 'token']].rename(columns={'symbol': 'CE_Symbol', 'token': 'CE_Token'}),
                            pe_df[['strike', 'symbol', 'token']].rename(columns={'symbol': 'PE_Symbol', 'token': 'PE_Token'}),
                            on='strike',
                            how='inner'
                        ).sort_values('strike').reset_index(drop=True)
                        
                        if not merged.empty:
                            mid_len = len(merged) // 2
                            start_idx = max(0, mid_len - 8)
                            end_idx = min(len(merged), mid_len + 8)
                            sub_merged = merged.iloc[start_idx:end_idx].copy()
                            
                            # टोकन लिस्ट तैयार करना जो WebSocket से जोड़ी जाएगी
                            token_list = []
                            for idx, row in sub_merged.iterrows():
                                token_list.append(str(row['CE_Token']))
                                token_list.append(str(row['PE_Token']))
                                
                            st.info(f"Connecting to WebSocket for {len(token_list)} contracts...")
                            
                            # WebSocket कॉलबैक फंग्शन
                            def on_data(wsapp, message):
                                st.write("Live Tick:", message)

                            def on_open(wsapp):
                                st.success("WebSocket Connection Established!")
                                # सब्सक्रिप्शन भेजना (मोड 2 = LTP)
                                sws.sub(
                                    correlation_id="stream_1",
                                    mode=2,
                                    token_list=[{"exchangeType": 2, "tokens": token_list}]
                                )

                            def on_error(wsapp, error):
                                st.error(f"WebSocket Error: {error}")

                            def on_close(wsapp, close_status_code, close_msg):
                                st.warning("WebSocket Connection Closed.")

                            # WebSocket ऑब्जेक्ट बनाना
                            sws = SmartWebSocketV2(auth_token=data['data']['jwtToken'], api_key=api_key, client_code=client_id, feed_token=feed_token)
                            
                            sws.on_open = on_open
                            sws.on_data = on_data
                            sws.on_error = on_error
                            sws.on_close = on_close
                            
                            # बैकग्राउंड थ्रेड में WebSocket चलाना ताकि ऐप हैंग न हो
                            wst = threading.Thread(target=sws.connect)
                            wst.daemon = True
                            wst.start()
                            
                            st.success("✨ WebSocket बैकग्राउंड में लाइव डेटा स्ट्रीम करना शुरू कर चुका है!")
                        else:
                            st.warning("No contracts found.")
                else:
                    st.warning("No data available.")
            else:
                st.error("Could not load database.")
        else:
            st.error(f"Login Failed: {data.get('message', 'Unknown error')}")
            
    except Exception as e:
        st.error(f"Error: {e}")
else:
    st.warning("Please configure API_KEY, CLIENT_ID, PIN, and TOTP_TOKEN in Streamlit Secrets.")
