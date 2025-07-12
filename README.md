# 📚 Cookbook App

A simple multiplatform recipe management app built with Go backend and React Native frontend. Perfect for two users to share their favorite meals and recipes.

## 🚀 Features

- **User Authentication**: Simple JWT-based authentication for two users
- **Meal Management**: Create, read, update, and delete meals
- **Recipe Storage**: Store meal name, ingredients, recipe instructions, and difficulty level
- **Modern UI**: Clean, responsive design that works on iOS, Android, and web
- **Real-time Sync**: Changes from one user are visible to the other
- **Sharing**: Share recipes with others using the built-in share functionality

## 🛠 Tech Stack

### Backend
- **Go 1.21** with Gin framework
- **PostgreSQL** database
- **JWT** authentication
- **Docker** for containerization

### Frontend
- **React Native** with Expo
- **React Navigation** for routing
- **Axios** for API calls
- **AsyncStorage** for local data persistence

### Deployment
- **Railway/Render** for backend hosting
- **Expo** for mobile app distribution

## 📋 Prerequisites

- Go 1.21+
- Node.js 18+
- PostgreSQL (for local development)
- Expo CLI (`npm install -g @expo/cli`)

## 🏃‍♂️ Quick Start

### 🚀 One-Command Start (Recommended)

Choose the method that works best for your system:

#### **Windows (PowerShell)**
```powershell
.\start.ps1 start
```

#### **Windows (Command Prompt)**
```cmd
start.bat start
```

#### **macOS/Linux (Make)**
```bash
make start
```

That's it! The script will:
1. Start the PostgreSQL database in Docker
2. Start the backend server
3. Start the frontend application
4. Open URLs for easy access

### 📋 Available Commands

**PowerShell Commands:**
- `.\start.ps1 start` - Start the complete application
- `.\start.ps1 start-dev` - Start with development mode
- `.\start.ps1 install` - Install all dependencies
- `.\start.ps1 test` - Run all tests
- `.\start.ps1 stop` - Stop all services
- `.\start.ps1 clean` - Clean up containers and volumes
- `.\start.ps1 status` - Show application status
- `.\start.ps1 health` - Check application health

**Batch Commands:**
- `start.bat start` - Start the complete application
- `start.bat start-dev` - Start with development mode
- `start.bat install` - Install all dependencies
- `start.bat test` - Run all tests
- `start.bat stop` - Stop all services

**Make Commands:**
- `make start` - Start the complete application
- `make start-dev` - Start with development mode
- `make install` - Install all dependencies
- `make test` - Run all tests
- `make stop` - Stop all services
- `make clean` - Clean up containers and volumes

### 🛠 Manual Setup (Advanced)

If you prefer to set up manually:

#### Backend Setup

1. **Navigate to backend directory**
   ```bash
   cd backend
   ```

2. **Install dependencies**
   ```bash
   go mod tidy
   ```

3. **Set up environment variables**
   Create a `.env` file in the backend directory:
   ```env
   DATABASE_URL=postgres://cookbook_user:cookbook_password@localhost:5432/cookbook_db?sslmode=disable
   JWT_SECRET=your-super-secret-jwt-key-for-development
   PORT=8080
   ```

4. **Start the server**
   ```bash
   go run main.go
   ```

   The backend will be available at `http://localhost:8080`

#### Frontend Setup

1. **Navigate to frontend directory**
   ```bash
   cd frontend
   ```

2. **Install dependencies**
   ```bash
   npm install
   ```

3. **Update API URL** (if needed)
   Edit `src/services/api.js` and update the `API_BASE_URL` to match your backend URL:
   ```javascript
   const API_BASE_URL = 'http://localhost:8080/api';
   ```

4. **Start the app**
   ```bash
   npm start
   ```

   This will start the Expo development server. You can then:
   - Press `w` to run in web browser
   - Use Expo Go app to scan QR code for mobile testing
   - Press `a` for Android emulator
   - Press `i` for iOS simulator (macOS only)

## 👥 Default Users

The app comes with two pre-configured users:

- **User 1**: `user1` / `password`
- **User 2**: `user2` / `password`

## 🧪 Testing

### Backend Tests
```bash
cd backend
go test ./...
```

### Frontend Tests
```bash
cd frontend
npm test
```

## 📦 Deployment

### Backend Deployment (Railway/Render)

1. **Create a new project** on Railway or Render
2. **Connect your repository**
3. **Set environment variables**:
   - `DATABASE_URL`: Your PostgreSQL connection string
   - `JWT_SECRET`: A secure random string
   - `PORT`: Set to 8080 (or use Railway/Render's PORT variable)

4. **Deploy**: The platform will automatically build and deploy using the provided Dockerfile

### Frontend Deployment (Expo)

1. **Build for production**
   ```bash
   cd frontend
   expo build:web  # For web deployment
   ```

2. **Mobile app distribution**
   ```bash
   expo publish  # For Over-the-Air updates
   expo build:android  # For Android APK
   expo build:ios  # For iOS IPA (requires Apple Developer account)
   ```

## 🗂 Project Structure

```
cookbook/
├── backend/                 # Go backend
│   ├── main.go             # Application entry point
│   ├── models/             # Database models
│   ├── handlers/           # HTTP handlers
│   ├── middleware/         # Authentication middleware
│   ├── database/           # Database connection and setup
│   ├── utils/              # JWT utilities
│   └── Dockerfile          # Docker configuration
├── frontend/               # React Native frontend
│   ├── src/
│   │   ├── components/     # Reusable UI components
│   │   ├── screens/        # App screens
│   │   ├── services/       # API services
│   │   └── contexts/       # React contexts
│   ├── App.js              # Main app component
│   └── package.json        # Dependencies
└── README.md               # This file
```

## 🔧 Configuration

### Backend Environment Variables
- `DATABASE_URL`: PostgreSQL connection string
- `JWT_SECRET`: Secret key for JWT token signing
- `PORT`: Server port (default: 8080)

### Frontend Configuration
- Update `API_BASE_URL` in `src/services/api.js` to match your backend URL
- Modify `app.json` for Expo configuration

## 🤝 API Endpoints

### Authentication
- `POST /api/auth/login` - User login

### Meals
- `GET /api/meals` - Get all meals
- `POST /api/meals` - Create new meal
- `GET /api/meals/:id` - Get specific meal
- `PUT /api/meals/:id` - Update meal
- `DELETE /api/meals/:id` - Delete meal

## 📱 App Screenshots

The app features:
- Clean login screen with user credentials
- Meal list with pull-to-refresh functionality
- Detailed meal view with sharing options
- Add/Edit meal form with difficulty selection
- Modern, responsive UI design

## 🔒 Security

- JWT-based authentication
- Password hashing with bcrypt
- CORS configuration for cross-origin requests
- Input validation and sanitization

## 🐛 Troubleshooting

### Common Issues

1. **Backend won't start**
   - Check if PostgreSQL is running
   - Verify DATABASE_URL is correct
   - Ensure JWT_SECRET is set

2. **Frontend can't connect to backend**
   - Verify API_BASE_URL is correct
   - Check if backend is running on the specified port
   - Ensure CORS is properly configured

3. **Authentication fails**
   - Check JWT_SECRET matches between restarts
   - Verify user credentials (user1/password, user2/password)

## 📝 License

This project is open source and available under the [MIT License](LICENSE).

## 🙏 Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 🎯 Future Enhancements

- Photo upload for meals
- Advanced search and filtering
- Meal categories and tags
- Recipe rating system
- Meal planning calendar
- Grocery list generation