/**
 * Sahay Frontend JavaScript
 * Interactive functionality for the Sahay platform
 */

// Global app object
const SahayApp = {
    // Configuration
    config: {
        apiBaseUrl: '/api/',
        refreshInterval: 30000,
        chatRefreshInterval: 5000
    },

    // Initialize the application
    init() {
        this.setupEventListeners();
        this.initializeComponents();
        this.loadUserPreferences();
    },

    // Setup global event listeners
    setupEventListeners() {
        // Navigation active state
        this.setActiveNavigation();
        
        // Language switcher
        const langSwitcher = document.getElementById('language-selector');
        if (langSwitcher) {
            langSwitcher.addEventListener('change', this.changeLanguage.bind(this));
        }

        // Theme switcher
        const themeSwitcher = document.getElementById('theme-toggle');
        if (themeSwitcher) {
            themeSwitcher.addEventListener('click', this.toggleTheme.bind(this));
        }
    },

    // Initialize page-specific components
    initializeComponents() {
        const path = window.location.pathname;
        
        if (path.includes('/wellness/')) {
            this.initializeWellness();
        } else if (path.includes('/learning/')) {
            this.initializeLearning();
        } else if (path.includes('/analytics/')) {
            this.initializeAnalytics();
        } else if (path === '/' || path.includes('/dashboard/')) {
            this.initializeDashboard();
        }
    },

    // Set active navigation item
    setActiveNavigation() {
        const currentPath = window.location.pathname;
        const navLinks = document.querySelectorAll('.nav-link');
        
        navLinks.forEach(link => {
            const href = link.getAttribute('href');
            if (currentPath.startsWith(href) && href !== '/') {
                link.classList.add('active');
            } else if (currentPath === '/' && href === '/') {
                link.classList.add('active');
            } else {
                link.classList.remove('active');
            }
        });
    },

    // Language change handler
    changeLanguage(event) {
        const selectedLang = event.target.value;
        // Store preference
        localStorage.setItem('sahay_language', selectedLang);
        // Reload page or update content dynamically
        this.loadLanguageContent(selectedLang);
    },

    // Load language-specific content
    loadLanguageContent(language) {
        // Update page text based on selected language
        const translations = {
            'English': {
                'welcome': 'Welcome to Sahay',
                'wellness': 'Wellness',
                'learning': 'Learning',
                'analytics': 'Analytics'
            },
            'Hindi': {
                'welcome': 'सहाय में आपका स्वागत है',
                'wellness': 'कल्याण',
                'learning': 'शिक्षा',
                'analytics': 'विश्लेषण'
            },
            'Bengali': {
                'welcome': 'সহায়তে স্বাগতম',
                'wellness': 'সুস্থতা',
                'learning': 'শিক্ষা',
                'analytics': 'বিশ্লেষণ'
            }
        };

        const texts = translations[language] || translations['English'];
        
        // Update translatable elements
        document.querySelectorAll('[data-translate]').forEach(element => {
            const key = element.getAttribute('data-translate');
            if (texts[key]) {
                element.textContent = texts[key];
            }
        });
    },

    // Theme toggle
    toggleTheme() {
        const body = document.body;
        const isDark = body.classList.contains('dark-theme');
        
        if (isDark) {
            body.classList.remove('dark-theme');
            localStorage.setItem('sahay_theme', 'light');
        } else {
            body.classList.add('dark-theme');
            localStorage.setItem('sahay_theme', 'dark');
        }
    },

    // Load user preferences
    loadUserPreferences() {
        // Load theme preference
        const savedTheme = localStorage.getItem('sahay_theme');
        if (savedTheme === 'dark') {
            document.body.classList.add('dark-theme');
        }

        // Load language preference
        const savedLang = localStorage.getItem('sahay_language');
        if (savedLang) {
            const langSelector = document.getElementById('language-selector');
            if (langSelector) {
                langSelector.value = savedLang;
                this.loadLanguageContent(savedLang);
            }
        }
    }
};

// Wellness module
SahayApp.initializeWellness = function() {
    // Mood tracker
    this.initializeMoodTracker();
    
    // Chat interface
    this.initializeChatInterface();
    
    // Wellness check form
    this.initializeWellnessCheck();
};

SahayApp.initializeMoodTracker = function() {
    const moodButtons = document.querySelectorAll('.mood-button');
    moodButtons.forEach(button => {
        button.addEventListener('click', (e) => {
            // Remove active class from all buttons
            moodButtons.forEach(btn => btn.classList.remove('active'));
            // Add active class to clicked button
            e.target.classList.add('active');
            
            const moodValue = e.target.getAttribute('data-mood');
            this.submitMoodScore(moodValue);
        });
    });
};

SahayApp.submitMoodScore = function(moodValue) {
    // Submit mood score to API
    fetch('/api/wellness/mood/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': this.getCSRFToken()
        },
        body: JSON.stringify({
            mood_score: moodValue,
            timestamp: new Date().toISOString()
        })
    })
    .then(response => response.json())
    .then(data => {
        this.showNotification('Mood score recorded successfully!', 'success');
    })
    .catch(error => {
        this.showNotification('Error recording mood score', 'error');
    });
};

SahayApp.initializeChatInterface = function() {
    const chatForm = document.getElementById('chat-form');
    const chatInput = document.getElementById('chat-input');
    const chatMessages = document.getElementById('chat-messages');
    const sendButton = document.getElementById('send-button');

    if (chatForm) {
        chatForm.addEventListener('submit', (e) => {
            e.preventDefault();
            const message = chatInput.value.trim();
            if (message) {
                this.sendChatMessage(message);
                chatInput.value = '';
            }
        });
    }

    // Auto-resize chat input
    if (chatInput) {
        chatInput.addEventListener('input', (e) => {
            e.target.style.height = 'auto';
            e.target.style.height = e.target.scrollHeight + 'px';
        });
    }
};

SahayApp.sendChatMessage = function(message) {
    const chatMessages = document.getElementById('chat-messages');
    
    // Add user message to chat
    this.addChatMessage(message, 'user');
    
    // Show typing indicator
    this.showTypingIndicator();
    
    // Send to API
    fetch('/api/chat/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': this.getCSRFToken()
        },
        body: JSON.stringify({
            message: message,
            student_id: this.getCurrentStudentId()
        })
    })
    .then(response => response.json())
    .then(data => {
        this.hideTypingIndicator();
        this.addChatMessage(data.response, 'bot');
    })
    .catch(error => {
        this.hideTypingIndicator();
        this.addChatMessage('Sorry, I encountered an error. Please try again.', 'bot');
    });
};

SahayApp.addChatMessage = function(message, sender) {
    const chatMessages = document.getElementById('chat-messages');
    const messageDiv = document.createElement('div');
    messageDiv.className = `chat-message ${sender}-message`;
    
    messageDiv.innerHTML = `
        <div class="message-content">
            <p>${message}</p>
            <span class="message-time">${new Date().toLocaleTimeString()}</span>
        </div>
    `;
    
    chatMessages.appendChild(messageDiv);
    chatMessages.scrollTop = chatMessages.scrollHeight;
};

SahayApp.showTypingIndicator = function() {
    const typingDiv = document.createElement('div');
    typingDiv.id = 'typing-indicator';
    typingDiv.className = 'chat-message bot-message typing';
    typingDiv.innerHTML = '<div class="typing-dots"><span></span><span></span><span></span></div>';
    
    document.getElementById('chat-messages').appendChild(typingDiv);
};

SahayApp.hideTypingIndicator = function() {
    const typingIndicator = document.getElementById('typing-indicator');
    if (typingIndicator) {
        typingIndicator.remove();
    }
};

// Learning module
SahayApp.initializeLearning = function() {
    this.initializeCourseCards();
    this.initializeCareerPlanner();
};

SahayApp.initializeCourseCards = function() {
    const courseCards = document.querySelectorAll('.course-card');
    courseCards.forEach(card => {
        card.addEventListener('click', (e) => {
            const courseId = card.getAttribute('data-course-id');
            this.openCourse(courseId);
        });
    });
};

SahayApp.openCourse = function(courseId) {
    // Navigate to course detail or open modal
    window.location.href = `/learning/course/${courseId}/`;
};

SahayApp.initializeCareerPlanner = function() {
    const careerCards = document.querySelectorAll('.career-card');
    careerCards.forEach(card => {
        const exploreBtn = card.querySelector('.explore-btn');
        if (exploreBtn) {
            exploreBtn.addEventListener('click', (e) => {
                e.stopPropagation();
                const careerId = card.getAttribute('data-career-id');
                this.exploreCareer(careerId);
            });
        }
    });
};

SahayApp.exploreCareer = function(careerId) {
    // Open career exploration modal or page
    this.showCareerModal(careerId);
};

// Analytics module
SahayApp.initializeAnalytics = function() {
    this.loadAnalyticsData();
    this.initializeCharts();
};

SahayApp.loadAnalyticsData = function() {
    fetch('/api/analytics/summary/')
        .then(response => response.json())
        .then(data => {
            this.updateAnalyticsDisplay(data);
        })
        .catch(error => {
            console.error('Error loading analytics:', error);
        });
};

SahayApp.updateAnalyticsDisplay = function(data) {
    // Update analytics cards with data
    const elements = {
        'total-sessions': data.total_sessions,
        'avg-mood': data.avg_mood_score,
        'completion-rate': data.completion_rate
    };

    Object.entries(elements).forEach(([id, value]) => {
        const element = document.getElementById(id);
        if (element) {
            element.textContent = value;
        }
    });
};

SahayApp.initializeCharts = function() {
    // Initialize charts if Chart.js is available
    if (typeof Chart !== 'undefined') {
        this.createMoodChart();
        this.createProgressChart();
    }
};

// Dashboard module
SahayApp.initializeDashboard = function() {
    this.loadDashboardData();
    this.initializeQuickActions();
};

SahayApp.loadDashboardData = function() {
    fetch('/api/dashboard/summary/')
        .then(response => response.json())
        .then(data => {
            this.updateDashboard(data);
        })
        .catch(error => {
            console.error('Error loading dashboard:', error);
        });
};

SahayApp.updateDashboard = function(data) {
    // Update dashboard widgets
    this.updateRecentActivity(data.recent_activity);
    this.updateQuickStats(data.stats);
};

// Utility functions
SahayApp.getCSRFToken = function() {
    return document.querySelector('[name=csrfmiddlewaretoken]')?.value || '';
};

SahayApp.getCurrentStudentId = function() {
    return localStorage.getItem('sahay_student_id') || 'guest';
};

SahayApp.showNotification = function(message, type = 'info') {
    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;
    notification.textContent = message;
    
    document.body.appendChild(notification);
    
    // Auto-remove after 3 seconds
    setTimeout(() => {
        notification.remove();
    }, 3000);
};

SahayApp.formatDate = function(dateString) {
    return new Date(dateString).toLocaleDateString();
};

SahayApp.formatTime = function(dateString) {
    return new Date(dateString).toLocaleTimeString();
};

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    SahayApp.init();
});

// Export for use in other scripts
window.SahayApp = SahayApp;
