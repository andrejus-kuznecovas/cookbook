@echo off
REM Cookbook App Startup Script for Windows
REM Simple commands to manage the full-stack application

if "%1"=="" goto help
if "%1"=="help" goto help
if "%1"=="start" goto start
if "%1"=="start-dev" goto start-dev
if "%1"=="install" goto install
if "%1"=="test" goto test
if "%1"=="stop" goto stop
if "%1"=="clean" goto clean
if "%1"=="status" goto status
if "%1"=="health" goto health
goto help

:help
echo 🍳 Cookbook App - Available Commands:
echo.
echo   start.bat start       - Start the complete application (recommended)
echo   start.bat start-dev   - Start with hot-reload for development
echo   start.bat install     - Install all dependencies
echo   start.bat test        - Run all tests
echo   start.bat stop        - Stop all services
echo   start.bat clean       - Clean up containers and volumes
echo   start.bat status      - Show application status
echo   start.bat health      - Check application health
echo.
echo 🚀 Quick Start: start.bat start
goto end

:start
echo 🗄️ Starting PostgreSQL database...
docker-compose up -d postgres
timeout /t 10 /nobreak > nul
echo 🔧 Starting backend server...
cd backend
start /B cmd /c "set DATABASE_URL=postgres://cookbook_user:cookbook_password@localhost:5432/cookbook_db?sslmode=disable&& set JWT_SECRET=your-super-secret-jwt-key-for-development&& set PORT=8080&& go run main.go"
cd ..
timeout /t 5 /nobreak > nul
echo 📱 Starting frontend application...
cd frontend
start /B cmd /c "npm start"
cd ..
echo 🎉 Cookbook app is starting!
echo 📱 Frontend: http://localhost:19006
echo 🔧 Backend: http://localhost:8080
echo 🗄️ Database: localhost:5432
echo.
echo Press any key to view logs or Ctrl+C to stop
pause > nul
docker-compose logs -f
goto end

:start-dev
echo 🗄️ Starting PostgreSQL database...
docker-compose up -d postgres
timeout /t 10 /nobreak > nul
echo 🔧 Starting backend server in development mode...
cd backend
start /B cmd /c "set DATABASE_URL=postgres://cookbook_user:cookbook_password@localhost:5432/cookbook_db?sslmode=disable&& set JWT_SECRET=your-super-secret-jwt-key-for-development&& set PORT=8080&& set GIN_MODE=debug&& go run main.go"
cd ..
timeout /t 5 /nobreak > nul
echo 📱 Starting frontend application in development mode...
cd frontend
start /B cmd /c "npm start"
cd ..
echo 🎉 Cookbook app is starting in development mode!
echo 📱 Frontend: http://localhost:19006
echo 🔧 Backend: http://localhost:8080
echo 🗄️ Database: localhost:5432
echo.
echo Press any key to view logs or Ctrl+C to stop
pause > nul
docker-compose logs -f
goto end

:install
echo 📦 Installing dependencies...
echo Installing backend dependencies...
cd backend
go mod tidy
cd ..
echo Installing frontend dependencies...
cd frontend
npm install
cd ..
echo ✅ All dependencies installed!
goto end

:test
echo 🧪 Running tests...
echo Running backend tests...
cd backend
go test ./... -v
cd ..
echo Running frontend tests...
cd frontend
npm test -- --watchAll=false
cd ..
echo ✅ All tests completed!
goto end

:stop
echo 🛑 Stopping all services...
docker-compose down
echo Stopping any running processes...
taskkill /F /IM "go.exe" 2>nul || echo No Go processes found
taskkill /F /IM "node.exe" 2>nul || echo No Node processes found
echo ✅ All services stopped!
goto end

:clean
echo 🧹 Cleaning up...
docker-compose down -v
docker system prune -f
echo ✅ Cleanup completed!
goto end

:status
echo 📊 Application Status:
echo Database:
docker-compose ps postgres
echo Backend:
tasklist /FI "IMAGENAME eq go.exe" | find /I "go.exe" && echo ✅ Backend running || echo ❌ Backend not running
echo Frontend:
tasklist /FI "IMAGENAME eq node.exe" | find /I "node.exe" && echo ✅ Frontend running || echo ❌ Frontend not running
goto end

:health
echo 🏥 Checking application health...
echo Database:
docker-compose exec postgres pg_isready -U cookbook_user -d cookbook_db || echo ❌ Database not ready
echo Backend:
curl -f http://localhost:8080/health || echo ❌ Backend not ready
echo ✅ Health check completed!
goto end

:end 