import pandas as pd
import streamlit as st

st.set_page_config(
    page_title="Hourly Stats", 
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS styling
st.markdown(
    """
    <style>
    /* Completely hide the sidebar container and collapse arrow */
    [data-testid="stSidebar"] { display: none !important; }
    [data-testid="collapsedControl"] { display: none !important; }

    /* Target the text label above input boxes */
    div[data-testid="stTextInput"] label p {
        font-size: 22px !important;
        font-weight: bold !important;
    }

    /* Hide the Deploy button */
    .stAppDeployButton { display: none !important; }

    /* Hide header menu and footer */
    #MainMenu {visibility: hidden;}
    header {visibility: hidden;}
    footer {visibility: hidden;}
    </style>
""",
    unsafe_allow_html=True,
)

# Fit columns tightly across screen width
            col_configs = {
                df_hourly.columns[0]: st.column_config.TextColumn(width="small"),
                "Site": st.column_config.TextColumn(width="small"),
                availability_column: st.column_config.TextColumn(width="small")
            }

            st.dataframe(
                display_df, 
                use_container_width=True, 
                hide_index=True,
                column_config=col_configs
            )
# Top Navigation Bar
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

    # Identify the availability column dynamically
    avail_col = [col for col in df_hourly.columns if "Availability" in col or "%" in col]
    availability_column = avail_col[0] if avail_col else df_hourly.columns[-1]

    site_id = st.text_input("Enter Site Number (e.g., 0001):")

    if site_id.strip() != "":
        search_term = site_id.strip()
        filtered_df = df_hourly[df_hourly['Site'].astype(str) == search_term].copy()
        
        count = len(filtered_df)

        if count > 0:
            st.success(f"Found **{count}** exact matching hourly records for Site **{search_term}**")

            # Calculate average and append summary row at bottom
            numeric_avail = pd.to_numeric(filtered_df[availability_column], errors='coerce')
            avg_value = round(numeric_avail.mean(), 2)

            summary_row = {
                filtered_df.columns[0]: "",
                "Site": "AVERAGE SITE AVAILABILITY",
                availability_column: f"{avg_value}%" if pd.notna(avg_value) else "N/A",
            }

            display_df = pd.concat(
                [filtered_df, pd.DataFrame([summary_row])], ignore_index=True
            )

            # Fit 3 columns cleanly across screen width without scrollbars
            col_configs = {
                df_hourly.columns[0]: st.column_config.TextColumn(width="medium"),
                "Site": st.column_config.TextColumn(width="large"),
                availability_column: st.column_config.TextColumn(width="medium")
            }

            st.dataframe(
                display_df, 
                use_container_width=True, 
                hide_index=True,
                column_config=col_configs
            )
        else:
            st.warning(f"No hourly records found for Site {search_term}.")
    else:
        st.info("Enter a site number above to display hourly stats.")

except FileNotFoundError:
    st.error("Error: 'pages/hourly_stats.csv' was not found in the pages folder.")
except Exception as e:
    st.error(f"Error loading file: {e}")
