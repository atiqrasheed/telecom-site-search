import pandas as pd
import streamlit as st

st.set_page_config(page_title="Hourly Stats", page_icon="📊", layout="wide")

# Custom CSS to hide default sidebar nav and styling
st.markdown("""
    <style>
    [data-testid="stSidebarNav"] {display: none !important;}
    header[data-testid="stHeader"] {display: none !important;}
    #stDecoration {display: none !important;}
    .stApp > footer {display: none !important;}
    </style>
""", unsafe_allow_html=True)

# Top navigation bar
col1, col2, col3 = st.columns([1, 1, 4])
with col1:
    st.page_link("app.py", label="🔍 Daily Search", use_container_width=True)
with col2:
    st.page_link("pages/1_Hourly_Stats.py", label="📊 Hourly Stats", use_container_width=True)

st.divider()

st.title("📊 Hourly Site Statistics")

@st.cache_data(ttl=3600)
def load_hourly_data():
    # Added encoding="cp1252" to fix the utf-8 decoding error
    df = pd.read_csv("pages/hourly_stats.csv", skiprows=1, dtype={"Site": str}, encoding="cp1252")
    df.columns = df.columns.str.strip()
    return df

try:
    df_hourly = load_hourly_data()

    site_id = st.text_input("Enter Site Number (e.g., 0001):")

    if site_id:
        search_term = site_id.strip()
        filtered_df = df_hourly[df_hourly['Site'] == search_term]
        
        if not filtered_df.empty:
            st.dataframe(filtered_df, use_container_width=True)
        else:
            st.warning(f"No hourly records found for Site {search_term}.")
    else:
        st.dataframe(df_hourly.head(100), use_container_width=True)

except Exception as e:
    st.error(f"Error loading file: {e}")
