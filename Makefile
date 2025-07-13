# Cookbook App Makefile
# Simple commands to manage the full-stack application

.PHONY: help start start-dev start-backend start-frontend start-db stop clean test install build

# Default target
help:
	@echo "🍳 Cookbook App - Available Commands:"
	@echo ""
	@echo "  make start       - Start the complete application (recommended)"
	@echo "  make start-dev   - Start with hot-reload for development"
	@echo "  make start-db    - Start only the database"
	@echo "  make start-backend - Start only the backend server"
	@echo "  make start-frontend - Start only the frontend app"
	@echo "  make install     - Install all dependencies"
	@echo "  make test        - Run all tests"
	@echo "  make build       - Build the application"
	@echo "  make stop        - Stop all services"
	@echo "  make clean       - Clean up containers and volumes"
	@echo "  make logs        - Show application logs"
	@echo ""
	@echo "🚀 Quick Start: make start"

# Start everything in production mode
start: start-db wait-for-db start-backend-prod start-frontend-prod
	@echo "🎉 Cookbook app is running!"
	@echo "📱 Frontend: http://localhost:19006"
	@echo "🔧 Backend: http://localhost:8080"
	@echo "🗄️ Database: localhost:5432"

# Start everything in development mode
start-dev: start-db wait-for-db start-backend-dev start-frontend-dev
	@echo "🎉 Cookbook app is running in development mode!"
	@echo "📱 Frontend: http://localhost:19006"
	@echo "🔧 Backend: http://localhost:8080"
	@echo "🗄️ Database: localhost:5432"

# Start database
start-db:
	@echo "🗄️ Starting PostgreSQL database..."
	docker-compose up -d postgres

# Wait for database to be ready
wait-for-db:
	@echo "⏳ Waiting for database to be ready..."
	@timeout 30 bash -c 'until docker-compose exec postgres pg_isready -U cookbook_user -d cookbook_db; do sleep 1; done' || true

start-backend-prod:
	@echo "🔧 Starting backend server..."
	cd backend && \
	DATABASE_URL=postgres://cookbook_user:cookbook_password@localhost:5432/cookbook_db?sslmode=disable \
	JWT_SECRET=your-super-secret-jwt-key-for-development \
	PORT=8080 \
	go run main.go &

start-backend-dev:
	@echo "🔧 Starting backend server in development mode..."
	cd backend && \
	DATABASE_URL=postgres://cookbook_user:cookbook_password@localhost:5432/cookbook_db?sslmode=disable \
	JWT_SECRET=your-super-secret-jwt-key-for-development \
	PORT=8080 \
	GIN_MODE=debug \
	go run main.go &

start-frontend-prod:
	@echo "📱 Starting frontend application..."
	cd frontend && npm start -- --web &

start-frontend-dev:
	@echo "📱 Starting frontend application in development mode..."
	cd frontend && npm start &

install:
	@echo "📦 Installing dependencies..."
	@echo "Installing backend dependencies..."
	cd backend && go mod tidy
	@echo "Installing frontend dependencies..."
	cd frontend && npm install
	@echo "✅ All dependencies installed!"

test:
	@echo "🧪 Running tests..."
	@echo "Running backend tests..."
	cd backend && go test ./... -v
	@echo "Running frontend tests..."
	cd frontend && npm test -- --watchAll=false
	@echo "✅ All tests completed!"

build:
	@echo "🔨 Building application..."
	@echo "Building backend..."
	cd backend && go build -o bin/cookbook-backend main.go
	@echo "Building frontend..."
	cd frontend && npm run build
	@echo "✅ Build completed!"

logs:
	@echo "📋 Application logs:"
	docker-compose logs -f

stop:
	@echo "🛑 Stopping all services..."
	docker-compose down
	@echo "Stopping any running Go processes..."
	pkill -f "go run main.go" || true
	@echo "Stopping any running Node processes..."
	pkill -f "expo start" || true
	@echo "✅ All services stopped!"

clean: stop
	@echo "🧹 Cleaning up..."
	docker-compose down -v
	docker system prune -f
	@echo "✅ Cleanup completed!"

dev: start-dev
prod: start


db: start-db
db-shell:
	@echo "🔍 Opening database shell..."
	docker-compose exec postgres psql -U cookbook_user -d cookbook_db

health:
	@echo "🏥 Checking application health..."
	@echo "Database:"
	@docker-compose exec postgres pg_isready -U cookbook_user -d cookbook_db || echo "❌ Database not ready"
	@echo "Backend:"
	@curl -f http://localhost:8080/health || echo "❌ Backend not ready"
	@echo "✅ Health check completed!"


status:
	@echo "📊 Application Status:"
	@echo "Database:"
	@docker-compose ps postgres
	@echo "Backend:"
	@pgrep -f "go run main.go" > /dev/null && echo "✅ Backend running" || echo "❌ Backend not running"
	@echo "Frontend:"
	@pgrep -f "expo start" > /dev/null && echo "✅ Frontend running" || echo "❌ Frontend not running" 