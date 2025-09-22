"""
services/data_processing.py - CSV Data Processing and Analytics
Modified for CSV-only operation (no database dependencies)
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
import os
import json
import hashlib
import logging

logger = logging.getLogger(__name__)

class CSVDataProcessor:
    """Handle CSV data operations with privacy preservation"""
    
    def __init__(self, data_dir: Optional[str] = None):
        # Use provided directory or default to current working directory + data
        if data_dir is None:
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            data_dir = os.path.join(base_dir, 'data')
        
        self.input_dir = os.path.join(data_dir, 'input')
        self.output_dir = os.path.join(data_dir, 'output')
        self.k_threshold = 5  # Default k-anonymity threshold
        
        # Ensure directories exist
        os.makedirs(self.input_dir, exist_ok=True)
        os.makedirs(self.output_dir, exist_ok=True)
        
        # Load all CSV data into memory for faster processing
        self._load_data()
    
    def _load_data(self):
        """Load all CSV files into memory"""
        self.data = {}
        
        # Define CSV files and their expected columns
        csv_files = {
            'users': ['Id', 'Name', 'UserName', 'Password', 'Hometown', 'Course', 'Interests'],  # User authentication data
            'students': ['student_id', 'age_band', 'language_pref', 'interests', 'enrollment_date', 'data_consent', 'anonymous_sharing', 'retention_period'],
            'courses': ['course_id', 'topic', 'difficulty_level', 'prerequisites'],
            'sahayaks': ['mentor_id', 'name', 'expertise', 'languages', 'availability', 'rating', 'sessions_completed', 'response_time_hours', 'is_active'],
            'screening_questions': ['question_id', 'screener_type', 'question_text', 'scoring_rules', 'order'],
            'wellness_sessions': ['session_id', 'student_id', 'created_at', 'mood_score', 'anxiety_score', 'screener_type', 'total_score', 'risk_level', 'needs_escalation', 'escalated_to'],
            'actions': ['action_id', 'student_id', 'session_id', 'action_text', 'category', 'duration_minutes', 'status', 'due_date', 'completed_at'],
            'career_paths': ['path_id', 'field', 'required_skills', 'typical_roles', 'growth_trajectory'],
            'learning_sessions': ['session_id', 'student_id', 'course_id', 'topic', 'duration_minutes', 'quiz_score', 'comprehension_level', 'focus_score', 'created_at'],
            'patterns': ['pattern_id', 'pattern_type', 'k_count', 'pattern_data', 'severity', 'class_id', 'location_bucket', 'time_window_days', 'recommended_actions', 'created_at'],
            'anonymous_reports': ['report_id', 'report_type', 'category', 'location_bucket', 'k_count', 'content_redacted', 'status', 'handler', 'resolution_notes', 'created_at'],
            'sahayak_sessions': ['session_id', 'mentor_id', 'student_hash', 'duration_minutes', 'topic', 'summary_bullets', 'next_steps', 'was_escalated', 'escalation_reason', 'student_rating', 'created_at'],
            'student_career_plans': ['plan_id', 'student_id', 'current_track_id', 'explore_track_id', 'confidence_score', 'feasibility_score', 'skills_acquired', 'next_steps', 'proof_points', 'readiness_level', 'created_at']
        }
        
        for table_name, columns in csv_files.items():
            file_path = os.path.join(self.input_dir, f'{table_name}.csv')
            if os.path.exists(file_path):
                try:
                    df = pd.read_csv(file_path)
                    # Parse pipe-separated columns
                    pipe_columns = ['interests', 'expertise', 'languages', 'required_skills', 'typical_roles', 
                                   'summary_bullets', 'next_steps', 'skills_acquired', 'proof_points']
                    
                    for col in pipe_columns:
                        if col in df.columns:
                            df[col] = df[col].apply(lambda x: x.split('|') if pd.notna(x) and isinstance(x, str) else [])
                    
                    # Parse JSON columns that are already in JSON format
                    json_columns = ['prerequisites', 'scoring_rules', 'pattern_data', 'recommended_actions']
                    
                    for col in json_columns:
                        if col in df.columns:
                            df[col] = df[col].apply(lambda x: json.loads(x.replace("'", '"')) if pd.notna(x) and x.strip() and x != '[]' else [])
                    
                    # Parse datetime columns
                    datetime_columns = ['created_at', 'enrollment_date', 'due_date', 'completed_at']
                    for col in datetime_columns:
                        if col in df.columns:
                            df[col] = pd.to_datetime(df[col], errors='coerce', utc=True)
                    
                    self.data[table_name] = df
                    logger.info(f"Loaded {len(df)} records from {table_name}.csv")
                except Exception as e:
                    logger.error(f"Error loading {table_name}.csv: {e}")
                    self.data[table_name] = pd.DataFrame()
            else:
                logger.warning(f"File not found: {file_path}")
                self.data[table_name] = pd.DataFrame()
    
    def get_students(self, filters: Optional[Dict[str, Any]] = None) -> pd.DataFrame:
        """Get students data with optional filters"""
        df = self.data.get('students', pd.DataFrame()).copy()
        
        if filters and not df.empty:
            for key, value in filters.items():
                if key in df.columns:
                    if isinstance(value, list):
                        df = df[df[key].isin(value)]
                    else:
                        df = df[df[key] == value]
        
        return df
    
    def get_wellness_sessions(self, student_id: Optional[str] = None, start_date: Optional[datetime] = None, 
                             end_date: Optional[datetime] = None) -> pd.DataFrame:
        """Get wellness sessions with optional filters"""
        df = self.data.get('wellness_sessions', pd.DataFrame()).copy()
        
        if df.empty:
            return df
        
        if student_id:
            df = df[df['student_id'] == student_id]
        
        if start_date:
            df = df[df['created_at'] >= start_date]
        
        if end_date:
            df = df[df['created_at'] <= end_date]
        
        return df
    
    def get_learning_sessions(self, student_id: Optional[str] = None, course_id: Optional[str] = None,
                             start_date: Optional[datetime] = None, end_date: Optional[datetime] = None) -> pd.DataFrame:
        """Get learning sessions with optional filters"""
        df = self.data.get('learning_sessions', pd.DataFrame()).copy()
        
        if df.empty:
            return df
        
        if student_id:
            df = df[df['student_id'] == student_id]
        
        if course_id:
            df = df[df['course_id'] == course_id]
        
        if start_date:
            df = df[df['created_at'] >= start_date]
        
        if end_date:
            df = df[df['created_at'] <= end_date]
        
        return df
    
    def get_sahayaks(self, expertise: Optional[str] = None, language: Optional[str] = None, 
                     availability: Optional[str] = None) -> pd.DataFrame:
        """Get sahayaks data with optional filters"""
        df = self.data.get('sahayaks', pd.DataFrame()).copy()
        
        if df.empty:
            return df
        
        if expertise:
            df = df[df['expertise'].apply(lambda x: expertise in x if isinstance(x, list) else False)]
        
        if language:
            df = df[df['languages'].apply(lambda x: language in x if isinstance(x, list) else False)]
        
        if availability:
            df = df[df['availability'] == availability]
        
        return df.sort_values('rating', ascending=False)
    
    def get_user_by_username(self, username: str) -> pd.Series:
        """Get user information by username"""
        df = self.data.get('users', pd.DataFrame())
        if df.empty:
            return pd.Series()
        
        user_data = df[df['UserName'] == username]
        return user_data.iloc[0] if not user_data.empty else pd.Series()
    
    def get_user_by_id(self, user_id: int) -> pd.Series:
        """Get user information by ID"""
        df = self.data.get('users', pd.DataFrame())
        if df.empty:
            return pd.Series()
        
        user_data = df[df['Id'] == user_id]
        return user_data.iloc[0] if not user_data.empty else pd.Series()
    
    def get_user_first_name(self, username: Optional[str] = None, user_id: Optional[int] = None) -> str:
        """Extract first name from user data"""
        try:
            if username:
                user = self.get_user_by_username(username)
            elif user_id:
                user = self.get_user_by_id(user_id)
            else:
                return ""
            
            if user.empty or 'Name' not in user:
                return ""
            
            full_name = user['Name']
            if isinstance(full_name, str) and full_name.strip():
                # Extract first name (everything before the first space)
                first_name = full_name.strip().split()[0]
                return first_name
            
            return ""
        except Exception as e:
            logger.error(f"Error extracting first name: {e}")
            return ""
    
    def get_user_hometown(self, username: Optional[str] = None, user_id: Optional[int] = None) -> str:
        """Get user's hometown"""
        try:
            if username:
                user = self.get_user_by_username(username)
            elif user_id:
                user = self.get_user_by_id(user_id)
            else:
                return ""
            
            if user.empty or 'Hometown' not in user:
                return ""
            
            hometown = user['Hometown']
            return hometown if isinstance(hometown, str) and hometown.strip() else ""
        except Exception as e:
            logger.error(f"Error getting hometown: {e}")
            return ""
    
    def get_user_interests(self, username: Optional[str] = None, user_id: Optional[int] = None) -> str:
        """Get user's interests"""
        try:
            if username:
                user = self.get_user_by_username(username)
            elif user_id:
                user = self.get_user_by_id(user_id)
            else:
                return ""
            
            if user.empty or 'Interests' not in user:
                return ""
            
            interests = user['Interests']
            return interests if isinstance(interests, str) and interests.strip() else ""
        except Exception as e:
            logger.error(f"Error getting interests: {e}")
            return ""
    
    def get_user_course(self, username: Optional[str] = None, user_id: Optional[int] = None) -> str:
        """Get user's course"""
        try:
            if username:
                user = self.get_user_by_username(username)
            elif user_id:
                user = self.get_user_by_id(user_id)
            else:
                return ""
            
            if user.empty or 'Course' not in user:
                return ""
            
            course = user['Course']
            return course if isinstance(course, str) and course.strip() else ""
        except Exception as e:
            logger.error(f"Error getting course: {e}")
            return ""
    
    def update_user_interests(self, username: Optional[str] = None, user_id: Optional[int] = None, interests: str = "") -> bool:
        """Update user's interests in CSV"""
        try:
            df = self.data.get('users', pd.DataFrame())
            if df.empty:
                return False
            
            # Find the user
            if username:
                mask = df['UserName'] == username
            elif user_id:
                mask = df['Id'] == user_id
            else:
                return False
            
            if not mask.any():
                return False
            
            # Update interests
            df.loc[mask, 'Interests'] = interests
            
            # Update the in-memory data
            self.data['users'] = df
            
            # Save back to CSV
            self._save_to_csv('users')
            
            # Reload the data to ensure consistency
            self._load_data()
            
            return True
            
        except Exception as e:
            logger.error(f"Error updating user interests: {e}")
            return False
    
    def add_wellness_session(self, session_data: Dict[str, Any]) -> bool:
        """Add a new wellness session"""
        try:
            # Generate session ID if not provided
            if 'session_id' not in session_data:
                session_data['session_id'] = f"WS{len(self.data.get('wellness_sessions', pd.DataFrame())) + 1:03d}"
            
            # Add timestamp if not provided
            if 'created_at' not in session_data:
                session_data['created_at'] = pd.Timestamp.now(tz='UTC')
            
            # Create new row and append
            new_row = pd.DataFrame([session_data])
            
            if 'wellness_sessions' not in self.data:
                self.data['wellness_sessions'] = new_row
            else:
                self.data['wellness_sessions'] = pd.concat([self.data['wellness_sessions'], new_row], ignore_index=True)
            
            # Save to CSV
            self._save_to_csv('wellness_sessions')
            return True
            
        except Exception as e:
            logger.error(f"Error adding wellness session: {e}")
            return False
    
    def add_action(self, action_data: Dict[str, Any]) -> bool:
        """Add a new action"""
        try:
            # Generate action ID if not provided
            if 'action_id' not in action_data:
                action_data['action_id'] = f"ACT{len(self.data.get('actions', pd.DataFrame())) + 1:03d}"
            
            # Create new row and append
            new_row = pd.DataFrame([action_data])
            
            if 'actions' not in self.data:
                self.data['actions'] = new_row
            else:
                self.data['actions'] = pd.concat([self.data['actions'], new_row], ignore_index=True)
            
            # Save to CSV
            self._save_to_csv('actions')
            return True
            
        except Exception as e:
            logger.error(f"Error adding action: {e}")
            return False
    
    def update_action_status(self, action_id: str, status: str, completed_at: Optional[datetime] = None) -> bool:
        """Update action status"""
        try:
            df = self.data.get('actions', pd.DataFrame())
            if df.empty:
                return False
            
            mask = df['action_id'] == action_id
            if not mask.any():
                return False
            
            df.loc[mask, 'status'] = status
            if status == 'completed' and completed_at:
                df.loc[mask, 'completed_at'] = completed_at
            
            self.data['actions'] = df
            self._save_to_csv('actions')
            return True
            
        except Exception as e:
            logger.error(f"Error updating action status: {e}")
            return False
    
    def _save_to_csv(self, table_name: str):
        """Save data back to CSV file"""
        try:
            if table_name in self.data:
                df = self.data[table_name].copy()
                
                # Convert JSON columns back to string representation
                json_columns = ['interests', 'prerequisites', 'expertise', 'languages', 'scoring_rules', 
                               'pattern_data', 'recommended_actions', 'required_skills', 'typical_roles',
                               'summary_bullets', 'next_steps', 'skills_acquired', 'proof_points']
                
                for col in json_columns:
                    if col in df.columns:
                        df[col] = df[col].apply(lambda x: json.dumps(x) if isinstance(x, (list, dict)) else x)
                
                file_path = os.path.join(self.input_dir, f'{table_name}.csv')
                df.to_csv(file_path, index=False)
                logger.info(f"Saved {len(df)} records to {table_name}.csv")
        except Exception as e:
            logger.error(f"Error saving {table_name} to CSV: {e}")
    
    def export_wellness_sessions(self, start_date: Optional[datetime] = None, 
                                end_date: Optional[datetime] = None) -> str:
        """Export wellness sessions to CSV with k-anonymity"""
        try:
            df = self.get_wellness_sessions(start_date=start_date, end_date=end_date)
            
            if df.empty:
                logger.warning("No wellness sessions to export")
                return ""
            
            # Hash student IDs for privacy
            df = df.copy()
            df['student_id_hash'] = df['student_id'].apply(self._hash_student_id)
            df = df.drop(columns=['student_id'])
            
            # Apply k-anonymity
            df_anonymous = self._apply_k_anonymity(df)
            
            # Save to output CSV
            output_path = os.path.join(self.output_dir, f'wellness_sessions_export_{pd.Timestamp.now().strftime("%Y%m%d_%H%M%S")}.csv')
            df_anonymous.to_csv(output_path, index=False)
            
            logger.info(f"Exported {len(df_anonymous)} anonymized wellness sessions to {output_path}")
            return output_path
            
        except Exception as e:
            logger.error(f"Error exporting wellness sessions: {e}")
            raise
    
    def generate_analytics_report(self, class_id: Optional[str] = None, 
                                 time_window_days: int = 7) -> Dict[str, Any]:
        """Generate comprehensive analytics report from CSV data"""
        try:
            cutoff_date = pd.Timestamp.now(tz='UTC') - pd.Timedelta(days=time_window_days)
            
            # Gather data from CSV files
            wellness_sessions = self.get_wellness_sessions(start_date=cutoff_date)
            learning_sessions = self.get_learning_sessions(start_date=cutoff_date)
            students = self.get_students()
            
            # Filter by class if specified
            if class_id:
                learning_sessions = learning_sessions[learning_sessions['course_id'] == class_id]
                # Get students who attended this class
                class_students = learning_sessions['student_id'].unique()
                wellness_sessions = wellness_sessions[wellness_sessions['student_id'].isin(class_students)]
            
            report = {
                'report_date': pd.Timestamp.now().isoformat(),
                'time_window_days': time_window_days,
                'class_id': class_id,
                'total_students': len(students),
                'active_students': len(wellness_sessions['student_id'].unique()) if not wellness_sessions.empty else 0,
                'wellness_metrics': self._calculate_wellness_metrics(wellness_sessions),
                'learning_metrics': self._calculate_learning_metrics(learning_sessions),
                'patterns': self._detect_patterns_csv(wellness_sessions, learning_sessions),
                'recommendations': []
            }
            
            # Add recommendations based on metrics
            report['recommendations'] = self._generate_recommendations(report)
            
            # Save report
            report_path = os.path.join(self.output_dir, f'analytics_report_{pd.Timestamp.now().strftime("%Y%m%d_%H%M%S")}.json')
            with open(report_path, 'w') as f:
                json.dump(report, f, indent=2, default=str)
            
            logger.info(f"Generated analytics report: {report_path}")
            return report
            
        except Exception as e:
            logger.error(f"Error generating analytics report: {e}")
            raise
    
    def get_student_risk_assessment(self, student_id: str, days_back: int = 30) -> Dict[str, Any]:
        """Get risk assessment for a specific student"""
        cutoff_date = pd.Timestamp.now(tz='UTC') - pd.Timedelta(days=days_back)
        sessions = self.get_wellness_sessions(student_id=student_id, start_date=cutoff_date)
        
        if sessions.empty:
            return {
                'student_id': student_id,
                'risk_level': 'Unknown',
                'trend': 'No data',
                'last_session': None,
                'recommendations': ['Complete wellness screening']
            }
        
        latest_session = sessions.sort_values('created_at').iloc[-1]
        
        # Calculate trend
        if len(sessions) >= 2:
            sessions_sorted = sessions.sort_values('created_at')
            first_half = sessions_sorted.head(len(sessions_sorted)//2)
            second_half = sessions_sorted.tail(len(sessions_sorted)//2)
            
            avg_first = first_half['anxiety_score'].mean()
            avg_second = second_half['anxiety_score'].mean()
            
            if avg_second > avg_first + 1:
                trend = 'Worsening'
            elif avg_second < avg_first - 1:
                trend = 'Improving'
            else:
                trend = 'Stable'
        else:
            trend = 'Insufficient data'
        
        return {
            'student_id': student_id,
            'risk_level': latest_session['risk_level'],
            'current_mood': latest_session['mood_score'],
            'current_anxiety': latest_session['anxiety_score'],
            'trend': trend,
            'last_session': latest_session['created_at'].isoformat(),
            'session_count': len(sessions),
            'recommendations': self._get_student_recommendations(latest_session, trend)
        }
    
    def get_personalized_actions(self, student_id: str, limit: int = 3) -> List[Dict[str, Any]]:
        """Get personalized actions for a student"""
        # Get student info
        student = self.get_students({'student_id': [student_id]})
        if student.empty:
            return []
        
        student_info = student.iloc[0]
        
        # Get recent wellness data
        recent_sessions = self.get_wellness_sessions(student_id=student_id).tail(1)
        if recent_sessions.empty:
            return []
        
        latest_session = recent_sessions.iloc[0]
        
        # Generate actions based on risk level and interests
        actions = []
        
        if latest_session['risk_level'] == 'L3':
            actions.extend([
                {
                    'category': 'wellness',
                    'action_text': 'Connect with counseling services immediately',
                    'duration_minutes': 60,
                    'priority': 'high'
                },
                {
                    'category': 'break',
                    'action_text': 'Take a complete break from studies for today',
                    'duration_minutes': 480,
                    'priority': 'high'
                }
            ])
        elif latest_session['risk_level'] == 'L2':
            actions.extend([
                {
                    'category': 'wellness',
                    'action_text': 'Practice deep breathing exercises',
                    'duration_minutes': 10,
                    'priority': 'medium'
                },
                {
                    'category': 'social',
                    'action_text': 'Connect with a friend or family member',
                    'duration_minutes': 30,
                    'priority': 'medium'
                }
            ])
        else:  # L1
            # Add interest-based activities
            if isinstance(student_info['interests'], list) and student_info['interests']:
                interest = student_info['interests'][0]  # Take first interest
                actions.append({
                    'category': 'interest',
                    'action_text': f'Spend time on {interest} activity',
                    'duration_minutes': 45,
                    'priority': 'low'
                })
        
        # Add study-related action if mood is good
        if latest_session['mood_score'] >= 6:
            actions.append({
                'category': 'study',
                'action_text': 'Continue with planned study schedule',
                'duration_minutes': 90,
                'priority': 'low'
            })
        
        return actions[:limit]
    
    def _hash_student_id(self, student_id: str) -> str:
        """Hash student ID for privacy"""
        return hashlib.sha256(student_id.encode()).hexdigest()[:16]
    
    def _apply_k_anonymity(self, df: pd.DataFrame) -> pd.DataFrame:
        """Apply k-anonymity to dataframe"""
        if len(df) < self.k_threshold:
            return pd.DataFrame()
        
        # Group by quasi-identifiers for wellness sessions
        quasi_identifiers = ['risk_level']
        if 'screener_type' in df.columns:
            quasi_identifiers.append('screener_type')
        
        # Remove rows that don't meet k-anonymity threshold
        for qi in quasi_identifiers:
            if qi in df.columns:
                group_counts = df.groupby(qi).size()
                valid_values = group_counts[group_counts >= self.k_threshold].index
                df = df[df[qi].isin(valid_values)]
        
        # Further anonymize timestamps (round to hour)
        if 'created_at' in df.columns:
            df = df.copy()
            df['created_at'] = pd.to_datetime(df['created_at']).dt.floor('H')
        
        return df
    
    def _calculate_wellness_metrics(self, sessions: pd.DataFrame) -> Dict[str, Any]:
        """Calculate wellness metrics from sessions"""
        if sessions.empty:
            return {
                'avg_mood_score': 0,
                'avg_anxiety_score': 0,
                'risk_distribution': {},
                'total_sessions': 0,
                'high_risk_percentage': 0
            }
        
        return {
            'avg_mood_score': float(sessions['mood_score'].mean()) if 'mood_score' in sessions else 0,
            'avg_anxiety_score': float(sessions['anxiety_score'].mean()) if 'anxiety_score' in sessions else 0,
            'risk_distribution': sessions['risk_level'].value_counts().to_dict() if 'risk_level' in sessions else {},
            'total_sessions': len(sessions),
            'high_risk_percentage': (sessions['risk_level'] == 'L3').mean() * 100 if 'risk_level' in sessions else 0
        }
    
    def _calculate_learning_metrics(self, sessions: pd.DataFrame) -> Dict[str, Any]:
        """Calculate learning metrics from sessions"""
        if sessions.empty:
            return {
                'avg_quiz_score': 0,
                'avg_duration': 0,
                'comprehension_distribution': {},
                'total_sessions': 0
            }
        
        return {
            'avg_quiz_score': float(sessions['quiz_score'].mean()) if 'quiz_score' in sessions else 0,
            'avg_duration': float(sessions['duration_minutes'].mean()) if 'duration_minutes' in sessions else 0,
            'comprehension_distribution': sessions['comprehension_level'].value_counts().to_dict() if 'comprehension_level' in sessions else {},
            'total_sessions': len(sessions)
        }
    
    def _detect_patterns_csv(self, wellness_sessions: pd.DataFrame, learning_sessions: pd.DataFrame) -> List[Dict[str, Any]]:
        """Detect patterns in CSV data"""
        patterns = []
        
        # Temporal patterns
        if not wellness_sessions.empty and 'created_at' in wellness_sessions.columns and 'anxiety_score' in wellness_sessions.columns:
            df_wellness = wellness_sessions.copy()
            df_wellness['hour'] = pd.to_datetime(df_wellness['created_at']).dt.hour
            
            hourly_anxiety = df_wellness.groupby('hour')['anxiety_score'].agg(['mean', 'count'])
            
            for hour, row in hourly_anxiety.iterrows():
                if row['count'] >= self.k_threshold and row['mean'] > 6:
                    patterns.append({
                        'type': 'temporal',
                        'description': f'High anxiety at hour {hour}',
                        'severity': 'high' if row['mean'] > 8 else 'medium',
                        'k_count': int(row['count'])
                    })
        
        # Academic patterns
        if not learning_sessions.empty and 'comprehension_level' in learning_sessions.columns:
            low_comprehension = learning_sessions[learning_sessions['comprehension_level'] == 'low']
            
            if len(low_comprehension) >= self.k_threshold:
                patterns.append({
                    'type': 'academic',
                    'description': 'Low comprehension detected',
                    'severity': 'high',
                    'k_count': len(low_comprehension),
                    'topics': low_comprehension['topic'].value_counts().head(3).to_dict() if 'topic' in low_comprehension else {}
                })
        
        return patterns
    
    def _generate_recommendations(self, report: Dict[str, Any]) -> List[str]:
        """Generate recommendations based on report"""
        recommendations = []
        
        # Wellness recommendations
        wellness = report.get('wellness_metrics', {})
        if wellness.get('avg_anxiety_score', 0) > 6:
            recommendations.append("Increase wellness support resources - high anxiety detected")
        
        if wellness.get('high_risk_percentage', 0) > 20:
            recommendations.append("Critical: Over 20% of sessions show high risk - immediate intervention needed")
        
        # Learning recommendations
        learning = report.get('learning_metrics', {})
        if learning.get('avg_quiz_score', 100) < 60:
            recommendations.append("Review teaching methods - low quiz scores across sessions")
        
        # Pattern-based recommendations
        for pattern in report.get('patterns', []):
            if pattern['type'] == 'temporal' and pattern['severity'] == 'high':
                recommendations.append("Schedule support during high-stress hours")
            
            if pattern['type'] == 'academic' and pattern['severity'] == 'high':
                recommendations.append("Provide additional resources for challenging topics")
        
        return recommendations
    
    def _get_student_recommendations(self, latest_session: pd.Series, trend: str) -> List[str]:
        """Get recommendations for a specific student"""
        recommendations = []
        
        if latest_session['risk_level'] == 'L3':
            recommendations.extend([
                "Seek immediate counseling support",
                "Take a break from academic work",
                "Contact crisis support if needed"
            ])
        elif latest_session['risk_level'] == 'L2':
            recommendations.extend([
                "Practice stress management techniques",
                "Consider talking to a counselor",
                "Take regular breaks from studies"
            ])
        else:
            recommendations.extend([
                "Continue current wellness practices",
                "Maintain healthy study schedule",
                "Stay connected with support network"
            ])
        
        if trend == 'Worsening':
            recommendations.append("Monitor symptoms closely and seek help if they worsen")
        elif trend == 'Improving':
            recommendations.append("Keep up the good work with current coping strategies")
        
        return recommendations


# Example usage and testing functions
def test_csv_data_processor():
    """Test function to demonstrate CSV data processor functionality"""
    processor = CSVDataProcessor()
    
    # Test getting students
    students = processor.get_students()
    print(f"Total students: {len(students)}")
    
    # Test getting wellness sessions
    sessions = processor.get_wellness_sessions()
    print(f"Total wellness sessions: {len(sessions)}")
    
    # Test analytics report
    report = processor.generate_analytics_report(time_window_days=30)
    print(f"Generated report with {len(report.get('patterns', []))} patterns")
    
    # Test student risk assessment
    if not students.empty:
        student_id = students.iloc[0]['student_id']
        risk_assessment = processor.get_student_risk_assessment(student_id)
        print(f"Risk assessment for {student_id}: {risk_assessment['risk_level']}")


if __name__ == "__main__":
    test_csv_data_processor()