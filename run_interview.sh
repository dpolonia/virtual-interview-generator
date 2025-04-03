#!/bin/bash

# Virtual Interview Generator Runner

# Check if virtual environment exists
if [ ! -d "venv" ]; then
  echo "Creating virtual environment..."
  python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Check if requirements are installed
pip freeze | grep -q "anthropic" || pip install -r requirements.txt

# Load API keys from .env file if it exists
if [ -f .env ]; then
  echo "Loading API keys from .env file..."
  set -a
  source .env
  set +a
else
  # Prompt for API keys if not set
  if [ -z "$ANTHROPIC_API_KEY" ]; then
    echo "Enter your Anthropic API key (leave empty to skip):"
    read -s ANTHROPIC_API_KEY
    export ANTHROPIC_API_KEY
  fi
  
  if [ -z "$OPENAI_API_KEY" ]; then
    echo "Enter your OpenAI API key (leave empty to skip):"
    read -s OPENAI_API_KEY
    export OPENAI_API_KEY
  fi
  
  if [ -z "$GOOGLE_API_KEY" ]; then
    echo "Enter your Google API key (leave empty to skip):"
    read -s GOOGLE_API_KEY
    export GOOGLE_API_KEY
  fi
fi

# Check if pandoc is installed for PDF generation
if ! command -v pandoc &> /dev/null; then
  echo "Pandoc is not installed. PDFs cannot be generated without it."
  echo "After running the script, you'll be prompted to install pandoc."
fi

# Create necessary base directories
mkdir -p exports data/interviews data/personas data/scripts

# Run the interactive interviews script with all API keys
python interactive_interviews.py --anthropic-key "$ANTHROPIC_API_KEY" --openai-key "$OPENAI_API_KEY" --google-key "$GOOGLE_API_KEY" "$@"

# Deactivate virtual environment
deactivate