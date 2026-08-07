import streamlit as st
from SmartApi import SmartConnect
import pyotp
import requests
import pandas as pd

st.set_page_config(layout="wide")
st.title("Aditi Trading Dashboard - Pro Option Chain")

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
                    
                    if st.button("Load App-Style Option Chain"):
                        with st.spinner("Fetching Live Chain Data..."):
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
                                # ऐप की तरह बीच के मुख्य स्ट्राइक्स दिखाने के लिए स्लाइस करना
                                mid_len = len(merged) // 2
                                start_idx = max(0, mid_len - 7)
                                end_idx = min(len(merged), mid_len + 7)
                                sub_merged = merged.iloc[start_idx:end_idx].copy()
                                
                                ce_ltps, pe_ltps = [], []
                                
                                for index, row in sub_merged.iterrows():
                                    try:
                                        ce_res = obj.ltpData("NFO", row['CE_Symbol'], row['CE_Token'])
                                        ce_ltp = ce_res['data']['ltp'] if ce_res and 'data' in ce_res else 0.0
                                    except:
                                        ce_ltp = 0.0
                                        
                                    try:
                                        pe_res = obj.ltpData("NFO", row['PE_Symbol'], row['PE_Token'])
                                        pe_ltp = pe_res['data']['ltp'] if pe_res and 'data' in pe_res else 0.0
                                    except:
                                        pe_ltp = 0.0
                                        
                                    ce_ltps.append(ce_ltp)
                                    pe_ltps.append(pe_ltp)
                                    
                                sub_merged['Call LTP'] = ce_ltps
                                sub_merged['Put LTP'] = pe_ltps
                                
                                # बिल्कुल एंजेल वन ऐप जैसा कॉलम लेआउट (Call -> Strike -> Put)
                                app_style_df = sub_merged[['Call LTP', 'CE_Symbol', 'strike', 'PE_Symbol', 'Put LTP']]
                                app_style_df.columns = ['Call LTP', 'Call Symbol', 'Strike Price', 'Put Symbol', 'Put LTP']
                                
                                st.write(f"### 📊 Option Chain Layout for {index_choice} ({expiry_choice})")
                                st.dataframe(app_style_df, use_container_width=True, hide_index=True)
                                st.success("ऑप्शन चेन अब ऐप के लेआउट फॉर्मेट में लोड हो गई है!")
                            else:
                                st.warning("No option data found.")
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
