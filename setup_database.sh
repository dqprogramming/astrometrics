#!/bin/bash
#
# PostgreSQL Database Setup Script
# This script creates the database and enables required extensions
#
# Usage: ./setup_database.sh
#

set -e  # Exit on error

DB_NAME="astrometrics"
DB_USER="ajrbyers"

echo "==================================="
echo "Journal Search Database Setup"
echo "==================================="
echo ""

# Check if PostgreSQL is running
if ! pg_isready -q; then
    echo "❌ ERROR: PostgreSQL is not running."
    echo "Start PostgreSQL and run this script again."
    exit 1
fi

echo "✓ PostgreSQL is running"
echo ""

# Check if database exists
if psql -U "$DB_USER" -lqt | cut -d \| -f 1 | grep -qw "$DB_NAME"; then
    echo "⚠️  Database '$DB_NAME' already exists."
    read -p "Do you want to drop and recreate it? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo "Dropping existing database..."
        dropdb -U "$DB_USER" "$DB_NAME" || {
            echo "❌ Failed to drop database. You may need to disconnect all connections first."
            exit 1
        }
        echo "✓ Database dropped"
    else
        echo "Keeping existing database. Skipping database creation."
        echo "Will only enable extensions..."
        SKIP_CREATE=1
    fi
fi

# Create database if needed
if [ -z "$SKIP_CREATE" ]; then
    echo "Creating database '$DB_NAME'..."
    createdb -U "$DB_USER" "$DB_NAME" || {
        echo "❌ Failed to create database"
        exit 1
    }
    echo "✓ Database created"
fi

echo ""
echo "Enabling PostgreSQL extensions..."

# Enable pg_trgm extension (required for fuzzy search)
psql -U "$DB_USER" -d "$DB_NAME" -c "CREATE EXTENSION IF NOT EXISTS pg_trgm;" || {
    echo "❌ Failed to create pg_trgm extension"
    exit 1
}
echo "✓ pg_trgm extension enabled (fuzzy search)"

# Enable unaccent extension (optional, for accent-insensitive search)
psql -U "$DB_USER" -d "$DB_NAME" -c "CREATE EXTENSION IF NOT EXISTS unaccent;" || {
    echo "⚠️  Could not enable unaccent extension (optional, not critical)"
}

echo ""
echo "==================================="
echo "✅ Database setup complete!"
echo "==================================="
echo ""
echo "Database details:"
echo "  Name: $DB_NAME"
echo "  User: $DB_USER"
echo "  Host: localhost"
echo "  Port: 5432"
echo ""
echo "Next steps:"
echo "  1. Update your Django settings.py with these database credentials"
echo "  2. Run: python manage.py makemigrations journals"
echo "  3. Run: python manage.py migrate"
echo "  4. Run: python manage.py createsuperuser"
echo "  5. Run: python manage.py runserver"
echo ""
