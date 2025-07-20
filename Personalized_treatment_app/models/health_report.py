# models/health_report.py
import uuid
import json
from datetime import datetime
from database.db_utils import DBManager

import json
import os
from config import UPLOAD_DIR  # Ensure this is imported to use the upload directory path


class HealthReport:
    def __init__(self, report_id=None, patient_id=None, uploaded_by=None, report_type=None,file_type=None,
                 upload_date=None, file_name=None, file_path=None, extracted_data_json=None,
                 processing_status=None, assigned_doctor_id: str = None):
        self.report_id = report_id if report_id else str(uuid.uuid4())
        self.patient_id = patient_id
        self.uploaded_by = uploaded_by # user_id of who uploaded
        self.report_type = report_type
        self.file_type = file_type  # e.g., 'pdf', 'docx', 'csv', 'json', 'image', etc.
        self.upload_date = upload_date if upload_date else datetime.now().isoformat()
        self.file_name = file_name
        self.file_path = file_path
        
        # Store as string in DB, load as dict/object
        # Ensure extracted_data_json is always a string when set
        if isinstance(extracted_data_json, dict):
            self.extracted_data_json = json.dumps(extracted_data_json)
        elif extracted_data_json is None:
            self.extracted_data_json = "{}" # Store an empty JSON object as a string
        else: # Assume it's already a string or handle other types as needed
            self.extracted_data_json = extracted_data_json
            
        self.processing_status = processing_status
        self.assigned_doctor_id = assigned_doctor_id  # ID of the doctor assigned to this report

    def save(self) -> bool:
        """Saves a new health report or updates an existing one in the database."""
        if not self.report_id:
            return False  # Cannot save without a report_id
            # Check if report exists to decide between INSERT and UPDATE
        try:
            existing_report = DBManager.fetch_one("SELECT report_id FROM health_reports WHERE report_id = ?", (self.report_id,))

            if existing_report:
                query = """
                    UPDATE health_reports
                    SET patient_id = ?, uploaded_by = ?, report_type = ?, upload_date = ?,
                    file_name = ?, file_path = ?, file_type = ?, extracted_data_json = ?, processing_status = ?,assigned_doctor_id = ?
                    WHERE report_id = ?
                """
                params = (self.patient_id, self.uploaded_by, self.report_type, self.upload_date,
                          self.file_name, self.file_path, self.file_type, self.extracted_data_json,
                          self.processing_status, self.assigned_doctor_id, self.report_id)
            else: # Insert new report
                query = """
                    INSERT INTO health_reports (report_id, patient_id, uploaded_by, report_type,
                                                upload_date, file_name, file_type, file_path, extracted_data_json, processing_status, assigned_doctor_id)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """
                params = (self.report_id, self.patient_id, self.uploaded_by, self.report_type,
                          self.upload_date, self.file_name, self.file_type, self.file_path, self.extracted_data_json, self.processing_status, self.assigned_doctor_id)
                
            print(f"Saving report to DB with report_id = {self.report_id}")
            print("SQL params:", params)

            success = DBManager.execute_query(query, params)

            if success:
                print("✅ Report saved.")
            else:
                print("❌ DBManager returned False")

            return success
        except Exception as e:
                    print(f"❌ Exception in HealthReport.save(): {e}")
                    import traceback
                    traceback.print_exc()
                    return False
        #     return DBManager.execute_query(query, params)
        # return False
    
    @staticmethod
    def upload_new_report(patient_id, uploaded_by, uploaded_file, report_type, description=None):
        from services.document_parser import DocumentParser
        """
        Handles saving the uploaded file, extracting metrics,
        and saving the full report with extracted data to the database.
        """
        try:
            # uploads_dir = "uploads"
            # os.makedirs(uploads_dir, exist_ok=True)

            file_id = str(uuid.uuid4())
            file_name = uploaded_file.name
            file_path = os.path.join(UPLOAD_DIR, f"{file_id}_{file_name}")

            # Save uploaded file to disk
            with open(file_path, "wb") as f:
                f.write(uploaded_file.getbuffer())
                print(f"✅ File saved to: {file_path}")
            
            # # Extract metrics and patient info
            # file_type = file_name.split('.')[-1].lower()  # Get file type from name
            # extracted = DocumentParser.parse_report(file_path)
            # # Debug print
            # print("📊 Extracted data from parser:", extracted)
            # if extracted is None:
            #     print("⚠️ DocumentParser returned None")
            # elif isinstance(extracted, dict):
            #     print("✅ Parsing succeeded with keys:", list(extracted.keys()))
            # else:
            #     print("⚠️ Unexpected format of extracted data:", type(extracted))

            # extracted_json = json.dumps(extracted, indent=2)

 # Only create an entry with minimal info
            report = HealthReport(
                patient_id=patient_id,
                uploaded_by=uploaded_by,
                report_type=report_type,
                file_name=file_name,
                file_path=file_path,
                file_type=file_name.split('.')[-1].lower(),  # Get file type from name
                extracted_data_json="{}",  # Start with empty JSON""
                processing_status="pending_extraction",  # Initial status
                assigned_doctor_id=None  # Default to None, can be updated later
            )

            if report.save():
                print(f"Triggering document processing pipeline for report {report.report_id}...")
                from services.document_parser import DocumentParser # Lazy import
                # Process the report to extract data and metrics
                DocumentParser.process_report_pipeline(report.report_id)
                print("✅ Report uploaded and saved successfully.")
                # Return True to indicate successful upload and trigger auto-allocation
                return True # Indicate successful upload and trigger
            else:
                print("❌ Failed to save report to database.")
                return False
            
        
        except Exception as e:
            print(f"❌ Upload failed: {e}")
            import traceback
            traceback.print_exc()
            return False
        
    @staticmethod
    def find_by_id(report_id: str):
        """Finds a health report by its report_id."""
        report_data = DBManager.fetch_one("SELECT * FROM health_reports WHERE report_id = ?", (report_id,))
        if report_data:
            # Convert extracted_data_json back to dict when loading
            report_data_dict = dict(report_data) # Convert Row object to dict first
            report_data_dict['extracted_data_json'] = json.loads(report_data_dict['extracted_data_json']) if report_data_dict['extracted_data_json'] else {}
            return HealthReport(**report_data_dict)
        return None

    @staticmethod
    def find_by_patient_id(patient_id: str):
        """Finds all health reports for a given patient_id."""
        reports_data = DBManager.fetch_all("SELECT * FROM health_reports WHERE patient_id = ? ORDER BY upload_date DESC", (patient_id,))
        if reports_data:
            report_objects = []
            for report in reports_data:
                report_dict = dict(report) # Convert Row object to dict
                report_dict['extracted_data_json'] = json.loads(report_dict['extracted_data_json']) if report_dict['extracted_data_json'] else {}
                report_objects.append(HealthReport(**report_dict))
            return report_objects
        return []
    
    @staticmethod
    def find_by_status(status: str):
        """Fetch all reports with a specific processing status."""
        query = "SELECT * FROM health_reports WHERE processing_status = ? ORDER BY upload_date DESC"
        result = DBManager.fetch_all(query, (status,))
        reports = []
        for row in result:
            row_dict = dict(row)
            # Convert extracted_data_json from string to dict
            row_dict['extracted_data_json'] = json.loads(row_dict['extracted_data_json']) if row_dict['extracted_data_json'] else {}
            reports.append(HealthReport(**row_dict))
        return reports
    
    @staticmethod
    def get_by_report_id(report_id: str) -> 'HealthReport':
        """Find a single health report by its report ID."""
        query = "SELECT * FROM health_reports WHERE report_id = ?"
        report_data = DBManager.fetch_one(query, (report_id,))
        if report_data:
            report_dict = dict(report_data)
            report_dict['extracted_data_json'] = json.loads(report_dict['extracted_data_json']) if report_dict['extracted_data_json'] else {}
            return HealthReport(**report_dict)
        return None

    @staticmethod
    def get_reports_by_patient(patient_id: str) -> list['HealthReport']:
        """Return all health reports for a given patient ID, sorted by upload date."""
        query = "SELECT * FROM health_reports WHERE patient_id = ? ORDER BY upload_date DESC"
        reports_data = DBManager.fetch_all(query, (patient_id,))
        report_objects = []
        for report in reports_data:
            report_dict = dict(report)
            report_dict['extracted_data_json'] = json.loads(report_dict['extracted_data_json']) if report_dict['extracted_data_json'] else {}
            report_objects.append(HealthReport(**report_dict))
        return report_objects
    #Auto-allocation will save assigned_doctor_id to the health_reports table
    # so we can retrieve reports by assigned doctor later.

    def update(self) -> bool:
        """Updates the entire HealthReport record in the database."""
        query = """
            UPDATE health_reports
            SET patient_id = ?, uploaded_by = ?, report_type = ?, file_type = ?,
                upload_date = ?, file_name = ?, file_path = ?, extracted_data_json = ?,
                processing_status = ?, assigned_doctor_id = ?
            WHERE report_id = ?
        """
        params = (
            self.patient_id,
            self.uploaded_by,
            self.report_type,
            self.file_type,
            self.upload_date,
            self.file_name,
            self.file_path,
            self.extracted_data_json,
            self.processing_status,
            self.assigned_doctor_id,
            self.report_id
        )
        return DBManager.execute_query(query, params)

    def update_processing_status(self, new_status: str) -> bool:
        self.processing_status = new_status
        query = "UPDATE health_reports SET processing_status = ? WHERE report_id = ?"
        return DBManager.execute_query(query, (self.processing_status, self.report_id))

    def update_extracted_data(self, extracted_data: dict) -> bool:
        self.extracted_data_json = json.dumps(extracted_data)
        self.processing_status = 'extracted' # Update status after extraction
        # The assigned_doctor_id is part of the `save()` method's UPDATE.
        # Calling save() will update all fields, including extracted_data_json and status.
        query = "UPDATE health_reports SET extracted_data_json = ?, processing_status = ?, assigned_doctor_id = ? WHERE report_id = ?"
        return DBManager.execute_query(query, (self.extracted_data_json, self.processing_status, self.assigned_doctor_id, self.report_id))
    
    @staticmethod
    def get_reports_by_assigned_doctor(doctor_id: str) -> list['HealthReport']:
        """
        Retrieves all health reports explicitly assigned to a given doctor.
        """
        query = "SELECT * FROM health_reports WHERE assigned_doctor_id = ? ORDER BY upload_date DESC"
        reports_data = DBManager.fetch_all(query, (doctor_id,))
        if reports_data:
            report_objects = []
            for row in reports_data:
                row_dict = dict(row)
                row_dict['extracted_data_json'] = json.loads(row_dict['extracted_data_json']) if row_dict['extracted_data_json'] else {}
                report_objects.append(HealthReport(**row_dict))
            return report_objects
        return []
    

    def get_extracted_data(self) -> dict:
        """Returns the extracted data as a Python dictionary."""
        return json.loads(self.extracted_data_json) if self.extracted_data_json else {}
    
    def get_recommendation(self):
        from models.recommendation import Recommendation
        """Returns the associated recommendation for this report, if it exists."""
        return Recommendation.find_by_report_id(self.report_id)

    def to_dict(self):
        return {
            "report_id": self.report_id,
            "patient_id": self.patient_id,
            "uploaded_by": self.uploaded_by,
            "report_type": self.report_type,
            "file_type": self.file_type,
            "upload_date": self.upload_date,
            "file_name": self.file_name,
            "file_path": self.file_path,
            "extracted_data_json": json.loads(self.extracted_data_json) if self.extracted_data_json else {},
            "processing_status": self.processing_status,
            "assigned_doctor_id": self.assigned_doctor_id
        }