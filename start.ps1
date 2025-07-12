param(
    [string]$Command = "help"
)

# Cookbook App Startup Script for Windows PowerShell
# Simple commands to manage the full-stack application

function Show-Help {
    Write-Host "Cookbook App - Available Commands:" -ForegroundColor Green
    Write-Host ""
    Write-Host "  .\start.ps1 start       - Start the complete application (recommended)"
    Write-Host "  .\start.ps1 start-dev   - Start with hot-reload for development"
    Write-Host "  .\start.ps1 install     - Install all dependencies"
    Write-Host "  .\start.ps1 test        - Run all tests"
    Write-Host "  .\start.ps1 stop        - Stop all services"
    Write-Host "  .\start.ps1 clean       - Clean up containers and volumes"
    Write-Host "  .\start.ps1 status      - Show application status"
    Write-Host "  .\start.ps1 health      - Check application health"
    Write-Host ""
    Write-Host "Quick Start: .\start.ps1 start" -ForegroundColor Yellow
}

function Start-App {
    Write-Host "Starting PostgreSQL database..." -ForegroundColor Blue
    docker-compose up -d postgres
    Start-Sleep -Seconds 10
    
    Write-Host "Starting backend server..." -ForegroundColor Blue
    $env:DATABASE_URL = "postgres://cookbook_user:cookbook_password@localhost:5432/cookbook_db?sslmode=disable"
    $env:JWT_SECRET = "your-super-secret-jwt-key-for-development"
    $env:PORT = "8080"
    
    Start-Process -FilePath "powershell" -ArgumentList "-NoExit", "-Command", "cd backend; go run main.go"
    Start-Sleep -Seconds 5
    
    Write-Host "Starting frontend application..." -ForegroundColor Blue
    Start-Process -FilePath "powershell" -ArgumentList "-NoExit", "-Command", "cd frontend; npm start"
    
    Write-Host "Cookbook app is starting!" -ForegroundColor Green
    Write-Host "Frontend: http://localhost:19006" -ForegroundColor Cyan
    Write-Host "Backend: http://localhost:8080" -ForegroundColor Cyan
    Write-Host "Database: localhost:5432" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Press Ctrl+C to stop or run '.\start.ps1 stop' to stop all services" -ForegroundColor Yellow
}

function Start-AppDev {
    Write-Host "Starting PostgreSQL database..." -ForegroundColor Blue
    docker-compose up -d postgres
    Start-Sleep -Seconds 10
    
    Write-Host "Starting backend server in development mode..." -ForegroundColor Blue
    $env:DATABASE_URL = "postgres://cookbook_user:cookbook_password@localhost:5432/cookbook_db?sslmode=disable"
    $env:JWT_SECRET = "your-super-secret-jwt-key-for-development"
    $env:PORT = "8080"
    $env:GIN_MODE = "debug"
    
    Start-Process -FilePath "powershell" -ArgumentList "-NoExit", "-Command", "cd backend; go run main.go"
    Start-Sleep -Seconds 5
    
    Write-Host "Starting frontend application in development mode..." -ForegroundColor Blue
    Start-Process -FilePath "powershell" -ArgumentList "-NoExit", "-Command", "cd frontend; npm start"
    
    Write-Host "Cookbook app is starting in development mode!" -ForegroundColor Green
    Write-Host "Frontend: http://localhost:19006" -ForegroundColor Cyan
    Write-Host "Backend: http://localhost:8080" -ForegroundColor Cyan
    Write-Host "Database: localhost:5432" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Press Ctrl+C to stop or run '.\start.ps1 stop' to stop all services" -ForegroundColor Yellow
}

function Install-Dependencies {
    Write-Host "Installing dependencies..." -ForegroundColor Blue
    Write-Host "Installing backend dependencies..."
    Set-Location backend
    go mod tidy
    Set-Location ..
    Write-Host "Installing frontend dependencies..."
    Set-Location frontend
    npm install
    Set-Location ..
    Write-Host "All dependencies installed!" -ForegroundColor Green
}

function Test-App {
    Write-Host "Running tests..." -ForegroundColor Blue
    Write-Host "Running backend tests..."
    Set-Location backend
    go test ./... -v
    Set-Location ..
    Write-Host "Running frontend tests..."
    Set-Location frontend
    npm test -- --watchAll=false
    Set-Location ..
    Write-Host "All tests completed!" -ForegroundColor Green
}

function Stop-App {
    Write-Host "Stopping all services..." -ForegroundColor Red
    docker-compose down
    Write-Host "Stopping any running processes..."
    Get-Process | Where-Object { $_.ProcessName -eq "go" } | Stop-Process -Force -ErrorAction SilentlyContinue
    Get-Process | Where-Object { $_.ProcessName -eq "node" } | Stop-Process -Force -ErrorAction SilentlyContinue
    Write-Host "All services stopped!" -ForegroundColor Green
}

function Clean-App {
    Write-Host "Cleaning up..." -ForegroundColor Blue
    docker-compose down -v
    docker system prune -f
    Write-Host "Cleanup completed!" -ForegroundColor Green
}

function Show-Status {
    Write-Host "Application Status:" -ForegroundColor Blue
    Write-Host "Database:"
    docker-compose ps postgres
    Write-Host "Backend:"
    if (Get-Process -Name "go" -ErrorAction SilentlyContinue) {
        Write-Host "Backend running" -ForegroundColor Green
    }
    else {
        Write-Host "Backend not running" -ForegroundColor Red
    }
    Write-Host "Frontend:"
    if (Get-Process -Name "node" -ErrorAction SilentlyContinue) {
        Write-Host "Frontend running" -ForegroundColor Green
    }
    else {
        Write-Host "Frontend not running" -ForegroundColor Red
    }
}

function Test-Health {
    Write-Host "Checking application health..." -ForegroundColor Blue
    Write-Host "Database:"
    try {
        docker-compose exec postgres pg_isready -U cookbook_user -d cookbook_db
        Write-Host "Database ready" -ForegroundColor Green
    }
    catch {
        Write-Host "Database not ready" -ForegroundColor Red
    }
    Write-Host "Backend:"
    try {
        $response = Invoke-WebRequest -Uri "http://localhost:8080/health" -UseBasicParsing
        if ($response.StatusCode -eq 200) {
            Write-Host "Backend ready" -ForegroundColor Green
        }
        else {
            Write-Host "Backend not ready" -ForegroundColor Red
        }
    }
    catch {
        Write-Host "Backend not ready" -ForegroundColor Red
    }
    Write-Host "Health check completed!" -ForegroundColor Green
}

# Main script logic
switch ($Command.ToLower()) {
    "start" { Start-App }
    "start-dev" { Start-AppDev }
    "install" { Install-Dependencies }
    "test" { Test-App }
    "stop" { Stop-App }
    "clean" { Clean-App }
    "status" { Show-Status }
    "health" { Test-Health }
    default { Show-Help }
} 