package models

import (
	"time"
)

type Meal struct {
	ID          int       `json:"id" db:"id"`
	Name        string    `json:"name" db:"name"`
	Ingredients string    `json:"ingredients" db:"ingredients"`
	Recipe      string    `json:"recipe" db:"recipe"`
	Difficulty  string    `json:"difficulty" db:"difficulty"`
	CreatedAt   time.Time `json:"created_at" db:"created_at"`
	UpdatedAt   time.Time `json:"updated_at" db:"updated_at"`
}

type CreateMealRequest struct {
	Name        string `json:"name" binding:"required"`
	Ingredients string `json:"ingredients" binding:"required"`
	Recipe      string `json:"recipe" binding:"required"`
	Difficulty  string `json:"difficulty" binding:"required"`
}

type UpdateMealRequest struct {
	Name        string `json:"name" binding:"required"`
	Ingredients string `json:"ingredients" binding:"required"`
	Recipe      string `json:"recipe" binding:"required"`
	Difficulty  string `json:"difficulty" binding:"required"`
}
