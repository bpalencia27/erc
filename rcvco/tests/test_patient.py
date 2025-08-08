"""
Core functionality tests for RCV-CO system
"""
import unittest
from datetime import datetime
from rcvco.models.patient import Patient

class TestPatient(unittest.TestCase):
    """Test cases for Patient model"""
    
    def setUp(self):
        """Set up test data"""
        self.patient_data = {
            "id": 1,
            "document_type": "CC",
            "document_number": "123456789",
            "first_name": "John",
            "last_name": "Doe",
            "date_of_birth": datetime(1980, 1, 1),
            "gender": "M",
            "ethnicity": "non_black",
            "email": "john.doe@example.com",
            "phone": "1234567890",
            "address": "123 Main St"
        }
        self.patient = Patient(**self.patient_data)
    
    def test_patient_creation(self):
        """Test patient object creation"""
        self.assertEqual(self.patient.id, 1)
        self.assertEqual(self.patient.document_type, "CC")
        self.assertEqual(self.patient.document_number, "123456789")
        self.assertEqual(self.patient.first_name, "John")
        self.assertEqual(self.patient.last_name, "Doe")
    
    def test_full_name(self):
        """Test full_name property"""
        self.assertEqual(self.patient.full_name, "John Doe")
    
    def test_age_calculation(self):
        """Test age calculation"""
        current_year = datetime.now().year
        expected_age = current_year - 1980
        # Adjust for birth date not reached this year
        if datetime.now().month < self.patient.date_of_birth.month or \
           (datetime.now().month == self.patient.date_of_birth.month and \
            datetime.now().day < self.patient.date_of_birth.day):
            expected_age -= 1
        self.assertEqual(self.patient.age, expected_age)
    
    def test_to_dict(self):
        """Test dictionary conversion"""
        patient_dict = self.patient.to_dict()
        self.assertEqual(patient_dict["id"], 1)
        self.assertEqual(patient_dict["document_type"], "CC")
        self.assertEqual(patient_dict["document_number"], "123456789")
        self.assertTrue(isinstance(patient_dict["created_at"], str))
        self.assertTrue(isinstance(patient_dict["updated_at"], str))
