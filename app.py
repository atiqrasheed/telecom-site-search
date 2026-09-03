import re
import pandas as pd
import streamlit as st

# Set page title and layout
st.set_page_config(page_title="Site Search Tool", layout="wide")

st.title("📡 Daily Site Stats Search")

# Custom CSS styling
st.markdown(
    """
    <style>
    /* Target the text label above the search bar */
    div[data-testid="stTextInput"] label p {
        font-size: 22px !important;
        font-weight: bold !important;
    }

    /* Hide the Deploy button */
    .stAppDeployButton {
        display: none !important;
    }

    /* Hide header menu and footer */
    #MainMenu {visibility: hidden;}
    header {visibility: hidden;}
    footer {visibility: hidden;}
    </style>
""",
    unsafe_allow_html=True,
)


# Load CSV data efficiently
@st.cache_data
def load_data():
    return pd.read_csv("test.csv")


try:
    df = load_data()

    # Dynamic identification of the availability column name
    avail_col = [col for col in df.columns if "Availability" in col]
    availability_column = avail_col[0] if avail_col else df.columns[-1]

    # Search bar input box
    site_input = st.text_input("Enter Site ID:", "")

    if site_input.strip():
        clean_site = site_input.strip()

        # Exact match regex pattern
        pattern = rf"(?<!\d){re.escape(clean_site)}(?!\d)"
        filtered_df = df[
            df["Site ID (EUtranCellFDD)"].str.contains(
                pattern, regex=True, na=False
            )
        ].copy()

        count = len(filtered_df)

        if count > 0:
            st.success(
                f"Found **{count}** exact matching cells for Site **{clean_site}**"
            )

            # Calculate average and create summary row
            avg_value = round(filtered_df[availability_column].mean(), 2)

            summary_row = {
                df.columns[0]: "",
                "Site ID (EUtranCellFDD)": "AVERAGE SITE AVAILABILITY",
                availability_column: f"{avg_value}%",
            }

            # Append summary row at the bottom of the table
            display_df = pd.concat(
                [filtered_df, pd.DataFrame([summary_row])], ignore_index=True
            )

            # Display table with the summary row inside
            st.dataframe(display_df, use_container_width=True, hide_index=True)
        else:
            st.warning(
                f"No exact matches found for Site '{clean_site}'. Try another site ID."
            )
    else:
        st.info("Please enter a site number above to view results.")

except FileNotFoundError:
    st.error("Error: 'test.csv' was not found in the project folder.")