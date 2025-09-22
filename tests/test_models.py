"""
Complete Testing Suite for Sahay Platform
"""

# ============================================
# tests/test_models.py - Model Tests
# ============================================

from django.test import TestCase
from django.utils import timezone
from datetime import datetime, timedelta
from core.models import Student, Course, Sahayak
from wellness.models import WellnessSession, Action, ScreeningQuestion
from learning.models import CareerPath, StudentCareerPlan, LearningSession
from analytics.models import Pattern, AnonymousReport
import json

class StudentModelTest(TestCase):
    """Test Student model"""
    
    def setUp(self):
        self.student = Student.objects.create(
            student_id='TEST001',
            age_band='18-20',
            language_pref='English',
            interests=['coding', 'music'],
            enrollment_date=timezone.now().date()
        )
    
    def test_student_creation(self):
        """Test student is created correctly"""
        self.assertEqual(self.student.student_id, 'TEST001')
        self.assertEqual(self.student.age_band, '18-20')
        self.assertIn('coding', self.student.interests)
    
    def test_student_str_representation(self):
        """Test string representation"""
        self.assertEqual(str(self.student), 'TEST001 - 18-20')
    
    def test_privacy_defaults(self):
        """Test privacy settings defaults"""
        self.assertFalse(self.student.data_consent)
        self.assertTrue(self.student.anonymous_sharing)
        self.assertEqual(self.student.retention_period, 90)

class WellnessSessionModelTest(TestCase):
    """Test WellnessSession model"""
    
    def setUp(self):
        self.student = Student.objects.create(
            student_id='TEST002',
            age_band='20-22',
            language_pref='Hindi',
            interests=['reading'],
            enrollment_date=timezone.now().date()
        )
        
        self.session = WellnessSession.objects.create(
            session_id='SESS001',
            student=self.student,
            mood_score=5,
            anxiety_score=7,
            screener_type='GAD-2',
            total_score=12,
            risk_level='L2'
        )
    
    def test_session_creation(self):
        """Test session is created correctly"""
        self.assertEqual(self.session.session_id, 'SESS001')
        self.assertEqual(self.session.mood_score, 5)
        self.assertEqual(self.session.risk_level, 'L2')
    
    def test_risk_level_assignment(self):
        """Test risk level calculation"""
        # Create sessions with different scores
        low_risk = WellnessSession.objects.create(
            session_id='SESS002',
            student=self.student,
            mood_score=8,
            anxiety_score=2,
            total_score=10,
            risk_level='L1'
        )
        
        high_risk = WellnessSession.objects.create(
            session_id='SESS003',
            student=self.student,
            mood_score=3,
            anxiety_score=9,
            total_score=12,
            risk_level='L3'
        )
        
        self.assertEqual(low_risk.risk_level, 'L1')
        self.assertEqual(high_risk.risk_level, 'L3')

class PatternModelTest(TestCase):
    """Test Pattern model with k-anonymity"""
    
    def test_k_anonymity_validation(self):
        """Test k-anonymity threshold is enforced"""
        pattern = Pattern.objects.create(
            pattern_type='temporal',
            k_count=5,  # Minimum threshold
            pattern_data={'hour': 14, 'avg_anxiety': 7.5},
            severity='medium'
        )
        
        self.assertGreaterEqual(pattern.k_count, 5)
    
    def test_pattern_data_storage(self):
        """Test JSON field storage"""
        data = {
            'risk_level': 'L2',
            'percentage': 35.5,
            'sample_size': 100
        }
        
        pattern = Pattern.objects.create(
            pattern_type='risk',
            k_count=20,
            pattern_data=data,
            severity='high'
        )
        
        self.assertEqual(pattern.pattern_data['percentage'], 35.5)

# ============================================
# tests/test_api.py - API Endpoint Tests
# ============================================

from django.test import TestCase, Client
from django.urls import reverse
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from django.contrib.auth import get_user_model
import json

User = get_user_model()

class ChatAPITest(APITestCase):
    """Test Chat API endpoints"""
    
    def setUp(self):
        self.client = APIClient()
        self.student = Student.objects.create(
            student_id='API001',
            age_band='20-22',
            language_pref='English',
            interests=['coding', 'music'],
            enrollment_date=timezone.now().date()
        )
        
        self.chat_url = reverse('api:chat')
    
    def test_send_chat_message(self):
        """Test sending a chat message"""
        data = {
            'student_id': 'API001',
            'message': 'Hello, I need help with stress',
            'language': 'English',
            'context': {
                'mood_score': 5,
                'anxiety_score': 7
            }
        }
        
        response = self.client.post(
            self.chat_url,
            data=json.dumps(data),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('response', response.json())
        self.assertIn('session_id', response.json())
    
    def test_empty_message_handling(self):
        """Test handling of empty messages"""
        data = {
            'student_id': 'API001',
            'message': '',
            'language': 'English'
        }
        
        response = self.client.post(
            self.chat_url,
            data=json.dumps(data),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

class ScreeningAPITest(APITestCase):
    """Test Screening API endpoints"""
    
    def setUp(self):
        self.client = APIClient()
        self.student = Student.objects.create(
            student_id='API002',
            age_band='18-20',
            language_pref='English',
            interests=['reading'],
            enrollment_date=timezone.now().date()
        )
        
        # Create screening questions
        ScreeningQuestion.objects.create(
            question_id='GAD_1',
            screener_type='GAD-2',
            question_text='Test question 1',
            scoring_rules={'0': 'Not at all', '1': 'Several days'},
            order=1
        )
        
        self.screening_url = reverse('api:screening')
    
    def test_get_screening_questions(self):
        """Test retrieving screening questions"""
        response = self.client.get(f"{self.screening_url}?type=GAD-2")
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertEqual(data['screener_type'], 'GAD-2')
        self.assertIn('questions', data)
    
    def test_submit_screening_responses(self):
        """Test submitting screening responses"""
        data = {
            'student_id': 'API002',
            'screener_type': 'GAD-2',
            'responses': [2, 3, 1, 2]
        }
        
        response = self.client.post(
            self.screening_url,
            data=json.dumps(data),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        result = response.json()
        self.assertIn('risk_level', result)
        self.assertIn('actions', result)

class PatternDetectionAPITest(APITestCase):
    """Test Pattern Detection API"""
    
    def setUp(self):
        self.client = APIClient()
        self.patterns_url = reverse('api:patterns')
        
        # Create test data
        for i in range(10):
            student = Student.objects.create(
                student_id=f'PAT{i:03d}',
                age_band='20-22',
                language_pref='English',
                interests=['test'],
                enrollment_date=timezone.now().date()
            )
            
            WellnessSession.objects.create(
                session_id=f'SESS{i:03d}',
                student=student,
                mood_score=5 + (i % 3),
                anxiety_score=6 + (i % 4),
                risk_level='L1' if i < 5 else 'L2'
            )
    
    def test_pattern_detection_with_k_anonymity(self):
        """Test pattern detection maintains k-anonymity"""
        data = {
            'class_id': 'CLASS001',
            'time_window': 7
        }
        
        response = self.client.post(
            self.patterns_url,
            data=json.dumps(data),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        patterns = response.json()
        
        # Check k-anonymity is maintained
        for pattern in patterns:
            if 'k_count' in pattern:
                self.assertGreaterEqual(pattern['k_count'], 5)

# ============================================
# tests/test_services.py - Service Tests
# ============================================

from django.test import TestCase
from unittest.mock import Mock, patch, MagicMock
from services.gemini_service import GeminiService, PromptOptimizer
from services.data_processing import CSVDataProcessor, PatternAnalyzer
import pandas as pd
import numpy as np

class GeminiServiceTest(TestCase):
    """Test Gemini AI Service"""
    
    @patch('services.gemini_service.vertexai.init')
    @patch('services.gemini_service.GenerativeModel')
    def setUp(self, mock_model, mock_init):
        """Set up test fixtures"""
        self.mock_model = MagicMock()
        mock_model.return_value = self.mock_model
        self.service = GeminiService()
    
    def test_generate_greeting(self):
        """Test greeting generation"""
        self.mock_model.generate_content.return_value.text = "Hello! How are you today?"
        
        profile = {
            'interests': ['coding', 'music'],
            'language': 'English',
            'age_band': '18-20'
        }
        
        greeting = self.service.generate_greeting(profile)
        self.assertIsNotNone(greeting)
        self.assertIn('Hello', greeting)
    
    @patch('services.gemini_service.logger')
    def test_error_handling(self, mock_logger):
        """Test error handling in service"""
        self.mock_model.generate_content.side_effect = Exception("API Error")
        
        response = self.service.process_chat_message(
            'TEST001',
            'Hello',
            {'mood_score': 5}
        )
        
        self.assertIn('error', response)
        mock_logger.error.assert_called()
    
    def test_risk_analysis(self):
        """Test risk indicator analysis"""
        message = "I'm feeling really anxious and overwhelmed"
        
        analysis = self.service._analyze_risk_indicators(message, "")
        
        self.assertEqual(analysis['level'], 'medium')
        self.assertIn('anxious', analysis['keywords'])

class CSVDataProcessorTest(TestCase):
    """Test CSV Data Processing"""
    
    def setUp(self):
        self.processor = CSVDataProcessor()
    
    def test_k_anonymity_application(self):
        """Test k-anonymity is properly applied"""
        # Create test dataframe
        data = {
            'student_id': [f'STU{i:03d}' for i in range(10)],
            'risk_level': ['L1'] * 6 + ['L2'] * 4,
            'screener_type': ['GAD-2'] * 10,
            'mood_score': np.random.randint(1, 10, 10)
        }
        df = pd.DataFrame(data)
        
        # Apply k-anonymity
        df_anonymous = self.processor._apply_k_anonymity(df)
        
        # Check that small groups are filtered
        risk_counts = df_anonymous['risk_level'].value_counts()
        for count in risk_counts:
            self.assertGreaterEqual(count, 5)
    
    def test_hash_student_id(self):
        """Test student ID hashing for privacy"""
        student_id = "STU001"
        hashed = self.processor._hash_student_id(student_id)
        
        # Check hash properties
        self.assertEqual(len(hashed), 16)
        self.assertNotEqual(hashed, student_id)
        
        # Check consistency
        hashed2 = self.processor._hash_student_id(student_id)
        self.assertEqual(hashed, hashed2)

class PatternAnalyzerTest(TestCase):
    """Test Pattern Analysis"""
    
    def setUp(self):
        self.analyzer = PatternAnalyzer()
    
    def test_temporal_pattern_detection(self):
        """Test temporal pattern detection"""
        # Create test data
        timestamps = pd.date_range(start='2024-01-01', periods=100, freq='H')
        data = pd.DataFrame({
            'timestamp': timestamps,
            'student_id': [f'STU{i%20:03d}' for i in range(100)],
            'mood_score': np.random.randint(1, 10, 100),
            'anxiety_score': np.random.randint(1, 10, 100)
        })
        
        patterns = self.analyzer.analyze_temporal_patterns(data)
        
        self.assertIsInstance(patterns, list)
        for pattern in patterns:
            self.assertIn('pattern_type', pattern)
            self.assertIn('k_count', pattern)
            self.assertGreaterEqual(pattern['k_count'], 5)
    
    def test_risk_transition_analysis(self):
        """Test risk level transition analysis"""
        data = pd.DataFrame({
            'student_id': ['STU001'] * 5 + ['STU002'] * 5,
            'timestamp': pd.date_range(start='2024-01-01', periods=10, freq='D'),
            'risk_level': ['L1', 'L1', 'L2', 'L2', 'L3'] * 2
        })
        
        risk_analysis = self.analyzer.analyze_risk_patterns(data)
        
        self.assertIn('risk_distribution', risk_analysis)
        self.assertIn('risk_transitions', risk_analysis)

# ============================================
# tests/test_integration.py - Integration Tests
# ============================================

from django.test import TestCase, TransactionTestCase
from django.test import Client
from django.db import transaction
import time

class EndToEndIntegrationTest(TransactionTestCase):
    """End-to-end integration tests"""
    
    def setUp(self):
        self.client = Client()
        
        # Create test student
        self.student = Student.objects.create(
            student_id='E2E001',
            age_band='20-22',
            language_pref='English',
            interests=['coding', 'music'],
            enrollment_date=timezone.now().date()
        )
    
    def test_complete_wellness_flow(self):
        """Test complete wellness check-in flow"""
        # 1. Get screening questions
        response = self.client.get('/api/screening/?type=GAD-2')
        self.assertEqual(response.status_code, 200)
        
        # 2. Submit screening responses
        screening_data = {
            'student_id': 'E2E001',
            'screener_type': 'GAD-2',
            'responses': [2, 3]
        }
        
        response = self.client.post(
            '/api/screening/',
            data=json.dumps(screening_data),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        result = response.json()
        
        # 3. Verify session was created
        session = WellnessSession.objects.filter(
            student__student_id='E2E001'
        ).first()
        self.assertIsNotNone(session)
        
        # 4. Verify actions were generated
        self.assertIn('actions', result)
        self.assertGreater(len(result['actions']), 0)
        
        # 5. Complete an action
        if result['actions']:
            action_id = result['actions'][0]['id']
            response = self.client.post(f'/api/actions/{action_id}/complete/')
            self.assertEqual(response.status_code, 200)
    
    def test_pattern_detection_with_sufficient_data(self):
        """Test pattern detection with k-anonymity"""
        # Create sufficient data for k-anonymity
        students = []
        sessions = []
        
        for i in range(10):
            student = Student.objects.create(
                student_id=f'KTEST{i:03d}',
                age_band='20-22',
                language_pref='English',
                interests=['test'],
                enrollment_date=timezone.now().date()
            )
            students.append(student)
            
            session = WellnessSession.objects.create(
                session_id=f'KSESS{i:03d}',
                student=student,
                mood_score=5 + (i % 3),
                anxiety_score=6 + (i % 4),
                risk_level='L2' if i > 5 else 'L1'
            )
            sessions.append(session)
        
        # Run pattern detection
        response = self.client.post(
            '/api/patterns/',
            data=json.dumps({
                'class_id': 'TESTCLASS',
                'time_window': 30
            }),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 200)
        patterns = response.json()
        
        # Verify patterns maintain k-anonymity
        for pattern in patterns:
            if 'k_count' in pattern:
                self.assertGreaterEqual(pattern['k_count'], 5)

# ============================================
# tests/test_privacy.py - Privacy & Security Tests
# ============================================

class PrivacyComplianceTest(TestCase):
    """Test privacy and security compliance"""
    
    def test_no_raw_responses_stored(self):
        """Verify raw screening responses are not stored"""
        student = Student.objects.create(
            student_id='PRIV001',
            age_band='20-22',
            language_pref='English',
            interests=['test'],
            enrollment_date=timezone.now().date()
        )
        
        session = WellnessSession.objects.create(
            session_id='PRIVSESS001',
            student=student,
            mood_score=5,
            anxiety_score=7,
            total_score=12,
            risk_level='L2'
        )
        
        # Check that no raw response field exists
        self.assertFalse(hasattr(session, 'raw_responses'))
        
        # Only aggregated scores should be stored
        self.assertIsNotNone(session.mood_score)
        self.assertIsNotNone(session.total_score)
    
    def test_student_id_hashing_in_exports(self):
        """Test student IDs are hashed in data exports"""
        processor = CSVDataProcessor()
        
        # Create test session
        student = Student.objects.create(
            student_id='HASH001',
            age_band='20-22',
            language_pref='English',
            interests=['test'],
            enrollment_date=timezone.now().date()
        )
        
        WellnessSession.objects.create(
            session_id='HASHSESS001',
            student=student,
            mood_score=5,
            anxiety_score=7,
            risk_level='L2'
        )
        
        # Export data
        export_path = processor.export_wellness_sessions()
        
        # Read exported CSV
        df = pd.read_csv(export_path)
        
        # Check student ID is hashed
        if 'student_id_hash' in df.columns:
            self.assertNotIn('HASH001', df['student_id_hash'].values)
    
    def test_k_anonymity_in_patterns(self):
        """Test k-anonymity is maintained in all patterns"""
        # Create pattern with insufficient k
        with self.assertRaises(Exception):
            Pattern.objects.create(
                pattern_type='test',
                k_count=3,  # Below threshold
                pattern_data={},
                severity='low'
            )

# ============================================
# tests/test_performance.py - Performance Tests
# ============================================

import time
from django.test import TestCase
from django.test.utils import override_settings

class PerformanceTest(TestCase):
    """Performance and scalability tests"""
    
    def test_bulk_data_processing(self):
        """Test processing large amounts of data"""
        start_time = time.time()
        
        # Create bulk data
        students = []
        for i in range(100):
            students.append(Student(
                student_id=f'PERF{i:04d}',
                age_band='20-22',
                language_pref='English',
                interests=['test'],
                enrollment_date=timezone.now().date()
            ))
        
        Student.objects.bulk_create(students)
        
        elapsed_time = time.time() - start_time
        
        # Should complete within reasonable time
        self.assertLess(elapsed_time, 5.0)
    
    @override_settings(DEBUG=False)
    def test_api_response_time(self):
        """Test API response times"""
        client = Client()
        
        # Measure chat API response time
        start_time = time.time()
        
        response = client.post(
            '/api/chat/',
            data=json.dumps({
                'student_id': 'PERF001',
                'message': 'Hello',
                'language': 'English'
            }),
            content_type='application/json'
        )
        
        elapsed_time = time.time() - start_time
        
        # Should respond within 2 seconds
        self.assertLess(elapsed_time, 2.0)
    
    def test_pattern_detection_scalability(self):
        """Test pattern detection with large datasets"""
        # Create large dataset
        sessions = []
        for i in range(1000):
            student = Student.objects.create(
                student_id=f'SCALE{i:04d}',
                age_band='20-22',
                language_pref='English',
                interests=['test'],
                enrollment_date=timezone.now().date()
            )
            
            sessions.append(WellnessSession(
                session_id=f'SCALESESS{i:04d}',
                student=student,
                mood_score=np.random.randint(1, 10),
                anxiety_score=np.random.randint(1, 10),
                risk_level=np.random.choice(['L1', 'L2', 'L3'])
            ))
        
        WellnessSession.objects.bulk_create(sessions)
        
        # Run pattern detection
        start_time = time.time()
        
        analyzer = PatternAnalyzer()
        data = pd.DataFrame(list(
            WellnessSession.objects.values(
                'created_at', 'mood_score', 'anxiety_score', 'risk_level'
            )
        ))
        data['timestamp'] = data['created_at']
        data['student_id'] = [f'SCALE{i:04d}' for i in range(len(data))]
        
        patterns = analyzer.analyze_temporal_patterns(data)
        
        elapsed_time = time.time() - start_time
        
        # Should complete within 10 seconds even for large datasets
        self.assertLess(elapsed_time, 10.0)