package handlers

import (
	"net/http"

	"cookbook-backend/models"
	"cookbook-backend/utils"

	"github.com/gin-gonic/gin"
	"golang.org/x/crypto/bcrypt"
)

// Hardcoded users for the two-person system
var users = map[string]models.User{
	"user1": {
		ID:           1,
		Username:     "user1",
		PasswordHash: "$2a$10$92IXUNpkjO0rOQ5byMi.Ye4oKoEa3Ro9llC/.og/at2.uheWG/igi", // "password"
	},
	"user2": {
		ID:           2,
		Username:     "user2",
		PasswordHash: "$2a$10$92IXUNpkjO0rOQ5byMi.Ye4oKoEa3Ro9llC/.og/at2.uheWG/igi", // "password"
	},
}

func Login(c *gin.Context) {
	var req models.LoginRequest
	if err := c.ShouldBindJSON(&req); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": err.Error()})
		return
	}

	// Check if user exists
	user, exists := users[req.Username]
	if !exists {
		c.JSON(http.StatusUnauthorized, gin.H{"error": "Invalid username or password"})
		return
	}

	// Verify password
	if err := bcrypt.CompareHashAndPassword([]byte(user.PasswordHash), []byte(req.Password)); err != nil {
		c.JSON(http.StatusUnauthorized, gin.H{"error": "Invalid username or password"})
		return
	}

	// Generate JWT token
	token, err := utils.GenerateToken(user.ID, user.Username)
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to generate token"})
		return
	}

	response := models.LoginResponse{
		Token: token,
		User:  user,
	}

	c.JSON(http.StatusOK, response)
}

func GetProfile(c *gin.Context) {
	userID := c.GetInt("user_id")
	username := c.GetString("username")

	// Find user by ID
	var user models.User
	for _, u := range users {
		if u.ID == userID {
			user = u
			break
		}
	}

	if user.ID == 0 {
		c.JSON(http.StatusNotFound, gin.H{"error": "User not found"})
		return
	}

	c.JSON(http.StatusOK, gin.H{
		"user_id":  userID,
		"username": username,
		"user":     user,
	})
} 