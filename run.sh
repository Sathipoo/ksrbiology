#!/bin/bash
# Startup script for KSR Biology Portal
cd "$(dirname "$0")"

# Activate virtualenv if present
if [ -d "venv" ]; then
  source venv/bin/activate
fi

export FLASK_APP=app.py
export FLASK_ENV=development

echo "🌱 Starting KSR Biology Portal..."
echo "📍 Access Student Portal: http://127.0.0.1:5001"
echo "🔐 Teacher Admin Login: http://127.0.0.1:5001/admin/login (Password: ksradmin2026)"

python3 app.py
