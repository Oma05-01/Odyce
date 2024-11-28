#!/usr/bin/env bash
# Exit on error
set -o errexit
set -o nounset  # Treat unset variables as an error and exit

# Ensure pip is installed
if ! command -v pip &>/dev/null; then
    echo "Error: pip is not installed."
    exit 1
fi

# Ensure python is available
if ! command -v python &>/dev/null; then
    echo "Error: python is not installed."
    exit 1
fi

# Install dependencies from requirements.txt
if [ -f "requirements.txt" ]; then
    pip install -r "requirements.txt"
else
    echo "Error: requirements.txt file not found!"
    exit 1
fi

# Collect static files (this command should run in Django projects)
if [ -f "manage.py" ]; then
    python manage.py collectstatic --no-input
else
    echo "Error: manage.py not found!"
    exit 1
fi

# Apply any outstanding database migrations
python manage.py migrate

