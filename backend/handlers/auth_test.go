package handlers

import (
	"bytes"
	"encoding/json"
	"net/http"
	"net/http/httptest"
	"os"
	"testing"

	"cookbook-backend/models"

	"github.com/gin-gonic/gin"
)

func TestLogin(t *testing.T) {
	// Set up test environment
	os.Setenv("JWT_SECRET", "test-secret-key")
	defer os.Unsetenv("JWT_SECRET")

	// Set Gin to test mode
	gin.SetMode(gin.TestMode)

	// Create a test router
	router := gin.New()
	router.POST("/login", Login)

	// Test valid login
	t.Run("ValidLogin", func(t *testing.T) {
		loginReq := models.LoginRequest{
			Username: "user1",
			Password: "password",
		}

		jsonReq, _ := json.Marshal(loginReq)
		req := httptest.NewRequest(http.MethodPost, "/login", bytes.NewReader(jsonReq))
		req.Header.Set("Content-Type", "application/json")

		w := httptest.NewRecorder()
		router.ServeHTTP(w, req)

		if w.Code != http.StatusOK {
			t.Errorf("Expected status %d, got %d", http.StatusOK, w.Code)
		}

		var response models.LoginResponse
		if err := json.Unmarshal(w.Body.Bytes(), &response); err != nil {
			t.Fatalf("Failed to unmarshal response: %v", err)
		}

		if response.Token == "" {
			t.Error("Expected token to be present in response")
		}

		if response.User.Username != "user1" {
			t.Errorf("Expected username 'user1', got '%s'", response.User.Username)
		}
	})

	// Test invalid username
	t.Run("InvalidUsername", func(t *testing.T) {
		loginReq := models.LoginRequest{
			Username: "invalid",
			Password: "password",
		}

		jsonReq, _ := json.Marshal(loginReq)
		req := httptest.NewRequest(http.MethodPost, "/login", bytes.NewReader(jsonReq))
		req.Header.Set("Content-Type", "application/json")

		w := httptest.NewRecorder()
		router.ServeHTTP(w, req)

		if w.Code != http.StatusUnauthorized {
			t.Errorf("Expected status %d, got %d", http.StatusUnauthorized, w.Code)
		}
	})

	// Test invalid password
	t.Run("InvalidPassword", func(t *testing.T) {
		loginReq := models.LoginRequest{
			Username: "user1",
			Password: "wrongpassword",
		}

		jsonReq, _ := json.Marshal(loginReq)
		req := httptest.NewRequest(http.MethodPost, "/login", bytes.NewReader(jsonReq))
		req.Header.Set("Content-Type", "application/json")

		w := httptest.NewRecorder()
		router.ServeHTTP(w, req)

		if w.Code != http.StatusUnauthorized {
			t.Errorf("Expected status %d, got %d", http.StatusUnauthorized, w.Code)
		}
	})

	// Test malformed JSON
	t.Run("MalformedJSON", func(t *testing.T) {
		req := httptest.NewRequest(http.MethodPost, "/login", bytes.NewReader([]byte("invalid json")))
		req.Header.Set("Content-Type", "application/json")

		w := httptest.NewRecorder()
		router.ServeHTTP(w, req)

		if w.Code != http.StatusBadRequest {
			t.Errorf("Expected status %d, got %d", http.StatusBadRequest, w.Code)
		}
	})
} 