import sys
import os
import anthropic


def main():
    if len(sys.argv) < 2:
        print('Uso: claude "prompt"')
        return

    prompt = sys.argv[1]
    client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
    response = client.messages.create(
        model="claude-3-opus-20240229",
        max_tokens=1024,
        messages=[{"role": "user", "content": prompt}],
    )
    print(response.content[0].text)


if __name__ == "__main__":
    main()
