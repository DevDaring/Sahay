#!/usr/bin/env python3
"""
Career Monitoring Service
Monitors student interests and automatically updates career recommendations
"""

import os
import sys
import django
import pandas as pd
import json
from datetime import datetime, timedelta
import logging
from typing import Dict, List, Optional, Tuple

# Add the project directory to Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sahay.settings')
django.setup()

from services.data_processing import CSVDataProcessor
from services.gemini_service import GeminiService

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class CareerMonitoringService:
    """Background service to monitor and update career recommendations"""
    
    def __init__(self):
        self.csv_processor = CSVDataProcessor()
        self.gemini_service = GeminiService()
        self.data_dir = 'data/input'
        self.output_dir = 'data/output'
        
        # Ensure directories exist
        os.makedirs(self.data_dir, exist_ok=True)
        os.makedirs(self.output_dir, exist_ok=True)
        
        # File paths
        self.student_interests_file = os.path.join(self.data_dir, 'student_interests.csv')
        self.course_careers_file = os.path.join(self.data_dir, 'course_careers.csv')
        self.career_match_file = os.path.join(self.data_dir, 'career_match.csv')
        
        # Initialize CSV files if they don't exist
        self._initialize_csv_files()
    
    def _initialize_csv_files(self):
        """Initialize CSV files with proper headers if they don't exist"""
        
        # Initialize student_interests.csv
        if not os.path.exists(self.student_interests_file):
            student_interests_df = pd.DataFrame(columns=[
                'user_id', 'username', 'name', 'hometown', 'course', 'interests',
                'career_recommendations', 'last_updated', 'recommendation_count'
            ])
            student_interests_df.to_csv(self.student_interests_file, index=False)
            logger.info(f"Created {self.student_interests_file}")
        
        # Initialize course_careers.csv
        if not os.path.exists(self.course_careers_file):
            course_careers_df = pd.DataFrame(columns=[
                'course_name', 'career_paths', 'last_updated', 'path_count'
            ])
            course_careers_df.to_csv(self.course_careers_file, index=False)
            logger.info(f"Created {self.course_careers_file}")
        
        # Initialize career_match.csv
        if not os.path.exists(self.career_match_file):
            career_match_df = pd.DataFrame(columns=[
                'user_id', 'username', 'name', 'hometown', 'course', 'interests',
                'matched_careers', 'futuristic_roles', 'key_skills', 'last_updated'
            ])
            career_match_df.to_csv(self.career_match_file, index=False)
            logger.info(f"Created {self.career_match_file}")
    
    def monitor_and_update(self):
        """Main monitoring function - checks for changes and updates recommendations"""
        logger.info("Starting career monitoring service...")
        
        try:
            # Check for student interest changes
            self._check_student_interests()
            
            # Check for course career paths
            self._check_course_careers()
            
            # Update career matches based on user interests
            self._update_career_matches()
            
            logger.info("Career monitoring completed successfully")
            
        except Exception as e:
            logger.error(f"Error in career monitoring: {e}", exc_info=True)
    
    def _check_student_interests(self):
        """Check for changes in student interests and update recommendations"""
        logger.info("Checking student interests...")
        
        # Load current users
        users_df = self.csv_processor.data.get('users', pd.DataFrame())
        if users_df.empty:
            logger.warning("No users found in users.csv")
            return
        
        # Load existing student interests
        student_interests_df = pd.read_csv(self.student_interests_file) if os.path.exists(self.student_interests_file) else pd.DataFrame()
        
        updated_count = 0
        
        for _, user in users_df.iterrows():
            user_id = user.get('Id')
            username = user.get('UserName')
            name = user.get('Name')
            hometown = user.get('Hometown', '')
            course = user.get('Course', '')
            current_interests = user.get('Interests', '')
            
            if not user_id or not username:
                continue
            
            # Check if user exists in student_interests
            existing_record = student_interests_df[student_interests_df['user_id'] == user_id]
            
            needs_update = False
            
            if existing_record.empty:
                # New user - needs recommendations
                logger.info(f"New user {username} - generating recommendations")
                needs_update = True
            else:
                # Check if interests have changed
                existing_interests = existing_record.iloc[0].get('interests', '')
                if existing_interests != current_interests:
                    logger.info(f"Interests changed for {username}: '{existing_interests}' -> '{current_interests}'")
                    needs_update = True
                else:
                    # Check if recommendations are empty or outdated (older than 7 days)
                    last_updated = existing_record.iloc[0].get('last_updated', '')
                    if last_updated:
                        try:
                            last_update_date = datetime.strptime(last_updated, '%Y-%m-%d %H:%M:%S')
                            if datetime.now() - last_update_date > timedelta(days=7):
                                logger.info(f"Recommendations outdated for {username} - regenerating")
                                needs_update = True
                        except ValueError:
                            logger.warning(f"Invalid date format for {username}: {last_updated}")
                            needs_update = True
                    else:
                        needs_update = True
            
            if needs_update:
                self._update_student_recommendations(
                    user_id, username, name, hometown, course, current_interests
                )
                updated_count += 1
        
        logger.info(f"Updated recommendations for {updated_count} students")
    
    def _update_student_recommendations(self, user_id, username, name, hometown, course, interests):
        """Generate and store career recommendations for a student"""
        try:
            logger.info(f"Generating recommendations for {username}")
            
            # Generate recommendations using Gemini
            recommendations = self._generate_career_recommendations(name, hometown, course, interests)
            
            # Load existing data
            student_interests_df = pd.read_csv(self.student_interests_file)
            
            # Remove existing record if it exists
            student_interests_df = student_interests_df[student_interests_df['user_id'] != user_id]
            
            # Add new record
            new_record = {
                'user_id': user_id,
                'username': username,
                'name': name,
                'hometown': hometown,
                'course': course,
                'interests': interests,
                'career_recommendations': json.dumps(recommendations),
                'last_updated': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'recommendation_count': len(recommendations)
            }
            
            student_interests_df = pd.concat([student_interests_df, pd.DataFrame([new_record])], ignore_index=True)
            
            # Save to CSV
            student_interests_df.to_csv(self.student_interests_file, index=False)
            
            logger.info(f"Successfully updated recommendations for {username}")
            
        except Exception as e:
            logger.error(f"Error updating recommendations for {username}: {e}", exc_info=True)
    
    def _generate_career_recommendations(self, name, hometown, course, interests):
        """Generate career recommendations using Gemini"""
        try:
            # Create a prompt for career recommendations
            system_context = f"""You are a career guidance counselor helping students in India. Provide personalized career recommendations based on their profile.

USER PROFILE:
- Name: {name if name else "Student"}
- Hometown: {hometown if hometown else "Not specified"}
- Course: {course if course else "Not specified"}
- Interests: {interests if interests else "Not specified"}

TASK: Generate exactly 3 personalized career recommendations that connect their academic studies with their personal interests.

REQUIREMENTS:
- Keep each recommendation SHORT (1-2 sentences maximum)
- CONNECT their course with their interests
- Include LOCAL context when relevant (hometown, Indian market)
- Suggest SPECIFIC career paths, not generic advice
- Be ENCOURAGING and realistic
- Include both traditional and emerging career options
- Keep descriptions under 200 characters each
- Use simple, clear language

CRITICAL: You MUST respond with ONLY a valid JSON array. No other text, explanations, or formatting.
IMPORTANT: Ensure all strings are properly escaped and the JSON is complete and valid.

EXAMPLE RESPONSE:
[
  {{
    "title": "Sports Analytics Developer",
    "description": "Combine your CS skills with football passion to build data-driven solutions for sports teams.",
    "skills_needed": ["Python", "Data Analysis", "Machine Learning"],
    "growth_potential": "High",
    "local_opportunities": "Growing sports industry in Kolkata with ISL teams"
  }},
  {{
    "title": "Technical Writer",
    "description": "Use your writing skills and CS background to create engaging tech content.",
    "skills_needed": ["Technical Writing", "Communication", "Research"],
    "growth_potential": "Medium",
    "local_opportunities": "High demand in Kolkata's tech startup ecosystem"
  }},
  {{
    "title": "AI/ML Engineer",
    "description": "Build intelligent systems using your CS foundation and sci-fi interests.",
    "skills_needed": ["Machine Learning", "Python", "TensorFlow"],
    "growth_potential": "High",
    "local_opportunities": "Strong demand in Kolkata's IT sector"
  }}
]

Generate exactly 3 personalized career recommendations as JSON:"""

            response = self.gemini_service.model.generate_content(
                system_context,
                generation_config=self.gemini_service.generation_config,
                safety_settings=self.gemini_service.safety_settings
            )
            
            if response and response.text:
                # Clean the response text
                response_text = response.text.strip()
                
                # Try to extract JSON from the response if it's wrapped in other text
                if response_text.startswith('```json'):
                    response_text = response_text[7:]
                if response_text.endswith('```'):
                    response_text = response_text[:-3]
                
                # Try to parse JSON response
                try:
                    recommendations = json.loads(response_text)
                    if isinstance(recommendations, list) and len(recommendations) > 0:
                        return recommendations
                    else:
                        logger.warning(f"Empty or invalid recommendations: {recommendations}")
                        return self._get_fallback_recommendations(course, interests)
                except json.JSONDecodeError as e:
                    logger.warning(f"JSON parsing error: {e}")
                    logger.warning(f"Response text: {response_text}")
                    
                    # Try to extract partial recommendations from incomplete JSON
                    partial_recommendations = self._extract_partial_recommendations(response_text)
                    if partial_recommendations:
                        logger.info(f"Extracted {len(partial_recommendations)} partial recommendations")
                        return partial_recommendations
                    
                    return self._get_fallback_recommendations(course, interests)
            else:
                logger.warning("No response from Gemini")
                return self._get_fallback_recommendations(course, interests)
                
        except Exception as e:
            logger.error(f"Error generating career recommendations: {e}")
            return self._get_fallback_recommendations(course, interests)
    
    def _extract_partial_recommendations(self, response_text):
        """Extract partial recommendations from incomplete JSON response"""
        try:
            import re
            
            # Find all complete recommendation objects using regex
            # Look for patterns like {"title": "...", "description": "...", ...}
            pattern = r'\{[^{}]*"title"[^{}]*"description"[^{}]*"skills_needed"[^{}]*"growth_potential"[^{}]*"local_opportunities"[^{}]*\}'
            matches = re.findall(pattern, response_text, re.DOTALL)
            
            recommendations = []
            for match in matches:
                try:
                    # Clean up the match and try to parse it
                    cleaned_match = match.strip()
                    if cleaned_match.endswith(','):
                        cleaned_match = cleaned_match[:-1]
                    
                    # Try to parse as JSON
                    rec = json.loads(cleaned_match)
                    if isinstance(rec, dict) and 'title' in rec and 'description' in rec:
                        recommendations.append(rec)
                except json.JSONDecodeError:
                    continue
            
            # If we found at least one complete recommendation, return them
            if recommendations:
                logger.info(f"Successfully extracted {len(recommendations)} recommendations from partial JSON")
                return recommendations
            
            # If no complete recommendations found, try to extract individual fields
            return self._extract_fields_from_text(response_text)
            
        except Exception as e:
            logger.error(f"Error extracting partial recommendations: {e}")
            return []
    
    def _extract_fields_from_text(self, text):
        """Extract recommendation fields from text when JSON parsing fails"""
        try:
            import re
            recommendations = []
            
            # Split by recommendation blocks
            blocks = text.split('{')
            
            for block in blocks[1:]:  # Skip first empty split
                if 'title' in block:
                    try:
                        # Extract title - look for the first complete title
                        title_match = re.search(r'"title":\s*"([^"]+)"', block)
                        title = title_match.group(1) if title_match else "Career Path"
                        
                        # Extract description - look for description after title
                        desc_match = re.search(r'"description":\s*"([^"]+)"', block)
                        description = desc_match.group(1) if desc_match else "A career opportunity"
                        
                        # Extract skills - look for skills array
                        skills_match = re.search(r'"skills_needed":\s*\[([^\]]*)\]', block)
                        skills_text = skills_match.group(1) if skills_match else ""
                        skills = [s.strip().strip('"') for s in skills_text.split(',') if s.strip()]
                        
                        # Extract growth potential
                        growth_match = re.search(r'"growth_potential":\s*"([^"]+)"', block)
                        growth = growth_match.group(1) if growth_match else "Medium"
                        
                        # Extract local opportunities
                        local_match = re.search(r'"local_opportunities":\s*"([^"]+)"', block)
                        local = local_match.group(1) if local_match else "Various opportunities available"
                        
                        # Only add if we have a valid title
                        if title and title != "Career Path":
                            recommendations.append({
                                'title': title,
                                'description': description,
                                'skills_needed': skills,
                                'growth_potential': growth,
                                'local_opportunities': local
                            })
                        
                    except Exception as e:
                        logger.warning(f"Error extracting fields from block: {e}")
                        continue
            
            return recommendations[:3]  # Limit to 3 recommendations
            
        except Exception as e:
            logger.error(f"Error extracting fields from text: {e}")
            return []
    
    def _update_career_matches(self):
        """Update career matches based on user interests"""
        logger.info("Updating career matches...")
        
        try:
            users_df = self.csv_processor.data.get('users', pd.DataFrame())
            
            if users_df.empty:
                logger.info("No users found for career matching")
                return
            
            updated_count = 0
            for index, user in users_df.iterrows():
                user_id = user['Id']
                username = user['UserName']
                name = user['Name']
                hometown = user['Hometown']
                course = user['Course']
                interests = user['Interests']
                
                # Check if we need to update career matches
                current_matches = self._get_career_matches_from_csv(username=username, user_id=user_id)
                
                if not current_matches or self._interests_changed_for_matches(user, current_matches):
                    logger.info(f"Generating career matches for {username}")
                    matched_careers, futuristic_roles, key_skills = self._generate_career_matches(
                        name, hometown, course, interests
                    )
                    self._save_career_matches(
                        user_id, username, name, hometown, course, interests,
                        matched_careers, futuristic_roles, key_skills
                    )
                    updated_count += 1
                else:
                    logger.info(f"Career matches for {username} are up-to-date")
            
            logger.info(f"Updated career matches for {updated_count} users")
            
        except Exception as e:
            logger.error(f"Error updating career matches: {e}", exc_info=True)
    
    def _get_career_matches_from_csv(self, username=None, user_id=None):
        """Get career matches from career_match.csv"""
        if not os.path.exists(self.career_match_file):
            return None
        
        try:
            career_match_df = pd.read_csv(self.career_match_file)
            
            if username:
                user_record = career_match_df[career_match_df['username'] == username]
            elif user_id:
                user_record = career_match_df[career_match_df['user_id'] == user_id]
            else:
                return None
            
            if not user_record.empty:
                return {
                    'matched_careers': user_record.iloc[0].get('matched_careers', ''),
                    'futuristic_roles': user_record.iloc[0].get('futuristic_roles', ''),
                    'key_skills': user_record.iloc[0].get('key_skills', ''),
                    'interests': user_record.iloc[0].get('interests', '')
                }
            return None
            
        except Exception as e:
            logger.error(f"Error reading career matches: {e}")
            return None
    
    def _interests_changed_for_matches(self, user_data, current_matches):
        """Check if user interests have changed compared to stored matches"""
        if not current_matches:
            return True
        
        stored_interests = current_matches.get('interests', '')
        return stored_interests != user_data['Interests']
    
    def _generate_career_matches(self, name, hometown, course, interests):
        """Generate career matches based on user interests using Gemini"""
        logger.info(f"Generating career matches for {name}")
        
        system_context = f"""You are a career guidance expert specializing in matching user interests with career paths. Generate personalized career matches based on user profile.

USER PROFILE:
- Name: {name if name else "Student"}
- Hometown: {hometown if hometown else "Not specified"}
- Course: {course if course else "Not specified"}
- Interests: {interests if interests else "Not specified"}

TASK: Generate career matches that connect user interests with specific career paths, including futuristic roles and key skills.

REQUIREMENTS:
- Match interests to relevant careers (e.g., detective novels -> cybersecurity, data analysis)
- Include futuristic/emerging roles based on interests
- Provide comprehensive key skills for each career
- Focus on Indian job market and local opportunities
- Be specific and actionable
- Keep descriptions under 150 characters each
- Limit to 2 matched careers and 2 futuristic roles maximum

CRITICAL: You MUST respond with ONLY a valid JSON object. No other text, explanations, or formatting.
IMPORTANT: Ensure all strings are properly escaped and the JSON is complete and valid.

EXAMPLE RESPONSE:
{{
  "matched_careers": [
    {{
      "title": "Cybersecurity Analyst",
      "description": "Perfect for detective novel lovers - investigate digital threats and solve cyber mysteries",
      "interest_match": "detective novels",
      "key_skills": ["Network Security", "Digital Forensics", "Risk Assessment", "Incident Response", "Python", "Linux"],
      "growth_potential": "Very High",
      "local_opportunities": "High demand in Kolkata's growing IT security sector"
    }},
    {{
      "title": "Data Detective",
      "description": "Use analytical thinking from detective stories to uncover insights in data",
      "interest_match": "detective novels",
      "key_skills": ["Data Analysis", "Statistical Modeling", "Python", "SQL", "Machine Learning", "Critical Thinking"],
      "growth_potential": "High",
      "local_opportunities": "Growing data analytics market in India"
    }}
  ],
  "futuristic_roles": [
    {{
      "title": "AI Ethics Investigator",
      "description": "Investigate AI bias and ensure ethical AI deployment - like a detective for algorithms",
      "interest_match": "detective novels + technology",
      "key_skills": ["AI Ethics", "Algorithm Analysis", "Bias Detection", "Regulatory Compliance", "Python", "Statistics"],
      "growth_potential": "Very High",
      "local_opportunities": "Emerging field with high demand in tech companies"
    }},
    {{
      "title": "Quantum Security Specialist",
      "description": "Protect quantum systems from cyber threats - the ultimate digital detective",
      "interest_match": "detective novels + science fiction",
      "key_skills": ["Quantum Computing", "Cryptography", "Security Protocols", "Physics", "Programming"],
      "growth_potential": "Very High",
      "local_opportunities": "Future-focused role in emerging quantum tech sector"
    }}
  ],
  "key_skills_summary": [
    "Critical Thinking and Problem Solving",
    "Data Analysis and Interpretation",
    "Programming (Python, SQL)",
    "Security and Risk Assessment",
    "Communication and Documentation",
    "Continuous Learning and Adaptation"
  ]
}}

Generate career matches as JSON:"""

        try:
            response = self.gemini_service.model.generate_content(
                system_context,
                generation_config=self.gemini_service.generation_config,
                safety_settings=self.gemini_service.safety_settings
            )
            
            if response and response.text:
                response_text = response.text.strip()
                
                # Clean up response text
                if response_text.startswith('```json'):
                    response_text = response_text[7:]
                if response_text.endswith('```'):
                    response_text = response_text[:-3]
                
                # Parse JSON response
                try:
                    matches = json.loads(response_text)
                    if isinstance(matches, dict):
                        matched_careers = matches.get('matched_careers', [])
                        futuristic_roles = matches.get('futuristic_roles', [])
                        key_skills = matches.get('key_skills_summary', [])
                        
                        return matched_careers, futuristic_roles, key_skills
                    else:
                        logger.warning(f"Invalid matches format: {matches}")
                        return self._get_fallback_career_matches(course, interests)
                        
                except json.JSONDecodeError as e:
                    logger.warning(f"JSON parsing error: {e}")
                    logger.warning(f"Response text: {response_text}")
                    
                    # Try to extract partial career matches from incomplete JSON
                    partial_matches = self._extract_partial_career_matches(response_text)
                    if partial_matches:
                        logger.info(f"Extracted partial career matches")
                        return partial_matches
                    
                    return self._get_fallback_career_matches(course, interests)
            else:
                logger.warning("No response from Gemini for career matches")
                return self._get_fallback_career_matches(course, interests)
                
        except Exception as e:
            logger.error(f"Error generating career matches: {e}")
            return self._get_fallback_career_matches(course, interests)
    
    def _extract_partial_career_matches(self, response_text):
        """Extract partial career matches from incomplete JSON response"""
        try:
            import re
            
            matched_careers = []
            futuristic_roles = []
            key_skills = []
            
            # Extract matched careers
            career_pattern = r'"matched_careers":\s*\[(.*?)\]'
            career_match = re.search(career_pattern, response_text, re.DOTALL)
            if career_match:
                career_text = career_match.group(1)
                # Extract individual career objects
                career_objects = re.findall(r'\{[^{}]*"title"[^{}]*"description"[^{}]*\}', career_text, re.DOTALL)
                for career_obj in career_objects:
                    try:
                        career = json.loads(career_obj)
                        if isinstance(career, dict) and 'title' in career:
                            matched_careers.append(career)
                    except json.JSONDecodeError:
                        continue
            
            # Extract futuristic roles
            futuristic_pattern = r'"futuristic_roles":\s*\[(.*?)\]'
            futuristic_match = re.search(futuristic_pattern, response_text, re.DOTALL)
            if futuristic_match:
                futuristic_text = futuristic_match.group(1)
                futuristic_objects = re.findall(r'\{[^{}]*"title"[^{}]*"description"[^{}]*\}', futuristic_text, re.DOTALL)
                for futuristic_obj in futuristic_objects:
                    try:
                        role = json.loads(futuristic_obj)
                        if isinstance(role, dict) and 'title' in role:
                            futuristic_roles.append(role)
                    except json.JSONDecodeError:
                        continue
            
            # Extract key skills
            skills_pattern = r'"key_skills_summary":\s*\[(.*?)\]'
            skills_match = re.search(skills_pattern, response_text, re.DOTALL)
            if skills_match:
                skills_text = skills_match.group(1)
                skills = [s.strip().strip('"') for s in skills_text.split(',') if s.strip()]
                key_skills = skills
            
            # If we found at least some data, return it
            if matched_careers or futuristic_roles or key_skills:
                return matched_careers, futuristic_roles, key_skills
            
            return None
            
        except Exception as e:
            logger.error(f"Error extracting partial career matches: {e}")
            return None
    
    def _get_fallback_career_matches(self, course, interests):
        """Fallback career matches if Gemini fails"""
        matched_careers = []
        futuristic_roles = []
        key_skills = []
        
        # Course-based matches
        if course and 'computer' in course.lower():
            matched_careers.extend([
                {
                    "title": "Software Developer",
                    "description": "Build applications and software solutions",
                    "interest_match": "technology",
                    "key_skills": ["Programming", "Problem Solving", "System Design", "Algorithms"],
                    "growth_potential": "High",
                    "local_opportunities": "Growing tech sector across India"
                },
                {
                    "title": "Data Analyst",
                    "description": "Analyze data to help businesses make informed decisions",
                    "interest_match": "analytical thinking",
                    "key_skills": ["Data Analysis", "Statistics", "SQL", "Python", "Visualization"],
                    "growth_potential": "High",
                    "local_opportunities": "High demand in startups and enterprises"
                }
            ])
            
            futuristic_roles.extend([
                {
                    "title": "AI/ML Engineer",
                    "description": "Build intelligent systems and applications",
                    "interest_match": "technology + innovation",
                    "key_skills": ["Machine Learning", "Python", "TensorFlow", "Deep Learning", "Statistics"],
                    "growth_potential": "Very High",
                    "local_opportunities": "Strong demand in emerging AI sector"
                }
            ])
        
        # Interest-based matches
        if interests:
            interests_lower = interests.lower()
            if 'football' in interests_lower:
                matched_careers.append({
                    "title": "Sports Analytics Specialist",
                    "description": "Analyze player performance and team strategies",
                    "interest_match": "football",
                    "key_skills": ["Data Analysis", "Sports Knowledge", "Statistics", "Python", "Visualization"],
                    "growth_potential": "Medium",
                    "local_opportunities": "Growing sports industry in India"
                })
            
            if 'writing' in interests_lower or 'reading' in interests_lower:
                matched_careers.append({
                    "title": "Technical Writer",
                    "description": "Create documentation and content for technology",
                    "interest_match": "writing",
                    "key_skills": ["Technical Writing", "Communication", "Research", "Documentation", "SEO"],
                    "growth_potential": "Medium",
                    "local_opportunities": "High demand in tech companies"
                })
        
        # Key skills summary
        key_skills = [
            "Programming and Software Development",
            "Data Analysis and Statistics",
            "Problem Solving and Critical Thinking",
            "Communication and Documentation",
            "Continuous Learning and Adaptation"
        ]
        
        return matched_careers, futuristic_roles, key_skills
    
    def _save_career_matches(self, user_id, username, name, hometown, course, interests, matched_careers, futuristic_roles, key_skills):
        """Save career matches to CSV"""
        try:
            # Convert to JSON strings
            matched_careers_json = json.dumps(matched_careers)
            futuristic_roles_json = json.dumps(futuristic_roles)
            key_skills_json = json.dumps(key_skills)
            
            # Load existing data
            if os.path.exists(self.career_match_file):
                df = pd.read_csv(self.career_match_file)
            else:
                df = pd.DataFrame(columns=[
                    'user_id', 'username', 'name', 'hometown', 'course', 'interests',
                    'matched_careers', 'futuristic_roles', 'key_skills', 'last_updated'
                ])
            
            # Check if user already exists
            if username in df['username'].values:
                # Update existing record
                df.loc[df['username'] == username, 'matched_careers'] = matched_careers_json
                df.loc[df['username'] == username, 'futuristic_roles'] = futuristic_roles_json
                df.loc[df['username'] == username, 'key_skills'] = key_skills_json
                df.loc[df['username'] == username, 'last_updated'] = datetime.now().isoformat()
                df.loc[df['username'] == username, 'interests'] = interests
            else:
                # Add new record
                new_record = pd.DataFrame([{
                    'user_id': user_id,
                    'username': username,
                    'name': name,
                    'hometown': hometown,
                    'course': course,
                    'interests': interests,
                    'matched_careers': matched_careers_json,
                    'futuristic_roles': futuristic_roles_json,
                    'key_skills': key_skills_json,
                    'last_updated': datetime.now().isoformat()
                }])
                df = pd.concat([df, new_record], ignore_index=True)
            
            # Save to CSV
            df.to_csv(self.career_match_file, index=False)
            logger.info(f"Successfully updated career matches for {username}")
            
        except Exception as e:
            logger.error(f"Error saving career matches: {e}")
    
    def _get_fallback_recommendations(self, course, interests):
        """Fallback recommendations if Gemini fails"""
        recommendations = []
        
        # Course-based recommendations
        if course and 'computer' in course.lower():
            recommendations.extend([
                {
                    'title': 'Software Developer',
                    'description': f'Build applications and software solutions using your {course} knowledge',
                    'skills_needed': ['Programming', 'Problem Solving', 'System Design'],
                    'growth_potential': 'High',
                    'local_opportunities': 'Growing tech sector across India'
                },
                {
                    'title': 'Data Analyst',
                    'description': f'Analyze data to help businesses make informed decisions with your technical background',
                    'skills_needed': ['Data Analysis', 'Statistics', 'Programming'],
                    'growth_potential': 'High',
                    'local_opportunities': 'High demand in startups and enterprises'
                }
            ])
        
        # Interest-based recommendations
        if interests:
            interests_lower = interests.lower()
            if 'football' in interests_lower:
                recommendations.append({
                    'title': 'Sports Analytics Specialist',
                    'description': 'Combine your technical skills with passion for football to analyze player performance and team strategies',
                    'skills_needed': ['Data Analysis', 'Sports Knowledge', 'Programming'],
                    'growth_potential': 'Medium',
                    'local_opportunities': 'Growing sports industry in India'
                })
            
            if 'writing' in interests_lower or 'reading' in interests_lower:
                recommendations.append({
                    'title': 'Technical Writer',
                    'description': 'Create documentation and content that bridges technology and communication',
                    'skills_needed': ['Writing', 'Technical Knowledge', 'Communication'],
                    'growth_potential': 'Medium',
                    'local_opportunities': 'High demand in tech companies'
                })
        
        return recommendations[:3]
    
    def _check_course_careers(self):
        """Check for course career paths and update if needed"""
        logger.info("Checking course career paths...")
        
        # Load current users to get unique courses
        users_df = self.csv_processor.data.get('users', pd.DataFrame())
        if users_df.empty:
            logger.warning("No users found in users.csv")
            return
        
        # Get unique courses
        courses = users_df['Course'].dropna().unique()
        
        # Load existing course careers
        course_careers_df = pd.read_csv(self.course_careers_file) if os.path.exists(self.course_careers_file) else pd.DataFrame()
        
        updated_count = 0
        
        for course in courses:
            if not course or course.strip() == '':
                continue
            
            # Check if course exists in course_careers
            existing_record = course_careers_df[course_careers_df['course_name'] == course]
            
            needs_update = False
            
            if existing_record.empty:
                # New course - needs career paths
                logger.info(f"New course {course} - generating career paths")
                needs_update = True
            else:
                # Check if career paths are empty or outdated
                career_paths = existing_record.iloc[0].get('career_paths', '')
                if not career_paths or career_paths.strip() == '':
                    logger.info(f"Empty career paths for {course} - generating")
                    needs_update = True
                else:
                    # Check if outdated (older than 30 days)
                    last_updated = existing_record.iloc[0].get('last_updated', '')
                    if last_updated:
                        try:
                            last_update_date = datetime.strptime(last_updated, '%Y-%m-%d %H:%M:%S')
                            if datetime.now() - last_update_date > timedelta(days=30):
                                logger.info(f"Career paths outdated for {course} - regenerating")
                                needs_update = True
                        except ValueError:
                            logger.warning(f"Invalid date format for {course}: {last_updated}")
                            needs_update = True
                    else:
                        needs_update = True
            
            if needs_update:
                self._update_course_careers(course)
                updated_count += 1
        
        logger.info(f"Updated career paths for {updated_count} courses")
    
    def _update_course_careers(self, course_name):
        """Generate and store career paths for a course"""
        try:
            logger.info(f"Generating career paths for {course_name}")
            
            # Generate career paths using Gemini
            career_paths = self._generate_course_career_paths(course_name)
            
            # Load existing data
            course_careers_df = pd.read_csv(self.course_careers_file)
            
            # Remove existing record if it exists
            course_careers_df = course_careers_df[course_careers_df['course_name'] != course_name]
            
            # Add new record
            new_record = {
                'course_name': course_name,
                'career_paths': json.dumps(career_paths),
                'last_updated': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'path_count': len(career_paths)
            }
            
            course_careers_df = pd.concat([course_careers_df, pd.DataFrame([new_record])], ignore_index=True)
            
            # Save to CSV
            course_careers_df.to_csv(self.course_careers_file, index=False)
            
            logger.info(f"Successfully updated career paths for {course_name}")
            
        except Exception as e:
            logger.error(f"Error updating career paths for {course_name}: {e}", exc_info=True)
    
    def _generate_course_career_paths(self, course_name):
        """Generate career paths for a specific course using Gemini"""
        try:
            # Create a prompt for course career paths
            system_context = f"""You are a career guidance counselor helping students in India. Provide comprehensive career paths for a specific academic course.

COURSE: {course_name}

TASK: Generate exactly 5 career paths that are directly related to this course, including both traditional and emerging opportunities.

REQUIREMENTS:
- Keep each career path SHORT (2-3 sentences)
- Include SPECIFIC job titles and roles
- Mention GROWTH POTENTIAL (High/Medium/Low)
- Include SALARY RANGE in Indian context (₹LPA format)
- Suggest REQUIRED SKILLS
- Include INDUSTRY DEMAND level
- Be REALISTIC and ENCOURAGING

CRITICAL: You MUST respond with ONLY a valid JSON array. No other text, explanations, or formatting.

EXAMPLE RESPONSE:
[
  {{
    "title": "Software Engineer",
    "description": "Design, develop, and maintain software applications and systems using programming languages and development frameworks.",
    "skills": ["Programming", "Problem Solving", "System Design", "Database Management"],
    "salary_range": "₹6-25 LPA",
    "growth_potential": "High",
    "demand_level": "High",
    "industries": ["IT Services", "Product Companies", "Startups", "Fintech"]
  }},
  {{
    "title": "Data Scientist",
    "description": "Analyze complex data sets to extract insights and build predictive models for business decision-making.",
    "skills": ["Python", "Machine Learning", "Statistics", "Data Visualization"],
    "salary_range": "₹8-30 LPA",
    "growth_potential": "High",
    "demand_level": "High",
    "industries": ["E-commerce", "Banking", "Healthcare", "Consulting"]
  }}
]

Generate exactly 5 career paths for {course_name} as JSON:"""

            response = self.gemini_service.model.generate_content(
                system_context,
                generation_config=self.gemini_service.generation_config,
                safety_settings=self.gemini_service.safety_settings
            )
            
            if response and response.text:
                # Clean the response text
                response_text = response.text.strip()
                
                # Try to extract JSON from the response if it's wrapped in other text
                if response_text.startswith('```json'):
                    response_text = response_text[7:]
                if response_text.endswith('```'):
                    response_text = response_text[:-3]
                
                # Try to parse JSON response
                try:
                    career_paths = json.loads(response_text)
                    if isinstance(career_paths, list) and len(career_paths) > 0:
                        return career_paths
                    else:
                        logger.warning(f"Empty or invalid career paths: {career_paths}")
                        return self._get_fallback_course_careers(course_name)
                except json.JSONDecodeError as e:
                    logger.warning(f"JSON parsing error: {e}")
                    logger.warning(f"Response text: {response_text}")
                    return self._get_fallback_course_careers(course_name)
            else:
                logger.warning("No response from Gemini")
                return self._get_fallback_course_careers(course_name)
                
        except Exception as e:
            logger.error(f"Error generating course career paths: {e}")
            return self._get_fallback_course_careers(course_name)
    
    def _get_fallback_course_careers(self, course_name):
        """Fallback career paths if Gemini fails"""
        fallback_paths = []
        
        if 'computer' in course_name.lower() or 'cs' in course_name.lower():
            fallback_paths = [
                {
                    'title': 'Software Developer',
                    'description': 'Design and develop software applications using programming languages and development frameworks.',
                    'skills': ['Programming', 'Problem Solving', 'System Design'],
                    'salary_range': '₹6-25 LPA',
                    'growth_potential': 'High',
                    'demand_level': 'High',
                    'industries': ['IT Services', 'Product Companies', 'Startups']
                },
                {
                    'title': 'Data Analyst',
                    'description': 'Analyze data to help businesses make informed decisions using statistical methods and tools.',
                    'skills': ['Data Analysis', 'Statistics', 'SQL', 'Excel'],
                    'salary_range': '₹4-15 LPA',
                    'growth_potential': 'High',
                    'demand_level': 'High',
                    'industries': ['Banking', 'E-commerce', 'Consulting']
                },
                {
                    'title': 'System Administrator',
                    'description': 'Manage and maintain computer systems, networks, and servers for organizations.',
                    'skills': ['Linux', 'Networking', 'Security', 'Troubleshooting'],
                    'salary_range': '₹4-12 LPA',
                    'growth_potential': 'Medium',
                    'demand_level': 'Medium',
                    'industries': ['IT Services', 'Banking', 'Government']
                },
                {
                    'title': 'Web Developer',
                    'description': 'Create and maintain websites and web applications using various technologies.',
                    'skills': ['HTML', 'CSS', 'JavaScript', 'React'],
                    'salary_range': '₹3-18 LPA',
                    'growth_potential': 'High',
                    'demand_level': 'High',
                    'industries': ['Digital Agencies', 'E-commerce', 'Startups']
                },
                {
                    'title': 'Cybersecurity Analyst',
                    'description': 'Protect organizations from cyber threats by monitoring and securing their digital assets.',
                    'skills': ['Security Analysis', 'Risk Assessment', 'Incident Response'],
                    'salary_range': '₹6-20 LPA',
                    'growth_potential': 'High',
                    'demand_level': 'High',
                    'industries': ['Banking', 'IT Services', 'Government']
                }
            ]
        else:
            # Generic fallback for other courses
            fallback_paths = [
                {
                    'title': f'{course_name} Graduate',
                    'description': f'Apply your {course_name} knowledge in various professional settings.',
                    'skills': ['Critical Thinking', 'Communication', 'Problem Solving'],
                    'salary_range': '₹3-10 LPA',
                    'growth_potential': 'Medium',
                    'demand_level': 'Medium',
                    'industries': ['General', 'Consulting', 'Government']
                }
            ]
        
        return fallback_paths[:5]


def main():
    """Main function to run the career monitoring service"""
    service = CareerMonitoringService()
    service.monitor_and_update()


if __name__ == "__main__":
    main()
