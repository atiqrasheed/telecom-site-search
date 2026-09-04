import re
import pandas as pd
import streamlit as st

st.set_page_config(
    page_title="4G Cell FDD", 
    page_icon="📡", 
    layout="wide",
    initial_sidebar_state="collapsed"
)

if "daily_search_value" not in st.session_state:
    st.session_state["daily_search_value"] = ""

st.markdown(
    """
    <style>
    [data-testid="stSidebar"] { display: none !important; }
    [data-testid="collapsedControl"] { display: none !important; }
    
    div[data-testid="stPageLink"] a {
        transition: all 0.25s ease-in-out !important;
        border-radius: 8px !important;
    }

    div[data-testid="stPageLink"] a:hover {
        transform: scale(1.06) !important;
        background-color: #1f2937 !important;
        color: #38bdf8 !important;
        box-shadow: 0px 4px 12px rgba(0, 0, 0, 0.3) !important;
    }

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

st.title("📡 Daily Site Stats")

@st.cache_data
def load_data():
    return pd.read_csv("test.csv")

try:
    df = load_data()

    avail_col = [col for col in df.columns if "Availability" in col]
    availability_column = avail_col[0] if avail_col else df.columns[-1]

    search_col, metric_col, _ = st.columns([1.5, 2, 4.5])
    
    with search_col:
        def update_daily_input():
            st.session_state["daily_search_value"] = st.session_state["daily_input_key"]

        site_input = st.text_input(
            "Enter Site ID:", 
            value=st.session_state["daily_search_value"],
            key="daily_input_key",
            on_change=update_daily_input
        )

    current_search = st.session_state["daily_search_value"].strip()

    if current_search != "":
        pattern = rf"(?<!\d){re.escape(current_search)}(?!\d)"
        filtered_df = df[
            df["Site ID (EUtranCellFDD)"].astype(str).str.contains(
                pattern, regex=True, na=False
            )
        ].copy()

        count = len(filtered_df)

        if count > 0:
            numeric_avail = pd.to_numeric(filtered_df[availability_column], errors='coerce')
            avg_value = round(numeric_avail.mean(), 2)

            with metric_col:
                st.metric(
                    label="Average Site Availability", 
                    value=f"{avg_value}%" if pd.notna(avg_value) else "N/A"
                )

            st.success(
                f"Found **{count}** exact matching cells for Site **{current_search}**"
            )

            col_configs = {
                availability_column: st.column_config.TextColumn(
                    alignment="left"
                )
            }

            st.dataframe(
                filtered_df, 
                use_container_width=True, 
                hide_index=True,
                column_config=col_configs
            )
        else:
            st.warning(
                f"No exact matches found for Site '{current_search}'. Try another site ID."
            )
    else:
        st.info("Please enter a site number above to view results.")

except FileNotFoundError:
    st.error("Error: 'test.csv' was not found in the project folder.")
