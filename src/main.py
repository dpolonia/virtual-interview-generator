import os
import click
import questionary
from rich.console import Console
from rich.table import Table
from rich.progress import Progress

from database.db_manager import db_manager
from models.ai_models import AIModelInterface, get_available_models, BatchProcessor
from prompts.prompt_templates import (
    INTERVIEWER_PERSONA_PROMPT,
    INTERVIEWEE_PERSONA_PROMPT,
    INTERVIEW_GENERATION_PROMPT,
    XML_FORMATTING_PROMPT,
    ANALYSIS_PROMPT
)
from utils.script_parser import (
    parse_interview_scripts,
    format_script_for_interview,
    get_category_key,
    save_scripts_to_files,
    STAKEHOLDER_CATEGORIES,
    NORMALIZED_CATEGORIES
)
from utils.persona_manager import FinePersonaManager

console = Console()

@click.group()
def cli():
    """Virtual Interview Generator for AI in Consulting Research"""
    pass

def select_ai_model():
    """Interactive model selection."""
    # First, select provider
    provider_choices = [
        "OpenAI (GPT models)",
        "Anthropic (Claude models)",
        "Google (Gemini models)"
    ]
    
    provider = questionary.select(
        "Select AI provider:",
        choices=provider_choices
    ).ask()
    
    # Extract provider name
    provider_key = provider.split()[0].lower()
    
    # Display model information
    table = Table(title=f"{provider} Models")
    table.add_column("Model Name")
    table.add_column("Description")
    table.add_column("Best For")
    
    if provider_key == "openai":
        table.add_row("gpt-4.5-preview-2025-02-27", "Latest preview model", "Advanced reasoning and complex interviews")
        table.add_row("gpt-4o-2024-08-06", "Balanced GPT-4o model", "High-quality interviews")
        table.add_row("gpt-4o-mini-2024-07-18", "Smaller GPT-4o variant", "Faster interview generation")
        table.add_row("o1-2024-12-17", "Optimized for reasoning", "Deep analytical thinking")
        table.add_row("o3-mini-2025-01-31", "Compact but powerful", "Efficient generation")
    elif provider_key == "anthropic":
        table.add_row("claude-3-7-sonnet-20250219", "Latest Claude 3.7 Sonnet", "Premium quality interviews")
        table.add_row("claude-3-5-sonnet-20240620", "Claude 3.5 Sonnet (June)", "Well-balanced interviews")
        table.add_row("claude-3-5-sonnet-20241022", "Claude 3.5 Sonnet (Oct)", "Updated Sonnet capabilities")
        table.add_row("claude-3-5-haiku-20241022", "Claude 3.5 Haiku", "Fast generation")
        table.add_row("claude-3-haiku-20240307", "Claude 3 Haiku (cheapest)", "Cost-effective interviews")
    elif provider_key == "google":
        table.add_row("gemini-2-0-flash", "Gemini 2.0 Flash", "High-quality responses")
        table.add_row("gemini-2-0-flash-lite", "Gemini 2.0 Flash-Lite", "Efficient processing")
    
    console.print(table)
    
    # Select specific model
    model_choices = get_available_models()[provider_key]
    model = questionary.select(
        "Select specific model:",
        choices=model_choices
    ).ask()
    
    return {"provider": provider_key, "model": model}

@cli.command()
def parse_scripts():
    """Parse interview scripts from the source document."""
    script_path = questionary.text(
        "Enter the path to the interview script document:",
        default="docs/Master Dissertation - Script Interviews.pdf"
    ).ask()
    
    console.print(f"Parsing scripts from {script_path}...")
    
    try:
        scripts = parse_interview_scripts(script_path)
        save_scripts_to_files(scripts)
        
        console.print("[green]Scripts successfully parsed and saved to data/scripts/[/green]")
        
        # Display found categories
        table = Table(title="Parsed Interview Scripts")
        table.add_column("Category")
        table.add_column("File")
        
        for category, script in scripts.items():
            category_key = get_category_key(category)
            table.add_row(category, f"data/scripts/{category_key}.txt")
        
        console.print(table)
        
    except Exception as e:
        console.print(f"[red]Error parsing scripts: {str(e)}[/red]")

@cli.command()
def generate_personas():
    """Generate interviewer and interviewee personas."""
    # Ask if user wants to use FinePersonas
    use_finepersonas = questionary.confirm(
        "Do you want to use FinePersonas dataset for persona generation?",
        default=True
    ).ask()
    
    if use_finepersonas:
        # Initialize FinePersona manager
        persona_manager = FinePersonaManager(use_sample=True)  # Use the smaller sample by default
        
        # Load the dataset
        if not persona_manager.load_dataset():
            console.print("[yellow]Failed to load FinePersonas dataset. Falling back to AI generation.[/yellow]")
            use_finepersonas = False
    
    if use_finepersonas:
        # Generate interviewer personas from FinePersonas
        num_interviewers = questionary.text(
            "How many interviewer personas do you want to generate?",
            default="5"
        ).ask()
        num_interviewers = int(num_interviewers)
        
        # Use 'industry_analysts' as a good source for interviewers
        interviewer_personas = persona_manager.get_personas_by_category('industry_analysts', num_interviewers)
        
        console.print(f"Selected {len(interviewer_personas)} interviewer personas from FinePersonas")
        
        # Save interviewers to database
        for persona_data in interviewer_personas:
            formatted_persona = persona_manager.format_persona_for_interview(persona_data, 'interviewer')
            db_manager.create_persona(formatted_persona)
        
        # Ask which categories to generate interviewees for
        categories = []
        while not categories:
            categories = questionary.checkbox(
                "Select at least one stakeholder category to generate personas for (IMPORTANT: You must select at least one):",
                choices=[
                    'senior_executives',
                    'ai_specialists',
                    'mid_level_consultants',
                    'clients',
                    'technology_providers',
                    'regulatory_stakeholders',
                    'industry_analysts'
                ]
            ).ask()
            
            if not categories:
                console.print("[red]ERROR: Please select at least one category. You did not select any categories.[/red]")
        
        # Ask how many personas per category
        num_per_category = questionary.text(
            "How many personas to generate per category?",
            default="10"
        ).ask()
        num_per_category = int(num_per_category)
        
        # Generate interviewee personas for each category
        for category in categories:
            console.print(f"\nGenerating personas for {category}...")
            
            category_personas = persona_manager.get_personas_by_category(category, num_per_category)
            console.print(f"Selected {len(category_personas)} personas from FinePersonas")
            
            # Save personas to database
            for persona_data in category_personas:
                formatted_persona = persona_manager.format_persona_for_interview(persona_data, 'interviewee')
                formatted_persona['category'] = category  # Ensure correct category
                db_manager.create_persona(formatted_persona)
        
        console.print("[green]All personas generated successfully from FinePersonas![/green]")
        
    else:
        # Select AI model for persona generation
        console.print("Selecting AI model for persona generation:")
        model_info = select_ai_model()
        
        try:
            ai_model = AIModelInterface(model_info["provider"], model_info["model"])
            
            # Ask how many interviewer personas to generate
            num_interviewers = questionary.text(
                "How many interviewer personas do you want to generate?",
                default="5"
            ).ask()
            num_interviewers = int(num_interviewers)
            
            # Generate interviewer personas
            console.print(f"Generating {num_interviewers} interviewer personas...")
            
            with Progress() as progress:
                task = progress.add_task("[green]Generating interviewer personas...", total=num_interviewers)
                
                for i in range(num_interviewers):
                    response = ai_model.generate_text(INTERVIEWER_PERSONA_PROMPT)
                    
                    # Parse the response to extract persona details
                    # This is a simplified version - you might want to add more structured parsing
                    persona_data = {
                        "name": f"Interviewer {i+1}",  # Placeholder - extract from response
                        "category": "interviewer",
                        "role": "interviewer",
                        "background": response,
                        "created_by": f"{model_info['provider']}/{model_info['model']}"
                    }
                    
                    # Save to database
                    db_manager.create_persona(persona_data)
                    progress.update(task, advance=1)
            
            # Ask which categories to generate interviewees for
            categories = []
            while not categories:
                categories = questionary.checkbox(
                    "Select at least one stakeholder category to generate personas for (IMPORTANT: You must select at least one):",
                    choices=STAKEHOLDER_CATEGORIES
                ).ask()
                
                if not categories:
                    console.print("[red]ERROR: Please select at least one category. You did not select any categories.[/red]")
            
            # Ask how many personas per category
            num_per_category = questionary.text(
                "How many personas to generate per category?",
                default="10"
            ).ask()
            num_per_category = int(num_per_category)
            
            # Generate interviewee personas
            for category in categories:
                console.print(f"\nGenerating {num_per_category} personas for {category}...")
                
                with Progress() as progress:
                    task = progress.add_task(f"[green]Generating {category} personas...", total=num_per_category)
                    
                    for i in range(num_per_category):
                        prompt = INTERVIEWEE_PERSONA_PROMPT.format(category=category)
                        response = ai_model.generate_text(prompt)
                        
                        # Parse the response to extract persona details
                        # This is a simplified version - you might want to add more structured parsing
                        persona_data = {
                            "name": f"{category} {i+1}",  # Placeholder - extract from response
                            "category": get_category_key(category),
                            "role": "interviewee",
                            "background": response,
                            "created_by": f"{model_info['provider']}/{model_info['model']}"
                        }
                        
                        # Save to database
                        db_manager.create_persona(persona_data)
                        progress.update(task, advance=1)
            
            console.print("[green]All personas generated successfully![/green]")
            
        except Exception as e:
            console.print(f"[red]Error generating personas: {str(e)}[/red]")

@cli.command()
def generate_interviews():
    """Generate interviews between selected personas."""
    # Select AI model for interview generation
    console.print("Selecting AI model for interview generation:")
    model_info = select_ai_model()
    
    try:
        ai_model = AIModelInterface(model_info["provider"], model_info["model"])
        
        # Select stakeholder category
        category_name = questionary.select(
            "Select stakeholder category for interviews:",
            choices=STAKEHOLDER_CATEGORIES
        ).ask()
        
        category_key = get_category_key(category_name)
        
        # Load script for this category
        script_path = f"data/scripts/{category_key}.txt"
        if not os.path.exists(script_path):
            console.print(f"[yellow]Script not found. Run 'parse_scripts' command first.[/yellow]")
            return
        
        with open(script_path, 'r', encoding='utf-8') as f:
            script = f.read()
        
        # Get interviewer personas
        interviewers = db_manager.get_personas_by_category("interviewer", "interviewer")
        if not interviewers:
            console.print("[yellow]No interviewer personas found. Run 'generate_personas' first.[/yellow]")
            return
        
        # Create more descriptive choices to better represent personas
        interviewer_choices = []
        for p in interviewers:
            # Extract a short description from the background (first sentence or part of it)
            short_desc = ""
            if p.background:
                first_sentence = p.background.split('.')[0]
                short_desc = (first_sentence[:100] + '...') if len(first_sentence) > 100 else first_sentence
            interviewer_choices.append(f"{p.name} - {short_desc}")
        
        selected_interviewer_display = questionary.select(
            "Select interviewer persona:",
            choices=interviewer_choices
        ).ask()
        
        # Extract just the name part
        selected_interviewer_name = selected_interviewer_display.split(' - ')[0]
        selected_interviewer = next(p for p in interviewers if p.name == selected_interviewer_name)
        
        # Get interviewee personas for this category
        interviewees = db_manager.get_personas_by_category(category_key, "interviewee")
        if not interviewees:
            console.print(f"[yellow]No personas found for category {category_name}. Run 'generate_personas' first and select this category.[/yellow]")
            return
        
        # Create more descriptive choices for interviewees too
        interviewee_choices = []
        for p in interviewees:
            # Extract a short description from the background (first sentence or part of it)
            short_desc = ""
            if p.background:
                first_sentence = p.background.split('.')[0]
                short_desc = (first_sentence[:100] + '...') if len(first_sentence) > 100 else first_sentence
            interviewee_choices.append(f"{p.name} - {short_desc}")
        
        selected_interviewee_displays = questionary.checkbox(
            f"Select interviewee personas (up to 10) for {category_name}:",
            choices=interviewee_choices
        ).ask()
        
        selected_interviewee_names = [display.split(' - ')[0] for display in selected_interviewee_displays]
        
        # Generate interviews
        console.print(f"\nGenerating interviews for {len(selected_interviewee_names)} personas in {category_name} category...")
        
        # Ask if user wants to use batch processing
        use_batch = questionary.confirm(
            "Do you want to use batch processing for faster generation (experimental)?",
            default=False
        ).ask()
        
        if use_batch:
            # Initialize batch processor
            batch_processor = BatchProcessor(model_info["provider"], model_info["model"])
            
            # Prepare prompts for all interviews
            interview_prompts = []
            for interviewee_name in selected_interviewee_names:
                interviewee = next(p for p in interviewees if p.name == interviewee_name)
                
                prompt = INTERVIEW_GENERATION_PROMPT.format(
                    interviewer_details=selected_interviewer.background,
                    interviewee_details=interviewee.background,
                    script=script
                )
                interview_prompts.append((interviewee, prompt))
            
            # Process interviews in batch
            console.print(f"Generating {len(interview_prompts)} interviews in batch...")
            prompts_only = [p[1] for p in interview_prompts]
            
            results = batch_processor.process_batch_sync(prompts_only, max_tokens=3000)
            
            # Process results
            for i, (interviewee, _) in enumerate(interview_prompts):
                interview_text = results[i]
                
                # Format as XML
                xml_prompt = XML_FORMATTING_PROMPT.format(
                    interview_id=f"{category_key}_{interviewee.id}",
                    interviewer_details=selected_interviewer.background,
                    interviewee_details=interviewee.background,
                    interview_text=interview_text
                )
                
                console.print(f"Formatting interview with {interviewee.name} as XML...")
                xml_formatted = ai_model.generate_text(xml_prompt)
                
                # Save interview to database
                interview_id = db_manager.create_interview(
                    interviewer_id=selected_interviewer.id,
                    interviewee_id=interviewee.id,
                    category=category_key,
                    model_used=f"{model_info['provider']}/{model_info['model']}",
                    raw_interview=interview_text,
                    xml_formatted=xml_formatted
                )
                
                # Generate analysis
                analysis_prompt = ANALYSIS_PROMPT.format(
                    interview_text=interview_text
                )
                
                console.print(f"Generating analysis for {interviewee.name}...")
                analysis_text = ai_model.generate_text(analysis_prompt)
                
                # Parse analysis into components (simplified)
                analysis_data = {
                    "key_points": analysis_text,
                    "notable_quotes": "",
                    "ai_attitudes": "",
                    "rq1_insights": "",
                    "rq2_insights": "",
                    "rq3_insights": "",
                    "rq4_insights": "",
                    "contradictions": "",
                    "authenticity_assessment": ""
                }
                
                db_manager.create_analysis(interview_id, analysis_data)
                
        else:
            # Process interviews sequentially 
            with Progress() as progress:
                tasks = {}
                for name in selected_interviewee_names:
                    task_id = progress.add_task(f"[green]Generating interview with {name}...", total=3)
                    tasks[name] = task_id
                
                for interviewee_name in selected_interviewee_names:
                    interviewee = next(p for p in interviewees if p.name == interviewee_name)
                    
                    # 1. Generate interview
                    prompt = INTERVIEW_GENERATION_PROMPT.format(
                        interviewer_details=selected_interviewer.background,
                        interviewee_details=interviewee.background,
                        script=script
                    )
                    
                    console.print(f"\nGenerating interview between {selected_interviewer.name} and {interviewee.name}...")
                    interview_text = ai_model.generate_text(prompt, max_tokens=3000)
                    progress.update(tasks[interviewee_name], advance=1)
                    
                    # 2. Format as XML
                    xml_prompt = XML_FORMATTING_PROMPT.format(
                        interview_id=f"{category_key}_{interviewee.id}",
                        interviewer_details=selected_interviewer.background,
                        interviewee_details=interviewee.background,
                        interview_text=interview_text
                    )
                    
                    console.print(f"Formatting interview as XML...")
                    xml_formatted = ai_model.generate_text(xml_prompt)
                    progress.update(tasks[interviewee_name], advance=1)
                    
                    # 3. Save interview to database
                    interview_id = db_manager.create_interview(
                        interviewer_id=selected_interviewer.id,
                        interviewee_id=interviewee.id,
                        category=category_key,
                        model_used=f"{model_info['provider']}/{model_info['model']}",
                        raw_interview=interview_text,
                        xml_formatted=xml_formatted
                    )
                    
                    # 4. Generate analysis
                    analysis_prompt = ANALYSIS_PROMPT.format(
                        interview_text=interview_text
                    )
                    
                    console.print(f"Generating analysis...")
                    analysis_text = ai_model.generate_text(analysis_prompt)
                    
                    # Parse analysis into components (simplified)
                    analysis_data = {
                        "key_points": analysis_text,
                        "notable_quotes": "",
                        "ai_attitudes": "",
                        "rq1_insights": "",
                        "rq2_insights": "",
                        "rq3_insights": "",
                        "rq4_insights": "",
                        "contradictions": "",
                        "authenticity_assessment": ""
                    }
                    
                    db_manager.create_analysis(interview_id, analysis_data)
                    progress.update(tasks[interviewee_name], advance=1)
        
        console.print("[green]Interviews generated successfully![/green]")
        
    except Exception as e:
        console.print(f"[red]Error generating interviews: {str(e)}[/red]")

@cli.command()
@click.option('--format', type=click.Choice(['xml', 'txt']), default='xml')
@click.option('--output-dir', default='exports')
def export_interviews(format, output_dir):
    """Export generated interviews to files."""
    # Get all interviews from the database
    try:
        # Create output directory if it doesn't exist
        os.makedirs(output_dir, exist_ok=True)
        
        # Get interviews from database
        # This is a simplified placeholder - implement the actual query
        interviews = []  # Replace with actual database query
        
        if not interviews:
            console.print("[yellow]No interviews found in the database.[/yellow]")
            return
        
        # Export each interview
        with Progress() as progress:
            task = progress.add_task("[green]Exporting interviews...", total=len(interviews))
            
            for interview in interviews:
                # Export logic would go here
                # For XML format, save the xml_formatted field
                # For TXT format, save the raw_interview field
                progress.update(task, advance=1)
        
        console.print(f"[green]Successfully exported {len(interviews)} interviews to {output_dir}/[/green]")
    
    except Exception as e:
        console.print(f"[red]Error exporting interviews: {str(e)}[/red]")

@cli.command()
def generate_report():
    """Generate a comprehensive report of all interviews."""
    try:
        # Get all analyses from the database
        # This is a simplified placeholder - implement the actual query
        analyses = []  # Replace with actual database query
        
        if not analyses:
            console.print("[yellow]No interview analyses found in the database.[/yellow]")
            return
        
        # Generate report
        report_path = os.path.join('exports', 'report.md')
        
        # Report generation logic would go here
        
        console.print(f"[green]Successfully generated report at {report_path}[/green]")
    
    except Exception as e:
        console.print(f"[red]Error generating report: {str(e)}[/red]")

if __name__ == '__main__':
    # Ensure directories exist
    os.makedirs('data/scripts', exist_ok=True)
    os.makedirs('data/personas', exist_ok=True)
    os.makedirs('data/interviews', exist_ok=True)
    os.makedirs('exports', exist_ok=True)
    
    cli()