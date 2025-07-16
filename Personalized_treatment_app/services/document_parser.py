# services/document_parser.py

import os
from typing import Dict, Any, Optional, Tuple
import streamlit as st

# Import the specific extractors from the new extraction sub-package

from services.extraction.text_extractor import RawTextExtractor
from services.extraction.patient_info_extractor import PatientInfoExtractor
from services.extraction.metric_extractor import MetricExtractor

class DocumentParser:
    """
    Orchestrates the extraction of raw text, patient meta-info, and health metrics
    from various types of health report files.
    """

    @staticmethod
    def parse_report(file_path: str) -> Dict[str, Any]:
        """
        Parses a given health report file, extracts patient information and metrics.
        
        Args:
            file_path (str): The full path to the uploaded report file.
            
        Returns:
            Dict[str, Any]: A dictionary containing 'patient_info' and 'metrics' data.
                            Returns None for either if extraction fails.
        """
        raw_text = None
        patient_info: Dict[str, Optional[str]] = {}
        metrics: Dict[str, Tuple[str, str]] = {} # FlaggedMetric is Tuple[str, str]

        # 1. Extract raw text from the document
        try:
            # Check file extension to differentiate image from document types
            ext = os.path.splitext(file_path.lower())[1]
            if ext in ['.jpg', '.jpeg', '.png', '.gif']: # Add other image formats if supported by Tesseract
                raw_text = RawTextExtractor.get_text_from_image(file_path)
            else:
                raw_text = RawTextExtractor.extract_text(file_path)
            
            if not raw_text or len(raw_text.strip()) < 20: # Basic check for meaningful text
                st.warning(f"Could not extract sufficient text from {os.path.basename(file_path)}. It might be an image without proper OCR setup or an unreadable file.")
                raw_text = "" # Ensure it's an empty string for subsequent steps
        except ValueError as e:
            st.error(f"Unsupported file type for text extraction: {ext}. Error: {e}")
            return {"patient_info": {}, "metrics": {}} # Return empty data
        except Exception as e:
            st.error(f"Error during raw text extraction from {os.path.basename(file_path)}: {e}")
            return {"patient_info": {}, "metrics": {}}

        # If text extraction was successful, proceed to extract info and metrics
        if raw_text:
            # 2. Extract patient meta-information
            try:
                patient_info = PatientInfoExtractor.extract_patient_info(raw_text)
            except Exception as e:
                st.warning(f"Failed to extract patient info from {os.path.basename(file_path)}: {e}")
                patient_info = {} # Ensure it's an empty dict

            # 3. Extract and flag health metrics
            try:
                # MetricExtractor expects either a path or raw text, since we have raw text, we pass it directly
                metrics = MetricExtractor.extract_metrics(raw_text, is_path=False)
            except Exception as e:
                st.warning(f"Failed to extract health metrics from {os.path.basename(file_path)}: {e}")
                metrics = {} # Ensure it's an empty dict
        else:
            st.warning(f"No text extracted from {os.path.basename(file_path)}. Skipping patient info and metric extraction.")


        return {
            "patient_info": patient_info,
            "metrics": metrics,
            "raw_text": raw_text # Optionally include raw text for debugging/display
        }