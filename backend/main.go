package main

import (
	"log"
	"os"

	"cookbook-backend/database"
	"cookbook-backend/handlers"
	"cookbook-backend/middleware"

	"github.com/gin-contrib/cors"
	"github.com/gin-gonic/gin"
	"github.com/joho/godotenv"
)

func main() {
	// Only try to load .env file if we're not in production (Railway sets RAILWAY_ENVIRONMENT)
	if os.Getenv("RAILWAY_ENVIRONMENT") == "" {
		err := godotenv.Load()
		if err != nil {
			log.Println("No .env file found, using environment variables")
		} else {
			log.Println("Loaded .env file for local development")
		}
	} else {
		log.Println("Production environment detected, using Railway environment variables")
	}

	// Debug: Print environment variables
	log.Println("=== Environment Variables Debug ===")
	dbURL := os.Getenv("DATABASE_URL")
	jwtSecret := os.Getenv("JWT_SECRET")
	portDebug := os.Getenv("PORT")
	railwayEnv := os.Getenv("RAILWAY_ENVIRONMENT")
	
	log.Printf("RAILWAY_ENVIRONMENT: '%s'", railwayEnv)
	log.Printf("JWT_SECRET value: '%s'", jwtSecret)
	log.Printf("PORT value: '%s'", portDebug)
	log.Printf("DATABASE_URL value: '%s'", dbURL)
	log.Println("=== End Debug ===")

	// Connect to database
	if err := database.Connect(); err != nil {
		log.Fatal("Failed to connect to database:", err)
	}
	defer database.Close()

	// Create database tables
	if err := database.CreateTables(); err != nil {
		log.Fatal("Failed to create database tables:", err)
	}

	// Initialize Gin router
	router := gin.Default()

	// CORS configuration
	allowedOrigins := []string{"*"}
	if origins := os.Getenv("ALLOWED_ORIGINS"); origins != "" {
		allowedOrigins = []string{origins}
	}
	
	router.Use(cors.New(cors.Config{
		AllowOrigins:     allowedOrigins,
		AllowMethods:     []string{"GET", "POST", "PUT", "PATCH", "DELETE"},
		AllowHeaders:     []string{"Content-Type", "Authorization"},
		AllowCredentials: true,
	}))

	// Health check endpoint
	router.GET("/health", func(c *gin.Context) {
		c.JSON(200, gin.H{"status": "ok"})
	})

	// API routes group
	api := router.Group("/api")
	{
		// Authentication routes (no middleware required)
		auth := api.Group("/auth")
		{
			auth.POST("/login", handlers.Login)
		}

		// Protected routes (require authentication)
		protected := api.Group("/")
		protected.Use(middleware.AuthMiddleware())
		{
			protected.GET("/profile", handlers.GetProfile)

			meals := protected.Group("/meals")
			{
				meals.GET("", handlers.GetMeals)
				meals.POST("", handlers.CreateMeal)
				meals.GET("/:id", handlers.GetMeal)
				meals.PUT("/:id", handlers.UpdateMeal)
				meals.DELETE("/:id", handlers.DeleteMeal)
			}
		}
	}

	// Start server
	port := os.Getenv("PORT")
	if port == "" {
		port = "8080"
	}

	log.Printf("Server starting on port %s", port)
	if err := router.Run(":" + port); err != nil {
		log.Fatal("Failed to start server:", err)
	}
}