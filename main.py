import os, sys
from dotenv import load_dotenv
from google import genai
from google.genai import types

def main():
    if len(sys.argv) < 2:
        print('Usage: python main.py "prompt"')
        sys.exit(1)
        return

    verbose = False
    if len(sys.argv) > 2 and sys.argv[2] == "--verbose":
        verbose = True

    load_dotenv()
    my_api_key = os.environ.get("GEMINI_API_KEY")

    client = genai.Client(api_key=my_api_key)

    prompt = sys.argv[1]

    messages = [
        types.Content(role="user", parts=[types.Part(text=prompt)]),
    ]

    
    response = client.models.generate_content(
        model="gemini-2.0-flash-001",
        contents=messages
    )

    if verbose:
        print(f"User prompt: {prompt}")
    
    print(response.text)
    
    if verbose:
        print(f"Prompt tokens: {response.usage_metadata.prompt_token_count}")
        print(f"Response tokens: {response.usage_metadata.candidates_token_count}")


if __name__ == "__main__":
    main()
