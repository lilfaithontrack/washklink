#!/bin/bash

# Production Deployment Script for WashLink Backend

echo "🚀 Starting WashLink Backend Production Deployment..."

# Set production environment
export ENVIRONMENT=production

# Copy production environment file
if [ -f ".env.production" ]; then
    cp .env.production .env
    echo "✅ Production environment file copied"
else
    echo "❌ .env.production file not found. Please create it first."
    exit 1
fi

# Install dependencies
echo "📦 Installing dependencies..."
pip install -r requirements.txt

# Run database migrations if needed
echo "🗄️ Setting up database..."
python setup_mongodb.py

# Create admin user if needed
echo "👤 Setting up admin user..."
python create_admin.py

# Start the application
echo "🌟 Starting production server..."
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4

echo "✅ Deployment complete!" 