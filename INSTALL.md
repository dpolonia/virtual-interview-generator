# Virtual Interview Generator - Installation Guide

## Manual Installation Steps

Follow these steps to set up the Virtual Interview Generator on your system:

### 1. Install Python Dependencies

First, make sure you have Python 3.8+ and pip installed. Then install the virtual environment package:

```bash
# On Ubuntu/Debian:
sudo apt install python3-venv

# On CentOS/RHEL:
sudo yum install python3-venv

# On macOS (with Homebrew):
brew install python3
```

### 2. Create a Virtual Environment

```bash
# Create the virtual environment
python3 -m venv venv

# Activate it
# On Linux/Mac:
source venv/bin/activate
# On Windows:
venv\Scripts\activate
```

### 3. Install Required Packages

```bash
# With virtual environment activated:
pip install -r requirements.txt
```

### 4. Configure API Keys

Edit the `.env` file in the project root directory:

```
OPENAI_API_KEY=your_openai_api_key
ANTHROPIC_API_KEY=your_anthropic_api_key
GOOGLE_API_KEY=your_google_api_key
```

Replace the placeholder values with your actual API keys.

### 5. Initialize the Database

```bash
# With virtual environment activated:
python -c "from src.database.db_manager import db_manager"
```

### 6. Running the Application

```bash
# With virtual environment activated:
python src/main.py
```

This will display the available commands:

- `parse-scripts`: Parse interview scripts from source documents
- `generate-personas`: Create interviewer and interviewee personas
- `generate-interviews`: Generate interviews between personas
- `export-interviews`: Export interviews to files
- `generate-report`: Create comprehensive report

## Troubleshooting

- If you see errors related to missing modules, make sure your virtual environment is activated and all dependencies are installed.
- If you encounter API errors, verify that your API keys in the `.env` file are correct.
- For database errors, make sure the data directories exist and have appropriate permissions.

For more detailed information, refer to the deployment_tutorial/README.md file.