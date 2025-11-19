# Scripts Directory

This directory contains utility scripts for database setup and service initialization.

## Service Scripts (Used by Docker)

### `entrypoint.sh`
- **Purpose**: Docker container entrypoint
- **When it runs**: Automatically on `docker-compose up`
- **What it does**:
  1. Initializes database (creates DB, enables pgvector)
  2. Runs Alembic migrations
  3. Starts the FastAPI application
- **Used by**: Docker container (referenced in Dockerfile)

### `init_database.sh`
- **Purpose**: Automatic database initialization
- **When it runs**: Called by `entrypoint.sh` on container startup
- **What it does**:
  1. Waits for PostgreSQL to be ready
  2. Creates database if it doesn't exist
  3. Enables pgvector extension
- **Works with**: Both container and local PostgreSQL modes

## Setup Scripts (Run Manually - One Time)

### `install_pgvector.sh`
- **Purpose**: Install pgvector extension on local PostgreSQL
- **When to run**: Before using local PostgreSQL mode (one-time)
- **Usage**: `./scripts/install_pgvector.sh`
- **Requirements**: PostgreSQL installed, build tools (gcc, make)
- **What it does**:
  1. Installs build dependencies
  2. Downloads pgvector source code
  3. Compiles and installs pgvector extension

### `configure_postgres_docker.sh`
- **Purpose**: Configure local PostgreSQL to accept Docker connections
- **When to run**: Before using local PostgreSQL mode (one-time)
- **Usage**: `./scripts/configure_postgres_docker.sh`
- **Requirements**: sudo access
- **What it does**:
  1. Configures PostgreSQL to listen on all interfaces
  2. Adds Docker network (172.17.0.0/16) to allowed hosts
  3. Restarts PostgreSQL service

### `fix_docker_network.sh`
- **Purpose**: Add additional Docker network to PostgreSQL
- **When to run**: If you get "no pg_hba.conf entry" errors
- **Usage**: `./scripts/fix_docker_network.sh`
- **Requirements**: sudo access
- **What it does**:
  1. Adds Docker network (172.19.0.0/16) to allowed hosts
  2. Restarts PostgreSQL service

### `setup_local_db.sh`
- **Purpose**: Complete local PostgreSQL setup (legacy/manual)
- **When to run**: Optional - manual database setup
- **Usage**: `./scripts/setup_local_db.sh`
- **Requirements**: PostgreSQL installed, pgvector available, sudo access
- **What it does**:
  1. Verifies PostgreSQL installation
  2. Creates database user
  3. Creates database
  4. Enables pgvector extension
  5. Grants privileges

**Note**: With automatic initialization (`init_database.sh`), this script is only needed if you want to pre-create the database before running `docker-compose up`.

## Quick Start

### For Container Mode (Default)
No scripts needed! Just run:
```bash
docker-compose up
```

### For Local PostgreSQL Mode
One-time setup:
```bash
# 1. Install pgvector
./scripts/install_pgvector.sh

# 2. Configure PostgreSQL for Docker
./scripts/configure_postgres_docker.sh

# 3. Fix Docker network (if needed)
./scripts/fix_docker_network.sh

# 4. Update .env to use local PostgreSQL
# DATABASE_URL=postgresql+asyncpg://postgres:password@host.docker.internal:5432/hylancer_ai

# 5. Start service (database auto-created!)
docker-compose up
```

## Troubleshooting

If you encounter issues:

1. **"pgvector extension not found"**
   - Run: `./scripts/install_pgvector.sh`

2. **"Connection refused"**
   - Run: `./scripts/configure_postgres_docker.sh`

3. **"no pg_hba.conf entry for host"**
   - Run: `./scripts/fix_docker_network.sh`

4. **"permission denied to create database"**
   - Use postgres superuser in DATABASE_URL, or
   - Grant CREATEDB: `sudo -u postgres psql -c "ALTER USER \"user\" WITH CREATEDB;"`

## Script Permissions

All scripts should be executable:
```bash
chmod +x scripts/*.sh
```
