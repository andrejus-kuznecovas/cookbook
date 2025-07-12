package main

import (
	"log"
	"os"
	"path/filepath"

	"cookbook-backend/database"
	"cookbook-backend/handlers"
	"cookbook-backend/middleware"

	"github.com/gin-contrib/cors"
	"github.com/gin-gonic/gin"
	"github.com/joho/godotenv"
)

func main() {
	currentDir, _ := os.Getwd()
	err := godotenv.Load(filepath.Join(currentDir, ".env"))
	if err != nil {
		log.Fatal("Error loading .env file:", err)
	}

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
	router.Use(cors.New(cors.Config{
		AllowOrigins:     []string{"http://localhost:8081"}, // Update before deployment
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
