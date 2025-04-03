import os
import re
import json
import PyPDF2

# Script categories
STAKEHOLDER_CATEGORIES = [
    'Senior Executives from Consulting Firms',
    'AI Specialists and Data Scientists within Consulting',
    'Mid-Level Consultants and Associate Managers',
    'Clients of Consulting Services',
    'Technology Providers and AI Solution Vendors',
    'Regulatory and Policy Stakeholders',
    'Industry Analysts or Academics Specializing in Consulting and AI'
]

# Normalized category names for database use
NORMALIZED_CATEGORIES = {
    'Senior Executives from Consulting Firms': 'senior_executives',
    'AI Specialists and Data Scientists within Consulting': 'ai_specialists',
    'Mid-Level Consultants and Associate Managers': 'mid_level_consultants',
    'Clients of Consulting Services': 'clients',
    'Technology Providers and AI Solution Vendors': 'technology_providers',
    'Regulatory and Policy Stakeholders': 'regulatory_stakeholders',
    'Industry Analysts or Academics Specializing in Consulting and AI': 'industry_analysts'
}

def parse_interview_scripts(file_path):
    """Parse the interview script document and extract scripts for each stakeholder category."""
    # Check if it's a PDF file
    if file_path.lower().endswith('.pdf'):
        content = extract_text_from_pdf(file_path)
    else:
        # For text files, read normally
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as file:
            content = file.read()
    
    scripts = {}
    
    # Find sections for each stakeholder category
    for category in STAKEHOLDER_CATEGORIES:
        # Look for sections in the document that match category names
        pattern = rf"{category}.*?\n(.*?)(?=(?:{STAKEHOLDER_CATEGORIES[0]})|$)"
        match = re.search(pattern, content, re.DOTALL)
        if match:
            scripts[category] = match.group(1).strip()
    
    # If no scripts were found, try an alternative parsing approach
    if not scripts:
        # Try to extract sections between category headings
        for i, category in enumerate(STAKEHOLDER_CATEGORIES):
            # Find the start position of this category
            start_pos = content.find(category)
            if start_pos == -1:
                continue
                
            # Find the end position (start of the next category)
            end_pos = -1
            if i < len(STAKEHOLDER_CATEGORIES) - 1:
                end_pos = content.find(STAKEHOLDER_CATEGORIES[i+1], start_pos)
            
            # Extract the content
            if end_pos == -1:
                section_content = content[start_pos + len(category):]
            else:
                section_content = content[start_pos + len(category):end_pos]
                
            scripts[category] = section_content.strip()
    
    return scripts

def extract_text_from_pdf(pdf_path):
    """Extract text content from a PDF file."""
    text = ""
    try:
        with open(pdf_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            for page_num in range(len(pdf_reader.pages)):
                page = pdf_reader.pages[page_num]
                text += page.extract_text() + "\n"
    except Exception as e:
        print(f"Error reading PDF: {str(e)}")
    
    return text

def format_script_for_interview(script_text):
    """Format the raw script text into a structured interview guide."""
    # Extract question sections
    sections = {
        "Demographic": [],
        "RQ1": [],
        "RQ2": [],
        "RQ3": [],
        "RQ4": []
    }
    
    current_section = None
    lines = script_text.split('\n')
    
    for line in lines:
        line = line.strip()
        if not line:
            continue
            
        # Identify section headers
        if "Demographic Data" in line:
            current_section = "Demographic"
        elif "RQ1:" in line:
            current_section = "RQ1"
        elif "RQ2:" in line:
            current_section = "RQ2"
        elif "RQ3:" in line:
            current_section = "RQ3"
        elif "RQ4:" in line:
            current_section = "RQ4"
        elif current_section and (line.startswith("- ") or line.startswith("Initial") or 
                                 line.startswith("Role") or line.startswith("Consulting") or
                                 line.startswith("Professional") or ":" in line):
            # This is likely a question
            sections[current_section].append(line)
    
    # Format the interview guide
    formatted_script = "# INTERVIEW GUIDE\n\n"
    
    # Introduction
    formatted_script += "## INTRODUCTION\n"
    formatted_script += "Hello, thank you for participating in this interview about AI adoption in consulting. "
    formatted_script += "I'd like to start with some background questions and then dive into specific areas.\n\n"
    
    # Format each section
    if sections["Demographic"]:
        formatted_script += "## DEMOGRAPHIC QUESTIONS\n"
        for q in sections["Demographic"]:
            formatted_script += f"- {q}\n"
        formatted_script += "\n"
    
    if sections["RQ1"]:
        formatted_script += "## RQ1: AI ADOPTION QUESTIONS\n"
        formatted_script += "Let's discuss how established AI adoption is within the consulting industry.\n"
        for q in sections["RQ1"]:
            formatted_script += f"- {q}\n"
        formatted_script += "\n"
    
    if sections["RQ2"]:
        formatted_script += "## RQ2: MARKET TRENDS QUESTIONS\n"
        formatted_script += "Now I'd like to ask about current trends in the consulting market in Portugal.\n"
        for q in sections["RQ2"]:
            formatted_script += f"- {q}\n"
        formatted_script += "\n"
    
    if sections["RQ3"]:
        formatted_script += "## RQ3: AUTOMATION & KNOWLEDGE INTERNALIZATION QUESTIONS\n"
        formatted_script += "Let's discuss how AI affects consulting firms in terms of automation and knowledge internalization.\n"
        for q in sections["RQ3"]:
            formatted_script += f"- {q}\n"
        formatted_script += "\n"
    
    if sections["RQ4"]:
        formatted_script += "## RQ4: ETHICAL RISKS QUESTIONS\n"
        formatted_script += "Finally, I'd like to explore ethical risks associated with integrating AI in consulting.\n"
        for q in sections["RQ4"]:
            formatted_script += f"- {q}\n"
        formatted_script += "\n"
    
    # Closing
    formatted_script += "## CLOSING\n"
    formatted_script += "Thank you for your time and insights. Is there anything else you'd like to add before we conclude?\n"
    
    return formatted_script

def get_category_key(category_name):
    """Get the normalized category key for a given category name."""
    return NORMALIZED_CATEGORIES.get(category_name, category_name.lower().replace(' ', '_'))

def save_scripts_to_files(scripts, output_dir='data/scripts'):
    """Save parsed scripts to individual files."""
    os.makedirs(output_dir, exist_ok=True)
    
    for category, script in scripts.items():
        category_key = get_category_key(category)
        file_path = os.path.join(output_dir, f"{category_key}.txt")
        
        formatted_script = format_script_for_interview(script)
        
        with open(file_path, 'w', encoding='utf-8') as file:
            file.write(formatted_script)
    
    return True

def save_scripts_to_json(scripts, output_path='data/scripts/scripts.json'):
    """Save all scripts to a JSON file."""
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    # Create dictionary with normalized keys
    formatted_scripts = {}
    for category, script in scripts.items():
        category_key = get_category_key(category)
        formatted_scripts[category_key] = {
            "name": category,
            "script": script,
            "formatted_script": format_script_for_interview(script)
        }
    
    with open(output_path, 'w', encoding='utf-8') as file:
        json.dump(formatted_scripts, file, indent=2)
    
    return True