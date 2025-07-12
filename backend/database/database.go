package database

import (
	"database/sql"
	"fmt"
	"log"
	"os"

	_ "github.com/lib/pq"
)

var DB *sql.DB

func Connect() error {
	databaseURL := os.Getenv("DATABASE_URL")
	if databaseURL == "" {
		return fmt.Errorf("DATABASE_URL environment variable is not set")
	}

	var err error
	DB, err = sql.Open("postgres", databaseURL)
	if err != nil {
		return fmt.Errorf("failed to connect to database: %w", err)
	}

	if err = DB.Ping(); err != nil {
		return fmt.Errorf("failed to ping database: %w", err)
	}

	log.Println("Connected to database successfully")
	return nil
}

func CreateTables() error {
	// Create users table
	usersTable := `
		CREATE TABLE IF NOT EXISTS users (
			id SERIAL PRIMARY KEY,
			username VARCHAR(255) UNIQUE NOT NULL,
			password_hash VARCHAR(255) NOT NULL,
			created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
		);
	`

	// Create meals table
	mealsTable := `
		CREATE TABLE IF NOT EXISTS meals (
			id SERIAL PRIMARY KEY,
			name VARCHAR(255) NOT NULL,
			ingredients TEXT NOT NULL,
			recipe TEXT NOT NULL,
			difficulty VARCHAR(50) NOT NULL,
			created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
			updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
		);
	`

	// Create trigger for updated_at
	updateTrigger := `
		CREATE OR REPLACE FUNCTION update_updated_at_column()
		RETURNS TRIGGER AS $$
		BEGIN
			NEW.updated_at = CURRENT_TIMESTAMP;
			RETURN NEW;
		END;
		$$ language 'plpgsql';

		DROP TRIGGER IF EXISTS update_meals_updated_at ON meals;
		CREATE TRIGGER update_meals_updated_at
			BEFORE UPDATE ON meals
			FOR EACH ROW
			EXECUTE FUNCTION update_updated_at_column();
	`

	if _, err := DB.Exec(usersTable); err != nil {
		return fmt.Errorf("failed to create users table: %w", err)
	}

	if _, err := DB.Exec(mealsTable); err != nil {
		return fmt.Errorf("failed to create meals table: %w", err)
	}

	if _, err := DB.Exec(updateTrigger); err != nil {
		return fmt.Errorf("failed to create update trigger: %w", err)
	}

	log.Println("Database tables created successfully")
	return nil
}

func Close() error {
	if DB != nil {
		return DB.Close()
	}
	return nil
}
