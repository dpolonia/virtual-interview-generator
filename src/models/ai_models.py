import os
import openai
import anthropic
import asyncio
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure API keys
openai.api_key = os.getenv("OPENAI_API_KEY")
anthropic_api_key = os.getenv("ANTHROPIC_API_KEY")
google_api_key = os.getenv("GOOGLE_API_KEY")

# Updated model configurations
AVAILABLE_MODELS = {
    'openai': [
        'gpt-4.5-preview-2025-02-27',
        'gpt-4o-2024-08-06',
        'gpt-4o-mini-2024-07-18',
        'o1-2024-12-17',
        'o3-mini-2025-01-31'
    ],
    'anthropic': [
        'claude-3-7-sonnet-20250219',  # Claude 3.7 Sonnet
        'claude-3-5-sonnet-20240620',  # Claude 3.5 Sonnet (June)
        'claude-3-5-sonnet-20241022',  # Claude 3.5 Sonnet (October)
        'claude-3-5-haiku-20241022',   # Claude 3.5 Haiku
        'claude-3-haiku-20240307'      # Claude 3 Haiku (cheapest)
    ],
    'google': [
        'gemini-2-0-flash',            # Gemini 2.0 Flash
        'gemini-2-0-flash-lite'        # Gemini 2.0 Flash-Lite
    ]
}

# Model information for display
MODEL_INFO = {
    # OpenAI models
    'gpt-4.5-preview-2025-02-27': {
        'description': 'Latest preview model with advanced capabilities',
        'best_for': 'Advanced reasoning and complex interview simulation'
    },
    'gpt-4o-2024-08-06': {
        'description': 'Balanced GPT-4o model',
        'best_for': 'High-quality interviews with balanced performance'
    },
    'gpt-4o-mini-2024-07-18': {
        'description': 'Smaller GPT-4o variant',
        'best_for': 'Faster generation with good quality'
    },
    'o1-2024-12-17': {
        'description': 'Optimized for reasoning',
        'best_for': 'Interviews requiring deep analytical thinking'
    },
    'o3-mini-2025-01-31': {
        'description': 'Compact but powerful model',
        'best_for': 'Efficient generation with good reasoning'
    },
    
    # Anthropic models
    'claude-3-7-sonnet-20250219': {
        'description': 'Latest Claude 3.7 Sonnet model',
        'best_for': 'Premium quality interviews with nuanced responses'
    },
    'claude-3-5-sonnet-20240620': {
        'description': 'Claude 3.5 Sonnet (June 2024)',
        'best_for': 'Well-balanced interviews with good detail'
    },
    'claude-3-5-sonnet-20241022': {
        'description': 'Claude 3.5 Sonnet (October 2024)',
        'best_for': 'Updated Sonnet with improved capabilities'
    },
    'claude-3-5-haiku-20241022': {
        'description': 'Claude 3.5 Haiku model',
        'best_for': 'Fast generation while maintaining quality'
    },
    'claude-3-haiku-20240307': {
        'description': 'Claude 3 Haiku (cheapest option)',
        'best_for': 'Cost-effective interview generation'
    },
    
    # Google models
    'gemini-2-0-flash': {
        'description': 'Google\'s Gemini 2.0 Flash model',
        'best_for': 'High-quality responses with good speed'
    },
    'gemini-2-0-flash-lite': {
        'description': 'Lighter version of Gemini 2.0 Flash',
        'best_for': 'Efficient processing for simpler interviews'
    }
}

class AIModelInterface:
    def __init__(self, provider, model):
        self.provider = provider
        self.model = model
        
        # Initialize appropriate client
        if provider == 'anthropic':
            self.client = anthropic.Anthropic(api_key=anthropic_api_key)
        elif provider == 'openai':
            self.client = openai.OpenAI()
        elif provider == 'google':
            try:
                import google.generativeai as genai
                genai.configure(api_key=google_api_key)
                self.client = genai
            except ImportError:
                raise ImportError("Google GenerativeAI package not installed.")
        else:
            raise ValueError(f"Unsupported provider: {provider}")
    
    def generate_text(self, prompt, max_tokens=4000):
        """Generate text using the selected model."""
        if self.provider == 'anthropic':
            response = self.client.messages.create(
                model=self.model,
                max_tokens=max_tokens,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
            return response.content[0].text
        
        elif self.provider == 'openai':
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "user", "content": prompt}
                ],
                max_tokens=max_tokens
            )
            return response.choices[0].message.content
        
        elif self.provider == 'google':
            model = self.client.GenerativeModel(self.model)
            response = model.generate_content(prompt)
            return response.text
        
        return None
    
    async def generate_text_async(self, prompt, max_tokens=4000):
        """Asynchronously generate text using the selected model."""
        if self.provider == 'anthropic':
            client = anthropic.AsyncAnthropic(api_key=anthropic_api_key)
            response = await client.messages.create(
                model=self.model,
                max_tokens=max_tokens,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
            return response.content[0].text
        
        elif self.provider == 'openai':
            client = openai.AsyncOpenAI()
            response = await client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "user", "content": prompt}
                ],
                max_tokens=max_tokens
            )
            return response.choices[0].message.content
        
        elif self.provider == 'google':
            # Use synchronous version for Google as their async API is less standardized
            # Convert to async using run_in_executor
            loop = asyncio.get_event_loop()
            return await loop.run_in_executor(None, self.generate_text, prompt, max_tokens)
        
        return None

class BatchProcessor:
    def __init__(self, provider, model, max_concurrency=3):
        self.provider = provider
        self.model = model
        self.max_concurrency = max_concurrency
    
    async def process_batch(self, prompts, max_tokens=4000):
        """Process a batch of prompts concurrently."""
        model = AIModelInterface(self.provider, self.model)
        
        # Create a semaphore to limit concurrency
        semaphore = asyncio.Semaphore(self.max_concurrency)
        
        async def process_with_semaphore(prompt):
            async with semaphore:
                return await model.generate_text_async(prompt, max_tokens)
        
        # Create tasks for all prompts
        tasks = [process_with_semaphore(prompt) for prompt in prompts]
        
        # Run all tasks and return results
        return await asyncio.gather(*tasks)
    
    def process_batch_sync(self, prompts, max_tokens=4000):
        """Process a batch of prompts synchronously (for environments without asyncio)."""
        model = AIModelInterface(self.provider, self.model)
        results = []
        
        for prompt in prompts:
            result = model.generate_text(prompt, max_tokens)
            results.append(result)
        
        return results

def get_available_models():
    """Return the dictionary of available models."""
    return AVAILABLE_MODELS

def get_model_info(model_name):
    """Return detailed information about a specific model."""
    return MODEL_INFO.get(model_name, {
        'description': 'No detailed information available',
        'best_for': 'General use'
    })

def get_all_model_info():
    """Return detailed information about all models."""
    return MODEL_INFO