#!/bin/bash
# Test runner script for auth API tests

echo "🧪 Running Auth API Tests..."
echo ""

# Activate virtual environment and run tests
.venv/bin/pytest tests/test_auth_api.py -v --asyncio-mode=auto

echo ""
echo "✅ Tests complete!"
