import os, sys
from dotenv import load_dotenv
from google import genai
from google.genai import types
from functions.get_files_info import schema_get_files_info, get_files_info

available_functions = types.Tool(
    function_declarations=[
        schema_get_files_info,
    ]
)


system_prompt = """
You are a helpful AI coding agent.

When a user asks a question or makes a request, make a function call plan. You can perform the following operations:

- List files and directories

All paths you provide should be relative to the working directory. You do not need to specify the working directory in your function calls as it is automatically injected for security reasons.
"""


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
        contents=messages,
        config=types.GenerateContentConfig(
            tools=[available_functions], system_instruction=system_prompt
        )
    )

    if verbose:
        print(f"User prompt: {prompt}")
    

    if response.function_calls:
        for function_call in response.function_calls:
            print(f"Calling function: {function_call.name}({function_call.args})")
    else:
        print(response.text)
    
    if verbose:
        print(f"Prompt tokens: {response.usage_metadata.prompt_token_count}")
        print(f"Response tokens: {response.usage_metadata.candidates_token_count}")


if __name__ == "__main__":
    main()
