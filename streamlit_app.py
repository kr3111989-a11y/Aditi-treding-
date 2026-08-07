import streamlit as st
from SmartApi import SmartConnect
import pyotp
import requests
import pandas as pd

st.set_page_config(layout="wide")

# एंजेल वन ऐप जैसी हूबहू डार्क थीम और स्टाइल शीट
st.markdown("""
    <style>
    .main { background-color: #0b0e14; color: #ffffff; }
    .stSelectbox, .stButton { font-size: 14px; }
    .oc-table { width: 100%; border-collapse: collapse; background-color: #12161c; font-family: sans-serif; margin-top: 10px; }
    .oc-th { background-color: #1a222d; color: #8b949e; text-align: center; padding: 12px; font-size: 13px; border-bottom: 2px solid #30363d; }
    .oc-td { text-align: center; padding: 10px; border-bottom: 1px solid #21262d; font-size: 15px; }
    .call-ltp { color: #ff7b72; font-weight: bold; background-color: rgba(255, 123, 114, 0.08); }
    .put-ltp { color: #3fb950; font-weight: bold; background-color: rgba(63, 185, 80, 0.08); }
    .strike-box { background-color: #1f2937; color: #ffffff; font-weight: bold; font-size: 16px; border-left: 2px solid #30363d; border-right: 2px solid #30363d; }
    </style>
""", unsafe_allow_html=True)

st.title("📊 Aditi Angel One - Live Option Chain")

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
            st.success("🟢 Connected to Angel One Successfully!")
            
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
                    
                    if st.button("🚀 Load App-Style Option Chain"):
                        with st.spinner("Fetching Live Market Prices..."):
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
                                
                                # ऐप जैसा लेआउट टेबल बनाना
                                html_table = """
                                <table class="oc-table">
                                    <tr>
                                        <th class="oc-th">Call Symbol</th>
                                        <th class="oc-th">Call LTP (₹)</th>
                                        <th class="oc-th" style="background-color: #212d3b; color: #fff;">Strike Price</th>
                                        <th class="oc-th">Put LTP (₹)</th>
                                        <th class="oc-th">Put Symbol</th>
                                    </tr>
                                """
                                
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
                                        
                                    html_table += f"""
                                    <tr>
                                        <td class="oc-td" style="color: #8b949e; font-size: 11px;">{row['CE_Symbol']}</td>
                                        <td class="oc-td call-ltp">₹{ce_ltp}</td>
                                        <td class="oc-td strike-box">{row['strike']}</td>
                                        <td class="oc-td put-ltp">₹{pe_ltp}</td>
                                        <td class="oc-td" style="color: #8b949e; font-size: 11px;">{row['PE_Symbol']}</td>
                                    </tr>
                                    """
                                    
                                html_table += "</table>"
                                st.markdown(html_table, unsafe_allow_html=True)
                                st.success("✨ ऑप्शन चेन अब बिल्कुल एंजेल वन ऐप के डार्क लुक और फॉर्मेट में लोड हो गई है!")
                            else:
                                st.warning("No option data found.")
                else:
                    st.warning("No options data available.")
            else:
                st.error("Could not load database.")
        else:
            st.error(f"Login Failed: {data.get('message', 'Unknown error')}")
            
    except Exception as e:
        st.error(f"Error: {e}")
else:
    st.warning("Please configure API_KEY, CLIENT_ID, PIN, and TOTP_TOKEN in Streamlit Secrets.")
