# Virtual Interview Generator: Workflow Documentation

## System Overview

The Virtual Interview Generator is a comprehensive tool designed to simulate and analyze research interviews focused on AI in consulting. The system uses Large Language Models (LLMs) to generate realistic conversations between interviewers and various stakeholder categories, creating a rich dataset for analysis.

## Core Workflow Components

### 1. Initial Configuration & Setup

**Input Options:**
- **API Key Management**:
  - Supports Anthropic (Claude), OpenAI (GPT), and Google (Gemini) APIs
  - Keys can be provided via:
    - Environment variables (`ANTHROPIC_API_KEY`, `OPENAI_API_KEY`, `GOOGLE_API_KEY`)
    - Command-line arguments (`--anthropic-key`, `--openai-key`, `--google-key`)
    - Interactive prompts (secure password input)
    - `.env` file (detected and loaded automatically)

- **Model Selection**:
  - Anthropic Claude models:
    - claude-3-7-sonnet-20250219 (powerful)
    - claude-3-5-sonnet-20240620/20241022 (balanced)
    - claude-3-5-haiku-20241022 (fast)
    - claude-3-haiku-20240307 (fastest & cheapest)
  - OpenAI GPT models:
    - gpt-4.5-preview-2025-02-27 (most powerful)
    - gpt-4o-2024-08-06 (powerful)
    - gpt-4o-mini-2024-07-18 (balanced)
    - o1-2024-12-17 (powerful)
    - o3-mini-2025-01-31 (fast)
  - Google Gemini models:
    - gemini-2.0-flash (powerful)
    - gemini-2.0-flash-lite (faster)

- **Stakeholder Category Selection**:
  - All categories or specific subset from:
    - senior_executives
    - ai_specialists
    - mid_level_consultants
    - clients
    - technology_providers
    - regulatory_stakeholders
    - industry_analysts

- **Persona Selection**:
  - Basic built-in personas (4 per stakeholder category)
  - FinePersonas integration option for enhanced, realistic personas
  - Number of interviews per category (1-10)

### 2. Interview Generation Process

**Transformation Steps:**
1. **Persona Selection & Pairing**:
   - Each stakeholder category persona is paired with an interviewer
   - When using FinePersonas, detailed demographic and background information is incorporated

2. **Interview Generation**:
   - For each pairing, an LLM generates a realistic interview scenario
   - Prompt focuses on key research areas:
     - Current state of AI adoption in consulting
     - Market trends in consulting industry related to AI
     - Impact of AI on automation and knowledge management
     - Ethical considerations and risks in AI consulting
   - Each interview spans approximately 1000-1500 words
   - Average of 5-7 questions with detailed responses

3. **Error Handling & Resilience**:
   - Rate limiting detection with exponential backoff (5-20 seconds)
   - Maximum retries (3 attempts) before skipping to next interview
   - Specific parameter handling for different model requirements
   - Graceful keyboard interrupt handling

### 3. Analysis Pipeline

**Transformation Steps:**
1. **Individual Interview Analysis**:
   - Each raw interview is processed by the LLM to generate structured analysis
   - Analysis sections include:
     - Key points (3-5 main takeaways)
     - Notable quotes (2-3 direct quotations)
     - AI attitudes assessment (positive/negative/neutral/nuanced)
     - RQ1-RQ4 insights (research question-specific findings)
     - Contradictions and authenticity assessment

2. **Stakeholder Category Synthesis**:
   - Combines all interviews within a stakeholder category
   - Creates executive summary (400-500 words)
   - Generates presentation-ready bullet points across research areas
   - Identifies patterns and unique perspectives from the stakeholder group

3. **Comprehensive Final Report**:
   - Model-aware token management (adjusts output length based on model capabilities)
   - Creates complete research report with sections:
     - Executive summary
     - Key findings for presentation (across 6 areas)
     - Stakeholder perspectives
     - Cross-category analysis
     - Research questions analysis
     - Methodology

### 4. Output Generation

**Output Formats:**
1. **Directory Structure** (timestamped with model info):
   ```
   exports/
   ├── YYYYMMDD_HHMMSS_provider_model/
   │   ├── interviews/               # Raw interview transcripts
   │   │   ├── senior_executives/    # Categorized by stakeholder type
   │   │   ├── ai_specialists/
   │   │   └── ...
   │   ├── reports/                  # Analysis and reports
   │   │   ├── individual/           # Per-interview analysis
   │   │   ├── stakeholder_groups/   # Category summaries
   │   │   ├── summary/              # Final comprehensive report
   │   │   └── presentation/         # Presentation materials
   │   ├── interview_combinations.json  # Metadata on interviews
   │   └── interview_summary.md      # Overview document
   ```

2. **Document Types**:
   - Raw interview transcripts (.txt)
   - Individual interview analyses (.md and .pdf)
   - Stakeholder category summaries (.md and .pdf)
   - Comprehensive research report (.md and .pdf)
   - Presentation bullets (.md and .pdf)
   - Metadata JSON (interview_combinations.json)

3. **PDF Generation**:
   - Multiple LaTeX engine support (pdflatex, xelatex)
   - Progressive fallback mechanisms for PDF generation
   - Dependency checking and automatic installation prompts
   - Detailed error diagnostics and reporting

## Key Features and Capabilities

### 1. Flexibility & Customization

- **Model Selection Tradeoffs**:
  - More powerful models (Claude-3-Sonnet, GPT-4.5, Gemini Flash) produce higher quality, more insightful interviews but cost more and run slower
  - Faster models (Claude Haiku, O3-mini) enable quick iteration but with somewhat reduced depth
  - Token limits handled automatically based on model capability

- **Stakeholder Coverage**:
  - Full-spectrum stakeholder selection generates comprehensive dataset across all 7 categories
  - Targeted selection allows focus on specific stakeholder perspectives
  - Variable interview count allows balancing depth vs. breadth (1-10 per category)

### 2. Error Handling & Resilience

- **API Rate Limiting**:
  - Automatic detection and handling of rate limits
  - Exponential backoff with intelligent retry
  - Progress preservation when errors occur

- **Dependency Management**:
  - Automatic detection of PDF generation dependencies
  - Interactive installation of missing components
  - Multiple fallback options when primary approach fails

### 3. Output Flexibility

- **Document Formats**:
  - Consistent Markdown for easy version control
  - PDF generation for formal reports
  - JSON structured data for further processing
  - Hierarchical file organization by timestamp, model, and category

## Practical Use Cases

1. **Limited Interview Set (1-3 interviews per category)**:
   - Quick generation (15-20 minutes)
   - Good for preliminary research or methodology testing
   - Provides initial insights across stakeholder groups
   - Uses less API quota but may have limited representativeness

2. **Comprehensive Research Dataset (7-10 interviews per category)**:
   - In-depth coverage (1-2 hours generation time)
   - Comprehensive perspectives with statistical validity
   - Rich dataset for qualitative analysis
   - Higher API quota consumption but greater research validity

3. **Single Stakeholder Deep Dive**:
   - Focused exploration of one stakeholder perspective
   - Useful for targeted research questions
   - Provides nuanced understanding of specific group's viewpoint
   - Efficient use of API quota while maintaining depth

4. **Model Comparison Research**:
   - Generate same interviews across different models
   - Compare quality, insight depth, and nuance
   - Analyze how different AI systems approach the same interview scenarios
   - Valuable for AI capabilities research

## System Requirements & Dependencies

- **Python Environment**:
  - Python 3.8+ with virtual environment
  - Core libraries: anthropic, openai, google-generativeai
  - Interface: questionary, rich (for CLI)

- **PDF Generation**:
  - pypandoc Python package
  - System packages: texlive-latex-base, texlive-fonts-recommended, texlive-latex-extra, texlive-xetex
  - LaTeX engines: pdflatex or xelatex

- **Deployment Options**:
  - Local development environment
  - Docker container (via provided Dockerfile)
  - CI/CD integration possible with GitHub Actions

## Running the Application

To run the Virtual Interview Generator, use one of the following commands:

```bash
# Using the shell script (recommended)
./run_interview.sh

# Running the Python script directly
./interactive_interviews.py

# With explicit API keys
./run_interview.sh --anthropic-key "your_key" --openai-key "your_key" --google-key "your_key"
```

The application will guide you through the setup process, including:
1. API key selection
2. Model selection
3. Stakeholder category selection
4. Number of interviews per category
5. PDF generation options

After completion, you'll find all generated content in the `exports/` directory with a timestamped folder.