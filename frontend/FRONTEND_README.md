# Sahay Platform Frontend Documentation

## 🎯 Overview

The Sahay Platform frontend is a comprehensive Django-based web application designed to provide a seamless, multi-language interface for student wellness and learning management. The frontend integrates AI-powered features with privacy-first design principles.

## 📁 Frontend Structure

```
frontend/
├── static/
│   ├── css/
│   │   ├── sahay.css          # Main stylesheet
│   │   └── components.css     # Component-specific styles
│   ├── js/
│   │   └── sahay.js          # Main JavaScript functionality
│   └── images/               # Static images and assets
└── templates/
    ├── base/
    │   └── base.html         # Base template with navigation
    ├── core/
    │   ├── home.html         # Landing page
    │   └── dashboard.html    # Student dashboard
    ├── wellness/
    │   ├── index.html        # Wellness overview
    │   ├── chat.html         # AI Chat interface
    │   └── check.html        # Wellness check-in
    ├── learning/
    │   ├── index.html        # Learning dashboard
    │   └── career.html       # Career planning
    └── analytics/
        └── index.html        # Analytics dashboard
```

## 🏠 Pages Overview

### 1. Home Page (`/`)
**File**: `templates/core/home.html`

**Purpose**: Landing page introducing the Sahay platform

**Features**:
- Multi-language welcome message (English, Hindi, Bengali)
- Platform overview with key statistics
- Quick access buttons to main sections
- Responsive hero section with call-to-action

**Key Components**:
- Hero banner with platform introduction
- Feature highlights (Wellness, Learning, Analytics)
- Statistics overview (Total students, Active sessions)
- Language selector
- Quick start navigation

### 2. Dashboard (`/dashboard/`)
**File**: `templates/core/dashboard.html`

**Purpose**: Personalized student dashboard

**Features**:
- Recent activity overview
- Quick access widgets
- Wellness status summary
- Learning progress tracking
- Upcoming actions and recommendations

**Key Components**:
- Wellness status card
- Recent activities timeline
- Quick action buttons
- Progress indicators
- Notification center

### 3. Wellness Section

#### 3.1 Wellness Overview (`/wellness/`)
**File**: `templates/wellness/index.html`

**Purpose**: Central hub for wellness activities

**Features**:
- Mood tracking interface
- Quick wellness check-in
- Access to AI chat support
- Recent wellness history
- Mental health resources

**Key Components**:
- Mood selector (emoji-based)
- Wellness score display
- Quick check-in form
- Chat access button
- Historical mood chart

#### 3.2 AI Chat Interface (`/wellness/chat/`)
**File**: `templates/wellness/chat.html`

**Purpose**: Conversational AI support using Google Gemini

**Features**:
- Real-time chat with AI counselor
- Multi-language support (English, Hindi, Bengali)
- Contextual wellness advice
- Conversation history
- Privacy-protected interactions

**Key Components**:
- Chat message container
- Message input with auto-resize
- Typing indicators
- Send button with animations
- Language-aware responses

**Technical Details**:
- WebSocket-ready architecture
- CSRF protection
- Message validation
- Response streaming capability

#### 3.3 Wellness Check-in (`/wellness/check/`)
**File**: `templates/wellness/check.html`

**Purpose**: Comprehensive wellness assessment

**Features**:
- Structured wellness questionnaire
- Mood and anxiety scoring
- Risk assessment
- Personalized recommendations
- Progress tracking

**Key Components**:
- Multi-step form interface
- Sliding scale inputs
- Progress indicators
- Submit confirmation
- Results summary

### 4. Learning Section

#### 4.1 Learning Dashboard (`/learning/`)
**File**: `templates/learning/index.html`

**Purpose**: Learning management and course access

**Features**:
- Course catalog browsing
- Progress tracking
- Difficulty-based filtering
- Personalized recommendations
- Learning analytics

**Key Components**:
- Course grid layout
- Search and filter bar
- Progress indicators
- Difficulty badges
- Quick enroll buttons

**Course Card Features**:
- Course title and description
- Difficulty level indicator
- Duration estimate
- Prerequisites display
- Enrollment status

#### 4.2 Career Planning (`/learning/career/`)
**File**: `templates/learning/career.html`

**Purpose**: Career exploration and planning tools

**Features**:
- Career path exploration
- Skills assessment
- Dual-track planning (current/explore)
- Industry insights
- Goal setting interface

**Key Components**:
- Career path cards
- Skills matrix display
- Progress tracking
- Recommendation engine
- Goal milestone tracker

**Career Card Features**:
- Field description
- Required skills tags
- Typical roles list
- Growth trajectory
- Explore button

### 5. Analytics Dashboard (`/analytics/`)
**File**: `templates/analytics/index.html`

**Purpose**: Data insights and pattern analysis

**Features**:
- Wellness trend analysis
- Learning progress visualization
- Risk pattern detection (k-anonymized)
- Performance metrics
- Comparative analytics

**Key Components**:
- Statistics overview cards
- Interactive charts
- Trend visualizations
- Pattern insights
- Export functionality

**Analytics Cards**:
- Total sessions
- Average mood score
- Completion rates
- Risk level distribution
- Learning progress

## 🎨 Design System

### Color Palette
```css
:root {
    --primary: #6B5B95;        /* Purple - Main brand */
    --secondary: #88D8B0;      /* Green - Success/Growth */
    --accent: #FFCC5C;         /* Yellow - Attention */
    --background: #F7F9FC;     /* Light gray - Background */
    --text: #2C3E50;          /* Dark blue - Text */
    --success: #27AE60;        /* Green - Success states */
    --warning: #F39C12;        /* Orange - Warnings */
    --error: #E74C3C;          /* Red - Errors */
    --white: #FFFFFF;          /* Pure white */
    --gray-light: #ECF0F1;     /* Light gray - Borders */
    --gray: #95A5A6;           /* Medium gray - Secondary text */
}
```

### Typography
- **Primary Font**: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto
- **Headings**: Font weights 600-700
- **Body Text**: Font weight 400, line-height 1.6
- **Small Text**: Font size 0.875rem for metadata

### Layout Principles
- **Mobile-first responsive design**
- **Grid-based layouts** with CSS Grid and Flexbox
- **Consistent spacing** using 8px base unit
- **Card-based components** with subtle shadows
- **Maximum content width**: 1200px

## 🔧 JavaScript Functionality

### Core Features

#### 1. Application Initialization
```javascript
SahayApp.init() // Initializes all components
```

#### 2. Multi-language Support
- Dynamic content translation
- Language preference persistence
- Automatic language detection

#### 3. Theme Management
- Dark/light theme toggle
- User preference storage
- System theme detection

#### 4. Interactive Components

**Mood Tracker**:
- Visual mood selection
- API integration for data submission
- Real-time feedback

**Chat Interface**:
- Message sending/receiving
- Typing indicators
- Auto-scroll functionality
- Message history

**Course Management**:
- Course card interactions
- Progress tracking
- Enrollment management

**Analytics Visualization**:
- Chart rendering (Chart.js integration)
- Data refresh capabilities
- Interactive elements

### API Integration

#### Endpoints Used:
- `POST /api/wellness/mood/` - Submit mood scores
- `POST /api/chat/` - Send chat messages
- `GET /api/analytics/summary/` - Fetch analytics data
- `GET /api/dashboard/summary/` - Load dashboard data

#### Authentication:
- CSRF token integration
- Session-based authentication
- Student ID management

## 📱 Responsive Design

### Breakpoints:
- **Mobile**: 480px and below
- **Tablet**: 768px and below
- **Desktop**: 1024px and above

### Mobile Optimizations:
- Touch-friendly button sizes (minimum 44px)
- Simplified navigation
- Stacked layouts
- Optimized form inputs
- Reduced visual complexity

### Tablet Adaptations:
- Two-column layouts
- Medium-sized interactive elements
- Balanced information density

### Desktop Features:
- Multi-column layouts
- Hover interactions
- Advanced filtering
- Sidebar navigation

## 🔒 Privacy & Security

### Data Protection:
- **K-anonymity compliance** for analytics
- **Local storage encryption** for sensitive data
- **CSRF protection** on all forms
- **Input validation** and sanitization

### Privacy Features:
- Anonymous chat options
- Data retention controls
- Consent management
- Minimal data collection

## 🌐 Multi-language Support

### Supported Languages:
1. **English** (Default)
2. **Hindi** (हिंदी)
3. **Bengali** (বাংলা)

### Implementation:
- Client-side translation system
- Language preference persistence
- Dynamic content switching
- Cultural adaptation considerations

### Translation Keys:
```javascript
const translations = {
    'welcome': ['Welcome to Sahay', 'सहाय में आपका स्वागत है', 'সহায়তে স্বাগতম'],
    'wellness': ['Wellness', 'कल्याण', 'সুস্থতা'],
    'learning': ['Learning', 'शिक्षा', 'শিক্ষা'],
    'analytics': ['Analytics', 'विश्लेषण', 'বিশ্লেষণ']
}
```

## 🚀 Performance Optimizations

### Loading Performance:
- **Lazy loading** for images and components
- **Minified CSS/JS** for production
- **CDN integration** for external libraries
- **Gzip compression** for static assets

### Runtime Performance:
- **Event delegation** for dynamic content
- **Debounced API calls** for search/filter
- **Efficient DOM manipulation**
- **Memory management** for single-page features

### Caching Strategy:
- **Browser caching** for static assets
- **LocalStorage** for user preferences
- **API response caching** where appropriate

## 🧪 Testing Considerations

### Manual Testing Checklist:
- [ ] All navigation links work correctly
- [ ] Forms submit and validate properly
- [ ] Chat interface sends/receives messages
- [ ] Mood tracker saves selections
- [ ] Course cards are clickable
- [ ] Analytics data loads correctly
- [ ] Language switching works
- [ ] Theme toggle functions
- [ ] Mobile responsive design
- [ ] Cross-browser compatibility

### User Experience Testing:
- [ ] Page load times under 3 seconds
- [ ] Smooth animations and transitions
- [ ] Intuitive navigation flow
- [ ] Accessible color contrast
- [ ] Keyboard navigation support
- [ ] Screen reader compatibility

## 🔧 Development Setup

### Prerequisites:
- Django 5.2.6+
- Python 3.11+
- Modern web browser
- Internet connection (for CDN resources)

### Local Development:
1. Start Django development server
2. Access frontend at `http://127.0.0.1:8000/`
3. Use browser developer tools for debugging
4. Test across different devices/screen sizes

### File Modification:
- **Templates**: Edit HTML structure and Django template tags
- **Styles**: Modify CSS in `static/css/` directory
- **JavaScript**: Update functionality in `static/js/sahay.js`
- **Images**: Add assets to `static/images/` directory

## 📊 Analytics Integration

### Tracked Events:
- Page views and navigation
- Feature usage (chat, mood tracking, course access)
- User engagement metrics
- Error occurrences and performance issues

### Privacy-Compliant Analytics:
- No personal data collection
- Aggregated metrics only
- k-anonymity maintained
- User consent respected

## 🎯 Future Enhancements

### Planned Features:
1. **Progressive Web App (PWA)** capabilities
2. **Offline functionality** for core features
3. **Push notifications** for important updates
4. **Advanced analytics** dashboard
5. **Video chat** integration for counseling
6. **Gamification** elements for engagement
7. **AI-powered** course recommendations
8. **Social features** (study groups, peer support)

### Technical Improvements:
1. **WebSocket** implementation for real-time chat
2. **Service Worker** for offline support
3. **Code splitting** for better performance
4. **Unit testing** framework integration
5. **Accessibility** enhancements (WCAG 2.1 AA)
6. **SEO optimization** for public pages

## 📞 Support & Maintenance

### Browser Support:
- Chrome 90+
- Firefox 88+
- Safari 14+
- Edge 90+

### Maintenance Tasks:
- Regular security updates
- Performance monitoring
- User feedback incorporation
- Cross-browser testing
- Accessibility audits

---

**Last Updated**: September 7, 2025  
**Version**: 1.0.0  
**Author**: Sahay Development Team
