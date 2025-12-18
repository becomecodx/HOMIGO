#!/bin/bash
# Add Firebase Project ID to .env file

ENV_FILE=".env"
FIREBASE_PROJECT_ID="homigo-26880"

# Check if .env exists
if [ ! -f "$ENV_FILE" ]; then
    echo "Error: .env file not found!"
    exit 1
fi

# Check if FIREBASE_PROJECT_ID already exists
if grep -q "^FIREBASE_PROJECT_ID=" "$ENV_FILE"; then
    echo "FIREBASE_PROJECT_ID already exists in .env"
    echo "Current value: $(grep "^FIREBASE_PROJECT_ID=" "$ENV_FILE")"
else
    # Add Firebase project ID to .env
    echo "" >> "$ENV_FILE"
    echo "# Firebase Configuration" >> "$ENV_FILE"
    echo "FIREBASE_PROJECT_ID=$FIREBASE_PROJECT_ID" >> "$ENV_FILE"
    echo "✓ Added FIREBASE_PROJECT_ID=$FIREBASE_PROJECT_ID to .env"
fi

echo ""
echo "Please restart your server for changes to take effect:"
echo ".venv/bin/python -m uvicorn app.main:app --reload --port 8000"
