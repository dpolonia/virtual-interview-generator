# Exports Directory

This directory contains the output of the Virtual Interview Generator, organized as follows:

## Directory Structure

Each run of the interview generator creates a timestamped directory with the following structure:

```
exports/
├── YYYYMMDD_HHMMSS_provider_model/   # Timestamp and model information
│   ├── interviews/                   # Raw interview transcripts
│   │   ├── senior_executives/        # Interviews by stakeholder category
│   │   ├── ai_specialists/
│   │   └── ...
│   ├── reports/                      # Analysis and reports
│   │   ├── individual/               # Individual interview analyses
│   │   ├── stakeholder_groups/       # Stakeholder category summaries
│   │   ├── summary/                  # Final comprehensive report
│   │   └── presentation/             # Presentation-ready materials
│   ├── interview_combinations.json   # Detailed mapping of all interviews
│   └── interview_summary.md          # Overview of the interview batch
```

## File Formats

- **Interviews**: Raw interview transcripts are stored as text files
- **Reports**: Available in both Markdown (.md) and PDF (.pdf) formats 
- **Metadata**: JSON files contain detailed information about each interview

## Notes

- PDF generation requires LaTeX packages to be installed
- To install required packages: `sudo apt-get install texlive-latex-base texlive-fonts-recommended texlive-latex-extra`