import pandas as pd
import streamlit as st

st.set_page_config(page_title="Daily Site Search", page_icon="🔍", layout="wide")

st.title("🔍 Daily Site Search")

@st.cache_data(ttl=3600)
def load_daily_data():
    df = pd.read_csv("test.csv", skiprows=1, encoding="cp1252")
    df.columns = df.columns.str.strip()
    
    site_col = [col for col in df.columns if 'site' in col.lower()]
    if site_col:
        df.rename(columns={site_col[0]: 'Site'}, inplace=True)
        
    df['Site'] = df['Site'].astype(str).str.strip().str.replace(r'\.0$', '', regex=True)
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
