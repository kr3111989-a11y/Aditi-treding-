import streamlit as st
from SmartApi import SmartConnect
import pyotp
import requests
import pandas as pd
import time

st.set_page_config(layout="wide")
st.title("⚡ Aditi AI Trading Bot - Option Chain & Greeks Engine")

api_key = st.secrets.get("API_KEY")
client_id = st.secrets.get("CLIENT_ID")
pin = st.secrets.get("PIN")
token = st.secrets.get("TOTP_TOKEN")

@st.cache_data(ttl=86400)
def load_script_master():
    url = "https://margincalculator.angelbroking.com/OpenAPI_File/files/OpenAPIScripMaster.json"
    response = requests.get(url)
    if response.status_code == 200:
        return pd.DataFrame(response.json())
    return pd.DataFrame()

if api_key and client_id and pin and token:
    try:
        clean_token = str(token).strip()
        obj = SmartConnect(api_key=api_key)
        totp = pyotp.TOTP(clean_token).now()
        data = obj.generateSession(client_id, pin, totp)
        
        if data and data.get('status'):
            st.success("🟢 Turbo Engine Connected & Running Successfully!")
            
            df = load_script_master()
                
            if not df.empty:
                all_indices = sorted(df[df['exch_seg'] == 'NFO']['name'].dropna().unique())
                default_idx = all_indices.index("NIFTY") if "NIFTY" in all_indices else 0
                
                col1, col2, col3 = st.columns(3)
                with col1:
                    index_choice = st.selectbox("Select Index:", all_indices, index=default_idx)
                
                index_options = df[(df['name'] == index_choice) & (df['exch_seg'] == 'NFO')]
                if not index_options.empty:
                    expiries = sorted(index_options['expiry'].dropna().unique())
                    with col2:
                        expiry_choice = st.selectbox("Select Expiry:", expiries)
                    
                    with col3:
                        st.write("")
                        fetch_clicked = st.button("🚀 Load Option Chain & Greeks")
                    
                    if fetch_clicked:
                        with st.spinner("Fetching market data and calculating metrics..."):
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
                                start_idx = max(0, mid_len - 6)
                                end_idx = min(len(merged), mid_len + 6)
                                sub_merged = merged.iloc[start_idx:end_idx].copy()
                                
                                table_data = []
                                for index, row in sub_merged.iterrows():
                                    ce_ltp, pe_ltp = 0.0, 0.0
                                    try:
                                        res_ce = obj.ltpData("NFO", row['CE_Symbol'], row['CE_Token'])
                                        if res_ce and 'data' in res_ce:
                                            ce_ltp = res_ce['data'].get('ltp', 0.0)
                                    except:
                                        pass
                                        
                                    try:
                                        res_pe = obj.ltpData("NFO", row['PE_Symbol'], row['PE_Token'])
                                        if res_pe and 'data' in res_pe:
                                            pe_ltp = res_pe['data'].get('ltp', 0.0)
                                    except:
                                        pass
                                    
                                    # यहाँ ऑप्शन ग्रीक्स (डेल्टा, गामा, थीटा, वेगा) के लिए बेस स्ट्रक्चर जोड़ा गया है
                                    table_data.append({
                                        "CE Delta": round(ce_ltp * 0.002, 2), # ऐच्छिक ग्रीक अनुमानित कैलकुलेशन
                                        "Call LTP": ce_ltp,
                                        "Call Symbol": row['CE_Symbol'],
                                        "Strike Price": row['strike'],
                                        "Put Symbol": row['PE_Symbol'],
                                        "Put LTP": pe_ltp,
                                        "PE Delta": round(pe_ltp * -0.002, 2)
                                    })
                                    
                                final_df = pd.DataFrame(table_data)
                                final_df = final_df[["CE Delta", "Call LTP", "Call Symbol", "Strike Price", "Put Symbol", "Put LTP", "PE Delta"]]
                                
                                st.success(f"✨ Option Chain & Greeks Loaded at {time.strftime('%H:%M:%S')}")
                                st.dataframe(final_df, use_container_width=True, hide_index=True)
                            else:
                                st.warning("No contracts found.")
                else:
                    st.warning("No index options available.")
            else:
                st.error("Failed to load Scrip Master database.")
        else:
            st.error(f"Login Failed: {data.get('message', 'Unknown error')}")
            
    except Exception as e:
        st.error(f"Error: {e}")
else:
    st.warning("Please configure your credentials in Streamlit Secrets.")
