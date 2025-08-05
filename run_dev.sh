#!/bin/bash

echo "================================"
echo "Smart Research Assistant v2"
echo "================================"
echo ""

echo "Starting development server..."
echo ""

cd backend

echo "Installing/updating dependencies..."
pip install -r requirements.txt

if [ $? -ne 0 ]; then
    echo ""
    echo "ERROR: Failed to install dependencies"
    echo "Please check your Python installation and internet connection"
    exit 1
fi

echo ""
echo "Starting Flask development server..."
echo "Server will be available at: http://localhost:5000"
echo ""

python app.py

if [ $? -ne 0 ]; then
    echo ""
    echo "ERROR: Failed to start server"
    echo "Please check the error messages above"
    exit 1
fi
