# Virtual Interview Generator - Deployment Guide

This guide will help you deploy the Virtual Interview Generator application, which creates simulated AI-based interviews for research on consulting services.

## Prerequisites

- Python 3.8+ installed
- pip package manager
- Internet connection for AI API access

## Deployment Steps

### 1. Environment Setup

Create and activate a virtual environment:

```bash
# Create virtual environment
python -m venv venv

# Activate it
# On Linux/Mac:
source venv/bin/activate
# On Windows:
venv\Scripts\activate
```

### 2. Install Dependencies

```bash
# Install required packages
pip install -r requirements.txt
```

### 3. Configure API Keys

Create a `.env` file in the project root:

```bash
# Create .env file
touch .env

# Add your API keys
echo "OPENAI_API_KEY=your_openai_api_key" >> .env
echo "ANTHROPIC_API_KEY=your_anthropic_api_key" >> .env
echo "GOOGLE_API_KEY=your_google_api_key" >> .env
```

Replace `your_*_api_key` with your actual API keys.

### 4. Initialize the Database

```bash
# Run this Python command to initialize the database
python -c "from src.database.db_manager import db_manager"
```

### 5. Run the Application

```bash
# Start the CLI application
python src/main.py
```

## Usage Workflow

The application follows this standard workflow:

1. **Parse Interview Scripts**
   ```bash
   python src/main.py parse-scripts
   ```
   This will extract interview scripts from source documents (default: `docs/Master Dissertation - Script Interviews.pdf`).

2. **Generate Personas**
   ```bash
   python src/main.py generate-personas
   ```
   Creates interviewer and interviewee personas using either AI models or the FinePersonas dataset.

3. **Generate Interviews**
   ```bash
   python src/main.py generate-interviews
   ```
   Produces simulated interviews between selected personas following the script templates.

4. **Export Interviews**
   ```bash
   python src/main.py export-interviews --format xml
   ```
   Exports all interviews to files (XML or TXT format).

5. **Generate Report**
   ```bash
   python src/main.py generate-report
   ```
   Creates a comprehensive analysis report of all interviews.

## Troubleshooting

- **API Key Issues**: Ensure your `.env` file has the correct API keys.
- **Database Errors**: Check that the `data/` directory and subdirectories exist.
- **Document Parsing Problems**: Verify the source document path and format.

## Production Deployment (Optional)

For production use, consider:

1. **Docker Container**:
   Create a Dockerfile to containerize the application.

2. **Scheduled Jobs**:
   Use cron or a job scheduler for periodic interview generation.

3. **Web Interface**:
   Develop a Flask/FastAPI front-end for easier interaction.