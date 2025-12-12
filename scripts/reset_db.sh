#!/bin/bash
"""
Reset and reseed the database
This script will:
1. Delete the existing database
2. Create fresh tables with the current schema
3. Seed with sample data
"""

# Get the directory where this script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
VENV_PYTHON="$PROJECT_ROOT/backend/venv/bin/python"

echo "🗑️  Removing old database..."
rm -f "$PROJECT_ROOT/data/housescope.db"

echo "📋 Creating database tables..."
"$VENV_PYTHON" "$SCRIPT_DIR/init_db.py"

echo "🌱 Seeding sample data..."
"$VENV_PYTHON" "$SCRIPT_DIR/seed_data.py"

echo ""
echo "✅ Database reset complete!"
