import os
import pandas as pd
import streamlit as st

# ⬇️ NEW imports using the three classes
from modules.extractor.text_extractor import RawTextExtractor
from modules.extractor.metric_extractor import MetricExtractor
from modules.extractor.patient_info_extractor import PatientInfoExtractor

# from DataCollectionAndStructuring.modules.extractor.extractor import extract_metrics, extract_text, extract_patient_info
from modules.consolidator import Consolidator  # ensure this is implemented
from config import UPLOAD_DIR, DOWNLOAD_DIR, RECORDS_PATH
from modules.data_filter import apply_filters


# ---------------------- Streamlit App Setup ----------------------

st.set_page_config(
    page_title="Smart Health Report Analyzer - The Remedy Lab",
    page_icon="🩺",
    layout="centered",
)

st.title("🩺 Smart Health Report Analyzer –  The Remedy Lab")

st.markdown(
    "Upload **PDF, DOCX, CSV, or JSON** lab reports. "
    "The app auto‑extracts key metrics, runs OCR on scanned PDFs, "
    "maps synonyms, and flags abnormal or missing values."
)

# ---------------------- Upload File ----------------------
uploaded = st.file_uploader("Choose report file",
                            type=["pdf", "docx", "csv", "json"])

if uploaded:
    # Save file to disk
    path = os.path.join(UPLOAD_DIR, uploaded.name)
    with open(path, "wb") as f:
        f.write(uploaded.getbuffer())
    st.success(f"Uploaded: {uploaded.name}")

    # ---------------------- Analyze and Auto-Save ----------------------
    with st.spinner("Analyzing and saving…"):
        try:
            # 1️⃣ raw text
            text = RawTextExtractor.extract_text(path)

            # 2️⃣ metrics (flagged)  — pass raw text, so is_path=False
            flagged = MetricExtractor.extract_metrics(text, is_path=False)

            # 3️⃣ patient meta
            patient_md = PatientInfoExtractor.extract_patient_info(text)
            # text = extract_text(path)
            # flagged = extract_metrics(text, is_path=False)
            # patient_md = extract_patient_info(text)

            # Metrics DataFrame
            df_metrics = pd.DataFrame(
                [(k, v[0], v[1]) for k, v in flagged.items()],
                columns=["Metric", "Value", "Color"]
            )

            # Patient Info DataFrame
            df_patient = pd.DataFrame.from_dict(patient_md, orient='index', columns=['Value']).reset_index()
            df_patient.columns = ['Metric', 'Value']

            # Save combined report to downloads folder
            output_filename = os.path.splitext(uploaded.name)[0] + "_extracted.csv"
            csv_path = os.path.join(DOWNLOAD_DIR, output_filename)

            combined_df = pd.DataFrame(patient_md.items(), columns=["Field", "Value"])
            combined_df = pd.concat([
                combined_df,
                pd.DataFrame([["---", "---"]], columns=["Field", "Value"]),
                df_metrics[["Metric", "Value"]].rename(columns={"Metric": "Field"})
            ], ignore_index=True)
            combined_df.to_csv(csv_path, index=False)

            # Save one-row flat record to records.csv (for training)
            consolidator = Consolidator()
            consolidator.save_structured_record(patient_md, flagged)


        except ValueError as err:
            st.error(str(err))
            st.stop()

    # ---------------------- Display Patient Info ----------------------
    st.subheader("🧾 Patient Details")
    st.table(df_patient)

    # ---------------------- Display Metrics with Color ----------------------
    st.subheader("🔬 Extracted Metrics")

    def _style(row):
        color = flagged[row.Metric][1]
        return [f"background-color: {color}; color: white"
                if col == 1 else "" for col, _ in enumerate(row)]

    st.dataframe(df_metrics.style.apply(_style, axis=1), use_container_width=True)

    # ---------------------- Download Button ----------------------
    with open(csv_path, "rb") as f:
        st.download_button("⬇️ Click to Download CSV", f, file_name=output_filename)
# --- Display Full Records with Filters ---
st.markdown("## 📊 Historical Patient Records")

if os.path.exists(RECORDS_PATH):
    df_records = pd.read_csv(RECORDS_PATH)
    
    # Apply filters from filters.py
    filtered_df = apply_filters(df_records)

    st.dataframe(filtered_df, use_container_width=True)
else:
    st.info("No records found yet.")
