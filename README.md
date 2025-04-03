# Virtual Interview Generator

A tool for generating simulated interviews between personas about AI in the consulting industry.

## Overview

This project creates realistic virtual interviews for research on "The Role of Business Consulting Firms in the Era of Artificial Intelligence." It uses large language models (LLMs) to simulate conversations between interviewers and various stakeholders in the consulting industry.

## Features

- Interview generation with multiple LLM providers (OpenAI, Anthropic, Google)
- Support for various stakeholder categories
- Option to generate up to 10 interviews per category
- Analysis of interviews with structured insights
- Category-specific summary reports
- Comprehensive final report with executive summary
- Presentation-ready bullet points
- Markdown and PDF output formats
- Robust error handling with fallback mechanisms
- Integration with FinePersonas database

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

# Set up API keys in .env file (see .env.example)
cp .env.example .env
# Edit .env with your API keys

# Run the interactive interview generator
./run_interview.sh
```

## Usage

The simplest way to use the tool is with the interactive script:

```bash
# Run the interactive interview generator
./run_interview.sh
```

This will:
1. Prompt you to select an LLM provider and model
2. Allow you to choose stakeholder categories
3. Let you specify the number of interviews per category (1-10)
4. Generate interviews, analyses, and comprehensive reports
5. Save all outputs in a timestamped directory structure

### Traditional CLI Usage

The application also provides a command-line interface with the following commands:

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

### Output Structure

All generated content is saved in a timestamped directory structure:

```
exports/{timestamp}/
├── interviews/                 # Raw interview transcripts
│   └── {stakeholder_category}/
│       └── {interviewee_name}.txt
├── reports/                    # Analysis and reports
│   ├── individual/             # Individual interview analyses
│   │   ├── {analysis_1}.md
│   │   └── {analysis_1}.pdf
│   ├── stakeholder_groups/     # Category-specific reports
│   │   ├── {category_1}.md
│   │   └── {category_1}.pdf
│   ├── comprehensive/          # Final comprehensive reports
│   │   ├── comprehensive_report.md
│   │   └── comprehensive_report.pdf
│   └── presentation/           # Presentation-ready content
│       ├── key_findings.md
│       └── key_findings.pdf
├── interview_combinations.json # Metadata about all interviews
└── interview_summary.md        # Human-readable summary
```

## PDF Generation

For PDF generation, you need pandoc and basic LaTeX installed:

```bash
sudo apt-get update && sudo apt-get install -y pandoc texlive-latex-base texlive-fonts-recommended
```

The script will automatically detect if pandoc is installed and offer to install it if needed.

## Directory Structure

- `src/`: Source code for the traditional CLI application
  - `database/`: Database management
  - `models/`: AI model interfaces
  - `prompts/`: Prompt templates for AI models
  - `utils/`: Utility functions
- `data/`: Data storage
  - `scripts/`: Parsed interview scripts
  - `personas/`: Generated personas
  - `interviews/`: Generated interviews
- `exports/`: Output files (timestamped directories)
- `interactive_interviews.py`: Main interactive script
- `run_interview.sh`: Shell script to run the interactive generator

## License

[MIT License](LICENSE)