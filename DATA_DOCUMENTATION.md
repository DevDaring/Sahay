# 📊 SAHAY - Data Architecture & CSV Structure

**Complete documentation for the CSV-based data system with privacy protection**

---

## 🎯 **Data Architecture Overview**

Sahay uses a **pure CSV-based data architecture** designed for:
- **Privacy-first operation** with k-anonymity protection
- **Easy deployment** without database setup requirements
- **Synthetic data generation** for testing and demonstrations
- **Scalable analytics** with pandas-based processing

---

## 📁 **CSV File Structure**

### **Core Data Files**

#### **1. students.csv** - Student Demographics & Preferences
```csv
student_id,age_band,language_pref,interests,enrollment_date,data_consent,anonymous_sharing,retention_period
STU001,18-20,English,coding|music|reading,2024-01-15,true,true,90
STU002,20-22,Hindi,sports|art|photography,2024-01-20,true,true,90
STU003,18-20,Bengali,dance|cooking|movies,2024-01-25,true,false,60
```
**Fields:**
- `student_id`: Anonymized identifier (STU001, STU002, etc.)
- `age_band`: Age ranges for privacy (18-20, 20-22, 22-24)
- `language_pref`: Preferred language (English, Hindi, Bengali)
- `interests`: Pipe-separated interests for personalization
- `enrollment_date`: When student joined platform
- `data_consent`: Explicit consent for data processing
- `anonymous_sharing`: Consent for anonymous analytics
- `retention_period`: Data retention period in days

#### **2. wellness_logs.csv** - Mental Health Tracking
```csv
log_id,student_hash,mood_score,anxiety_score,timestamp,privacy_level,anonymized
WL001,a1b2c3d4,7,4,2024-01-15 10:30:00,high,true
WL002,e5f6g7h8,5,6,2024-01-15 14:20:00,medium,true
WL003,i9j0k1l2,8,3,2024-01-15 16:45:00,high,true
```
**Fields:**
- `log_id`: Unique wellness log identifier
- `student_hash`: Hashed student ID for privacy
- `mood_score`: Mood rating (1-10 scale)
- `anxiety_score`: Anxiety level (1-10 scale)
- `timestamp`: When the assessment was taken
- `privacy_level`: Data sensitivity level
- `anonymized`: Whether data has been anonymized

#### **3. academic_performance.csv** - Academic Data
```csv
record_id,student_hash,subject_category,performance_band,semester,completion_status,anonymized
AP001,a1b2c3d4,STEM,high,2024-1,completed,true
AP002,e5f6g7h8,Arts,medium,2024-1,in_progress,true
AP003,i9j0k1l2,Science,high,2024-1,completed,true
```
**Fields:**
- `record_id`: Academic record identifier
- `student_hash`: Hashed student identifier
- `subject_category`: Subject area (STEM, Arts, Science, etc.)
- `performance_band`: Performance level (high, medium, low)
- `semester`: Academic period
- `completion_status`: Course completion status
- `anonymized`: Anonymization flag

#### **4. ai_interactions.csv** - AI Chat History
```csv
interaction_id,student_hash,message_type,language_detected,response_type,timestamp,privacy_level
AI001,a1b2c3d4,wellness_query,English,supportive,2024-01-15 10:30:00,high
AI002,e5f6g7h8,study_help,Hindi,academic,2024-01-15 14:20:00,medium
AI003,i9j0k1l2,career_guidance,Bengali,advisory,2024-01-15 16:45:00,high
```
**Fields:**
- `interaction_id`: Unique interaction identifier
- `student_hash`: Hashed student ID
- `message_type`: Type of student query
- `language_detected`: Auto-detected language
- `response_type`: Type of AI response provided
- `timestamp`: Interaction timestamp
- `privacy_level`: Data sensitivity classification

#### **5. crisis_interventions.csv** - Emergency Support
```csv
intervention_id,student_hash,risk_level,intervention_type,timestamp,follow_up_required,anonymized
CI001,a1b2c3d4,L2,supportive_response,2024-01-15 10:30:00,true,true
CI002,e5f6g7h8,L1,wellness_check,2024-01-15 14:20:00,false,true
CI003,i9j0k1l2,L3,emergency_protocol,2024-01-15 16:45:00,true,true
```
**Fields:**
- `intervention_id`: Crisis intervention identifier
- `student_hash`: Anonymized student identifier
- `risk_level`: L1 (low), L2 (medium), L3 (high)
- `intervention_type`: Type of intervention provided
- `timestamp`: When intervention occurred
- `follow_up_required`: Whether follow-up is needed
- `anonymized`: Anonymization status

#### **6. courses.csv** - Course Catalog
```csv
course_id,course_name,subject_area,difficulty_level,language_available,credits
CS101,Introduction to Programming,Computer Science,beginner,English|Hindi,3
MATH201,Advanced Calculus,Mathematics,intermediate,English|Bengali,4
BIO301,Molecular Biology,Biology,advanced,English,3
```
**Fields:**
- `course_id`: Unique course identifier
- `course_name`: Course title
- `subject_area`: Academic discipline
- `difficulty_level`: Course difficulty
- `language_available`: Available instruction languages
- `credits`: Credit hours

#### **7. sahayaks.csv** - AI Mentor Profiles
```csv
sahayak_id,name,specialization,languages,availability,personality_type
SAH001,Dr. Wellness,Mental Health,English|Hindi|Bengali,24/7,empathetic
SAH002,Study Buddy,Academic Support,English|Hindi,weekdays,encouraging
SAH003,Career Guide,Career Counseling,English|Bengali,business_hours,practical
```
**Fields:**
- `sahayak_id`: AI mentor identifier
- `name`: Mentor persona name
- `specialization`: Area of expertise
- `languages`: Supported languages
- `availability`: When mentor is available
- `personality_type`: Interaction style

#### **8. feedback.csv** - Student Feedback
```csv
feedback_id,student_hash,interaction_type,rating,language_used,timestamp,anonymized
FB001,a1b2c3d4,wellness_chat,5,English,2024-01-15 10:30:00,true
FB002,e5f6g7h8,study_tips,4,Hindi,2024-01-15 14:20:00,true
FB003,i9j0k1l2,career_advice,5,Bengali,2024-01-15 16:45:00,true
```
**Fields:**
- `feedback_id`: Feedback record identifier
- `student_hash`: Anonymized student ID
- `interaction_type`: Type of interaction rated
- `rating`: Student rating (1-5 scale)
- `language_used`: Language of interaction
- `timestamp`: Feedback timestamp
- `anonymized`: Anonymization status

---

## 🔒 **Privacy Protection Mechanisms**

### **K-Anonymity Implementation**
```python
def apply_k_anonymity(df: pd.DataFrame, k: int = 3) -> pd.DataFrame:
    """
    Ensures k-anonymity by grouping records so that each
    individual cannot be distinguished from at least k-1 others
    """
    # Group by quasi-identifiers
    grouped = df.groupby(['age_band', 'subject_category', 'semester'])
    
    # Remove groups with less than k records
    filtered_groups = grouped.filter(lambda x: len(x) >= k)
    
    return filtered_groups
```

### **Student ID Hashing**
```python
import hashlib

def hash_student_id(student_id: str) -> str:
    """Create privacy-preserving hash of student ID"""
    return hashlib.sha256(student_id.encode()).hexdigest()[:8]
```

### **Data Retention Policies**
- **High Privacy**: 30-60 days retention
- **Medium Privacy**: 60-90 days retention
- **Low Privacy**: 90-180 days retention
- **Anonymous Analytics**: Indefinite (aggregated only)

---

## 📊 **Analytics Capabilities**

### **Privacy-Preserving Analytics**
```python
class CSVDataProcessor:
    def generate_analytics_report(self, anonymization_k: int = 3):
        """Generate insights while maintaining k-anonymity"""
        
        # Wellness trends
        wellness_trends = self.analyze_wellness_patterns(k=anonymization_k)
        
        # Academic performance
        academic_insights = self.analyze_academic_performance(k=anonymization_k)
        
        # Language usage patterns
        language_stats = self.analyze_language_preferences(k=anonymization_k)
        
        return {
            'wellness_trends': wellness_trends,
            'academic_insights': academic_insights,
            'language_statistics': language_stats,
            'anonymization_level': f"k={anonymization_k}"
        }
```

### **Sample Analytics Output**
```json
{
  "wellness_trends": {
    "average_mood": 6.8,
    "anxiety_patterns": "higher during exam periods",
    "improvement_rate": "73% show mood improvement"
  },
  "academic_insights": {
    "high_performers": "35% of students",
    "support_needed": "STEM subjects show higher stress",
    "completion_rate": "89% course completion"
  },
  "language_statistics": {
    "english_users": "45%",
    "hindi_users": "35%", 
    "bengali_users": "20%",
    "multilingual": "15% use multiple languages"
  }
}
```

---

## 🛠️ **Data Processing Features**

### **Synthetic Data Generation**
```python
def generate_synthetic_students(count: int = 40) -> pd.DataFrame:
    """Generate realistic synthetic student data"""
    
    # Demographics with realistic distributions
    age_bands = ['18-20', '20-22', '22-24', '24+']
    languages = ['English', 'Hindi', 'Bengali']
    interests = ['coding', 'music', 'reading', 'sports', 'art', 'science']
    
    # Generate with realistic patterns
    students = []
    for i in range(count):
        student = {
            'student_id': f'STU{i+1:03d}',
            'age_band': random.choice(age_bands),
            'language_pref': random.choice(languages),
            'interests': '|'.join(random.sample(interests, k=3)),
            'enrollment_date': generate_realistic_date(),
            'data_consent': random.choice([True, False], p=[0.85, 0.15]),
            'anonymous_sharing': random.choice([True, False], p=[0.70, 0.30]),
            'retention_period': random.choice([30, 60, 90, 180])
        }
        students.append(student)
    
    return pd.DataFrame(students)
```

### **Multi-Language Data Support**
- **Script Detection**: Automatic detection of Devanagari, Bengali, Latin scripts
- **Language Tagging**: All interactions tagged with detected language
- **Cultural Context**: Responses adapted to cultural and regional context
- **Localized Resources**: Crisis support resources by language/region

---

## 🚀 **Scalability Design**

### **From CSV to Production**
```python
# Easy migration path to production databases
class DataAdapter:
    def __init__(self, mode='csv'):
        if mode == 'csv':
            self.storage = CSVStorage()
        elif mode == 'postgres':
            self.storage = PostgreSQLStorage()
        elif mode == 'firestore':
            self.storage = FirestoreStorage()
    
    def save_student_data(self, data):
        return self.storage.save(data)
```

### **Performance Optimization**
- **Indexed CSV reading** with pandas optimization
- **Chunked processing** for large datasets
- **Memory-efficient** analytics with streaming
- **Caching layer** for frequent queries

---

## 📈 **Usage Examples**

### **Loading Student Data**
```python
from services.data_processing import CSVDataProcessor

processor = CSVDataProcessor()

# Load and analyze student data
students = processor.load_students()
wellness_data = processor.load_wellness_logs()

# Generate privacy-preserving insights
analytics = processor.generate_analytics_report(anonymization_k=3)
```

### **Multi-Language Analytics**
```python
# Analyze language usage patterns
language_stats = processor.analyze_language_usage()

# Output:
# {
#   'most_used': 'English',
#   'growth_language': 'Hindi', 
#   'crisis_support_by_language': {
#     'English': 45, 'Hindi': 32, 'Bengali': 23
#   }
# }
```

---

## 🔄 **Data Flow Architecture**

```
📥 Student Input (Multi-Language)
    ↓
🤖 Gemini AI Processing
    ↓
🔒 Privacy Layer (Hashing, Anonymization)
    ↓
📊 CSV Storage (Structured Data)
    ↓
📈 Analytics Engine (K-Anonymous Insights)
    ↓
📋 Reports & Dashboards
```

---

## ✅ **Production Ready Features**

- **Data Validation**: Comprehensive CSV validation and error handling
- **Backup & Recovery**: Automated CSV backup and versioning
- **Migration Tools**: Easy transition from CSV to database systems
- **Monitoring**: Data quality and privacy compliance monitoring
- **Audit Trails**: Complete anonymized interaction logging

**This CSV-based architecture provides a solid foundation for hackathon demonstrations while being production-scalable with proper privacy protection and multi-language support!** 🏆
