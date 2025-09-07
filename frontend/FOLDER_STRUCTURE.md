# Sahay Frontend Folder Structure

```
frontend/
├── FRONTEND_README.md              # Complete frontend documentation
├── static/                         # Static assets (CSS, JS, Images)
│   ├── css/
│   │   ├── sahay.css              # Main stylesheet with base styles
│   │   └── components.css         # Component-specific styles
│   ├── js/
│   │   └── sahay.js               # Main JavaScript application logic
│   └── images/                    # Static images and assets
└── templates/                     # Django HTML templates
    ├── base/
    │   └── base.html              # Base template with navigation & layout
    ├── core/                      # Core application pages
    │   ├── home.html              # Landing page (/)
    │   └── dashboard.html         # Student dashboard (/dashboard/)
    ├── wellness/                  # Wellness & mental health features
    │   ├── index.html             # Wellness overview (/wellness/)
    │   ├── chat.html              # AI chat interface (/wellness/chat/)
    │   └── check.html             # Wellness check-in (/wellness/check/)
    ├── learning/                  # Learning & career management
    │   ├── index.html             # Learning dashboard (/learning/)
    │   └── career.html            # Career planning (/learning/career/)
    └── analytics/                 # Analytics & insights
        └── index.html             # Analytics dashboard (/analytics/)
```

## File Descriptions

### 📁 Static Assets (`/static/`)

#### CSS Files
- **`sahay.css`**: Primary stylesheet containing global styles, layout, navigation, and core component styles
- **`components.css`**: Specialized styles for interactive components (chat, mood tracker, cards, charts)

#### JavaScript Files
- **`sahay.js`**: Complete frontend application logic including:
  - Application initialization
  - Multi-language support
  - Theme management
  - Interactive components (chat, mood tracker, course cards)
  - API integration
  - Utility functions

#### Images Directory
- **Purpose**: Storage for logos, icons, illustrations, and other static images
- **Format Support**: PNG, JPG, SVG, WebP
- **Organization**: Organized by feature/section

### 📁 Templates (`/templates/`)

#### Base Template (`/base/`)
- **`base.html`**: Master template providing:
  - HTML structure and meta tags
  - Navigation menu with active state management
  - Footer and global elements
  - CSS/JS inclusions
  - Multi-language support infrastructure

#### Core Pages (`/core/`)
- **`home.html`**: Platform landing page featuring:
  - Hero section with platform introduction
  - Feature highlights and statistics
  - Call-to-action buttons
  - Language selection interface

- **`dashboard.html`**: Personalized student dashboard with:
  - Recent activity overview
  - Quick access widgets
  - Wellness and learning summaries
  - Notification center

#### Wellness Section (`/wellness/`)
- **`index.html`**: Wellness hub containing:
  - Mood tracking interface
  - Wellness status overview
  - Quick access to chat and check-in
  - Historical wellness data

- **`chat.html`**: AI-powered chat interface featuring:
  - Real-time messaging with Gemini AI
  - Multi-language conversation support
  - Message history and typing indicators
  - Privacy-protected interactions

- **`check.html`**: Comprehensive wellness assessment with:
  - Structured questionnaire forms
  - Mood and anxiety scoring systems
  - Risk assessment calculations
  - Personalized recommendations

#### Learning Section (`/learning/`)
- **`index.html`**: Learning management dashboard with:
  - Course catalog and browsing
  - Progress tracking visualizations
  - Difficulty-based filtering
  - Enrollment management

- **`career.html`**: Career planning interface featuring:
  - Career path exploration tools
  - Skills assessment matrices
  - Dual-track planning (current/explore)
  - Goal setting and milestone tracking

#### Analytics Section (`/analytics/`)
- **`index.html`**: Data insights dashboard containing:
  - Statistical overview cards
  - Interactive charts and visualizations
  - Trend analysis displays
  - K-anonymized pattern insights

## Integration Points

### Django Template System
- All templates extend `base/base.html`
- Django template tags for dynamic content
- Context variables from Django views
- CSRF protection on all forms

### Static File Integration
- CSS files linked in base template
- JavaScript modules loaded conditionally
- Image assets referenced via Django static files
- CDN integration for external libraries

### API Endpoints
Templates integrate with backend APIs:
- `/api/chat/` - Chat message processing
- `/api/wellness/mood/` - Mood score submission
- `/api/analytics/summary/` - Analytics data
- `/api/dashboard/summary/` - Dashboard content

### Multi-language Support
- Client-side translation system
- Language preference persistence
- Dynamic content switching
- Cultural adaptation considerations

This organized structure ensures maintainable, scalable frontend code with clear separation of concerns and optimal user experience across all platform features.
