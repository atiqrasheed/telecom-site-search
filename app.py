import re
import pandas as pd
import streamlit as st

st.set_page_config(
    page_title="4G Cell FDD", 
    page_icon="📡", 
    layout="wide",
    initial_sidebar_state="collapsed"
)

st.markdown(
    """
    <style>
    [data-testid="stSidebar"] { display: none !important; }
    [data-testid="collapsedControl"] { display: none !important; }
    
    /* Target top navigation links for hover zoom & color effects */
    div[data-testid="stPageLink"] a {
        transition: all 0.25s ease-in-out !important;
        border-radius: 8px !important;
    }

    /* Hover effect: Size increase & color highlight */
    div[data-testid="stPageLink"] a:hover {
        transform: scale(1.06) !important; /* Increases size by 6% */
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

    site_input = st.text_input("Enter Site ID:", "")

    # Check explicitly if input is not empty (allows '0')
    if site_input.strip() != "":
        clean_site = site_input.strip()

        # Regex matching cast explicitly to string column
        pattern = rf"(?<!\d){re.escape(clean_site)}(?!\d)"
        filtered_df = df[
            df["Site ID (EUtranCellFDD)"].astype(str).str.contains(
                pattern, regex=True, na=False
            )
        ].copy()

        count = len(filtered_df)

        if count > 0:
            st.success(
                f"Found **{count}** exact matching cells for Site **{clean_site}**"
            )

            # Convert numeric column explicitly before mean calculation
            numeric_avail = pd.to_numeric(filtered_df[availability_column], errors='coerce')
            avg_value = round(numeric_avail.mean(), 2)

            summary_row = {
                df.columns[0]: "",
                "Site ID (EUtranCellFDD)": "AVERAGE SITE AVAILABILITY",
                availability_column: f"{avg_value}%" if pd.notna(avg_value) else "N/A",
            }

            display_df = pd.concat(
                [filtered_df, pd.DataFrame([summary_row])], ignore_index=True
            )

            st.dataframe(display_df, use_container_width=True, hide_index=True)
        else:
            st.warning(
                f"No exact matches found for Site '{clean_site}'. Try another site ID."
            )
    else:
        st.info("Please enter a site number above to view results.")

except FileNotFoundError:
    st.error("Error: 'test.csv' was not found in the project folder.")
