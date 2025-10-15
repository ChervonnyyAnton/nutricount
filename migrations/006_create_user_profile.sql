-- Migration to create user_profile table for personal information
CREATE TABLE IF NOT EXISTS user_profile (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    gender TEXT NOT NULL CHECK (gender IN ('male', 'female')),
    birth_date DATE NOT NULL,
    height_cm INTEGER NOT NULL CHECK (height_cm >= 100 AND height_cm <= 250),
    weight_kg REAL NOT NULL CHECK (weight_kg >= 30 AND weight_kg <= 500),
    activity_level TEXT NOT NULL CHECK (activity_level IN ('sedentary', 'light', 'moderate', 'active', 'very_active')),
    goal TEXT NOT NULL CHECK (goal IN ('weight_loss', 'maintenance', 'muscle_gain')),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create trigger to update updated_at timestamp
CREATE TRIGGER IF NOT EXISTS update_user_profile_timestamp 
    AFTER UPDATE ON user_profile
BEGIN
    UPDATE user_profile SET updated_at = CURRENT_TIMESTAMP WHERE id = NEW.id;
END;

-- Insert default profile (optional)
INSERT OR IGNORE INTO user_profile (
    gender, birth_date, height_cm, weight_kg, activity_level, goal
) VALUES (
    'male', '1990-01-01', 175, 70, 'moderate', 'maintenance'
);
