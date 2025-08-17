import os, sys
from dotenv import load_dotenv
from google import genai
from google.genai import types
from functions.get_files_info import schema_get_files_info, get_files_info
from functions.get_file_content import schema_get_file_content, get_file_content
from functions.write_file import schema_write_file, write_file
from functions.run_python_file import schema_run_python_file, run_python_file

available_functions = types.Tool(
    function_declarations=[
        schema_get_files_info,
        schema_get_file_content,
        schema_write_file,
        schema_run_python_file,
    ]
)


MAX_ITERATIONS = 20

system_prompt = """
You are a helpful AI coding agent.

When a user asks a question or makes a request, make a function call plan. You can perform the following operations:

- List files and directories
- Read file contents
- Execute Python files with optional arguments
- Write or overwrite files

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

    if verbose:
        print(f"User prompt: {prompt}")

    messages = [
        types.Content(role="user", parts=[types.Part(text=prompt)]),
    ]
    
    try:
        for iterations in range(MAX_ITERATIONS):
            response = client.models.generate_content(
                model="gemini-2.0-flash-001",
                contents=messages,
                config=types.GenerateContentConfig(
                    tools=[available_functions], system_instruction=system_prompt
                )
            )
            for candidate in response.candidates:
                messages.append(candidate.content)
            

            if response.function_calls:
                for function_call in response.function_calls:
                    function_call_result = call_function(function_call, verbose)
                    function_response = function_call_result.parts[0].function_response.response
                    if not function_response:
                        raise Exception(
                            f"Function call {function_call.name} did not return a response."
                        )
                    if verbose:
                        print(f"-> {function_response}")
                    
                    new_message = types.Content(role="user", parts=[types.Part(text=str(function_response))])
                    messages.append(new_message)
            elif response.text:
                print("Final response:")
                print(response.text)
                break
    except Exception as e:
        print(f"Error during processing: {str(e)}")
        sys.exit(1)
    
    if verbose:
        print(f"Prompt tokens: {response.usage_metadata.prompt_token_count}")
        print(f"Response tokens: {response.usage_metadata.candidates_token_count}")


functions_by_function_name = {
    "get_files_info": get_files_info,
    "get_file_content": get_file_content,
    "write_file": write_file,
    "run_python_file": run_python_file,
}


def call_function(function_call_part, verbose=False):
    function_name = function_call_part.name
    function_args = function_call_part.args
    
    
    if verbose:
        print(f"Calling function: {function_name}({function_args})")
    else:
        print(f" - Calling function: {function_name}")
    
    if function_name not in functions_by_function_name:
        return types.Content(
            role="tool",
            parts=[
                types.Part.from_function_response(
                    name=function_name,
                    response={"error": f"Unknown function: {function_name}"},
                )
            ],
        )

    function = functions_by_function_name.get(function_name)
    
    function_result = function(
        working_directory="./calculator",
        **function_call_part.args
    )

    return types.Content(
        role="tool",
        parts=[
            types.Part.from_function_response(
                name=function_name,
                response={"result": function_result},
            )
        ],
    )
    


if __name__ == "__main__":
    main()
