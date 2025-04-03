#!/bin/bash
#
# Virtual Interview Generator Runner
# 
# Usage: ./run_interview.sh [options]
#
# Options:
#   --help                 Show help message
#   --use-finepersonas     Use the FinePersonas database for enhanced personas
#   --anthropic-key KEY    Set Anthropic API key
#   --openai-key KEY       Set OpenAI API key
#   --google-key KEY       Set Google API key

# Initialize environment and dependencies

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

# Check for dependencies required for PDF generation
echo "Checking PDF generation dependencies..."

# Check if pandoc is installed
if ! command -v pandoc &> /dev/null; then
  echo "Warning: Pandoc is not installed. PDFs cannot be generated without it."
  MISSING_DEPS=1
else
  echo "✓ Pandoc is installed."
fi

# Check if pypandoc is installed
if ! pip show pypandoc &> /dev/null; then
  echo "Warning: Python package pypandoc is not installed."
  MISSING_DEPS=1
else
  echo "✓ Python package pypandoc is installed."
fi

# Check for LaTeX packages
LATEX_ISSUE=0

# Check for texlive-xetex (provides xelatex)
if ! command -v xelatex &> /dev/null; then
  echo "Warning: xelatex is not installed."
  LATEX_ISSUE=1
else
  echo "✓ xelatex is installed."
fi

# Check for pdflatex as a fallback
if ! command -v pdflatex &> /dev/null; then
  echo "Warning: pdflatex is not installed."
  LATEX_ISSUE=1
else
  echo "✓ pdflatex is installed."
fi

# Check for texlive-latex-base
if ! dpkg-query -W -f='${Status}' texlive-latex-base 2>/dev/null | grep -q "install ok installed"; then
  echo "Warning: texlive-latex-base is not installed."
  LATEX_ISSUE=1
else
  echo "✓ texlive-latex-base is installed."
fi

# Check for texlive-fonts-recommended
if ! dpkg-query -W -f='${Status}' texlive-fonts-recommended 2>/dev/null | grep -q "install ok installed"; then
  echo "Warning: texlive-fonts-recommended is not installed."
  LATEX_ISSUE=1
else
  echo "✓ texlive-fonts-recommended is installed."
fi

# Check for texlive-latex-extra (contains xcolor.sty and other required packages)
if ! dpkg-query -W -f='${Status}' texlive-latex-extra 2>/dev/null | grep -q "install ok installed"; then
  echo "Warning: texlive-latex-extra is not installed."
  LATEX_ISSUE=1
else
  echo "✓ texlive-latex-extra is installed."
fi

# Explicit check for xcolor.sty
if ! find /usr -name "xcolor.sty" 2>/dev/null | grep -q "xcolor.sty"; then
  echo "Warning: LaTeX package 'xcolor.sty' not found. PDF generation will fail."
  LATEX_ISSUE=1
else
  echo "✓ LaTeX package xcolor.sty is available."
fi

# Provide installation instructions if there are missing dependencies
if [ "$LATEX_ISSUE" -eq 1 ]; then
  echo ""
  echo "LaTeX packages are required for PDF generation. Please run:"
  echo "sudo apt-get install texlive-latex-base texlive-fonts-recommended texlive-latex-extra texlive-xetex"
  echo ""
  echo "After installing, try running the script again."
  echo "Alternatively, you can continue without PDF generation capabilities."
  echo ""
  
  # Ask if the user wants to install the packages now
  read -p "Do you want to install the LaTeX packages now? (y/n) " -n 1 -r
  echo
  if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "Installing LaTeX packages..."
    sudo apt-get update
    sudo apt-get install -y texlive-latex-base texlive-fonts-recommended texlive-latex-extra texlive-xetex
    echo "LaTeX packages installation completed."
  fi
fi

# Create necessary base directories
mkdir -p exports data/interviews data/personas data/scripts

# Run the interactive interviews script with all API keys
python interactive_interviews.py --anthropic-key "$ANTHROPIC_API_KEY" --openai-key "$OPENAI_API_KEY" --google-key "$GOOGLE_API_KEY" "$@"

# Deactivate virtual environment
deactivate