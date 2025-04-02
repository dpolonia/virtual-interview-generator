# Virtual Interview Generator

A tool for generating simulated interviews between personas about AI in the consulting industry.

## Overview

This project creates realistic virtual interviews for research on "The Role of Business Consulting Firms in the Era of Artificial Intelligence." It uses large language models (LLMs) to simulate conversations between interviewers and various stakeholders in the consulting industry.

## Features

- Interview script parsing from source documents
- AI-powered persona generation for interviewers and stakeholders
- Interview simulation following structured scripts
- Support for multiple AI models (OpenAI, Anthropic, Google)
- XML output formatting for structured data analysis
- Optional integration with FinePersonas dataset

## Stakeholder Categories

- Senior Executives from Consulting Firms
- AI Specialists and Data Scientists
- Mid-Level Consultants
- Clients of Consulting Services
- Technology Providers
- Regulatory Stakeholders
- Industry Analysts/Academics

## Installation

See [INSTALL.md](INSTALL.md) for detailed installation instructions.

Quick start:
```bash
# Clone the repository
git clone <repository-url>
cd virtual-interview-generator

# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up API keys in .env file
# Example:
# OPENAI_API_KEY=your_key_here
# ANTHROPIC_API_KEY=your_key_here
# GOOGLE_API_KEY=your_key_here

# Run the application
python src/main.py
```

## Usage

The application provides a command-line interface with the following commands:

```bash
# Parse interview scripts from source documents
python src/main.py parse-scripts

# Generate personas for interviewers and stakeholders
python src/main.py generate-personas

# Generate interviews between selected personas
python src/main.py generate-interviews

# Export interviews to files
python src/main.py export-interviews

# Generate a comprehensive report
python src/main.py generate-report
```

## Directory Structure

- `src/`: Source code
  - `database/`: Database management
  - `models/`: AI model interfaces
  - `prompts/`: Prompt templates for AI models
  - `utils/`: Utility functions
- `data/`: Data storage
  - `scripts/`: Parsed interview scripts
  - `personas/`: Generated personas
  - `interviews/`: Generated interviews
- `docs/`: Documentation
- `exports/`: Output files

## License

[Specify your license here]

## Contributing

[Add contribution guidelines if applicable]