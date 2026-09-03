import pandas as pd
import streamlit as st

# Page Configuration
st.set_page_config(
    page_title="Hourly Stats",
    page_icon="📊",
    layout="wide"
)

# Apply dark theme styling
st.markdown("""
    <style>
    header[data-testid="stHeader"] {display: none !important;}
    #stDecoration {display: none !important;}
    .stApp > footer {display: none !important;}
    </style>
""", unsafe_allow_html=True)

st.title("📊 Hourly Site Statistics")

# Load hourly CSV file
@st.cache_data(ttl=3600)
def load_hourly_data():
    # skiprows=1 ignores 'InstantQueryElement' on Row 1
    # dtype={'Site': str} keeps site IDs like '0001' from losing leading zeros
    df = pd.read_csv("hourly_stats.csv", skiprows=1, dtype={"Site": str})
    df.columns = df.columns.str.strip()
    return df

try:
    df_hourly = load_hourly_data()

    # Search input for site number
    site_id = st.text_input("Enter Site Number (e.g., 0001):")

    if site_id:
        search_term = site_id.strip()
        filtered_df = df_hourly[df_hourly['Site'] == search_term]
        
        if not filtered_df.empty:
            st.dataframe(filtered_df, use_container_width=True)
        else:
            st.warning(f"No hourly records found for Site {search_term}.")
    else:
        st.info("Enter a site number above to display hourly stats.")

except Exception as e:
    st.error("Please ensure `hourly_stats.csv` is uploaded to your GitHub repository root.")