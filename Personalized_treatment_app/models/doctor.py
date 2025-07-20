# models/doctor.py
import uuid
from database.db_utils import DBManager

    
class Doctor:
    def __init__(self, doctor_id: str, user_id: str, medical_license_number: str = None, specialization: str = None, contact_number: str = None, hospital_affiliation: str = None, is_available: int = 1, last_assignment_date: str = None):
        self.doctor_id = doctor_id
        self.user_id = user_id
        self.medical_license_number = medical_license_number
        self.specialization = specialization
        self.contact_number = contact_number
        self.hospital_affiliation = hospital_affiliation
        self.is_available = is_available
        self.last_assignment_date = last_assignment_date # This will be ISO format string

    from models.health_report import HealthReport
    from models.patient_doctor_mapping import PatientDoctorMapping # Importing the mapping model
    from models.patient import Patient # Importing Patient model for type hinting
    from models.recommendation import Recommendation # Importing Recommendation model for type hinting


    @classmethod
    def create(cls, user_id: str, medical_license_number: str = None, specialization: str = None, contact_number: str = None, hospital_affiliation: str = None, is_available: int = 1, last_assignment_date: str = None) -> 'Doctor':
      
        # Check for duplicate license
        from database.db_utils import DBManager
        existing = DBManager.fetch_one("SELECT * FROM doctors WHERE medical_license_number = ?", (medical_license_number,))
        if existing:
            return None, "duplicate_license" # Prevent duplicate license numbers

        doctor_id = str(uuid.uuid4())
        query ="""
        INSERT INTO doctors 
                (doctor_id, 
                user_id,
                medical_license_number,
                specialization,
                contact_number,
                hospital_affiliation,
                is_available,
                last_assignment_date) 
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)"""
        success = DBManager.execute_query(query, (doctor_id, user_id, medical_license_number, specialization, contact_number, hospital_affiliation, is_available, last_assignment_date))
        if success:
            print(f"Doctor record created for user {user_id}.")
            return cls(doctor_id, user_id, medical_license_number, specialization, contact_number, hospital_affiliation, is_available, last_assignment_date)
        return None,"database_error"
       
    @classmethod
    def get_by_doctor_id(cls, doctor_id: str) -> 'Doctor':
        query = "SELECT * FROM doctors WHERE doctor_id = ?"
        doctor_data = DBManager.fetch_one(query, (doctor_id,))
        if doctor_data:
            return cls(**doctor_data)
        return None

    @classmethod
    def get_by_user_id(cls, user_id: str) -> 'Doctor':
        query = "SELECT * FROM doctors WHERE user_id = ?"
        doctor_data = DBManager.fetch_one(query, (user_id,))
        if doctor_data:
            return cls(**doctor_data)
        return None
    @classmethod
    def get_all_doctors(cls) -> list['Doctor']:
        """Fetches all doctors from the database."""
        query = "SELECT * FROM doctors"
        doctors_data = DBManager.fetch_all(query)
        if doctors_data:
            return [cls(**data) for data in doctors_data]
        return []

    @classmethod
    def get_available_doctors_by_specialization(cls, specialization: str) -> list['Doctor']:
        """
        Fetches available doctors matching a specific specialization,
        ordered by last assignment date (oldest first for workload balancing).
        """
        query = """
            SELECT * FROM doctors
            WHERE specialization = ? AND is_available = 1
            ORDER BY last_assignment_date ASC NULLS FIRST -- NULLS FIRST puts unassigned doctors first
        """
        doctors_data = DBManager.fetch_all(query, (specialization,))
        if doctors_data:
            return [cls(**data) for data in doctors_data]
        return []

    def update(self) -> bool:
        """Updates an existing doctor's record."""
        query = """
            UPDATE doctors SET 
            medical_license_number = ?, 
            specialization = ?, 
            contact_number = ?, 
            hospital_affiliation = ?,
            is_available = ?,
            last_assignment_date = ?
            WHERE doctor_id = ?
        """
        return DBManager.execute_query(
            query,
            (self.medical_license_number, self.specialization, self.contact_number, self.hospital_affiliation, self.is_available, self.last_assignment_date, self.doctor_id)
        )

    def delete(self) -> bool:
        query = "DELETE FROM doctors WHERE doctor_id = ?"
        return DBManager.execute_query(query, (self.doctor_id,))

    def get_assigned_patients(self) -> list['Patient']:

        from models.patient_doctor_mapping import PatientDoctorMapping
        """
        Retrieves a list of Patient objects that are currently assigned to this doctor.
        Delegates to PatientDoctorMapping model.
        """
       
        return PatientDoctorMapping.get_patients_for_doctor(self.doctor_id)

    def get_pending_reviews(self) -> list['Recommendation']:
        """
        Retrieves a list of Recommendation objects that are pending review by this doctor.
        Delegates to Recommendation model.
        """
        from models.recommendation import Recommendation # Lazy import
        return Recommendation.get_pending_for_doctor(self.doctor_id)

    def get_reports_assigned_to_me(self) -> list['HealthReport']:
        """
        Retrieves a list of HealthReport objects directly assigned to this doctor.
        This is distinct from pending recommendations if reports can be assigned without immediate recommendations.
        """
        from models.health_report import HealthReport # Lazy import
        return HealthReport.get_reports_by_assigned_doctor(self.doctor_id)