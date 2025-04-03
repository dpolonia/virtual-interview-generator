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

# Store API keys
export ANTHROPIC_API_KEY="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"
export OPENAI_API_KEY="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"
export GOOGLE_API_KEY="AIzaSyCFBrW4dMl3uT5s0z3JhvboYwJacGTILYs"

# Check if pandoc is installed for PDF generation
if ! command -v pandoc &> /dev/null; then
  echo "Pandoc is not installed. PDFs cannot be generated without it."
  echo "After running the script, you'll be prompted to install pandoc."
fi

# Create necessary base directories
mkdir -p exports data/interviews data/personas data/scripts

# Run the interactive interviews script with all API keys
python interactive_interviews.py --anthropic-key "$ANTHROPIC_API_KEY" --openai-key "$OPENAI_API_KEY" --google-key "$GOOGLE_API_KEY" --use-finepersonas

# Deactivate virtual environment
deactivate