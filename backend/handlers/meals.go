package handlers

import (
	"net/http"
	"strconv"

	"cookbook-backend/database"
	"cookbook-backend/models"

	"github.com/gin-gonic/gin"
)

func GetMeals(c *gin.Context) {
	query := `
		SELECT id, name, ingredients, recipe, difficulty, created_at, updated_at
		FROM meals
		ORDER BY created_at DESC
	`

	rows, err := database.DB.Query(query)
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to fetch meals"})
		return
	}
	defer rows.Close()

	var meals []models.Meal
	for rows.Next() {
		var meal models.Meal
		err := rows.Scan(&meal.ID, &meal.Name, &meal.Ingredients, &meal.Recipe, &meal.Difficulty, &meal.CreatedAt, &meal.UpdatedAt)
		if err != nil {
			c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to scan meal"})
			return
		}
		meals = append(meals, meal)
	}

	c.JSON(http.StatusOK, gin.H{"meals": meals})
}

func GetMeal(c *gin.Context) {
	id, err := strconv.Atoi(c.Param("id"))
	if err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid meal ID"})
		return
	}

	query := `
		SELECT id, name, ingredients, recipe, difficulty, created_at, updated_at
		FROM meals
		WHERE id = $1
	`

	var meal models.Meal
	err = database.DB.QueryRow(query, id).Scan(&meal.ID, &meal.Name, &meal.Ingredients, &meal.Recipe, &meal.Difficulty, &meal.CreatedAt, &meal.UpdatedAt)
	if err != nil {
		c.JSON(http.StatusNotFound, gin.H{"error": "Meal not found"})
		return
	}

	c.JSON(http.StatusOK, gin.H{"meal": meal})
}

func CreateMeal(c *gin.Context) {
	var req models.CreateMealRequest
	if err := c.ShouldBindJSON(&req); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": err.Error()})
		return
	}

	query := `
		INSERT INTO meals (name, ingredients, recipe, difficulty)
		VALUES ($1, $2, $3, $4)
		RETURNING id, name, ingredients, recipe, difficulty, created_at, updated_at
	`

	var meal models.Meal
	err := database.DB.QueryRow(query, req.Name, req.Ingredients, req.Recipe, req.Difficulty).Scan(
		&meal.ID, &meal.Name, &meal.Ingredients, &meal.Recipe, &meal.Difficulty, &meal.CreatedAt, &meal.UpdatedAt,
	)
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to create meal"})
		return
	}

	c.JSON(http.StatusCreated, gin.H{"meal": meal})
}

func UpdateMeal(c *gin.Context) {
	id, err := strconv.Atoi(c.Param("id"))
	if err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid meal ID"})
		return
	}

	var req models.UpdateMealRequest
	if err := c.ShouldBindJSON(&req); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": err.Error()})
		return
	}

	query := `
		UPDATE meals
		SET name = $1, ingredients = $2, recipe = $3, difficulty = $4
		WHERE id = $5
		RETURNING id, name, ingredients, recipe, difficulty, created_at, updated_at
	`

	var meal models.Meal
	err = database.DB.QueryRow(query, req.Name, req.Ingredients, req.Recipe, req.Difficulty, id).Scan(
		&meal.ID, &meal.Name, &meal.Ingredients, &meal.Recipe, &meal.Difficulty, &meal.CreatedAt, &meal.UpdatedAt,
	)
	if err != nil {
		c.JSON(http.StatusNotFound, gin.H{"error": "Meal not found"})
		return
	}

	c.JSON(http.StatusOK, gin.H{"meal": meal})
}

func DeleteMeal(c *gin.Context) {
	id, err := strconv.Atoi(c.Param("id"))
	if err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid meal ID"})
		return
	}

	query := `DELETE FROM meals WHERE id = $1`
	result, err := database.DB.Exec(query, id)
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to delete meal"})
		return
	}

	rowsAffected, err := result.RowsAffected()
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to check deletion"})
		return
	}

	if rowsAffected == 0 {
		c.JSON(http.StatusNotFound, gin.H{"error": "Meal not found"})
		return
	}

	c.JSON(http.StatusOK, gin.H{"message": "Meal deleted successfully"})
} 