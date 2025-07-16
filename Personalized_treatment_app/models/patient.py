# models/patient.py
import uuid
from database.db_utils import DBManager

class Patient:
    def __init__(self, patient_id: str, user_id: str, date_of_birth: str = None, gender: str = None, contact_number: str = None, address: str = None):
        self.patient_id = patient_id
        self.user_id = user_id
        self.date_of_birth = date_of_birth
        self.gender = gender
        self.contact_number = contact_number
        self.address = address

    @classmethod
    def create(cls, user_id: str, date_of_birth: str = None, gender: str = None, contact_number: str = None, address: str = None) -> 'Patient':
        patient_id = str(uuid.uuid4())
        query = "INSERT INTO patients (patient_id, user_id, date_of_birth, gender, contact_number, address) VALUES (?, ?, ?, ?, ?, ?)"
        success = DBManager.execute_query(query, (patient_id, user_id, date_of_birth, gender, contact_number, address))
        if success:
            print(f"Patient record created for user {user_id}.")
            return cls(patient_id, user_id, date_of_birth, gender, contact_number, address)
        return None

    @classmethod
    def get_by_patient_id(cls, patient_id: str) -> 'Patient':
        query = "SELECT * FROM patients WHERE patient_id = ?"
        patient_data = DBManager.fetch_one(query, (patient_id,))
        if patient_data:
            return cls(**patient_data)
        return None

    @classmethod
    def get_by_user_id(cls, user_id: str) -> 'Patient':
        query = "SELECT * FROM patients WHERE user_id = ?"
        patient_data = DBManager.fetch_one(query, (user_id,))
        if patient_data:
            return cls(**patient_data)
        return None

    def update(self) -> bool:
        query = """
            UPDATE patients SET date_of_birth = ?, gender = ?, contact_number = ?, address = ?
            WHERE patient_id = ?
        """
        return DBManager.execute_query(
            query,
            (self.date_of_birth, self.gender, self.contact_number, self.address, self.patient_id)
        )

    def delete(self) -> bool:
        query = "DELETE FROM patients WHERE patient_id = ?"
        return DBManager.execute_query(query, (self.patient_id,))

    def get_all_reports(self):
        # This will be implemented in health_report.py but called from here for an object-oriented feel
        # You'll need to create models/health_report.py later
        from models.health_report import HealthReport # Import locally to avoid circular dependency
        return HealthReport.find_by_patient_id(self.patient_id)

    def get_approved_recommendations(self):
        # This will be implemented in recommendation.py
        # You'll need to create models/recommendation.py later
        from models.recommendation import Recommendation
        return Recommendation.get_approved_for_patient(self.user_id)