#!/bin/bash
# Setup script for Virtual Interview Generator

echo "===== Virtual Interview Generator Setup ====="
echo

# Create virtual environment
echo "Creating Python virtual environment..."
python3 -m venv venv

# Activate virtual environment
echo "Activating virtual environment..."
VENV_ACTIVATE="./venv/bin/activate"
if [ -f "$VENV_ACTIVATE" ]; then
    source "$VENV_ACTIVATE"
    echo "Virtual environment activated successfully."
else
    echo "WARNING: Virtual environment activation failed. Continuing without it."
    echo "You may need to install python3-venv package:"
    echo "sudo apt install python3-venv"
fi

# Install dependencies
echo "Installing dependencies..."
pip install -r requirements.txt

# Create required directories
echo "Setting up directory structure..."
mkdir -p data/scripts
mkdir -p data/personas
mkdir -p data/interviews
mkdir -p exports

# Check for .env file
if [ ! -f .env ]; then
    echo "Creating .env file template..."
    echo "OPENAI_API_KEY=your_openai_api_key" > .env
    echo "ANTHROPIC_API_KEY=your_anthropic_api_key" >> .env
    echo "GOOGLE_API_KEY=your_google_api_key" >> .env
    echo "IMPORTANT: Edit the .env file with your actual API keys!"
else
    echo ".env file already exists, skipping..."
fi

# Initialize database
echo "Initializing database..."
python -c "from src.database.db_manager import db_manager" || echo "Database initialization failed. Please check Python setup."

echo
echo "===== Setup Complete ====="
echo "To activate the environment: source venv/bin/activate"
echo "To run the application: python src/main.py"
echo "Check deployment_tutorial/README.md for detailed usage instructions"