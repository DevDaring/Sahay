# ============================================
# Dockerfile - Django Application
# ============================================

FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    DEBIAN_FRONTEND=noninteractive

# Set work directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    netcat-openbsd \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt /app/
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy project
COPY . /app/

# Create necessary directories
RUN mkdir -p /app/logs /app/media /app/static /app/data/input /app/data/output

# Collect static files
RUN python manage.py collectstatic --noinput

# Create entrypoint script
RUN echo '#!/bin/bash\n\
set -e\n\
\n\
# Wait for database\n\
echo "Waiting for database..."\n\
while ! nc -z $DB_HOST $DB_PORT; do\n\
  sleep 0.1\n\
done\n\
echo "Database is ready!"\n\
\n\
# Run migrations\n\
echo "Running migrations..."\n\
python manage.py migrate --noinput\n\
\n\
# Load initial data if needed\n\
if [ "$LOAD_SAMPLE_DATA" = "true" ]; then\n\
    echo "Loading sample data..."\n\
    python manage.py load_sample_data\n\
fi\n\
\n\
# Start server\n\
echo "Starting server..."\n\
exec "$@"' > /app/entrypoint.sh && chmod +x /app/entrypoint.sh

# Expose port
EXPOSE 8000

# Run entrypoint
ENTRYPOINT ["/app/entrypoint.sh"]

# Start Gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--workers", "4", "--threads", "4", "sahay.wsgi:application"]

# ============================================
# docker-compose.yml - Full Stack Configuration
# ============================================

version: '3.8'

services:
  # PostgreSQL Database
  db:
    image: postgres:15-alpine
    container_name: sahay_db
    environment:
      POSTGRES_DB: sahay_db
      POSTGRES_USER: sahay_user
      POSTGRES_PASSWORD: ${DB_PASSWORD:-sahay_secret}
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U sahay_user"]
      interval: 10s
      timeout: 5s
      retries: 5

  # Redis Cache
  redis:
    image: redis:7-alpine
    container_name: sahay_redis
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 10s
      timeout: 5s
      retries: 5

  # Django Application
  web:
    build: .
    container_name: sahay_web
    command: gunicorn --bind 0.0.0.0:8000 --workers 4 sahay.wsgi:application
    volumes:
      - .:/app
      - static_volume:/app/staticfiles
      - media_volume:/app/media
      - ./data:/app/data
    ports:
      - "8000:8000"
    environment:
      - DEBUG=${DEBUG:-False}
      - SECRET_KEY=${SECRET_KEY:-django-insecure-change-this}
      - DATABASE_URL=postgresql://sahay_user:${DB_PASSWORD:-sahay_secret}@db:5432/sahay_db
      - REDIS_URL=redis://redis:6379/0
      - GCP_PROJECT_ID=${GCP_PROJECT_ID}
      - GCP_LOCATION=${GCP_LOCATION}
      - VERTEX_AI_MODEL=${VERTEX_AI_MODEL}
      - DB_HOST=db
      - DB_PORT=5432
      - LOAD_SAMPLE_DATA=${LOAD_SAMPLE_DATA:-false}
    depends_on:
      db:
        condition: service_healthy
      redis:
        condition: service_healthy

  # Celery Worker
  celery:
    build: .
    container_name: sahay_celery
    command: celery -A sahay worker -l info
    volumes:
      - .:/app
    environment:
      - DATABASE_URL=postgresql://sahay_user:${DB_PASSWORD:-sahay_secret}@db:5432/sahay_db
      - REDIS_URL=redis://redis:6379/0
      - GCP_PROJECT_ID=${GCP_PROJECT_ID}
      - GCP_LOCATION=${GCP_LOCATION}
    depends_on:
      - db
      - redis

  # Celery Beat Scheduler
  celery-beat:
    build: .
    container_name: sahay_celery_beat
    command: celery -A sahay beat -l info
    volumes:
      - .:/app
    environment:
      - DATABASE_URL=postgresql://sahay_user:${DB_PASSWORD:-sahay_secret}@db:5432/sahay_db
      - REDIS_URL=redis://redis:6379/0
    depends_on:
      - db
      - redis

  # Nginx Reverse Proxy
  nginx:
    image: nginx:alpine
    container_name: sahay_nginx
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf:ro
      - static_volume:/static
      - media_volume:/media
    ports:
      - "80:80"
      - "443:443"
    depends_on:
      - web
    healthcheck:
      test: ["CMD", "wget", "-q", "--spider", "http://localhost/health"]
      interval: 30s
      timeout: 10s
      retries: 3

volumes:
  postgres_data:
  redis_data:
  static_volume:
  media_volume:

# ============================================
# nginx.conf - Nginx Configuration
# ============================================

events {
    worker_connections 1024;
}

http {
    include /etc/nginx/mime.types;
    default_type application/octet-stream;

    # Logging
    access_log /var/log/nginx/access.log;
    error_log /var/log/nginx/error.log;

    # Gzip compression
    gzip on;
    gzip_comp_level 6;
    gzip_types text/plain text/css text/xml text/javascript 
               application/json application/javascript application/xml+rss 
               application/rss+xml application/atom+xml image/svg+xml 
               text/javascript application/x-font-ttf font/opentype 
               application/vnd.ms-fontobject image/x-icon;

    # Rate limiting
    limit_req_zone $binary_remote_addr zone=general:10m rate=10r/s;
    limit_req_zone $binary_remote_addr zone=api:10m rate=30r/s;

    # Upstream Django app
    upstream django {
        server web:8000;
    }

    # HTTP server - redirect to HTTPS in production
    server {
        listen 80;
        server_name localhost;

        # Client body size for file uploads
        client_max_body_size 10M;

        # Security headers
        add_header X-Content-Type-Options nosniff;
        add_header X-Frame-Options DENY;
        add_header X-XSS-Protection "1; mode=block";
        add_header Referrer-Policy "strict-origin-when-cross-origin";

        # Health check endpoint
        location /health {
            access_log off;
            return 200 "healthy\n";
            add_header Content-Type text/plain;
        }

        # Static files
        location /static/ {
            alias /static/;
            expires 30d;
            add_header Cache-Control "public, immutable";
        }

        # Media files
        location /media/ {
            alias /media/;
            expires 7d;
            add_header Cache-Control "public";
        }

        # API endpoints with rate limiting
        location /api/ {
            limit_req zone=api burst=50 nodelay;
            
            proxy_pass http://django;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
            
            # WebSocket support for real-time features
            proxy_http_version 1.1;
            proxy_set_header Upgrade $http_upgrade;
            proxy_set_header Connection "upgrade";
        }

        # Django app
        location / {
            limit_req zone=general burst=20 nodelay;
            
            proxy_pass http://django;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }
    }
}

# ============================================
# deploy.sh - Deployment Script
# ============================================

#!/bin/bash

set -e

echo "🚀 Starting Sahay Platform Deployment"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}✓${NC} $1"
}

print_error() {
    echo -e "${RED}✗${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}⚠${NC} $1"
}

# Check prerequisites
check_prerequisites() {
    echo "Checking prerequisites..."
    
    # Check Docker
    if ! command -v docker &> /dev/null; then
        print_error "Docker is not installed"
        exit 1
    fi
    print_status "Docker installed"
    
    # Check Docker Compose
    if ! command -v docker-compose &> /dev/null; then
        print_error "Docker Compose is not installed"
        exit 1
    fi
    print_status "Docker Compose installed"
    
    # Check for .env file
    if [ ! -f .env ]; then
        print_warning ".env file not found, creating from template..."
        cp .env.example .env
        print_warning "Please update .env file with your configuration"
        exit 1
    fi
    print_status ".env file found"
}

# Build containers
build_containers() {
    echo "Building Docker containers..."
    docker-compose build --no-cache
    print_status "Containers built successfully"
}

# Start services
start_services() {
    echo "Starting services..."
    docker-compose up -d
    print_status "Services started"
    
    # Wait for services to be ready
    echo "Waiting for services to be ready..."
    sleep 10
    
    # Check service health
    if docker-compose ps | grep -q "unhealthy"; then
        print_error "Some services are unhealthy"
        docker-compose ps
        exit 1
    fi
    print_status "All services are healthy"
}

# Run migrations
run_migrations() {
    echo "Running database migrations..."
    docker-compose exec web python manage.py migrate
    print_status "Migrations completed"
}

# Load initial data
load_initial_data() {
    echo "Loading initial data..."
    docker-compose exec web python manage.py load_sample_data
    print_status "Initial data loaded"
}

# Create superuser
create_superuser() {
    echo "Creating superuser..."
    docker-compose exec web python manage.py shell -c "
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@sahay.com', 'admin123')
    print('Superuser created: admin/admin123')
else:
    print('Superuser already exists')
"
    print_status "Superuser ready"
}

# Run tests
run_tests() {
    echo "Running tests..."
    docker-compose exec web python manage.py test
    print_status "Tests passed"
}

# Main deployment flow
main() {
    echo "======================================"
    echo "   Sahay Platform Deployment"
    echo "======================================"
    echo ""
    
    check_prerequisites
    
    # Parse command line arguments
    case "${1:-full}" in
        full)
            build_containers
            start_services
            run_migrations
            load_initial_data
            create_superuser
            run_tests
            ;;
        update)
            docker-compose pull
            docker-compose up -d --build
            run_migrations
            ;;
        restart)
            docker-compose restart
            ;;
        stop)
            docker-compose down
            ;;
        logs)
            docker-compose logs -f
            ;;
        test)
            run_tests
            ;;
        *)
            echo "Usage: $0 {full|update|restart|stop|logs|test}"
            exit 1
            ;;
    esac
    
    echo ""
    echo "======================================"
    echo -e "${GREEN}✓ Deployment completed successfully!${NC}"
    echo "======================================"
    echo ""
    echo "Access the application at:"
    echo "  - Web: http://localhost"
    echo "  - Admin: http://localhost/admin"
    echo "  - API: http://localhost/api"
    echo ""
    echo "Default credentials:"
    echo "  Username: admin"
    echo "  Password: admin123"
    echo ""
    print_warning "Remember to change the admin password!"
}

# Run main function
main "$@"

# ============================================
# .env.example - Environment Variables Template
# ============================================

# Django Settings
SECRET_KEY=django-insecure-change-this-in-production
DEBUG=False
ALLOWED_HOSTS=localhost,127.0.0.1

# Database
DB_PASSWORD=sahay_secret_password

# GCP Settings
GCP_PROJECT_ID=sahay-hackathon-2024
GCP_LOCATION=us-central1
GCP_BUCKET_NAME=sahay-data-bucket
VERTEX_AI_MODEL=gemini-1.5-flash

# Add path to GCP credentials if using service account
# GOOGLE_APPLICATION_CREDENTIALS=/path/to/credentials.json

# Privacy Settings
K_ANONYMITY_THRESHOLD=5
DATA_RETENTION_DAYS=90

# Risk Thresholds
RISK_L1_MAX=6
RISK_L2_MAX=10
RISK_L3_MAX=15

# Redis
REDIS_URL=redis://redis:6379/0

# Email (for production)
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password

# Load sample data on first run
LOAD_SAMPLE_DATA=true