# src/utils/persona_manager.py
from datasets import load_dataset
import json
import random
from typing import List, Dict, Any

class FinePersonaManager:
    def __init__(self, use_sample=True):
        """Initialize the FinePersona manager.
        
        Args:
            use_sample: If True, use the smaller 100k sample dataset instead of the full 21M dataset
        """
        self.use_sample = use_sample
        self.dataset = None
        self.category_personas = {}
        
    def load_dataset(self):
        """Load the FinePersonas dataset."""
        try:
            if self.use_sample:
                # Load the smaller clustering sample (100k)
                self.dataset = load_dataset("argilla/FinePersonas-v0.1-clustering-100k", split="train")
            else:
                # Load the full dataset (warning: this is 143GB)
                self.dataset = load_dataset("argilla/FinePersonas-v0.1", split="train")
            
            return True
        except Exception as e:
            print(f"Error loading FinePersonas dataset: {str(e)}")
            return False
    
    def get_personas_by_category(self, category: str, count: int = 30) -> List[Dict[str, Any]]:
        """Get personas that match a consulting-related category.
        
        Args:
            category: The consulting category to filter by
            count: Number of personas to return
            
        Returns:
            List of persona dictionaries
        """
        # Map our categories to likely FinePersonas labels
        category_keywords = {
            'senior_executives': ["Business", "Management", "Leadership", "Executive", "CEO", "CFO", "Strategy"],
            'ai_specialists': ["Artificial Intelligence", "Machine Learning", "Data Science", "Computer Science", "Programming", "Software Engineering"],
            'mid_level_consultants': ["Consulting", "Business Analysis", "Project Management", "Strategy", "Professional Services"],
            'clients': ["Business", "Corporate", "Industry", "Enterprise", "Operations"],
            'technology_providers': ["Technology", "Software", "Information Technology", "Engineering", "Computer Science"],
            'regulatory_stakeholders': ["Law", "Regulation", "Compliance", "Policy", "Government", "Legal"],
            'industry_analysts': ["Research", "Analysis", "Market Research", "Industry", "Academic", "Professor"]
        }
        
        # If we haven't loaded the dataset yet
        if self.dataset is None:
            self.load_dataset()
        
        # Check if we've already filtered this category
        if category in self.category_personas and len(self.category_personas[category]) >= count:
            return random.sample(self.category_personas[category], count)
        
        # Get relevant keywords for the category
        keywords = category_keywords.get(category, [])
        
        # Filter personas based on their labels containing any of our keywords
        filtered_personas = []
        
        # Look through the dataset and filter
        for persona in self.dataset:
            # Extract labels (format varies between the datasets)
            try:
                # For the clustering dataset
                if 'summary_label' in persona:
                    labels = json.loads(persona['summary_label'])
                # For the main dataset
                elif 'labels' in persona:
                    labels = persona['labels']
                else:
                    continue
                
                # Check if any keywords match labels
                if any(keyword in label for keyword in keywords for label in labels):
                    filtered_personas.append({
                        "id": persona["id"],
                        "persona_text": persona["persona"],
                        "labels": labels
                    })
            except:
                # Skip problematic entries
                continue
            
            # Break if we have enough
            if len(filtered_personas) >= count * 3:  # Get more than needed for randomization
                break
        
        # Store for future use
        self.category_personas[category] = filtered_personas
        
        # Return random selection
        return random.sample(filtered_personas, min(count, len(filtered_personas)))
    
    def format_persona_for_interview(self, persona_data: Dict[str, Any], role: str) -> Dict[str, Any]:
        """Format a FinePersona for use in the interview system.
        
        Args:
            persona_data: The raw persona data
            role: Either 'interviewer' or 'interviewee'
            
        Returns:
            Formatted persona dictionary
        """
        # Extract what we can from the persona text
        persona_text = persona_data["persona_text"]
        
        # Create a reasonable structure
        return {
            "name": f"Persona {persona_data['id'][:8]}",  # Use part of the ID as a name
            "category": role if role == "interviewer" else ", ".join(persona_data.get("labels", [])),
            "role": role,
            "background": persona_text,
            "created_by": "FinePersonas"
        }