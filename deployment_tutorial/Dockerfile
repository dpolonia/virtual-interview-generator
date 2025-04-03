FROM python:3.9-slim

WORKDIR /app

# Copy requirements first for better caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create required directories
RUN mkdir -p data/scripts data/personas data/interviews exports

# Set up environment variables (override these at runtime)
ENV OPENAI_API_KEY="your_openai_api_key"
ENV ANTHROPIC_API_KEY="your_anthropic_api_key"
ENV GOOGLE_API_KEY="your_google_api_key"

# Entry point
ENTRYPOINT ["python", "src/main.py"]

# Default command (override at runtime)
CMD ["--help"]