import pandas as pd
import streamlit as st

st.set_page_config(
    page_title="Hourly Stats", 
    layout="wide",
    initial_sidebar_state="collapsed"
)

st.markdown(
    """
    <style>
    [data-testid="stSidebar"] { display: none !important; }
    [data-testid="collapsedControl"] { display: none !important; }
    div[data-testid="stTextInput"] label p { font-size: 22px !important; font-weight: bold !important; }
    .stAppDeployButton { display: none !important; }
    #MainMenu {visibility: hidden;}
    header {visibility: hidden;}
    footer {visibility: hidden;}
    </style>
""",
    unsafe_allow_html=True,
)

col1, col2, col3 = st.columns([1, 1, 4])
with col1:
    st.page_link("app.py", label="🔍 Daily Search", use_container_width=True)
with col2:
    st.page_link("pages/1_Hourly_Stats.py", label="📊 Hourly Stats", use_container_width=True)

st.divider()

st.title("📊 Hourly Site Stats")

@st.cache_data(ttl=3600)
def load_hourly_data():
    df = pd.read_csv("pages/hourly_stats.csv", skiprows=1, encoding="cp1252")
    df.columns = df.columns.str.strip()
    
    site_col = [col for col in df.columns if 'site' in col.lower()]
    if site_col:
        df.rename(columns={site_col[0]: 'Site'}, inplace=True)
        
    df['Site'] = df['Site'].astype(str).str.strip().str.replace(r'\.0$', '', regex=True)
    return df

try:
    df_hourly = load_hourly_data()

    site_id = st.text_input("Enter Site Number (e.g., 0001):")

    if site_id.strip() != "":
        search_term = site_id.strip()
        filtered_df = df_hourly[df_hourly['Site'].astype(str) == search_term]
        
        if not filtered_df.empty:
            st.dataframe(filtered_df, use_container_width=True, hide_index=True)
        else:
            st.warning(f"No hourly records found for Site {search_term}.")
    else:
        st.info("Enter a site number above to display hourly stats.")

except FileNotFoundError:
    st.error("Error: 'pages/hourly_stats.csv' was not found in the pages folder.")
except Exception as e:
    st.error(f"Error loading file: {e}")
