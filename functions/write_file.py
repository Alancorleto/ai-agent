import os

def write_file(working_directory, file_path, content):
    try:
        full_path = os.path.abspath(os.path.join(working_directory, file_path))
        
        if not os.path.exists(full_path):
            os.makedirs(os.path.dirname(full_path), exist_ok=True)
        
        working_directory_full_path = os.path.abspath(working_directory)
        if not full_path.startswith(working_directory_full_path):
            return f'Error: Cannot read "{file_path}" as it is outside the permitted working directory'

        with open(full_path, "w") as f:
            f.write(content)
            return f'Successfully wrote to "{file_path}" ({len(content)} characters written)'


    except Exception as e:
        return f'Error: {str(e)}'