# services/auto_allocator.py
import datetime
import os

from streamlit import success


   # Assuming recommendations are created after AI analysis
    


def auto_assign_doctor(report_id: str) -> bool:
    from models.health_report import HealthReport
    from models.doctor import Doctor
    from models.report_specialist_mapping import ReportSpecialistMapping
    from models.recommendation import Recommendation 
    from models.patient_doctor_mapping import PatientDoctorMapping
   
    """
    Automates the assignment of a doctor to a health report based on its type and doctor availability/specialization.
    This function should be called after a report's data has been extracted.
    It updates the HealthReport with the assigned doctor and creates a PatientDoctorMapping.
    Returns the doctor_id of the assigned doctor, or None if no doctor could be assigned.
    """
    print(f"Auto-assigning doctor for report {report_id}...")
    
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

             # Ensure patient-doctor mapping exists
            PatientDoctorMapping.create(report.patient_id, assigned_doctor.doctor_id)
           
               # ✅ Add patient-doctor mapping if not exists
            existing_mapping = PatientDoctorMapping.find_active_mapping(report.patient_id, assigned_doctor.doctor_id)
            if not existing_mapping:
                print(f"Creating patient-doctor mapping: patient={report.patient_id}, doctor={assigned_doctor.doctor_id}")
                mapping = PatientDoctorMapping(patient_id=report.patient_id, doctor_id=assigned_doctor.doctor_id)
                mapping_success = mapping.save()
                print(f"✅ Patient-doctor mapping created: {mapping.patient_id} -> {mapping.doctor_id}")
                if mapping_success:
                    print(f"✅ Mapping saved for patient {report.patient_id} and doctor {assigned_doctor.doctor_id}")
                else:
                    print("❌ Failed to save patient-doctor mapping")
            else:
                print("Active mapping already exists.")

            # If a recommendation already exists for this report (e.g., from AI),
            # link the doctor to it if it's currently unassigned or pending review.

            # # Handle recommendation assignment
            # # This assumes a recommendation exists for the report, which should be the case after AI generation.
            # recommendation = Recommendation.find_by_report_id(report_id)
            # if recommendation:
            #     if recommendation.doctor_id is None or recommendation.status == 'AI_generated':
            #         recommendation.update_status(
            #             new_status='pending_doctor_review',
            #             doctor_id=assigned_doctor.doctor_id)
            #     print(f"Auto-allocation: Recommendation for report {report_id} linked to doctor {assigned_doctor.doctor_id} and status updated to 'pending_doctor_review'.")

            # else:
            #     # Recommendation doesn't exist, create one with doctor assigned
            #     Recommendation.create(
            #         report_id=report.report_id,
            #         patient_id=report.patient_id,
            #         doctor_id=assigned_doctor.doctor_id,
            #         ai_generated_treatment="Auto-generated treatment",
            #         ai_generated_lifestyle="Auto-generated lifestyle",
            #         ai_generated_priority="Medium",
            #         status="pending_doctor_review"
            #     )
            #     print(f"Created new recommendation for report {report.report_id} with doctor {assigned_doctor.doctor_id}.")

            print(f"Auto-allocation complete for report {report_id}.")
            return True
        else:
            print(f"Auto-allocation: Failed to update report {report_id} with assigned doctor.")
            return False
    return False

# Example of how you might populate report_specialist_mapping (run once or from admin interface)
def populate_default_specialist_mappings():
    from models.report_specialist_mapping import ReportSpecialistMapping
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
        print("All default mappings already exist or were added successfully.")