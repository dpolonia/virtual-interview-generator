import os
import sys
import json
import datetime
import time
import argparse
import questionary
from rich.console import Console
from rich.progress import Progress
from rich.panel import Panel
from rich.table import Table
import anthropic
import openai
import google.generativeai as genai

# Import the FinePersona manager
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
try:
    from src.utils.persona_manager import FinePersonaManager
except ImportError:
    # Create a simple version if the import fails
    class FinePersonaManager:
        def __init__(self, use_sample=True, cache_file=None):
            self.use_sample = use_sample
            self.cache_file = cache_file or "data/personas/finepersonas_cache.json"
            self.dataset = None
            self.category_personas = {}
        
        def load_dataset(self):
            # Try to load from cache
            if os.path.exists(self.cache_file):
                try:
                    with open(self.cache_file, 'r', encoding='utf-8') as f:
                        cached_data = json.load(f)
                    return True
                except:
                    pass
            return False
        
        def get_personas_by_category(self, category, count=30, search_query=None):
            # Return empty list if no data
            return []

# Initialize console for pretty output
console = Console()

# Stakeholder categories
STAKEHOLDER_CATEGORIES = [
    "senior_executives",
    "ai_specialists", 
    "mid_level_consultants",
    "clients",
    "technology_providers",
    "regulatory_stakeholders",
    "industry_analysts"
]

# Personas by category (4 personas per category)
PERSONAS = {
    "senior_executives": [
        {"name": "Sarah Chen", "role": "Chief Strategy Officer at a Fortune 500 consulting firm with 18 years of experience"},
        {"name": "Michael Rodriguez", "role": "CEO of a mid-sized consulting firm specializing in digital transformation"},
        {"name": "Jennifer Park", "role": "Managing Director at a top-tier consulting firm overseeing AI initiatives"},
        {"name": "Thomas Wilson", "role": "Global Head of Innovation at an international consulting conglomerate"}
    ],
    "ai_specialists": [
        {"name": "Dr. Alex Kumar", "role": "Head of AI Research at a consulting firm with a PhD in Machine Learning"},
        {"name": "Emma Watson", "role": "AI Ethics Lead with background in both technology and philosophy"},
        {"name": "David Chen", "role": "Chief AI Architect with extensive experience implementing enterprise solutions"},
        {"name": "Sophia Miller", "role": "AI Implementation Specialist focusing on practical applications in consulting"}
    ],
    "mid_level_consultants": [
        {"name": "James Peterson", "role": "Senior Consultant with 7 years of experience in AI-driven projects"},
        {"name": "Maria Garcia", "role": "Project Manager for AI implementation teams at a mid-tier firm"},
        {"name": "Robert Kim", "role": "Data Science Consultant bridging technical and business requirements"},
        {"name": "Aisha Johnson", "role": "Engagement Manager focusing on AI transformation projects"}
    ],
    "clients": [
        {"name": "Elizabeth Taylor", "role": "CFO at a manufacturing company using AI consulting services"},
        {"name": "Richard Martinez", "role": "CIO at a financial services firm evaluating AI implementations"},
        {"name": "Susan Yamamoto", "role": "COO at a healthcare provider working with AI consultants"},
        {"name": "Christopher Adams", "role": "VP of Strategy at a retail chain undergoing AI transformation"}
    ],
    "technology_providers": [
        {"name": "Michelle Lee", "role": "CEO of an AI platform company partnering with consulting firms"},
        {"name": "Ryan Patel", "role": "CTO of a software company developing tools for consultants"},
        {"name": "Jessica Brown", "role": "Product Director at an enterprise AI solutions provider"},
        {"name": "Nathan Williams", "role": "Partnership Lead at a major cloud and AI infrastructure company"}
    ],
    "regulatory_stakeholders": [
        {"name": "Dr. Gregory Scott", "role": "Former regulatory official now advising on AI compliance"},
        {"name": "Amanda Chen", "role": "Legal counsel specializing in AI and data regulation"},
        {"name": "Jonathan Baker", "role": "Director at an industry standards organization for AI"},
        {"name": "Patricia Reynolds", "role": "Ethics Board Member overseeing AI implementations in consulting"}
    ],
    "industry_analysts": [
        {"name": "Dr. Caroline White", "role": "Principal Analyst at a leading research firm covering AI in consulting"},
        {"name": "Marcus Johnson", "role": "Industry Researcher specializing in digital transformation trends"},
        {"name": "Hannah Diaz", "role": "Senior Analyst publishing reports on the consulting industry"},
        {"name": "Rajiv Patel", "role": "Market Intelligence Director with focus on technology adoption in services"}
    ]
}

# Interviewers
INTERVIEWERS = [
    {"name": "Dr. Maria Reynolds", "role": "Experienced researcher specializing in AI and consulting practices"},
    {"name": "Dr. James Harrison", "role": "Professor of Business Technology with focus on industry transformation"},
    {"name": "Dr. Sophia Lin", "role": "Research Director at a technology think tank studying AI adoption"},
    {"name": "Dr. Marcus Wellington", "role": "Academic specializing in organizational change and technology"}
]

def select_llm_provider():
    """Allow user to select an LLM provider and model."""
    provider = questionary.select(
        "Select an LLM provider:",
        choices=[
            "Anthropic (Claude)",
            "OpenAI (GPT)",
            "Google (Gemini)"
        ]
    ).ask()
    
    if "Anthropic" in provider:
        model = questionary.select(
            "Select Claude model:",
            choices=[
                "claude-3-7-sonnet-20250219 (powerful)",
                "claude-3-5-sonnet-20240620 (balanced)",
                "claude-3-5-sonnet-20241022 (balanced)",
                "claude-3-5-haiku-20241022 (fast)",
                "claude-3-haiku-20240307 (fastest & cheapest)"
            ]
        ).ask()
        model_name = model.split()[0]
        return "anthropic", model_name
    
    elif "OpenAI" in provider:
        model = questionary.select(
            "Select GPT model:",
            choices=[
                "gpt-4.5-preview-2025-02-27 (most powerful)",
                "gpt-4o-2024-08-06 (powerful)",
                "gpt-4o-mini-2024-07-18 (balanced)",
                "o1-2024-12-17 (powerful)",
                "o3-mini-2025-01-31 (fast)"
            ]
        ).ask()
        model_name = model.split()[0]
        return "openai", model_name
    
    elif "Google" in provider:
        model = questionary.select(
            "Select Gemini model:",
            choices=[
                "gemini-2.0-flash (powerful)",
                "gemini-2.0-flash-lite (faster)"
            ]
        ).ask()
        model_name = model.split()[0]
        return "google", model_name

def select_stakeholder_categories():
    """Allow user to select stakeholder categories to interview."""
    selection = questionary.select(
        "Select stakeholder categories to interview:",
        choices=[
            "All stakeholder categories",
            "Select specific categories"
        ]
    ).ask()
    
    if selection == "All stakeholder categories":
        console.print("[green]Using all stakeholder categories.[/green]")
        return STAKEHOLDER_CATEGORIES
    
    # User wants to select specific categories
    categories = questionary.checkbox(
        "Select specific categories (use spacebar to select, enter to confirm):",
        choices=STAKEHOLDER_CATEGORIES
    ).ask()
    
    # If no categories selected, use all
    if not categories:
        console.print("[yellow]No categories selected. Using all categories.[/yellow]")
        return STAKEHOLDER_CATEGORIES
    
    return categories

def select_interviews_per_category():
    """Allow user to select how many interviews per category."""
    num_interviews = questionary.select(
        "How many interviews per category?",
        choices=["1", "2", "3", "4", "5", "6", "7", "8", "9", "10"]
    ).ask()
    
    return int(num_interviews)

def initialize_llm_client(provider, model, api_key):
    """Initialize the appropriate LLM client."""
    if provider == "anthropic":
        return {
            "provider": provider,
            "model": model,
            "client": anthropic.Anthropic(api_key=api_key)
        }
    elif provider == "openai":
        client = openai.OpenAI(api_key=api_key)
        return {
            "provider": provider,
            "model": model,
            "client": client
        }
    elif provider == "google":
        genai.configure(api_key=api_key)
        return {
            "provider": provider,
            "model": model,
            "client": genai
        }

def generate_with_llm(llm_config, prompt, max_tokens=4000, max_retries=3, retry_delay=5):
    """Generate text using the configured LLM with retry logic."""
    provider = llm_config["provider"]
    model = llm_config["model"]
    client = llm_config["client"]
    
    for attempt in range(max_retries):
        try:
            if provider == "anthropic":
                response = client.messages.create(
                    model=model,
                    max_tokens=max_tokens,
                    messages=[{"role": "user", "content": prompt}]
                )
                return response.content[0].text
            
            elif provider == "openai":
                response = client.chat.completions.create(
                    model=model,
                    messages=[{"role": "user", "content": prompt}],
                    max_tokens=max_tokens
                )
                return response.choices[0].message.content
            
            elif provider == "google":
                model_obj = client.GenerativeModel(model)
                response = model_obj.generate_content(prompt)
                return response.text
                
        except KeyboardInterrupt:
            # Re-raise keyboard interrupt to allow clean exit
            console.print("\n[yellow]Process interrupted by user. Cleaning up...[/yellow]")
            raise
            
        except Exception as e:
            error_type = type(e).__name__
            
            # Handle rate limiting errors specially
            if "RateLimitError" in error_type or "429" in str(e) or "rate limit" in str(e).lower():
                wait_time = retry_delay * (attempt + 1)  # Exponential backoff
                
                if attempt < max_retries - 1:  # Don't show this on the last attempt
                    console.print(f"[yellow]Rate limit hit with {provider}. Waiting {wait_time} seconds before retry ({attempt+1}/{max_retries})...[/yellow]")
                    time.sleep(wait_time)
                    continue
            
            # Handle other errors
            if attempt < max_retries - 1:
                console.print(f"[yellow]Error with {provider} {model}: {str(e)}. Retrying ({attempt+1}/{max_retries})...[/yellow]")
                time.sleep(retry_delay)
            else:
                console.print(f"[red]Failed after {max_retries} attempts with {provider} {model}: {str(e)}[/red]")
                
                # For the final error, return a message that won't break downstream processing
                return f"Error occurred while generating content. The system encountered the following issue: {error_type}. Please check the logs for more details."
    
    # This should only happen if we exhaust all retries
    return "Error: Maximum retry attempts exceeded. Unable to generate content."

def generate_interview(llm_config, interviewer, interviewee, stakeholder_category):
    """Generate an interview between interviewer and interviewee."""
    interview_prompt = f"""
You are conducting an interview about AI in consulting. Please generate a realistic interview between these two personas:

INTERVIEWER: {interviewer['name']}, {interviewer['role']}

INTERVIEWEE: {interviewee['name']}, {interviewee['role']}

CONTEXT: This interview is with a {stakeholder_category.replace('_', ' ')} about AI in consulting firms.

The interview should focus on:
1. Current state of AI adoption in consulting
2. Market trends in the consulting industry related to AI
3. Impact of AI on automation and knowledge management in consulting
4. Ethical considerations and risks of AI in consulting

The interview should include at least 5 questions and detailed, thoughtful responses that demonstrate the interviewee's unique perspective as a {stakeholder_category.replace('_', ' ')}.

Format the interview as a back-and-forth conversation, with each person's name followed by a colon and then their dialogue.
The interview should be about 1000-1500 words.
"""

    return generate_with_llm(llm_config, interview_prompt)

def analyze_interview(llm_config, interview_text, interviewer, interviewee, stakeholder_category):
    """Generate analysis of an interview."""
    analysis_prompt = f"""
Analyze the following interview about AI in consulting between {interviewer['name']} and {interviewee['name']}, who is a {stakeholder_category.replace('_', ' ')}.
Provide a structured analysis with these sections:

INTERVIEW TEXT:
{interview_text}

Please format your analysis with these clear sections:

1. KEY POINTS: Summarize the 3-5 most important points from the interview.

2. NOTABLE QUOTES: Extract 2-3 direct quotes that best represent the interviewee's perspective.

3. AI ATTITUDES: Analyze the interviewee's attitude toward AI in consulting (positive, negative, neutral, nuanced).

4. RQ1 INSIGHTS: What insights does this interview provide about the state of AI adoption in consulting?

5. RQ2 INSIGHTS: What insights does this interview provide about current market trends in consulting?

6. RQ3 INSIGHTS: What insights does this interview provide about automation and knowledge management?

7. RQ4 INSIGHTS: What insights does this interview provide about ethical considerations and risks?

8. CONTRADICTIONS: Note any contradictions or inconsistencies in the interviewee's statements.

9. AUTHENTICITY ASSESSMENT: Evaluate how authentic and realistic this interview feels.
"""

    return generate_with_llm(llm_config, analysis_prompt)

def create_stakeholder_summary(llm_config, analyses, stakeholder_category):
    """Generate a summary of all interviews for a stakeholder category."""
    
    # Format the analyses as a condensed text
    analyses_text = "\n\n".join([
        f"ANALYSIS {i+1}:\n{analysis[:2000]}...(truncated)" 
        for i, analysis in enumerate(analyses)
    ])
    
    summary_prompt = f"""
Create a comprehensive synthesis of findings from {len(analyses)} interviews with {stakeholder_category.replace('_', ' ')} stakeholders about AI in consulting.

ANALYSES:
{analyses_text}

Please generate TWO sections:

## EXECUTIVE SUMMARY
Write a 400-500 word executive summary that:
1. Synthesizes the key findings across all {stakeholder_category.replace('_', ' ')} interviews
2. Identifies common themes and patterns
3. Highlights unique perspectives from this stakeholder group
4. Explains the significance of these findings

## PRESENTATION BULLETS
Create concise, presentation-ready bullet points organized by:

### Key Findings
- [3 bullet points on main findings]

### AI Adoption (RQ1)
- [2-3 bullet points]

### Market Trends (RQ2)
- [2-3 bullet points]

### Automation & Knowledge (RQ3)
- [2-3 bullet points]

### Ethical Considerations (RQ4)
- [2-3 bullet points]

Keep each bullet point clear, specific, and under 15 words.
"""

    return generate_with_llm(llm_config, summary_prompt)

def create_final_report(llm_config, stakeholder_summaries, stakeholder_categories):
    """Generate a comprehensive final report across all stakeholder categories."""
    
    # Format the summaries as a condensed text
    summaries_text = "\n\n".join([
        f"SUMMARY FOR {category.upper().replace('_', ' ')}:\n{summary[:3000]}...(truncated)" 
        for category, summary in zip(stakeholder_categories, stakeholder_summaries)
    ])
    
    report_prompt = f"""
Create a comprehensive research report on "The Role of AI in Consulting" based on interviews with {len(stakeholder_categories)} different stakeholder groups:
{', '.join([category.replace('_', ' ') for category in stakeholder_categories])}

STAKEHOLDER SUMMARIES:
{summaries_text}

Please generate a complete research report with these sections:

# AI in Consulting: Comprehensive Research Report

## Executive Summary
[400-500 word executive summary of the entire research]

## Key Findings for Presentation
[Create 3-4 bullet points for each of these sections:]
- Overall Insights
- AI Adoption Status
- Market Trends 
- Automation & Knowledge Effects
- Ethical Considerations
- Recommendations for Consulting Firms

## Stakeholder Perspectives
[For each stakeholder group, provide a 1-2 paragraph summary of their unique perspective]

## Cross-Category Analysis
[400-500 word analysis comparing and contrasting views across stakeholder groups]

## Research Questions Analysis
[For each research question (RQ1-RQ4), provide a 1-2 paragraph synthesis across all stakeholders]

## Methodology
[Brief explanation of the interview methodology]

Focus on synthesizing insights across stakeholder groups and identifying patterns, contradictions, and consensus points.
"""

    return generate_with_llm(llm_config, report_prompt, max_tokens=8000)

def save_interview(interview_text, interviewer, interviewee, stakeholder_category, model_info, timestamp, export_dir):
    """Save an interview to a file."""
    # Create stakeholder directory
    stakeholder_dir = os.path.join(export_dir, stakeholder_category)
    os.makedirs(stakeholder_dir, exist_ok=True)
    
    # Create filename
    safe_name = interviewee["name"].replace(" ", "")
    model_str = f"{model_info['provider']}_{model_info['model']}".replace("-", "_")
    filename = f"{timestamp}_{stakeholder_category}_{safe_name}_{model_str}.txt"
    filepath = os.path.join(stakeholder_dir, filename)
    
    # Save file
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(f"INTERVIEW: {interviewee['name']} ({stakeholder_category.replace('_', ' ')})\n")
        f.write(f"ROLE: {interviewee['role']}\n")
        f.write(f"INTERVIEWER: {interviewer['name']}\n")
        f.write(f"MODEL: {model_info['provider']}/{model_info['model']}\n")
        f.write(f"DATE: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        f.write(interview_text)
    
    return filepath

def save_interview_analysis(analysis_text, interviewer, interviewee, stakeholder_category, model_info, timestamp, reports_dir):
    """Save an interview analysis to files (MD and PDF)."""
    # Create individual report directory
    individual_dir = os.path.join(reports_dir, 'individual')
    os.makedirs(individual_dir, exist_ok=True)
    
    # Create filename
    safe_name = interviewee["name"].replace(" ", "")
    md_filename = f"{stakeholder_category}_{safe_name}.md"
    md_filepath = os.path.join(individual_dir, md_filename)
    
    # Create markdown content
    md_content = f"# Interview Analysis: {interviewee['name']} ({stakeholder_category.replace('_', ' ')})\n\n"
    md_content += f"**Date:** {datetime.datetime.now().strftime('%Y-%m-%d')}\n"
    md_content += f"**Interviewer:** {interviewer['name']}\n"
    md_content += f"**Model Used:** {model_info['provider']}/{model_info['model']}\n\n"
    md_content += analysis_text
    
    # Save markdown file
    with open(md_filepath, 'w', encoding='utf-8') as f:
        f.write(md_content)
    
    # Try to create PDF using pypandoc if available, or fall back to command-line pandoc
    pdf_filename = f"{stakeholder_category}_{safe_name}.pdf"
    pdf_filepath = os.path.join(individual_dir, pdf_filename)
    
    try:
        # First try to use pypandoc (Python wrapper that includes pandoc binaries)
        try:
            import pypandoc
            # Capture and redirect potential stderr output
            temp_stderr = os.dup(2)
            os.close(2)
            temp_file = open(os.devnull, 'w')
            os.dup2(temp_file.fileno(), 2)
            
            # Try the conversion with extra args to help with LaTeX packages
            pypandoc.convert_file(
                md_filepath, 
                'pdf', 
                outputfile=pdf_filepath,
                extra_args=['--pdf-engine=xelatex', '-V', 'geometry:margin=1in']
            )
            
            # Restore stderr
            os.close(2)
            os.dup2(temp_stderr, 2)
            temp_file.close()
            
            if os.path.exists(pdf_filepath) and os.path.getsize(pdf_filepath) > 0:
                console.print(f"[green]Saved PDF analysis to {pdf_filepath}[/green]")
            else:
                raise Exception("PDF file was not created or is empty")
                
        except ImportError:
            # If pypandoc is not installed, try command-line pandoc
            pandoc_installed = os.system("which pandoc > /dev/null 2>&1") == 0
            if pandoc_installed:
                # Run pandoc with xelatex engine which has better Unicode support
                exit_code = os.system(f"pandoc {md_filepath} --pdf-engine=xelatex -V geometry:margin=1in -o {pdf_filepath} 2>/dev/null")
                if exit_code == 0 and os.path.exists(pdf_filepath):
                    console.print(f"[green]Saved PDF analysis to {pdf_filepath}[/green]")
                else:
                    error_msg = ""
                    # Try to capture the error message for debugging
                    temp_error_file = os.path.join(individual_dir, "pandoc_error.log")
                    os.system(f"pandoc {md_filepath} --pdf-engine=xelatex -o {pdf_filepath} 2> {temp_error_file}")
                    if os.path.exists(temp_error_file):
                        with open(temp_error_file, 'r') as f:
                            error_msg = f.read().strip()
                        os.remove(temp_error_file)
                    
                    if "xcolor.sty" in error_msg:
                        console.print(f"[yellow]Failed to create PDF: Missing LaTeX package 'xcolor.sty'. Install texlive-latex-extra package.[/yellow]")
                    else:
                        console.print(f"[yellow]Failed to create PDF: pandoc returned error code {exit_code}[/yellow]")
                        if error_msg:
                            console.print(f"[dim]Error details: {error_msg}[/dim]")
            else:
                # Silently continue if neither pypandoc nor pandoc is available
                pass
    except Exception as e:
        error_msg = str(e)
        if "xcolor.sty" in error_msg:
            console.print(f"[yellow]Error during PDF creation: Missing LaTeX package 'xcolor.sty'. Install texlive-latex-extra package.[/yellow]")
        else:
            console.print(f"[yellow]Error during PDF creation: {error_msg}[/yellow]")
            console.print("[dim]Try installing the required LaTeX packages with: sudo apt-get install texlive-latex-base texlive-fonts-recommended texlive-latex-extra[/dim]")
    
    return md_filepath

def save_stakeholder_summary(summary_text, stakeholder_category, timestamp, reports_dir):
    """Save a stakeholder category summary to files (MD and PDF)."""
    # Create stakeholder group directory
    stakeholder_dir = os.path.join(reports_dir, 'stakeholder_groups')
    os.makedirs(stakeholder_dir, exist_ok=True)
    
    # Create filename
    md_filename = f"{stakeholder_category}_analysis.md"
    md_filepath = os.path.join(stakeholder_dir, md_filename)
    
    # Create markdown content
    md_content = f"# {stakeholder_category.replace('_', ' ').title()} Analysis Report\n\n"
    md_content += f"**Generated:** {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
    md_content += summary_text
    
    # Save markdown file
    with open(md_filepath, 'w', encoding='utf-8') as f:
        f.write(md_content)
    
    # Try to create PDF using pypandoc if available, or fall back to command-line pandoc
    pdf_filename = f"{stakeholder_category}_analysis.pdf"
    pdf_filepath = os.path.join(stakeholder_dir, pdf_filename)
    
    try:
        # First try to use pypandoc (Python wrapper that includes pandoc binaries)
        try:
            import pypandoc
            # Capture and redirect potential stderr output
            temp_stderr = os.dup(2)
            os.close(2)
            temp_file = open(os.devnull, 'w')
            os.dup2(temp_file.fileno(), 2)
            
            # Try the conversion with extra args to help with LaTeX packages
            pypandoc.convert_file(
                md_filepath, 
                'pdf', 
                outputfile=pdf_filepath,
                extra_args=['--pdf-engine=xelatex', '-V', 'geometry:margin=1in']
            )
            
            # Restore stderr
            os.close(2)
            os.dup2(temp_stderr, 2)
            temp_file.close()
            
            if os.path.exists(pdf_filepath) and os.path.getsize(pdf_filepath) > 0:
                console.print(f"[green]Saved PDF summary to {pdf_filepath}[/green]")
            else:
                raise Exception("PDF file was not created or is empty")
                
        except ImportError:
            # If pypandoc is not installed, try command-line pandoc
            pandoc_installed = os.system("which pandoc > /dev/null 2>&1") == 0
            if pandoc_installed:
                # Run pandoc with xelatex engine which has better Unicode support
                exit_code = os.system(f"pandoc {md_filepath} --pdf-engine=xelatex -V geometry:margin=1in -o {pdf_filepath} 2>/dev/null")
                if exit_code == 0 and os.path.exists(pdf_filepath):
                    console.print(f"[green]Saved PDF summary to {pdf_filepath}[/green]")
                else:
                    error_msg = ""
                    # Try to capture the error message for debugging
                    temp_error_file = os.path.join(stakeholder_dir, "pandoc_error.log")
                    os.system(f"pandoc {md_filepath} --pdf-engine=xelatex -o {pdf_filepath} 2> {temp_error_file}")
                    if os.path.exists(temp_error_file):
                        with open(temp_error_file, 'r') as f:
                            error_msg = f.read().strip()
                        os.remove(temp_error_file)
                    
                    if "xcolor.sty" in error_msg:
                        console.print(f"[yellow]Failed to create PDF summary: Missing LaTeX package 'xcolor.sty'. Install texlive-latex-extra package.[/yellow]")
                    else:
                        console.print(f"[yellow]Failed to create PDF summary: pandoc returned error code {exit_code}[/yellow]")
                        if error_msg:
                            console.print(f"[dim]Error details: {error_msg}[/dim]")
            else:
                # Silently continue if neither pypandoc nor pandoc is available
                pass
    except Exception as e:
        error_msg = str(e)
        if "xcolor.sty" in error_msg:
            console.print(f"[yellow]Error during PDF creation: Missing LaTeX package 'xcolor.sty'. Install texlive-latex-extra package.[/yellow]")
        else:
            console.print(f"[yellow]Error during PDF creation: {error_msg}[/yellow]")
            console.print("[dim]Try installing the required LaTeX packages with: sudo apt-get install texlive-latex-base texlive-fonts-recommended texlive-latex-extra[/dim]")
    
    return md_filepath

def save_final_report(report_text, timestamp, reports_dir):
    """Save the final report to files (MD and PDF)."""
    # Create summary directory
    summary_dir = os.path.join(reports_dir, 'summary')
    os.makedirs(summary_dir, exist_ok=True)
    
    # Create filename
    md_filename = f"comprehensive_report_{timestamp}.md"
    md_filepath = os.path.join(summary_dir, md_filename)
    
    # Save markdown file
    with open(md_filepath, 'w', encoding='utf-8') as f:
        f.write(report_text)
    
    # Try to create PDF using pypandoc if available, or fall back to command-line pandoc
    pdf_filename = f"comprehensive_report_{timestamp}.pdf"
    pdf_filepath = os.path.join(summary_dir, pdf_filename)
    
    try:
        # First try to use pypandoc (Python wrapper that includes pandoc binaries)
        try:
            import pypandoc
            # Capture and redirect potential stderr output
            temp_stderr = os.dup(2)
            os.close(2)
            temp_file = open(os.devnull, 'w')
            os.dup2(temp_file.fileno(), 2)
            
            # Try the conversion with extra args to help with LaTeX packages
            pypandoc.convert_file(
                md_filepath, 
                'pdf', 
                outputfile=pdf_filepath,
                extra_args=['--pdf-engine=xelatex', '-V', 'geometry:margin=1in']
            )
            
            # Restore stderr
            os.close(2)
            os.dup2(temp_stderr, 2)
            temp_file.close()
            
            if os.path.exists(pdf_filepath) and os.path.getsize(pdf_filepath) > 0:
                console.print(f"[green]Saved PDF report to {pdf_filepath}[/green]")
            else:
                raise Exception("PDF file was not created or is empty")
                
        except ImportError:
            # If pypandoc is not installed, try command-line pandoc
            pandoc_installed = os.system("which pandoc > /dev/null 2>&1") == 0
            if pandoc_installed:
                # Run pandoc with xelatex engine which has better Unicode support
                exit_code = os.system(f"pandoc {md_filepath} --pdf-engine=xelatex -V geometry:margin=1in -o {pdf_filepath} 2>/dev/null")
                if exit_code == 0 and os.path.exists(pdf_filepath):
                    console.print(f"[green]Saved PDF report to {pdf_filepath}[/green]")
                else:
                    error_msg = ""
                    # Try to capture the error message for debugging
                    temp_error_file = os.path.join(summary_dir, "pandoc_error.log")
                    os.system(f"pandoc {md_filepath} --pdf-engine=xelatex -o {pdf_filepath} 2> {temp_error_file}")
                    if os.path.exists(temp_error_file):
                        with open(temp_error_file, 'r') as f:
                            error_msg = f.read().strip()
                        os.remove(temp_error_file)
                    
                    if "xcolor.sty" in error_msg:
                        console.print(f"[yellow]Failed to create PDF report: Missing LaTeX package 'xcolor.sty'. Install texlive-latex-extra package.[/yellow]")
                    else:
                        console.print(f"[yellow]Failed to create PDF report: pandoc returned error code {exit_code}[/yellow]")
                        if error_msg:
                            console.print(f"[dim]Error details: {error_msg}[/dim]")
            else:
                # Silently continue if neither pypandoc nor pandoc is available
                pass
    except Exception as e:
        error_msg = str(e)
        if "xcolor.sty" in error_msg:
            console.print(f"[yellow]Error during PDF creation: Missing LaTeX package 'xcolor.sty'. Install texlive-latex-extra package.[/yellow]")
        else:
            console.print(f"[yellow]Error during PDF creation: {error_msg}[/yellow]")
            console.print("[dim]Try installing the required LaTeX packages with: sudo apt-get install texlive-latex-base texlive-fonts-recommended texlive-latex-extra[/dim]")
    
    return md_filepath

def extract_presentation_bullets(report_text):
    """Extract presentation bullets from the final report."""
    start_marker = "## Key Findings for Presentation"
    end_markers = ["## Stakeholder Perspectives", "## Cross-Category Analysis"]
    
    # Find the start of the presentation bullets
    if start_marker not in report_text:
        return "No presentation bullets found."
    
    start_idx = report_text.index(start_marker)
    
    # Find the end of the presentation bullets
    end_idx = len(report_text)
    for marker in end_markers:
        if marker in report_text[start_idx:]:
            marker_idx = report_text.index(marker, start_idx)
            if marker_idx < end_idx:
                end_idx = marker_idx
    
    # Extract the bullets
    bullets_text = report_text[start_idx:end_idx].strip()
    return bullets_text

def save_presentation(report_text, timestamp, reports_dir):
    """Save the presentation bullets to files (MD and PDF)."""
    # Create presentation directory
    presentation_dir = os.path.join(reports_dir, 'presentation')
    os.makedirs(presentation_dir, exist_ok=True)
    
    # Extract presentation bullets
    bullets_text = extract_presentation_bullets(report_text)
    
    # Create filename
    md_filename = f"key_findings_{timestamp}.md"
    md_filepath = os.path.join(presentation_dir, md_filename)
    
    # Create markdown content
    md_content = f"# AI in Consulting Research Findings\n\n"
    md_content += f"Generated: {datetime.datetime.now().strftime('%Y-%m-%d')}\n\n"
    md_content += bullets_text
    md_content += "\n\n# Thank You"
    
    # Save markdown file
    with open(md_filepath, 'w', encoding='utf-8') as f:
        f.write(md_content)
    
    # Try to create PDF using pypandoc if available, or fall back to command-line pandoc
    pdf_filename = f"key_findings_{timestamp}.pdf"
    pdf_filepath = os.path.join(presentation_dir, pdf_filename)
    
    try:
        # First try to use pypandoc (Python wrapper that includes pandoc binaries)
        try:
            import pypandoc
            # Capture and redirect potential stderr output
            temp_stderr = os.dup(2)
            os.close(2)
            temp_file = open(os.devnull, 'w')
            os.dup2(temp_file.fileno(), 2)
            
            # Try the conversion with extra args to help with LaTeX packages
            pypandoc.convert_file(
                md_filepath, 
                'pdf', 
                outputfile=pdf_filepath,
                extra_args=[
                    '--pdf-engine=xelatex', 
                    '-V', 'geometry:margin=1in',
                    '--slide-level=2'  # Treat level 2 headers as slides
                ]
            )
            
            # Restore stderr
            os.close(2)
            os.dup2(temp_stderr, 2)
            temp_file.close()
            
            if os.path.exists(pdf_filepath) and os.path.getsize(pdf_filepath) > 0:
                console.print(f"[green]Saved PDF presentation to {pdf_filepath}[/green]")
            else:
                raise Exception("PDF file was not created or is empty")
                
        except ImportError:
            # If pypandoc is not installed, try command-line pandoc
            pandoc_installed = os.system("which pandoc > /dev/null 2>&1") == 0
            if pandoc_installed:
                # Run pandoc with xelatex engine which has better Unicode support
                exit_code = os.system(f"pandoc {md_filepath} --pdf-engine=xelatex -V geometry:margin=1in --slide-level=2 -o {pdf_filepath} 2>/dev/null")
                if exit_code == 0 and os.path.exists(pdf_filepath):
                    console.print(f"[green]Saved PDF presentation to {pdf_filepath}[/green]")
                else:
                    error_msg = ""
                    # Try to capture the error message for debugging
                    temp_error_file = os.path.join(presentation_dir, "pandoc_error.log")
                    os.system(f"pandoc {md_filepath} --pdf-engine=xelatex -o {pdf_filepath} 2> {temp_error_file}")
                    if os.path.exists(temp_error_file):
                        with open(temp_error_file, 'r') as f:
                            error_msg = f.read().strip()
                        os.remove(temp_error_file)
                    
                    if "xcolor.sty" in error_msg:
                        console.print(f"[yellow]Failed to create PDF presentation: Missing LaTeX package 'xcolor.sty'. Install texlive-latex-extra package.[/yellow]")
                    else:
                        console.print(f"[yellow]Failed to create PDF presentation: pandoc returned error code {exit_code}[/yellow]")
                        if error_msg:
                            console.print(f"[dim]Error details: {error_msg}[/dim]")
            else:
                # Silently continue if neither pypandoc nor pandoc is available
                pass
    except Exception as e:
        error_msg = str(e)
        if "xcolor.sty" in error_msg:
            console.print(f"[yellow]Error during PDF creation: Missing LaTeX package 'xcolor.sty'. Install texlive-latex-extra package.[/yellow]")
        else:
            console.print(f"[yellow]Error during PDF creation: {error_msg}[/yellow]")
            console.print("[dim]Try installing the required LaTeX packages with: sudo apt-get install texlive-latex-base texlive-fonts-recommended texlive-latex-extra[/dim]")
    
    return md_filepath

def main():
    parser = argparse.ArgumentParser(description='Interactive Interview Generator')
    parser.add_argument('--anthropic-key', help='Anthropic API key')
    parser.add_argument('--openai-key', help='OpenAI API key')
    parser.add_argument('--google-key', help='Google API key')
    parser.add_argument('--use-finepersonas', action='store_true', help='Use FinePersonas database')
    args = parser.parse_args()
    
    # Get API keys
    anthropic_key = args.anthropic_key or os.getenv("ANTHROPIC_API_KEY") or questionary.password("Enter your Anthropic API key (or press Enter to skip):").ask()
    openai_key = args.openai_key or os.getenv("OPENAI_API_KEY") or questionary.password("Enter your OpenAI API key (or press Enter to skip):").ask()
    google_key = args.google_key or os.getenv("GOOGLE_API_KEY") or questionary.password("Enter your Google API key (or press Enter to skip):").ask()
    
    # Store API keys in environment variables
    if anthropic_key:
        os.environ["ANTHROPIC_API_KEY"] = anthropic_key
    if openai_key:
        os.environ["OPENAI_API_KEY"] = openai_key
    if google_key:
        os.environ["GOOGLE_API_KEY"] = google_key
    
    # Check if at least one API key is provided
    available_providers = []
    if anthropic_key:
        available_providers.append("Anthropic (Claude)")
    if openai_key:
        available_providers.append("OpenAI (GPT)")
    if google_key:
        available_providers.append("Google (Gemini)")
    
    if not available_providers:
        console.print("[red]Error: At least one API key must be provided to use LLM functionality.[/red]")
        return
    
    # Initialize FinePersona manager if requested
    persona_manager = None
    use_finepersonas = args.use_finepersonas or questionary.confirm(
        "Use FinePersonas database for enhanced personas?",
        default=False
    ).ask()
    
    if use_finepersonas:
        console.print("[cyan]Initializing FinePersona manager...[/cyan]")
        persona_manager = FinePersonaManager(use_sample=True)
        
        # Load the dataset
        console.print("[cyan]Loading FinePersonas dataset (this may take a moment)...[/cyan]")
        if not persona_manager.load_dataset():
            console.print("[yellow]Warning: Could not load FinePersonas dataset. Using default personas.[/yellow]")
            use_finepersonas = False
        else:
            console.print("[green]Successfully loaded FinePersonas dataset.[/green]")
    
    # Get settings from user
    console.print("\n[bold cyan]Select LLM Provider[/bold cyan]")
    provider, model = select_llm_provider()
    
    console.print("\n[bold cyan]Select Stakeholder Categories[/bold cyan]")
    selected_categories = select_stakeholder_categories()
    
    console.print("\n[bold cyan]Select Number of Interviews per Category[/bold cyan]")
    interviews_per_category = select_interviews_per_category()
    
    # Initialize LLM client
    api_key = {"anthropic": anthropic_key, "openai": openai_key, "google": google_key}[provider]
    llm_config = initialize_llm_client(provider, model, api_key)
    
    # Download personas from FinePersonas if enabled
    finepersonas = {}
    if use_finepersonas and persona_manager:
        console.print("[cyan]Downloading personas from FinePersonas database...[/cyan]")
        
        with Progress() as progress:
            download_task = progress.add_task("[green]Downloading personas...", total=len(selected_categories) + 1)
            
            # Download interviewer personas
            finepersonas["interviewer"] = persona_manager.get_personas_by_category(
                "interviewer", 
                count=max(4, interviews_per_category),
                search_query="academic researcher AI technology"
            )
            progress.update(download_task, advance=1)
            
            # Download personas for each category
            for category in selected_categories:
                finepersonas[category] = persona_manager.get_personas_by_category(
                    category,
                    count=max(4, interviews_per_category * 2),  # Get extra in case some are low quality
                    search_query=f"{category.replace('_', ' ')} expert"
                )
                progress.update(download_task, advance=1)
        
        console.print(f"[green]Downloaded personas for {len(finepersonas)} categories.[/green]")
    
    # Create output directories with timestamp and model name
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    model_short_name = model.split('-')[0] if '-' in model else model  # Extract first part of model name
    base_dir = f"exports/{timestamp}_{provider}_{model_short_name}"
    exports_dir = f"{base_dir}/interviews"
    reports_dir = f"{base_dir}/reports"
    os.makedirs(exports_dir, exist_ok=True)
    
    # Track all generated files
    all_interviews = []
    all_analyses = []
    stakeholder_summaries = []
    
    # Track all interview combinations
    interview_combinations = []
    
    # Generate interviews for each category
    total_interviews = len(selected_categories) * interviews_per_category
    
    with Progress() as progress:
        # Create tasks
        interview_task = progress.add_task("[green]Generating interviews...", total=total_interviews)
        
        # For each selected category
        for category in selected_categories:
            console.print(f"\n[bold cyan]Generating interviews for {category.replace('_', ' ')}[/bold cyan]")
            
            # Get personas for this category, generating more if needed
            available_personas = PERSONAS[category]
            # If we need more personas than available, generate additional ones
            if interviews_per_category > len(available_personas):
                # Generate additional personas as needed
                for i in range(len(available_personas), interviews_per_category):
                    new_persona = {
                        "name": f"Additional {category.replace('_', ' ')} {i+1}",
                        "role": f"Expert in the {category.replace('_', ' ')} sector with unique perspective {i+1}"
                    }
                    available_personas.append(new_persona)
            
            category_personas = available_personas[:interviews_per_category]
            category_analyses = []
            
            # Generate interviews for each persona
            for i, persona in enumerate(category_personas):
                # Select interviewer (cycle through them)
                interviewer_index = i % len(INTERVIEWERS)
                interviewer = INTERVIEWERS[interviewer_index]
                
                # For interviews beyond available interviewers, create variations
                if i >= len(INTERVIEWERS):
                    interviewer = {
                        "name": f"{interviewer['name']} (Session {int(i/len(INTERVIEWERS))+1})",
                        "role": interviewer['role']
                    }
                
                # Generate interview
                console.print(f"Generating interview between {interviewer['name']} and {persona['name']}...")
                try:
                    interview_text = generate_interview(llm_config, interviewer, persona, category)
                    
                    # Save interview
                    interview_file = save_interview(
                        interview_text, interviewer, persona, category, 
                        {"provider": provider, "model": model}, 
                        timestamp, exports_dir
                    )
                    all_interviews.append(interview_file)
                except KeyboardInterrupt:
                    console.print("\n[yellow]Interview generation interrupted. Saving progress so far...[/yellow]")
                    raise
                except Exception as e:
                    console.print(f"[red]Error generating interview between {interviewer['name']} and {persona['name']}: {str(e)}[/red]")
                    console.print("[yellow]Skipping this interview and continuing with the next one...[/yellow]")
                    continue
                
                # Get FinePersona data
                if use_finepersonas and finepersonas and "interviewer" in finepersonas and len(finepersonas["interviewer"]) > 0:
                    # Use real FinePersona data for interviewer
                    idx = interviewer_index % len(finepersonas["interviewer"])
                    interviewer_finepersona = {
                        "id": finepersonas["interviewer"][idx].get("id", f"fp_{interviewer_index}_001"),
                        "persona": finepersonas["interviewer"][idx].get("persona_text", interviewer["role"]),
                        "labels": finepersonas["interviewer"][idx].get("labels", ["Academic", "Research", "AI"])
                    }
                else:
                    # Generate mock FinePersona data
                    interviewer_finepersona = {
                        "id": f"fp_{interviewer_index}_001",
                        "persona": interviewer["role"],
                        "labels": ["Academic", "Research", "AI", "Consulting", "Technology"]
                    }
                
                if use_finepersonas and finepersonas and category in finepersonas and len(finepersonas[category]) > 0:
                    # Use real FinePersona data for interviewee
                    idx = i % len(finepersonas[category])
                    interviewee_finepersona = {
                        "id": finepersonas[category][idx].get("id", f"fp_{category}_{i}_001"),
                        "persona": finepersonas[category][idx].get("persona_text", persona["role"]),
                        "labels": finepersonas[category][idx].get("labels", [category.replace("_", " ").title()])
                    }
                else:
                    # Generate mock FinePersona data
                    interviewee_finepersona = {
                        "id": f"fp_{category}_{i}_001",
                        "persona": persona["role"],
                        "labels": [
                            category.replace("_", " ").title(),
                            "Business" if "executive" in category or "client" in category else "",
                            "Technology" if "tech" in category or "ai" in category else "",
                            "Consulting" if "consultant" in category else "",
                            "Government" if "regulatory" in category else "",
                            "Research" if "analyst" in category else ""
                        ]
                    }
                
                # Track interview combination
                combination = {
                    "interviewer": {
                        "name": interviewer["name"],
                        "role": interviewer["role"],
                        "user_id": f"interviewer_{interviewer_index}",
                        "demographics": {
                            "profession": "Researcher",
                            "experience": "Senior",
                            "expertise": "AI in Consulting"
                        },
                        "finepersona": {
                            "id": interviewer_finepersona["id"],
                            "persona": interviewer_finepersona["persona"],
                            "labels": [label for label in interviewer_finepersona["labels"] if label]
                        }
                    },
                    "interviewee": {
                        "name": persona["name"],
                        "role": persona["role"],
                        "user_id": f"{category}_{i}",
                        "demographics": {
                            "stakeholder_category": category.replace("_", " "),
                            "seniority": "Senior" if "Senior" in persona["role"] or "Chief" in persona["role"] or "Head" in persona["role"] else "Mid-level",
                            "years_experience": "15+" if "Senior" in persona["role"] or "Chief" in persona["role"] else "5-15"
                        },
                        "finepersona": {
                            "id": interviewee_finepersona["id"],
                            "persona": interviewee_finepersona["persona"],
                            "labels": [label for label in interviewee_finepersona["labels"] if label]
                        }
                    },
                    "interview_details": {
                        "category": category,
                        "file_path": interview_file,
                        "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        "model": model
                    }
                }
                interview_combinations.append(combination)
                
                # Generate analysis
                console.print(f"Analyzing interview with {persona['name']}...")
                try:
                    analysis_text = analyze_interview(llm_config, interview_text, interviewer, persona, category)
                    
                    # Save analysis
                    analysis_file = save_interview_analysis(
                        analysis_text, interviewer, persona, category,
                        {"provider": provider, "model": model},
                        timestamp, reports_dir
                    )
                    all_analyses.append(analysis_file)
                    category_analyses.append(analysis_text)
                except KeyboardInterrupt:
                    console.print("\n[yellow]Analysis generation interrupted. Saving progress so far...[/yellow]")
                    raise
                except Exception as e:
                    console.print(f"[red]Error analyzing interview with {persona['name']}: {str(e)}[/red]")
                    console.print("[yellow]Skipping this analysis and continuing with the next interview...[/yellow]")
                    # Add a placeholder analysis so the counts match
                    placeholder_analysis = f"Error analyzing interview with {persona['name']}. The system encountered an error."
                    category_analyses.append(placeholder_analysis)
                
                # Update progress
                progress.update(interview_task, advance=1)
                
                # Short pause to avoid rate limiting
                time.sleep(1)
            
            # Generate stakeholder summary for this category if we have analyses
            if category_analyses:
                console.print(f"\n[bold cyan]Generating summary for {category.replace('_', ' ')}[/bold cyan]")
                try:
                    summary_text = create_stakeholder_summary(llm_config, category_analyses, category)
                    
                    # Save stakeholder summary
                    summary_file = save_stakeholder_summary(summary_text, category, timestamp, reports_dir)
                    stakeholder_summaries.append(summary_text)
                except KeyboardInterrupt:
                    console.print("\n[yellow]Summary generation interrupted. Saving progress so far...[/yellow]")
                    raise
                except Exception as e:
                    console.print(f"[red]Error generating summary for {category.replace('_', ' ')}: {str(e)}[/red]")
                    console.print("[yellow]Skipping this summary and continuing with the next category...[/yellow]")
                    # Add a placeholder summary
                    placeholder_summary = f"Error generating summary for {category.replace('_', ' ')}. The system encountered an error."
                    stakeholder_summaries.append(placeholder_summary)
            else:
                console.print(f"[yellow]No analyses available for {category.replace('_', ' ')}. Skipping summary generation.[/yellow]")
    
    # Generate final report
    report_file = None
    comprehensive_report_dir = os.path.join(reports_dir, 'comprehensive')
    os.makedirs(comprehensive_report_dir, exist_ok=True)
    
    # Always generate a final report, even for a single category
    if stakeholder_summaries:
        console.print("\n[bold cyan]Generating comprehensive final report[/bold cyan]")
        try:
            # Create the comprehensive report
            report_text = create_final_report(llm_config, stakeholder_summaries, selected_categories)
            
            # Save final report
            report_file = save_final_report(report_text, timestamp, reports_dir)
            
            # Save presentation bullets
            presentation_file = save_presentation(report_text, timestamp, reports_dir)
            
            console.print(f"\n[bold green]Final report saved to: {report_file}[/bold green]")
            console.print(f"[bold green]Presentation saved to: {presentation_file}[/bold green]")
        except KeyboardInterrupt:
            console.print("\n[yellow]Final report generation interrupted. Saving progress so far...[/yellow]")
            raise
        except Exception as e:
            console.print(f"[red]Error generating comprehensive report: {str(e)}[/red]")
            
            # Create a simpler merged report in case the LLM-generated one fails
            try:
                console.print("[yellow]Attempting to create a basic merged report instead...[/yellow]")
                
                # Create a merged report from all stakeholder summaries
                merged_report_path = os.path.join(comprehensive_report_dir, f"merged_report_{timestamp}.md")
                with open(merged_report_path, 'w', encoding='utf-8') as f:
                    f.write(f"# AI in Consulting: Comprehensive Research Report\n\n")
                    f.write(f"Generated: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
                    f.write(f"## Overview\n\n")
                    f.write(f"This report compiles findings from {len(all_interviews)} interviews across {len(selected_categories)} stakeholder categories.\n\n")
                    
                    # Add a section for each stakeholder category
                    for i, (category, summary) in enumerate(zip(selected_categories, stakeholder_summaries)):
                        f.write(f"## {category.replace('_', ' ').title()} Findings\n\n")
                        
                        # Extract just the executive summary portion if available
                        exec_summary = ""
                        if "## EXECUTIVE SUMMARY" in summary:
                            parts = summary.split("## EXECUTIVE SUMMARY")
                            if len(parts) > 1:
                                exec_parts = parts[1].split("##")
                                if len(exec_parts) > 0:
                                    exec_summary = exec_parts[0].strip()
                        
                        # Use the extracted executive summary or the first 500 chars of the full summary
                        if exec_summary:
                            f.write(exec_summary + "\n\n")
                        else:
                            f.write(summary[:500] + "...\n\n")
                    
                    # Add a conclusion
                    f.write("## Conclusion\n\n")
                    f.write("This report represents a compilation of all stakeholder interviews. For detailed findings, please refer to the individual stakeholder reports.\n")
                
                report_file = merged_report_path
                console.print(f"[green]Basic merged report created at: {merged_report_path}[/green]")
            except Exception as e2:
                console.print(f"[red]Failed to create basic merged report: {str(e2)}[/red]")
                console.print("[yellow]Individual category reports are still available.[/yellow]")
    else:
        console.print("[yellow]No stakeholder summaries were generated, so no final report could be created.[/yellow]")
        
        # Try to create a very basic report from just the interview details
        if all_interviews:
            try:
                console.print("[yellow]Creating a minimal report from interview data...[/yellow]")
                minimal_report_path = os.path.join(comprehensive_report_dir, f"minimal_report_{timestamp}.md")
                
                with open(minimal_report_path, 'w', encoding='utf-8') as f:
                    f.write(f"# AI in Consulting: Interview Summary Report\n\n")
                    f.write(f"Generated: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
                    f.write(f"## Overview\n\n")
                    f.write(f"This report summarizes {len(all_interviews)} interviews conducted across {len(selected_categories)} stakeholder categories.\n\n")
                    
                    # Add a section for each category
                    for category in selected_categories:
                        category_interviews = [path for path in all_interviews if f"/{category}/" in path]
                        f.write(f"## {category.replace('_', ' ').title()}\n\n")
                        f.write(f"* {len(category_interviews)} interviews conducted\n")
                        
                        # List interviewees
                        for path in category_interviews:
                            # Extract interviewee name from filename
                            filename = os.path.basename(path)
                            parts = filename.split('_')
                            if len(parts) >= 3:
                                f.write(f"* Interview with {parts[2]}\n")
                        f.write("\n")
                
                report_file = minimal_report_path
                console.print(f"[green]Minimal report created at: {minimal_report_path}[/green]")
            except Exception as e:
                console.print(f"[red]Failed to create minimal report: {str(e)}[/red]")
    
    # Save interview combinations to a JSON file
    combinations_file = os.path.join(base_dir, "interview_combinations.json")
    with open(combinations_file, 'w', encoding='utf-8') as f:
        json.dump(interview_combinations, f, indent=2)
    
    # Create a more readable summary file
    summary_file = os.path.join(base_dir, "interview_summary.md")
    with open(summary_file, 'w', encoding='utf-8') as f:
        f.write(f"# Interview Summary\n\n")
        f.write(f"Generated: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"Model: {provider}/{model}\n\n")
        f.write(f"## Overview\n\n")
        f.write(f"- Total interviews: {len(all_interviews)}\n")
        f.write(f"- Stakeholder categories: {len(selected_categories)}\n")
        f.write(f"- Interviews per category: {interviews_per_category}\n\n")
        
        f.write(f"## Interview Combinations\n\n")
        for i, combo in enumerate(interview_combinations):
            f.write(f"### Interview {i+1}\n\n")
            f.write(f"**Interviewer**: {combo['interviewer']['name']} ({combo['interviewer']['user_id']})\n")
            f.write(f"- Role: {combo['interviewer']['role']}\n")
            f.write(f"- Demographics: {', '.join([f'{k}: {v}' for k, v in combo['interviewer']['demographics'].items()])}\n\n")
            
            f.write(f"**Interviewee**: {combo['interviewee']['name']} ({combo['interviewee']['user_id']})\n")
            f.write(f"- Role: {combo['interviewee']['role']}\n")
            f.write(f"- Demographics: {', '.join([f'{k}: {v}' for k, v in combo['interviewee']['demographics'].items()])}\n\n")
            
            f.write(f"**Details**:\n")
            f.write(f"- Category: {combo['interview_details']['category'].replace('_', ' ')}\n")
            f.write(f"- File: {os.path.basename(combo['interview_details']['file_path'])}\n")
            f.write(f"- Timestamp: {combo['interview_details']['timestamp']}\n\n")
    
    # Print summary
    console.print("\n[bold green]Process completed![/bold green]")
    console.print(f"Generated {len(all_interviews)} interviews across {len(selected_categories)} stakeholder categories")
    console.print(f"All files saved to: {base_dir}")
    console.print(f"  - Interviews: {exports_dir}")
    console.print(f"  - Reports: {reports_dir}")
    console.print(f"  - Interview combinations: {combinations_file}")
    console.print(f"  - Interview summary: {summary_file}")
    
    # Check for PDF generation capabilities and offer installation if needed
    try:
        # First check if pypandoc is available
        import pypandoc
        pypandoc_available = True
    except ImportError:
        pypandoc_available = False
        # Then check if system pandoc is available
        pandoc_available = os.system("which pandoc > /dev/null 2>&1") == 0
    
    # Check if latex packages are installed (specifically check for xcolor.sty)
    latex_extra_installed = False
    if os.system("dpkg-query -W -f='${Status}' texlive-latex-extra 2>/dev/null | grep 'install ok installed'") == 0:
        latex_extra_installed = True
    elif os.system("find /usr -name 'xcolor.sty' 2>/dev/null | grep -q 'xcolor.sty'") == 0:
        latex_extra_installed = True
    
    pdf_generation_issue = not (pypandoc_available or pandoc_available) or not latex_extra_installed
    
    if pdf_generation_issue:
        console.print("[yellow]PDF generation issue detected.[/yellow]")
        
        if not pypandoc_available and not pandoc_available:
            console.print("[yellow]Neither pypandoc nor pandoc is installed.[/yellow]")
        
        if not latex_extra_installed:
            console.print("[yellow]LaTeX package 'xcolor.sty' not found. This is required for PDF generation.[/yellow]")
        
        install_option = questionary.select(
            "How would you like to fix PDF generation?",
            choices=[
                "Install all requirements (pypandoc + LaTeX packages) - recommended",
                "Install system requirements only (requires admin privileges)",
                "Skip PDF generation"
            ]
        ).ask()
        
        if "all requirements" in install_option:
            console.print("[cyan]Installing pypandoc in the virtual environment...[/cyan]")
            exit_code = os.system("pip install pypandoc markdown2pdf")
            
            # Also install system dependencies
            console.print("[cyan]Installing LaTeX requirements (requires admin privileges)...[/cyan]")
            os.system("sudo apt-get update && sudo apt-get install -y texlive-latex-base texlive-fonts-recommended texlive-latex-extra")
            
            # Verify all installations
            pypandoc_ok = os.system("pip show pypandoc > /dev/null 2>&1") == 0
            latex_ok = os.system("dpkg-query -W -f='${Status}' texlive-latex-extra 2>/dev/null | grep 'install ok installed'") == 0
            
            if pypandoc_ok and latex_ok:
                console.print("[green]All PDF generation requirements installed successfully![/green]")
                console.print("[cyan]Do you want to convert the generated Markdown files to PDF now?[/cyan]")
                convert_now = questionary.confirm("Convert existing Markdown files to PDF?", default=True).ask()
                
                if convert_now:
                    try:
                        # Try to import the newly installed pypandoc
                        import pypandoc
                        console.print("[cyan]Converting Markdown files to PDF...[/cyan]")
                        
                        # Find all markdown files in the exports directory
                        md_files = []
                        for root, _, files in os.walk(base_dir):
                            for file in files:
                                if file.endswith(".md"):
                                    md_files.append(os.path.join(root, file))
                        
                        if md_files:
                            with Progress() as progress:
                                convert_task = progress.add_task("[green]Converting files...", total=len(md_files))
                                # Convert each markdown file to PDF
                                for md_file in md_files:
                                    try:
                                        pdf_file = md_file.replace(".md", ".pdf")
                                        pypandoc.convert_file(md_file, 'pdf', outputfile=pdf_file)
                                        progress.update(convert_task, advance=1)
                                    except Exception as e:
                                        console.print(f"[yellow]Error converting {md_file}: {str(e)}[/yellow]")
                            
                            console.print(f"[green]Converted {len(md_files)} Markdown files to PDF.[/green]")
                        else:
                            console.print("[yellow]No Markdown files found in the exports directory.[/yellow]")
                    except Exception as e:
                        console.print(f"[red]Error using pypandoc: {str(e)}[/red]")
            else:
                if not pypandoc_ok:
                    console.print("[red]Failed to install pypandoc.[/red]")
                if not latex_ok:
                    console.print("[red]Failed to install LaTeX packages. This may require manual installation.[/red]")
                    console.print("[yellow]Try running: sudo apt-get install -y texlive-latex-base texlive-fonts-recommended texlive-latex-extra[/yellow]")
        
        elif "system requirements" in install_option:
            console.print("[cyan]Installing pandoc and LaTeX requirements (requires admin privileges)...[/cyan]")
            os.system("sudo apt-get update && sudo apt-get install -y pandoc texlive-latex-base texlive-fonts-recommended texlive-latex-extra")
            
            # Verify installation
            pandoc_ok = os.system("which pandoc > /dev/null 2>&1") == 0
            latex_ok = os.system("dpkg-query -W -f='${Status}' texlive-latex-extra 2>/dev/null | grep 'install ok installed'") == 0
            
            if pandoc_ok and latex_ok:
                console.print("[green]All system dependencies installed successfully![/green]")
                console.print("[cyan]Do you want to convert the generated Markdown files to PDF now?[/cyan]")
                convert_now = questionary.confirm("Convert existing Markdown files to PDF?", default=True).ask()
                
                if convert_now:
                    console.print("[cyan]Converting Markdown files to PDF...[/cyan]")
                    # Find all markdown files in the exports directory
                    md_files = []
                    for root, _, files in os.walk(base_dir):
                        for file in files:
                            if file.endswith(".md"):
                                md_files.append(os.path.join(root, file))
                    
                    if md_files:
                        with Progress() as progress:
                            convert_task = progress.add_task("[green]Converting files...", total=len(md_files))
                            # Convert each markdown file to PDF
                            for md_file in md_files:
                                pdf_file = md_file.replace(".md", ".pdf")
                                os.system(f"pandoc {md_file} -o {pdf_file} 2>/dev/null")
                                progress.update(convert_task, advance=1)
                        
                        console.print(f"[green]Converted {len(md_files)} Markdown files to PDF.[/green]")
                    else:
                        console.print("[yellow]No Markdown files found in the exports directory.[/yellow]")
            else:
                if not pandoc_ok:
                    console.print("[red]Failed to install pandoc.[/red]")
                if not latex_ok:
                    console.print("[red]Failed to install LaTeX packages. This may require manual installation.[/red]")
                    console.print("[yellow]Try running: sudo apt-get install -y texlive-latex-extra[/yellow]")
        else:
            console.print("[yellow]Skipping PDF generation. All content is still available in Markdown format.[/yellow]")
    else:
        console.print("[green]PDF generation capabilities detected. Documents should be available in both Markdown and PDF formats.[/green]")
    
    # Ask user if they want to open the final report (if it exists)
    if report_file and os.path.exists(report_file):
        open_report = questionary.confirm("Would you like to view the final report now?").ask()
        if open_report:
            # Try to open the report with the default application
            try:
                if os.name == 'nt':  # Windows
                    os.system(f'start "" "{report_file}"')
                elif os.name == 'posix':  # Linux/Unix/MacOS
                    os.system(f'xdg-open "{report_file}"')
                else:
                    console.print("[yellow]Could not automatically open the report on this operating system.[/yellow]")
                    console.print(f"You can manually open the report at: {report_file}")
            except Exception as e:
                console.print(f"[yellow]Error opening report: {str(e)}[/yellow]")
                console.print(f"You can manually open the report at: {report_file}")
    elif report_file:
        console.print(f"[yellow]Report file {report_file} does not exist. Please check the exports directory.[/yellow]")
    else:
        console.print("[yellow]No report was generated to view.[/yellow]")

if __name__ == "__main__":
    console.print("\n[bold green]Interactive Interview Generator[/bold green]")
    console.print("This script will generate interviews, analyses, and reports about AI in consulting")
    console.print("with your chosen stakeholder categories and LLM provider.\n")
    
    try:
        main()
    except KeyboardInterrupt:
        console.print("\n[bold red]Process interrupted by user.[/bold red]")
        console.print("[yellow]Partial results may be available in the exports directory.[/yellow]")
    except Exception as e:
        console.print(f"\n[bold red]An unexpected error occurred: {str(e)}[/bold red]")
        console.print("[yellow]Partial results may be available in the exports directory.[/yellow]")
        import traceback
        console.print("[dim]" + traceback.format_exc() + "[/dim]")
