-- Create extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Create sessions table
CREATE TABLE IF NOT EXISTS sessions (
    id SERIAL PRIMARY KEY,
    date DATE NOT NULL,
    start_time TIME,
    training_name VARCHAR(100),
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create sets table
CREATE TABLE IF NOT EXISTS sets (
    id SERIAL PRIMARY KEY,
    session_id INTEGER REFERENCES sessions(id) ON DELETE CASCADE,
    exercise VARCHAR(100) NOT NULL,
    series_type VARCHAR(50), -- 'échauffement', 'principale', 'récupération'
    reps INTEGER,
    weight_kg DECIMAL(5,2),
    notes TEXT,
    skipped BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create exercises catalog
CREATE TABLE IF NOT EXISTS exercises (
    name VARCHAR(100) PRIMARY KEY,
    main_region VARCHAR(50),
    muscles_primary TEXT[],
    muscles_secondary TEXT[],
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_sessions_date ON sessions(date);
CREATE INDEX IF NOT EXISTS idx_sets_session_id ON sets(session_id);
CREATE INDEX IF NOT EXISTS idx_sets_exercise ON sets(exercise);
CREATE INDEX IF NOT EXISTS idx_exercises_region ON exercises(main_region);

