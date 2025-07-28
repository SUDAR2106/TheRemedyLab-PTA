
import uuid
import datetime
from database.db_utils import DBManager

class Recommendation:
    def __init__(self, recommendation_id: str, report_id: str, patient_id: str,
                 ai_generated_treatment: str = None, ai_generated_lifestyle: str = None,
                 ai_generated_priority: str = None, doctor_id: str = None,
                 doctor_notes: str = None, status: str = 'AI_generated',
                 reviewed_date: str = None, approved_treatment: str = None,
                 approved_lifestyle: str = None, created_at: str = None,
                 last_updated_at: str = None):
        self.recommendation_id = recommendation_id
        self.report_id = report_id
        self.patient_id = patient_id
        self.ai_generated_treatment = ai_generated_treatment
        self.ai_generated_lifestyle = ai_generated_lifestyle
        self.ai_generated_priority = ai_generated_priority
        self.doctor_id = doctor_id
        self.doctor_notes = doctor_notes
        self.status = status
        self.reviewed_date = reviewed_date
        self.approved_treatment = approved_treatment
        self.approved_lifestyle = approved_lifestyle
        self.created_at = created_at or datetime.datetime.now(datetime.timezone.utc).isoformat()
        self.last_updated_at = last_updated_at or datetime.datetime.now(datetime.timezone.utc).isoformat()

    @classmethod
    def create(cls, report_id: str, patient_id: str, doctor_id: str,  # doctor_id can be None
            ai_generated_treatment: str, ai_generated_lifestyle: str,
            ai_generated_priority: str, status: str = 'AI_generated') -> 'Recommendation':
        recommendation_id = str(uuid.uuid4())
        created_at = datetime.datetime.now(datetime.timezone.utc).isoformat()
        query = """
            INSERT INTO recommendations (recommendation_id, report_id, patient_id, doctor_id,
                                        ai_generated_treatment, ai_generated_lifestyle,
                                        ai_generated_priority, status, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """
        params = (recommendation_id, report_id, patient_id, doctor_id,
                ai_generated_treatment, ai_generated_lifestyle,
                ai_generated_priority, status, created_at)
        if DBManager.execute_query(query, params):
            return cls(recommendation_id, report_id, patient_id, doctor_id,
                    ai_generated_treatment, ai_generated_lifestyle,
                    ai_generated_priority, status, created_at)
        return None

    # @staticmethod
    # def get_by_id(recommendation_id: str) -> 'Recommendation':
    #     query = "SELECT * FROM recommendations WHERE recommendation_id = ?"
    #     rec_data = DBManager.fetch_one(query, (recommendation_id,))
    #     return Recommendation(**rec_data) if rec_data else None

    @staticmethod
    def find_by_report_id(report_id: str) -> 'Recommendation':
        query = "SELECT * FROM recommendations WHERE report_id = ?"
        rec_data = DBManager.fetch_one(query, (report_id,))
        return Recommendation(**rec_data) if rec_data else None

    @staticmethod
    def get_by_patient_id(patient_id: str) -> list['Recommendation']:
        query = "SELECT * FROM recommendations WHERE patient_id = ? ORDER BY created_at DESC"
        data = DBManager.fetch_all(query, (patient_id,))
        return [Recommendation(**rec) for rec in data] if data else []
    
    @staticmethod
    def get_pending_for_doctor(doctor_id: str) -> list['Recommendation']:
        """
        Returns all recommendations assigned to this doctor with status 'AI_generated'
        (i.e., pending doctor review).
        """
        query = """
            SELECT * FROM recommendations
            WHERE doctor_id = ? AND status = 'pending_doctor_review'
            ORDER BY created_at DESC
        """
        recs_data = DBManager.fetch_all(query, (doctor_id,))
        return [Recommendation(**rec) for rec in recs_data] if recs_data else []
    
    
    @staticmethod
    def get_reviewed_by_doctor(doctor_id: str):
        """
        Returns all recommendations reviewed by a specific doctor 
        (status: approved_by_doctor or modified_by_doctor).
        """
        query = """
            SELECT * FROM recommendations
            WHERE doctor_id = ? AND status IN ('approved_by_doctor', 'modified_and_approved_by_doctor', 'Consultation_required')
            ORDER BY reviewed_date DESC
        """
        results = DBManager.fetch_all(query, (doctor_id,))
        if results:
            return [Recommendation(**row) for row in results]
        return []
    @staticmethod
    def get_by_recommendation_id(recommendation_id: str) -> 'Recommendation':
        query = "SELECT * FROM recommendations WHERE recommendation_id = ?"
        rec_data = DBManager.fetch_one(query, (recommendation_id,))
        return Recommendation(**rec_data) if rec_data else None

    @staticmethod
    def get_approved_for_patient(patient_id: str) -> list[dict]:
        query = """
            SELECT 
                r.recommendation_id, r.report_id, r.patient_id,
                r.ai_generated_treatment, r.ai_generated_lifestyle, r.ai_generated_priority,
                r.doctor_id, r.doctor_notes, r.status, r.reviewed_date,
                r.approved_treatment, r.approved_lifestyle, r.created_at, r.last_updated_at,
                hr.file_name AS "Report Name",
                u.first_name AS doctor_first_name, u.last_name AS doctor_last_name
            FROM recommendations r
            JOIN health_reports hr ON r.report_id = hr.report_id
            LEFT JOIN doctors d ON r.doctor_id = d.doctor_id
            LEFT JOIN users u ON d.user_id = u.user_id
            WHERE r.patient_id = ? AND r.status IN ('approved_by_doctor', 'modified_and_approved_by_doctor')
            ORDER BY r.reviewed_date DESC
        """
        recs_data = DBManager.fetch_all(query, (patient_id,))
        for rec in recs_data or []:
            rec['Doctor Name'] = (
                f"Dr. {rec['doctor_first_name']} {rec['doctor_last_name']}"
                if rec['doctor_first_name'] and rec['doctor_last_name']
                else "N/A"
            )
        return recs_data or []

    def update_status(self, new_status: str, doctor_id: str = None, doctor_notes: str = None,
                      approved_treatment: str = None, approved_lifestyle: str = None) -> bool:
        self.status = new_status
        now = datetime.datetime.now(datetime.timezone.utc).isoformat()
        self.last_updated_at = now
        self.reviewed_date = now

        self.doctor_id = doctor_id or self.doctor_id
        self.doctor_notes = doctor_notes if doctor_notes is not None else self.doctor_notes
        self.approved_treatment = approved_treatment if approved_treatment is not None else self.approved_treatment
        self.approved_lifestyle = approved_lifestyle if approved_lifestyle is not None else self.approved_lifestyle

        query = """
            UPDATE recommendations
            SET status = ?, doctor_id = ?, doctor_notes = ?, 
                approved_treatment = ?, approved_lifestyle = ?, 
                reviewed_date = ?, last_updated_at = ?
            WHERE recommendation_id = ?
        """
        return DBManager.execute_query(query, (
            self.status, self.doctor_id, self.doctor_notes,
            self.approved_treatment, self.approved_lifestyle,
            self.reviewed_date, self.last_updated_at,
            self.recommendation_id
        ))
       
        # get doctor_id from logged-in user
        # if not self.doctor_id:
    # --- Approve the recommendation as-is without modifying treatment/lifestyle ---
    # This is a convenience method for doctors who want to approve the AI-generated recommendation without changes
   
    def approve(self, doctor_id: str, doctor_notes: str = "") -> bool:
        """
        Approves the recommendation as-is without modifying treatment/lifestyle.
        """
        return self.update_status(
            new_status="approved_by_doctor",
            doctor_id=doctor_id,
            doctor_notes=doctor_notes,
            approved_treatment=self.ai_generated_treatment,
            approved_lifestyle=self.ai_generated_lifestyle
        )
    
    # --- Modify the recommendation ---
    def modify_and_approve(self, doctor_id: str, approved_treatment: str, approved_lifestyle: str, doctor_notes: str = "") -> bool:
        """
        Allows the doctor to modify the treatment/lifestyle plan and approve the recommendation.
        """
        return self.update_status(
            new_status="modified_and_approved_by_doctor",
            doctor_id=doctor_id,
            doctor_notes=doctor_notes,
            approved_treatment=approved_treatment,
            approved_lifestyle=approved_lifestyle
        )
    
    def reject(self, doctor_id: str, doctor_notes: str = "") -> bool:
        """
        Rejects the AI-generated recommendations.
        """
        # When rejecting, clear approved treatment/lifestyle as they are not "approved"
        return self.update_status(
            new_status="Consultation_required",
            doctor_id=doctor_id,
            doctor_notes=doctor_notes,
            approved_treatment=None, # Clear any previous approved content
            approved_lifestyle=None  # Clear any previous approved content
        )


    def to_dict(self):
        return {
            "recommendation_id": self.recommendation_id,
            "report_id": self.report_id,
            "patient_id": self.patient_id,
            "ai_generated_treatment": self.ai_generated_treatment,
            "ai_generated_lifestyle": self.ai_generated_lifestyle,
            "ai_generated_priority": self.ai_generated_priority,
            "doctor_id": self.doctor_id,
            "doctor_notes": self.doctor_notes,
            "status": self.status,
            "reviewed_date": self.reviewed_date,
            "approved_treatment": self.approved_treatment,
            "approved_lifestyle": self.approved_lifestyle,
            "created_at": self.created_at,
            "last_updated_at": self.last_updated_at
        }
