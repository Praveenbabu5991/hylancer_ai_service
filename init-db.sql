-- init-db.sql - Database initialization script for Hylancer AI Service
-- This script runs automatically when the PostgreSQL container starts for the first time

-- Enable pgvector extension
CREATE EXTENSION IF NOT EXISTS vector;

-- Log successful initialization
DO $$
BEGIN
    RAISE NOTICE 'Hylancer AI Database initialized successfully';
    RAISE NOTICE 'pgvector extension enabled';
END $$;
