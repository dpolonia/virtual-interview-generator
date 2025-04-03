import os
import anthropic

api_key = os.getenv("ANTHROPIC_API_KEY")

if not api_key:
    raise ValueError("API key nd. " "Use 'set ANTHROPIC_API_KEY=sua_chave' .")

client = anthropic.Anthropic(api_key=api_key)

response = client.messages.create(
    model="claude-3-opus-20240229",
    max_tokens=1024,
    messages=[
        {
            "role": "user",
            "content": (
                "Gera 5 perguntas de entrevista para um gestor de inovação "
                "com foco em transformação digital."
            ),
        }
    ],
)

print(response.content[0].text)
