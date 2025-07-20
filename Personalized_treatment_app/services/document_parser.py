# services/document_parser.py

import os
import json
from datetime import datetime
from typing import Dict, Any, Optional, Tuple
import streamlit as st

# Import the specific extractors from the new extraction sub-package



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
            from services.extraction.text_extractor import RawTextExtractor
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
                from services.extraction.patient_info_extractor import PatientInfoExtractor
                patient_info = PatientInfoExtractor.extract_patient_info(raw_text)
            except Exception as e:
                st.warning(f"Failed to extract patient info from {os.path.basename(file_path)}: {e}")
                patient_info = {} # Ensure it's an empty dict

            # 3. Extract and flag health metrics
            try:
                from services.extraction.metric_extractor import MetricExtractor
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
    
    @classmethod
    def process_report_pipeline(cls, report_id: str) -> bool:
        """
        Orchestrates full processing:
        1. Loads report
        2. Extracts data
        3. Saves to DB
        4. Generates AI recommendations
        5. Saves/updates recommendations
        6. Triggers doctor auto-allocation
        """
        from models.health_report import HealthReport
        from models.recommendation import Recommendation
        from services.ai_recommendation_engine import generate_ai_recommendations
        from services.auto_allocator import auto_assign_doctor
        report = HealthReport.get_by_report_id(report_id)
        if not report:
            print(f"[DocumentParser] Report {report_id} not found.")
            return False

        print(f"[DocumentParser] 🔍 Processing report: {report.file_name} ({report.report_id})")

        # --- Step 1: Extract content
        extracted = cls.parse_report(report.file_path)

        if not extracted or not extracted.get("raw_text"):
            report.processing_status = 'failed_extraction'
            report.extracted_data_json = json.dumps({"error": "Extraction failed or empty content"})
        else:
            report.processing_status = 'extracted'
            report.extracted_data_json = json.dumps(extracted)

        if not report.save():
            print(f"[DocumentParser] ❌ Failed to update report with extracted data.")
            return False
        
         # --- Step 2. Doctor Auto-Allocation (NEW ORDER) ---
        # This happens AFTER extraction, but BEFORE AI recommendations.
        # This will update report.assigned_doctor_id and create PatientDoctorMapping.
        if report.processing_status == 'extracted':
            print(f"DocumentParser: Triggering doctor auto-allocation for report {report_id}...")
            assigned_doctor_id = auto_assign_doctor(report_id) # auto_assign_doctor now returns doctor_id
            
            if not assigned_doctor_id:
                print(f"DocumentParser: No doctor could be assigned for report {report_id}. Skipping AI recommendation.")
                # You might want to update report status to 'pending_manual_assignment' here
                return False
            
            # Re-fetch report to get the updated assigned_doctor_id if auto_assign_doctor saves it
            # Or, rely on the fact that auto_assign_doctor directly updates the HealthReport object.
            # Assuming auto_assign_doctor correctly updates `report.assigned_doctor_id` in the DB and potentially the in-memory object.
            # For safety, let's re-fetch the report or ensure the object is updated.
            # The current auto_assign_doctor saves the report itself, so this object should be fine.
            report = HealthReport.get_by_report_id(report_id) # Re-fetch to ensure assigned_doctor_id is up-to-date
            
            if not report.assigned_doctor_id:
                print(f"DocumentParser: Report {report_id} still has no assigned doctor after auto-allocation. Exiting pipeline.")
                return False

            print(f"DocumentParser: Doctor {report.assigned_doctor_id} assigned to report {report_id}.")

        # --- Step 2: AI Recommendation
        if report.processing_status == 'extracted':
            print(f"DocumentParser: Generating AI recommendations for report {report_id}...")
            ai_recommendations = generate_ai_recommendations(extracted)

            if ai_recommendations:
                print(f"DocumentParser: Creating/Updating recommendation for report {report_id} with AI data and assigned doctor...")
                existing_recommendation = Recommendation.find_by_report_id(report.report_id)

                if existing_recommendation:
                    updated = existing_recommendation.update_status(
                        new_status='pending_doctor_review',
                        doctor_id=report.assigned_doctor_id,
                        approved_treatment=ai_recommendations.get('treatment_suggestions', ''),
                        approved_lifestyle=ai_recommendations.get('lifestyle_recommendations', ''),
                        doctor_notes=''
                    )
                    if updated:
                        print(f"DocumentParser: Existing recommendation for report {report_id} updated successfully.")
                    else:
                        print(f"DocumentParser: Failed to update existing recommendation for report {report_id}.")
                else:
                    new_rec = Recommendation.create(
                        report_id=report.report_id,
                        patient_id=report.patient_id,
                        doctor_id=report.assigned_doctor_id,
                        ai_generated_treatment=ai_recommendations.get('treatment_suggestions', ''),
                        ai_generated_lifestyle=ai_recommendations.get('lifestyle_recommendations', ''),
                        ai_generated_priority=ai_recommendations.get('priority', 'Medium'),
                        status='pending_doctor_review'
                    )
                    if new_rec:
                        print(f"DocumentParser: New recommendation created for report {report_id}.")
                    else:
                        print(f"DocumentParser: Failed to create recommendation for report {report_id}.")
            else:
                print(f"DocumentParser: AI recommendation engine returned no results for report {report_id}.")
        else:
            print(f"DocumentParser: Skipping doctor assignment and AI generation — status not extracted.")

        return True

        # # --- Step 3: Auto-allocate to doctor
        # print(f"[DocumentParser] ⚙️ Triggering doctor allocation...")
        # auto_assign_doctor(report.report_id)
        # print(f"[DocumentParser] ✅ Auto-assignment completed for report {report.report_id}")
        # return True