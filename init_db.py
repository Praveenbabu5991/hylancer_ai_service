#!/usr/bin/env python3
"""
init_db.py - Database initialization script for Hylancer AI Service
This script creates the database, enables pgvector extension, and runs migrations.
Works with both local PostgreSQL and containerized setups.
"""

import os
import sys
import time
import subprocess
from urllib.parse import urlparse
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
from loguru import logger

# Configure logger
logger.remove()
logger.add(sys.stdout, format="<green>{time:HH:mm:ss}</green> | <level>{level: <8}</level> | <level>{message}</level>")


def parse_database_url(database_url: str) -> dict:
    """Parse DATABASE_URL into components."""
    # Replace asyncpg with psycopg2 for synchronous operations
    url = database_url.replace("postgresql+asyncpg", "postgresql")
    parsed = urlparse(url)

    # Convert localhost to host.docker.internal when running in Docker
    # This allows the container to connect to PostgreSQL on the host machine
    host = parsed.hostname
    if host in ["localhost", "127.0.0.1"]:
        # Check if we're running inside a Docker container
        if os.path.exists("/.dockerenv"):
            host = "host.docker.internal"
            logger.info(f"Running in Docker: Converting {parsed.hostname} -> host.docker.internal")

    return {
        "user": parsed.username,
        "password": parsed.password,
        "host": host,
        "port": parsed.port or 5432,
        "database": parsed.path.lstrip("/") if parsed.path else "postgres",
    }


def wait_for_postgres(host: str, port: int, user: str, password: str, max_retries: int = 30):
    """Wait for PostgreSQL to be ready."""
    logger.info(f"Waiting for PostgreSQL at {host}:{port}...")

    for attempt in range(1, max_retries + 1):
        try:
            conn = psycopg2.connect(
                host=host,
                port=port,
                user=user,
                password=password,
                database="postgres",
                connect_timeout=3
            )
            conn.close()
            logger.success("✓ PostgreSQL is ready!")
            return True
        except psycopg2.OperationalError as e:
            if attempt < max_retries:
                logger.warning(f"PostgreSQL not ready (attempt {attempt}/{max_retries}), retrying in 2s...")
                time.sleep(2)
            else:
                logger.error(f"✗ Failed to connect to PostgreSQL after {max_retries} attempts")
                logger.error(f"Error: {e}")
                return False

    return False


def database_exists(host: str, port: int, user: str, password: str, dbname: str) -> bool:
    """Check if database exists."""
    try:
        conn = psycopg2.connect(
            host=host,
            port=port,
            user=user,
            password=password,
            database="postgres"
        )
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cursor = conn.cursor()

        cursor.execute("SELECT 1 FROM pg_database WHERE datname = %s", (dbname,))
        exists = cursor.fetchone() is not None

        cursor.close()
        conn.close()

        return exists
    except Exception as e:
        logger.error(f"Error checking database existence: {e}")
        return False


def create_database(host: str, port: int, user: str, password: str, dbname: str) -> bool:
    """Create database if it doesn't exist."""
    try:
        if database_exists(host, port, user, password, dbname):
            logger.info(f"✓ Database '{dbname}' already exists")
            return True

        logger.info(f"Creating database '{dbname}'...")

        conn = psycopg2.connect(
            host=host,
            port=port,
            user=user,
            password=password,
            database="postgres"
        )
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cursor = conn.cursor()

        cursor.execute(f'CREATE DATABASE "{dbname}"')

        cursor.close()
        conn.close()

        logger.success(f"✓ Database '{dbname}' created successfully")
        return True

    except Exception as e:
        logger.error(f"✗ Failed to create database: {e}")
        return False


def enable_pgvector(host: str, port: int, user: str, password: str, dbname: str) -> bool:
    """Enable pgvector extension."""
    try:
        logger.info("Enabling pgvector extension...")

        conn = psycopg2.connect(
            host=host,
            port=port,
            user=user,
            password=password,
            database=dbname
        )
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cursor = conn.cursor()

        cursor.execute("CREATE EXTENSION IF NOT EXISTS vector")

        cursor.close()
        conn.close()

        logger.success("✓ pgvector extension enabled")
        return True

    except Exception as e:
        logger.error(f"✗ Failed to enable pgvector extension: {e}")
        logger.error("  Make sure pgvector is installed on your PostgreSQL server")
        logger.error("  Installation: https://github.com/pgvector/pgvector#installation")
        return False


def run_migrations() -> bool:
    """Run Alembic migrations."""
    try:
        logger.info("Running Alembic migrations...")

        # Run alembic upgrade head
        result = subprocess.run(
            ["alembic", "upgrade", "head"],
            capture_output=True,
            text=True,
            check=False
        )

        if result.returncode == 0:
            logger.success("✓ Database migrations completed successfully")
            return True
        else:
            logger.error(f"✗ Migration failed: {result.stderr}")
            return False

    except Exception as e:
        logger.error(f"✗ Failed to run migrations: {e}")
        return False


def main():
    """Main initialization function."""
    logger.info("=" * 50)
    logger.info("Hylancer AI Service - Database Initialization")
    logger.info("=" * 50)

    # Get DATABASE_URL from environment
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        logger.error("✗ DATABASE_URL environment variable not set")
        sys.exit(1)

    # Parse database URL
    db_config = parse_database_url(database_url)
    logger.info(f"Database Configuration:")
    logger.info(f"  Host: {db_config['host']}")
    logger.info(f"  Port: {db_config['port']}")
    logger.info(f"  User: {db_config['user']}")
    logger.info(f"  Database: {db_config['database']}")
    logger.info("")

    # Wait for PostgreSQL to be ready
    if not wait_for_postgres(
        db_config['host'],
        db_config['port'],
        db_config['user'],
        db_config['password']
    ):
        logger.error("✗ PostgreSQL is not accessible")
        sys.exit(1)

    # Create database if needed
    if not create_database(
        db_config['host'],
        db_config['port'],
        db_config['user'],
        db_config['password'],
        db_config['database']
    ):
        logger.error("✗ Database creation failed")
        sys.exit(1)

    # Enable pgvector extension
    if not enable_pgvector(
        db_config['host'],
        db_config['port'],
        db_config['user'],
        db_config['password'],
        db_config['database']
    ):
        logger.error("✗ pgvector extension setup failed")
        sys.exit(1)

    # Run migrations
    if not run_migrations():
        logger.error("✗ Database migrations failed")
        sys.exit(1)

    logger.info("")
    logger.info("=" * 50)
    logger.success("✓ Database initialization completed successfully!")
    logger.info("=" * 50)
    logger.info("")


if __name__ == "__main__":
    main()
