import pandas as pd
import streamlit as st

st.set_page_config(page_title="Daily Site Search", page_icon="🔍", layout="wide")

# Custom CSS to hide default sidebar navigation and header elements
st.markdown("""
    <style>
    [data-testid="stSidebarNav"] {display: none !important;}
    header[data-testid="stHeader"] {display: none !important;}
    #stDecoration {display: none !important;}
    .stApp > footer {display: none !important;}
    </style>
""", unsafe_allow_html=True)

# Top Navigation Bar
col1, col2, col3 = st.columns([1, 1, 4])
with col1:
    st.page_link("app.py", label="🔍 Daily Search", use_container_width=True)
with col2:
    st.page_link("pages/1_Hourly_Stats.py", label="📊 Hourly Stats", use_container_width=True)

st.divider()

st.title("🔍 Daily Site Search")

@st.cache_data(ttl=3600)
def load_daily_data():
    # Read test.csv from root without skipping rows
    df = pd.read_csv("test.csv", dtype=str, encoding="cp1252")
    
    # Strip whitespace from column headers
    df.columns = df.columns.str.strip()
    
    # Auto-map case variations (e.g., 'site', 'Site ID')
    site_col = [col for col in df.columns if 'site' in col.lower()]
    if site_col:
        df.rename(columns={site_col[0]: 'Site'}, inplace=True)
        
    return df

try:
    df_daily = load_daily_data()

    site_id = st.text_input("Enter Site Number (e.g., 0001):")

    if site_id.strip():
        search_term = site_id.strip()
        filtered_df = df_daily[df_daily['Site'] == search_term]
        
        if not filtered_df.empty:
            st.dataframe(filtered_df, use_container_width=True)
        else:
            st.warning(f"No daily records found for Site {search_term}.")
    else:
        st.info("Enter a site number above to display daily stats.")

except Exception as e:
    st.error(f"Error loading file: {e}")
