package utils

import (
	"os"
	"testing"
	"time"

	"github.com/golang-jwt/jwt/v5"
)

func TestGenerateToken(t *testing.T) {
	// Set up test environment
	os.Setenv("JWT_SECRET", "test-secret-key")
	defer os.Unsetenv("JWT_SECRET")

	userID := 1
	username := "testuser"

	token, err := GenerateToken(userID, username)
	if err != nil {
		t.Fatalf("Failed to generate token: %v", err)
	}

	if token == "" {
		t.Fatal("Generated token is empty")
	}

	// Verify the token can be parsed
	claims, err := ValidateToken(token)
	if err != nil {
		t.Fatalf("Failed to validate generated token: %v", err)
	}

	if claims.UserID != userID {
		t.Errorf("Expected UserID %d, got %d", userID, claims.UserID)
	}

	if claims.Username != username {
		t.Errorf("Expected Username %s, got %s", username, claims.Username)
	}
}

func TestValidateToken(t *testing.T) {
	// Set up test environment
	os.Setenv("JWT_SECRET", "test-secret-key")
	defer os.Unsetenv("JWT_SECRET")

	userID := 1
	username := "testuser"

	// Generate a test token
	token, err := GenerateToken(userID, username)
	if err != nil {
		t.Fatalf("Failed to generate token: %v", err)
	}

	// Validate the token
	claims, err := ValidateToken(token)
	if err != nil {
		t.Fatalf("Failed to validate token: %v", err)
	}

	if claims.UserID != userID {
		t.Errorf("Expected UserID %d, got %d", userID, claims.UserID)
	}

	if claims.Username != username {
		t.Errorf("Expected Username %s, got %s", username, claims.Username)
	}
}

func TestValidateTokenInvalid(t *testing.T) {
	// Set up test environment
	os.Setenv("JWT_SECRET", "test-secret-key")
	defer os.Unsetenv("JWT_SECRET")

	// Test with invalid token
	_, err := ValidateToken("invalid-token")
	if err == nil {
		t.Fatal("Expected error for invalid token, got nil")
	}
}

func TestValidateTokenExpired(t *testing.T) {
	// Set up test environment
	os.Setenv("JWT_SECRET", "test-secret-key")
	defer os.Unsetenv("JWT_SECRET")

	// Create an expired token
	claims := &Claims{
		UserID:   1,
		Username: "testuser",
		RegisteredClaims: jwt.RegisteredClaims{
			ExpiresAt: jwt.NewNumericDate(time.Now().Add(-time.Hour)), // Expired 1 hour ago
			IssuedAt:  jwt.NewNumericDate(time.Now().Add(-2 * time.Hour)),
		},
	}

	token := jwt.NewWithClaims(jwt.SigningMethodHS256, claims)
	tokenString, err := token.SignedString([]byte("test-secret-key"))
	if err != nil {
		t.Fatalf("Failed to create expired token: %v", err)
	}

	// Validate the expired token
	_, err = ValidateToken(tokenString)
	if err == nil {
		t.Fatal("Expected error for expired token, got nil")
	}
} 