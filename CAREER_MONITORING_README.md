# Career Monitoring Service

## Overview

The Career Monitoring Service is a background service that automatically monitors student interests and generates personalized career recommendations using Gemini AI. It stores these recommendations in CSV files for fast retrieval by the web application.

## Features

- **Automatic Interest Monitoring**: Detects changes in student interests
- **AI-Powered Recommendations**: Uses Gemini AI to generate personalized career suggestions
- **Course Career Paths**: Generates comprehensive career paths for each course
- **CSV Storage**: Stores recommendations in CSV files for fast access
- **Fallback System**: Provides fallback recommendations if AI fails
- **Scheduled Updates**: Can run periodically to keep recommendations fresh

## Files Created

### 1. `data/input/student_interests.csv`
Stores personalized career recommendations for each student:
- `user_id`: Student's unique ID
- `username`: Student's username
- `name`: Student's name
- `hometown`: Student's hometown
- `course`: Student's course
- `interests`: Student's current interests
- `career_recommendations`: JSON string of AI-generated recommendations
- `last_updated`: Timestamp of last update
- `recommendation_count`: Number of recommendations

### 2. `data/input/course_careers.csv`
Stores career paths for each course:
- `course_name`: Name of the course
- `career_paths`: JSON string of career paths
- `last_updated`: Timestamp of last update
- `path_count`: Number of career paths

## Usage

### Manual Execution

```bash
# Run the service once
python services/career_monitoring_service.py

# Or use Django management command
python manage.py update_career_recommendations
```

### Scheduled Execution

```bash
# Run the scheduler (runs every 6 hours)
python run_career_monitor.py
```

## How It Works

1. **Interest Monitoring**: 
   - Compares current interests with stored interests
   - Detects new users
   - Checks for outdated recommendations (>7 days old)

2. **Recommendation Generation**:
   - Uses Gemini AI to generate personalized recommendations
   - Connects student's course with their interests
   - Includes local context (hometown, Indian market)
   - Falls back to predefined recommendations if AI fails

3. **Course Career Paths**:
   - Generates comprehensive career paths for each course
   - Includes salary ranges, skills, and industry information
   - Updates when course is new or paths are outdated (>30 days)

## Integration with Web Application

The `CareerPlanningView` in `learning/views.py` now reads from CSV files instead of calling Gemini directly:

- **AI-Powered Recommendations**: Reads from `student_interests.csv`
- **All Career Paths**: Reads from `course_careers.csv`
- **Fallback**: Uses demo data if CSV files are empty

## Benefits

1. **Performance**: Fast page loads (no AI calls during page requests)
2. **Reliability**: Fallback recommendations ensure content is always available
3. **Scalability**: Pre-generated recommendations reduce AI API calls
4. **Consistency**: Same recommendations until interests change
5. **Cost Efficiency**: Reduces Gemini API usage

## Monitoring

The service logs all activities to:
- Console output
- `logs/career_monitor.log` (if using scheduler)

## Configuration

- **Student Recommendations**: Updated when interests change or >7 days old
- **Course Career Paths**: Updated when new course or >30 days old
- **Scheduler**: Runs every 6 hours (configurable in `run_career_monitor.py`)

## Error Handling

- JSON parsing errors fall back to predefined recommendations
- Missing CSV files are created automatically
- AI failures use fallback recommendations
- All errors are logged for debugging
