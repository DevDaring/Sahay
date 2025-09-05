#!/usr/bin/env python3
"""
Demo script for Sahay CSV Data Processing
Demonstrates the key features of the CSV-based data system
"""

import sys
import os
import pandas as pd
from datetime import datetime, timedelta

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from services.data_processing import CSVDataProcessor

def print_section(title):
    """Print a formatted section header"""
    print(f"\n{'='*50}")
    print(f" {title}")
    print(f"{'='*50}")

def demo_basic_data_access():
    """Demonstrate basic data access functionality"""
    print_section("BASIC DATA ACCESS")
    
    processor = CSVDataProcessor()
    
    # Students data
    students = processor.get_students()
    if not students.empty:
        print(f"📊 Total Students: {len(students)}")
        if 'language_pref' in students.columns:
            print(f"📊 Languages: {students['language_pref'].value_counts().to_dict()}")
        if 'age_band' in students.columns:
            print(f"📊 Age Distribution: {students['age_band'].value_counts().to_dict()}")
    else:
        print("⚠️ No student data available")
    
    # Wellness sessions
    sessions = processor.get_wellness_sessions()
    print(f"\n💭 Total Wellness Sessions: {len(sessions)}")
    if not sessions.empty:
        print(f"💭 Risk Levels: {sessions['risk_level'].value_counts().to_dict()}")
        print(f"💭 Average Mood Score: {sessions['mood_score'].mean():.1f}/10")
        print(f"💭 Average Anxiety Score: {sessions['anxiety_score'].mean():.1f}/10")
    
    # Sahayaks
    sahayaks = processor.get_sahayaks()
    print(f"\n👥 Total Mentors: {len(sahayaks)}")
    if not sahayaks.empty:
        print(f"👥 Average Rating: {sahayaks['rating'].mean():.1f}/5.0")
        print(f"👥 Availability: {sahayaks['availability'].value_counts().to_dict()}")

def demo_student_analysis():
    """Demonstrate individual student analysis"""
    print_section("STUDENT ANALYSIS")
    
    processor = CSVDataProcessor()
    students = processor.get_students()
    
    if students.empty:
        print("❌ No student data available")
        return
    
    # Analyze first student
    student_id = students.iloc[0]['student_id']
    student_info = students.iloc[0]
    
    print(f"🎓 Analyzing Student: {student_id}")
    print(f"   Age Band: {student_info['age_band']}")
    if 'language_pref' in student_info:
        print(f"   Language: {student_info['language_pref']}")
    print(f"   Interests: {', '.join(student_info['interests']) if isinstance(student_info['interests'], list) else student_info['interests']}")
    
    # Risk assessment
    risk_assessment = processor.get_student_risk_assessment(student_id)
    print(f"\n🔍 Risk Assessment:")
    print(f"   Current Risk Level: {risk_assessment['risk_level']}")
    print(f"   Trend: {risk_assessment['trend']}")
    print(f"   Last Session: {risk_assessment.get('last_session', 'None')}")
    print(f"   Session Count: {risk_assessment.get('session_count', 0)}")
    
    # Personalized actions
    actions = processor.get_personalized_actions(student_id)
    print(f"\n📋 Recommended Actions:")
    for i, action in enumerate(actions, 1):
        print(f"   {i}. [{action['category'].upper()}] {action['action_text']}")
        print(f"      Duration: {action['duration_minutes']} minutes | Priority: {action['priority']}")

def demo_analytics_report():
    """Demonstrate analytics report generation"""
    print_section("ANALYTICS REPORT")
    
    processor = CSVDataProcessor()
    
    # Generate comprehensive report
    report = processor.generate_analytics_report(time_window_days=30)
    
    print(f"📈 Analytics Report (Last 30 days)")
    print(f"   Report Date: {report['report_date']}")
    print(f"   Total Students: {report['total_students']}")
    print(f"   Active Students: {report['active_students']}")
    
    # Wellness metrics
    wellness = report.get('wellness_metrics', {})
    print(f"\n💚 Wellness Metrics:")
    print(f"   Average Mood: {wellness.get('avg_mood_score', 0):.1f}/10")
    print(f"   Average Anxiety: {wellness.get('avg_anxiety_score', 0):.1f}/10")
    print(f"   High Risk %: {wellness.get('high_risk_percentage', 0):.1f}%")
    print(f"   Total Sessions: {wellness.get('total_sessions', 0)}")
    
    # Learning metrics
    learning = report.get('learning_metrics', {})
    print(f"\n📚 Learning Metrics:")
    print(f"   Average Quiz Score: {learning.get('avg_quiz_score', 0):.1f}%")
    print(f"   Average Session Duration: {learning.get('avg_duration', 0):.0f} minutes")
    print(f"   Total Learning Sessions: {learning.get('total_sessions', 0)}")
    
    # Patterns detected
    patterns = report.get('patterns', [])
    print(f"\n🔍 Patterns Detected: {len(patterns)}")
    for pattern in patterns[:3]:  # Show first 3 patterns
        print(f"   • {pattern['type']}: {pattern['description']}")
        print(f"     Severity: {pattern['severity']} | Students: {pattern['k_count']}")
    
    # Recommendations
    recommendations = report.get('recommendations', [])
    print(f"\n💡 Recommendations:")
    for i, rec in enumerate(recommendations[:5], 1):  # Show first 5 recommendations
        print(f"   {i}. {rec}")

def demo_privacy_features():
    """Demonstrate privacy and k-anonymity features"""
    print_section("PRIVACY FEATURES")
    
    processor = CSVDataProcessor()
    
    # Export wellness sessions with privacy
    print("🔒 Exporting wellness sessions with privacy protection...")
    try:
        output_path = processor.export_wellness_sessions()
        if output_path:
            print(f"   ✅ Exported to: {output_path}")
            
            # Show sample of anonymized data
            df = pd.read_csv(output_path)
            print(f"   📊 Anonymized records: {len(df)}")
            if not df.empty:
                print("   Sample columns:", list(df.columns))
        else:
            print("   ⚠️ No data to export (insufficient for k-anonymity)")
    except Exception as e:
        print(f"   ❌ Export failed: {e}")
    
    # Show k-anonymity in action
    sessions = processor.get_wellness_sessions()
    if not sessions.empty:
        print(f"\n🔐 K-Anonymity Protection:")
        risk_groups = sessions.groupby('risk_level').size()
        print(f"   Risk level groups: {risk_groups.to_dict()}")
        valid_groups = risk_groups[risk_groups >= processor.k_threshold]
        print(f"   Groups meeting k-anonymity (k≥{processor.k_threshold}): {len(valid_groups)}")

def demo_csv_data_structure():
    """Show the CSV data files and their structure"""
    print_section("CSV DATA STRUCTURE")
    
    processor = CSVDataProcessor()
    
    print("📁 Available CSV Data Files:")
    for table_name, df in processor.data.items():
        if not df.empty:
            print(f"   📄 {table_name}.csv:")
            print(f"      Records: {len(df)}")
            print(f"      Columns: {list(df.columns)}")
            print(f"      Sample: {df.iloc[0].to_dict()}" if len(df) > 0 else "      (Empty)")
            print()

def main():
    """Run the complete demo"""
    print("🚀 Sahay Platform - CSV Data Processing Demo")
    print("=" * 50)
    
    try:
        demo_basic_data_access()
        demo_student_analysis()
        demo_analytics_report()
        demo_privacy_features()
        demo_csv_data_structure()
        
        print_section("DEMO COMPLETE")
        print("✅ All features demonstrated successfully!")
        print("📝 Check the CSV_DATA_README.md for detailed documentation")
        print("🗂️ CSV files are located in: data/input/")
        print("📊 Generated reports saved to: data/output/")
        
    except Exception as e:
        print(f"\n❌ Demo failed with error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
