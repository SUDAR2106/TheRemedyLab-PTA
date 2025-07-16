import pandas as pd
import streamlit as st

def apply_filters(df: pd.DataFrame) -> pd.DataFrame:
    """
    Apply interactive filters to the patient records DataFrame.
    Supports filtering by Patient Name and Report Date.
    """
    filtered = df.copy()

    st.markdown("### 🔍 Search & Filter Records")

    # --- Convert Report Date to datetime ---
    if "Report Date" in filtered.columns:
        filtered["Report Date"] = pd.to_datetime(filtered["Report Date"], errors="coerce")

    # --- Patient Name Filter ---
    if "Patient Name" in filtered.columns:
        patient_names = sorted(filtered["Patient Name"].dropna().unique())
        selected_name = st.selectbox("👤 Filter by Patient Name", options=["All"] + patient_names)

        if selected_name != "All":
            filtered = filtered[filtered["Patient Name"] == selected_name]

    # --- Date Range Filter ---
    if "Report Date" in filtered.columns and not filtered["Report Date"].isnull().all():
        min_date = filtered["Report Date"].min()
        max_date = filtered["Report Date"].max()

        date_range = st.date_input("📅 Filter by Report Date", value=(min_date, max_date))

        if isinstance(date_range, tuple) and len(date_range) == 2:
            start, end = pd.to_datetime(date_range[0]), pd.to_datetime(date_range[1])
            filtered = filtered[
                (filtered["Report Date"] >= start) & 
                (filtered["Report Date"] <= end)
            ]

    return filtered