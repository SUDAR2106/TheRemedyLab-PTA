# services/auto_allocator.py
import datetime
import os
from models.health_report import HealthReport
from models.doctor import Doctor
from models.report_specialist_mapping import ReportSpecialistMapping
from models.recommendation import Recommendation # Assuming recommendations are created after AI analysis
from models.patient_doctor_mapping import PatientDoctorMapping

def auto_assign_doctor(report_id: str) -> bool:
    """
    Automates the assignment of a doctor to a health report based on its type and doctor availability.
    This function should be called after a report's data has been 'extracted'.
    """
    report = HealthReport.get_by_report_id(report_id)
    if not report:
        print(f"Auto-allocation: Report with ID {report_id} not found.")
        return False
    
    if report.assigned_doctor_id:
        print(f"Auto-allocation: Report {report_id} already has an assigned doctor.")
        return True # Already assigned, nothing to do

    print(f"Auto-allocation: Starting for report '{report.file_name}' (ID: {report_id})")

    # 1. Determine required specialization from report type
    required_specialization = ReportSpecialistMapping.get_specialization_by_report_type(report.report_type)

    if not required_specialization:
        print(f"Auto-allocation: No specific specialization mapping found for report type '{report.report_type}'. Skipping auto-allocation.")
        # Consider a fallback here, e.g., assign to a general pool or flag for manual assignment
        return False

    print(f"Auto-allocation: Required specialization for '{report.report_type}' is '{required_specialization}'.")

    # 2. Select a suitable doctor
    # Get available doctors matching the specialization, sorted by last assignment date
    available_doctors = Doctor.get_available_doctors_by_specialization(required_specialization)

    assigned_doctor = None
    if available_doctors:
        # Simple selection: pick the first available doctor (who has the oldest last assignment date or is unassigned)
        assigned_doctor = available_doctors[0]
        print(f"Auto-allocation: Found suitable doctor {assigned_doctor.user_id} (ID: {assigned_doctor.doctor_id}) with specialization '{assigned_doctor.specialization}'.")
    else:
        print(f"Auto-allocation: No available doctor found for specialization '{required_specialization}'.")
        # Fallback: Flag for manual assignment, or assign to a default doctor/admin for triage
        report.processing_status = 'pending_manual_assignment' # A new status for this case
        report.update()
        print(f"Auto-allocation: Report {report_id} flagged for manual assignment due to no available doctors.")
        return False

    # 3. Assign the doctor to the report and update doctor's last assignment time
    if assigned_doctor:
        report.assigned_doctor_id = assigned_doctor.doctor_id
        
        # Update the report's processing status if it was extracted and not pending manual assignment
        # This is where you might set it to 'assigned_to_doctor' or keep 'extracted' and let recommendation status drive
        # For now, let's just ensure the assigned_doctor_id is set and status remains 'extracted' before AI.
        
        if report.update():
            # Update doctor's last assignment date
            assigned_doctor.last_assignment_date = datetime.datetime.now(datetime.timezone.utc).isoformat()
            assigned_doctor.update()

               # ✅ Add patient-doctor mapping if not exists
            existing_mapping = PatientDoctorMapping.find_active_mapping(report.patient_id, assigned_doctor.doctor_id)
            if not existing_mapping:
                print(f"Creating patient-doctor mapping: patient={report.patient_id}, doctor={assigned_doctor.doctor_id}")
                mapping = PatientDoctorMapping(patient_id=report.patient_id, doctor_id=assigned_doctor.doctor_id)
                mapping.save()
            else:
                print("Active mapping already exists.")

            # If a recommendation already exists for this report (e.g., from AI),
            # link the doctor to it if it's currently unassigned or pending review.
            
            recommendation = Recommendation.find_by_report_id(report_id)
            if recommendation and (recommendation.doctor_id is None or recommendation.status == 'AI_generated'):
                recommendation.doctor_id = assigned_doctor.doctor_id
                recommendation.status = 'pending_doctor_review' # Set status to indicate it's assigned for review
                recommendation.update()
                print(f"Auto-allocation: Recommendation for report {report_id} linked to doctor {assigned_doctor.doctor_id} and status updated to 'pending_doctor_review'.")

            print(f"Auto-allocation: Doctor {assigned_doctor.user_id} successfully assigned to report {report_id}.")
            return True
        else:
            print(f"Auto-allocation: Failed to update report {report_id} with assigned doctor.")
            return False
    return False

# Example of how you might populate report_specialist_mapping (run once or from admin interface)
def populate_default_specialist_mappings():
    mappings = {
        "Blood Test": "General Physician",
        "X-Ray": "Radiologist",
        "MRI Scan": "Radiologist",
        "Cardiology Report": "Cardiologist",
        "Neurology Report": "Neurologist",
        "General Checkup": "General Physician",
        "Diabetes Report": "Endocrinologist",
        "Liver Function Test": "Hepatologist",
        "Kidney Function Test": "Nephrologist",
        "lipid_profile": "General Physician",
        "thyroid_function_test": "Endocrinologist",
        "eye_test": "Ophthalmologist",
        "hearing_test": "ENT Specialist",
        "others test": "General Physician",  # Fallback for unclassified tests
        "urine_test": "Nephrologist",  # Example for urine tests
        "stool_test": "Gastroenterologist",  # Example for stool tests
        # Add more as needed
    }
    for report_type, specialization in mappings.items():
        if not ReportSpecialistMapping.get_specialization_by_report_type(report_type):
            ReportSpecialistMapping.create(report_type, specialization)
            print(f"Added mapping: {report_type} -> {specialization}")
        else:
            print(f"Mapping already exists for {report_type}.")

# # For testing outside the main app flow (optional)
# if __name__ == '__main__':
#     from database.db_utils import DBManager
#     DBManager.init_db() # Initialize DB for testing

#     # Populate mappings first time
#     populate_default_specialist_mappings()

#     # --- Create Dummy Data for Testing Auto-Allocation ---
#     from models.user import User
#     from models.patient import Patient
#     from models.doctor import Doctor
#     import json

#     # Create a dummy patient and doctor if they don't exist
#     test_patient_user = User.get_by_username("alloc_patient")
#     if not test_patient_user:
#         test_patient_user = User.create("alloc_patient", "password", "patient", "Alloc", "Patient", "allocp@example.com")
#         test_patient = Patient.create(test_patient_user.user_id, "2000-01-01", "Male", "1112223333", "123 Test St")
#     else:
#         test_patient = Patient.get_by_user_id(test_patient_user.user_id)

#     test_doc_user_gp = User.get_by_username("gp_doctor")
#     if not test_doc_user_gp:
#         test_doc_user_gp = User.create("gp_doctor", "password", "doctor", "Dr.", "GP", "gp@example.com")
#         test_doctor_gp = Doctor.create(test_doc_user_gp.user_id, "General Physician", "GP123", "9998887777", "City Hospital", is_available=1)
#     else:
#         test_doctor_gp = Doctor.get_by_user_id(test_doc_user_gp.user_id)
#         if test_doctor_gp: test_doctor_gp.is_available = 1; test_doctor_gp.update() # Ensure available

#     test_doc_user_rad = User.get_by_username("rad_doctor")
#     if not test_doc_user_rad:
#         test_doc_user_rad = User.create("rad_doctor", "password", "doctor", "Dr.", "Rad", "rad@example.com")
#         test_doctor_rad = Doctor.create(test_doc_user_rad.user_id, "Radiologist", "RAD456", "1112223333", "Imaging Center", is_available=1)
#     else:
#         test_doctor_rad = Doctor.get_by_user_id(test_doc_user_rad.user_id)
#         if test_doctor_rad: test_doctor_rad.is_available = 1; test_doctor_rad.update() # Ensure available

#     # Create dummy health reports with 'extracted' status
#     if test_patient:
#         print("\n--- Testing Auto-Allocation ---")
        
#         # Report 1: General Checkup (should go to GP)
#         report1_path = os.path.join("uploads", "general_checkup.txt")
#         os.makedirs(os.path.dirname(report1_path), exist_ok=True)
#         with open(report1_path, "w") as f:
#             f.write("General checkup results: All good.")
        
#         report1 = HealthReport.create(
#             test_patient.patient_id, "general_checkup.txt", report1_path,
#             "txt", "General Checkup", "extracted", json.dumps({"overall_health": "good"})
#         )
#         if report1:
#             print(f"Created Report 1: {report1.report_id}")
#             auto_assign_doctor(report1.report_id)
#             updated_report1 = HealthReport.get_by_report_id(report1.report_id)
#             print(f"Report 1 assigned to doctor: {updated_report1.assigned_doctor_id}")
#             # Ensure a recommendation exists for auto-assignment to update it
#             Recommendation.create(report1.report_id, report1.patient_id, None, "AI Gen Treatment GP", "AI Gen Lifestyle GP", "Medium", "AI_generated")


#         # Report 2: X-Ray (should go to Radiologist)
#         report2_path = os.path.join("uploads", "xray_results.txt")
#         with open(report2_path, "w") as f:
#             f.write("X-Ray results: Bone fracture detected.")
        
#         report2 = HealthReport.create(
#             test_patient.patient_id, "xray_results.txt", report2_path,
#             "txt", "X-Ray", "extracted", json.dumps({"findings": "fracture"})
#         )
#         if report2:
#             print(f"Created Report 2: {report2.report_id}")
#             auto_assign_doctor(report2.report_id)
#             updated_report2 = HealthReport.get_by_report_id(report2.report_id)
#             print(f"Report 2 assigned to doctor: {updated_report2.assigned_doctor_id}")
#             # Ensure a recommendation exists for auto-assignment to update it
#             Recommendation.create(report2.report_id, report2.patient_id, None, "AI Gen Treatment Rad", "AI Gen Lifestyle Rad", "High", "AI_generated")

#         # Report 3: Unknown Type (should not be assigned)
#         report3_path = os.path.join("uploads", "unknown_report.txt")
#         with open(report3_path, "w") as f:
#             f.write("This is an unknown report type.")
        
#         report3 = HealthReport.create(
#             test_patient.patient_id, "unknown_report.txt", report3_path,
#             "txt", "Unknown Type", "extracted", json.dumps({"info": "unknown"})
#         )
#         if report3:
#             print(f"Created Report 3: {report3.report_id}")
#             auto_assign_doctor(report3.report_id)
#             updated_report3 = HealthReport.get_by_report_id(report3.report_id)
#             print(f"Report 3 assigned to doctor: {updated_report3.assigned_doctor_id}") # Should be None

#     print("\n--- Auto-Allocation Testing Complete ---")