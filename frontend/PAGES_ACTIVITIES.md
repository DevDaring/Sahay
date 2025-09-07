# Sahay Frontend Pages & Activities Guide

## 🏠 Page-by-Page Activity Breakdown

### 1. HOME PAGE (`/`)
**Template**: `templates/core/home.html`

#### 🎯 Primary Activities
1. **Platform Introduction**
   - View Sahay platform overview
   - Read about wellness and learning features
   - Understand multi-language support

2. **Quick Navigation**
   - Access main sections (Wellness, Learning, Analytics)
   - Navigate to dashboard
   - Switch language preferences

3. **Statistics Overview**
   - View total registered students
   - See active wellness sessions
   - Check supported languages count

#### 💫 Interactive Elements
- **Language Selector**: Dropdown to choose between English, Hindi, Bengali
- **Get Started Button**: Direct navigation to dashboard
- **Feature Cards**: Clickable cards leading to respective sections
- **Hero Animation**: Animated welcome text and icons

#### 📊 Data Displayed
- Total students count (from CSV data)
- Active sessions in last 7 days
- Languages supported
- Platform statistics

---

### 2. DASHBOARD (`/dashboard/`)
**Template**: `templates/core/dashboard.html`

#### 🎯 Primary Activities
1. **Personal Overview**
   - View student profile summary
   - Check recent activity timeline
   - Monitor wellness status

2. **Quick Actions**
   - Start wellness check-in
   - Browse available courses
   - Access AI chat support
   - View analytics insights

3. **Progress Tracking**
   - Monitor learning progress
   - Track wellness trends
   - Review completed actions

#### 💫 Interactive Elements
- **Wellness Status Card**: Shows current mood/wellness level
- **Quick Action Buttons**: One-click access to main features
- **Recent Activities**: Scrollable timeline of user actions
- **Progress Bars**: Visual indicators for learning/wellness progress

#### 📊 Data Displayed
- Student profile information
- Recent wellness check-ins
- Learning course progress
- Upcoming recommended actions

---

### 3. WELLNESS OVERVIEW (`/wellness/`)
**Template**: `templates/wellness/index.html`

#### 🎯 Primary Activities
1. **Mood Tracking**
   - Quick mood check-in using emoji scale
   - View mood history and trends
   - Set daily wellness reminders

2. **Wellness Assessment**
   - Access comprehensive wellness check
   - Complete mental health screenings
   - View personalized recommendations

3. **Support Access**
   - Launch AI chat for immediate support
   - Browse wellness resources
   - Connect with mentors (Sahayaks)

#### 💫 Interactive Elements
- **Mood Emoji Selector**: 5-point scale with animated emojis
- **Wellness Score Display**: Circular progress indicator
- **Chat Launch Button**: Direct access to AI counselor
- **Check-in Calendar**: Visual mood history calendar

#### 📊 Data Displayed
- Current wellness score
- Mood trends over time
- Recent check-in history
- Personalized wellness recommendations

---

### 4. AI CHAT INTERFACE (`/wellness/chat/`)
**Template**: `templates/wellness/chat.html`

#### 🎯 Primary Activities
1. **AI Conversation**
   - Chat with Google Gemini AI counselor
   - Receive personalized wellness advice
   - Express concerns and emotions safely

2. **Multi-language Support**
   - Communicate in preferred language
   - Switch languages mid-conversation
   - Receive culturally appropriate responses

3. **Session Management**
   - Save important conversation points
   - Access chat history
   - End sessions when needed

#### 💫 Interactive Elements
- **Message Input Field**: Auto-expanding text area
- **Send Button**: Animated send action
- **Typing Indicators**: Shows when AI is responding
- **Message Bubbles**: Distinct styling for user/AI messages
- **Language Toggle**: Switch conversation language

#### 📊 Data Displayed
- Real-time conversation messages
- Message timestamps
- Conversation session duration
- AI response confidence indicators

---

### 5. WELLNESS CHECK-IN (`/wellness/check/`)
**Template**: `templates/wellness/check.html`

#### 🎯 Primary Activities
1. **Comprehensive Assessment**
   - Complete standardized mental health questionnaires
   - Rate anxiety and mood levels
   - Provide additional context and notes

2. **Risk Evaluation**
   - Automated risk level calculation
   - Immediate feedback on responses
   - Emergency resource access if needed

3. **Personalized Recommendations**
   - Receive tailored wellness actions
   - Schedule follow-up check-ins
   - Access relevant resources

#### 💫 Interactive Elements
- **Multi-step Form**: Progress indicator and navigation
- **Sliding Scale Inputs**: Visual mood/anxiety rating scales
- **Text Areas**: For additional notes and context
- **Submit Confirmation**: Clear completion feedback
- **Results Modal**: Immediate assessment results

#### 📊 Data Displayed
- Questionnaire progress
- Current mood/anxiety scores
- Risk level assessment
- Historical comparison data

---

### 6. LEARNING DASHBOARD (`/learning/`)
**Template**: `templates/learning/index.html`

#### 🎯 Primary Activities
1. **Course Discovery**
   - Browse available courses by category
   - Filter by difficulty level and duration
   - Search for specific topics or skills

2. **Enrollment Management**
   - Enroll in new courses
   - Track course progress
   - Access course materials

3. **Learning Analytics**
   - View learning statistics
   - Monitor skill development
   - Track time spent learning

#### 💫 Interactive Elements
- **Course Cards**: Hover effects and click interactions
- **Filter Controls**: Dropdown menus for category/difficulty
- **Search Bar**: Real-time course search
- **Progress Indicators**: Visual progress bars for enrolled courses
- **Enroll Buttons**: One-click course enrollment

#### 📊 Data Displayed
- Available courses list
- Course difficulty levels
- Prerequisites and duration
- Enrollment status and progress

---

### 7. CAREER PLANNING (`/learning/career/`)
**Template**: `templates/learning/career.html`

#### 🎯 Primary Activities
1. **Career Exploration**
   - Browse different career paths
   - Understand skill requirements
   - Learn about typical roles and growth

2. **Dual-Track Planning**
   - Set current career focus
   - Explore alternative career paths
   - Compare different options

3. **Skills Assessment**
   - Evaluate current skill levels
   - Identify skill gaps
   - Plan skill development roadmap

#### 💫 Interactive Elements
- **Career Path Cards**: Expandable cards with detailed information
- **Skill Tags**: Interactive skill requirement displays
- **Explore Buttons**: Deep dive into career details
- **Comparison Tool**: Side-by-side career path comparison
- **Progress Tracking**: Skill development progress bars

#### 📊 Data Displayed
- Career path descriptions
- Required skills matrix
- Typical roles and responsibilities
- Growth trajectory information
- Current vs. target skill levels

---

### 8. ANALYTICS DASHBOARD (`/analytics/`)
**Template**: `templates/analytics/index.html`

#### 🎯 Primary Activities
1. **Data Visualization**
   - View wellness trend charts
   - Analyze learning progress graphs
   - Monitor engagement metrics

2. **Pattern Recognition**
   - Identify wellness patterns (k-anonymized)
   - Understand learning behavior trends
   - Recognize at-risk indicators

3. **Comparative Analysis**
   - Compare personal progress to anonymized cohorts
   - Track improvement over time
   - Benchmark against goals

#### 💫 Interactive Elements
- **Interactive Charts**: Hover tooltips and drill-down capabilities
- **Time Range Selectors**: Choose analysis periods
- **Metric Cards**: Clickable statistics overview
- **Export Buttons**: Download analytics reports
- **Filter Controls**: Customize data views

#### 📊 Data Displayed
- Wellness trend charts
- Learning progress graphs
- Engagement statistics
- Risk pattern insights (k-anonymized)
- Performance benchmarks

---

## 🔄 Cross-Page Activities

### Navigation & User Flow
1. **Seamless Navigation**: Consistent navigation bar across all pages
2. **Context Preservation**: Maintain user state when switching between pages
3. **Quick Access**: One-click access to frequently used features
4. **Breadcrumb Navigation**: Clear path indication for complex workflows

### Data Synchronization
1. **Real-time Updates**: Live data refresh across pages
2. **Cross-section Integration**: Wellness data influencing learning recommendations
3. **Unified Profile**: Consistent user data across all sections
4. **Activity Tracking**: Comprehensive user journey recording

### Accessibility Features
1. **Keyboard Navigation**: Full keyboard accessibility
2. **Screen Reader Support**: ARIA labels and semantic HTML
3. **High Contrast Mode**: Accessibility-compliant color schemes
4. **Text Scaling**: Responsive text sizing for visual accessibility

### Performance Optimizations
1. **Lazy Loading**: Progressive content loading for faster page loads
2. **Caching Strategy**: Intelligent data caching for improved performance
3. **Responsive Images**: Adaptive image loading based on device capabilities
4. **Code Splitting**: Modular JavaScript loading for optimal performance

---

## 📱 Mobile-Specific Activities

### Touch Interactions
- **Swipe Gestures**: Navigate between sections on mobile
- **Tap Feedback**: Visual feedback for all touch interactions
- **Pull-to-Refresh**: Update data with pull gesture
- **Touch-Optimized**: Minimum 44px touch targets

### Mobile Navigation
- **Hamburger Menu**: Collapsible navigation for small screens
- **Bottom Navigation**: Quick access to main sections
- **Floating Action Buttons**: Primary actions easily accessible
- **Gesture Navigation**: Swipe-based navigation between pages

### Mobile-Optimized Features
- **Voice Input**: Speech-to-text for chat and forms
- **Camera Integration**: Quick photo uploads for profile
- **Offline Mode**: Limited functionality without internet
- **Push Notifications**: Important updates and reminders

This comprehensive breakdown ensures users understand all available activities and can effectively navigate and utilize the Sahay platform's frontend features.
