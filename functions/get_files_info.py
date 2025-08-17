import os
from google.genai import types


def get_files_info(working_directory, directory="."):
    try:
        res = ""

        directory_name = f"'{directory}' directory" if directory != "." else "current directory"
        res += f'Result for {directory_name}:\n'
        
        full_path = os.path.abspath(os.path.join(working_directory, directory))
        
        if not os.path.isdir(full_path):
            return f'Error: "{directory}" is not a directory'
        
        working_directory_full_path = os.path.abspath(working_directory)
        if not full_path.startswith(working_directory_full_path):
            return f'Error: Cannot list "{directory}" as it is outside the permitted working directory'
        
        file_names = os.listdir(full_path)
        for file_name in file_names:
            file_path = os.path.join(full_path, file_name)
            res += f'- {file_name}: file_size={os.path.getsize(file_path)} bytes, is_dir={os.path.isdir(file_path)}\n'
        
        return res
    except Exception as e:
        return f'Error: {str(e)}'


schema_get_files_info = types.FunctionDeclaration(
    name="get_files_info",
    description="Lists files in the specified directory along with their sizes, constrained to the working directory.",
    parameters=types.Schema(
        type=types.Type.OBJECT,
        properties={
            "directory": types.Schema(
                type=types.Type.STRING,
                description="The directory to list files from, relative to the working directory. If not provided, lists files in the working directory itself.",
            ),
        },
    ),
)
