import pandas as pd
import plotly.express as px
import streamlit as st

st.set_page_config(
    page_title="4G Cell FDD", 
    page_icon="📡", 
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Initialize Session State variable for persistent search across page switches
if "hourly_search_value" not in st.session_state:
    st.session_state["hourly_search_value"] = ""

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

    avail_col = [col for col in df_hourly.columns if "Availability" in col or "%" in col]
    availability_column = avail_col[0] if avail_col else df_hourly.columns[-1]

    search_col, metric_col, _ = st.columns([1.5, 2, 4.5])

    with search_col:
        def update_hourly_input():
            st.session_state["hourly_search_value"] = st.session_state["hourly_input_key"]

        site_id = st.text_input(
            "Enter Site ID: ", 
            value=st.session_state["hourly_search_value"],
            key="hourly_input_key",
            on_change=update_hourly_input
        )

    current_search = st.session_state["hourly_search_value"].strip()

    if current_search != "":
        filtered_df = df_hourly[df_hourly['Site'].astype(str) == current_search].copy()
        
        count = len(filtered_df)

        if count > 0:
            numeric_avail = pd.to_numeric(filtered_df[availability_column], errors='coerce')
            avg_value = round(numeric_avail.mean(), 2)

            with metric_col:
                st.metric(
                    label="Average Site Availability", 
                    value=f"{avg_value}%" if pd.notna(avg_value) else "N/A"
                )

            banner_col, toggle_col = st.columns([4, 1])
            with banner_col:
                st.success(f"Found **{count}** exact matching hourly records for Site **{current_search}**")
            with toggle_col:
                show_graph = st.checkbox("📈 Convert to Graph", key="hourly_show_graph")

            if show_graph:
                st.subheader("📈 24-Hour Availability Trend")
                
                plot_df = filtered_df.copy()
                plot_df[availability_column] = pd.to_numeric(plot_df[availability_column], errors='coerce')
                
                time_col = df_hourly.columns[0]
                plot_df["Time_Only"] = pd.to_datetime(plot_df[time_col], errors="coerce").dt.strftime("%H:%M")
                
                if plot_df["Time_Only"].isnull().all():
                    plot_df["Time_Only"] = plot_df[time_col].astype(str).str.split().str[-1]

                fig = px.line(
                    plot_df, 
                    x="Time_Only", 
                    y=availability_column,
                    markers=True,
                    labels={"Time_Only": "Time", availability_column: "Availability (%)"}
                )
                
                fig.update_layout(
                    margin=dict(l=20, r=20, t=20, b=20),
                    xaxis=dict(type='category'),
                    yaxis=dict(range=[0, 102]),  # Caps 100% at top
                    hovermode="x unified"
                )

                st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})

            col_configs = {
                df_hourly.columns[0]: st.column_config.TextColumn(width="small"),
                "Site": st.column_config.TextColumn(width="small"),
                availability_column: st.column_config.TextColumn(alignment="left")
            }

            st.dataframe(
                filtered_df, 
                use_container_width=True, 
                hide_index=True,
                column_config=col_configs
            )
        else:
            st.warning(f"No hourly records found for Site {current_search}.")
    else:
        st.info("Enter a site number above to display hourly stats.")

except FileNotFoundError:
    st.error("Error: 'pages/hourly_stats.csv' was not found in the pages folder.")
except Exception as e:
    st.error(f"Error loading file: {e}")
