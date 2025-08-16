import subprocess
import os

def run_python_file(working_directory, file_path, args=[]):
    try:
        full_path = os.path.abspath(os.path.join(working_directory, file_path))

        if not os.path.exists(full_path):
                return f'Error: File "{file_path}" not found.'
            
        working_directory_full_path = os.path.abspath(working_directory)
        if not full_path.startswith(working_directory_full_path):
            return f'Error: Cannot execute "{file_path}" as it is outside the permitted working directory'

        if not full_path.endswith('.py'):
            return f'Error: "{file_path}" is not a Python file.'

        try:
            subprocess_result = subprocess.run(
                ['python', full_path] + args,
                cwd=working_directory,
                capture_output=True,
                timeout=30,
            )

            output = subprocess_result.stdout.decode('utf-8').strip()
            error = subprocess_result.stderr.decode('utf-8').strip()
            res = f"STDOUT: {output}\nSTDERR: {error}"
            
            if subprocess_result.returncode != 0:
                res += f"Process exited with code {subprocess_result.returncode}"
            if len(output) == 0:
                return "No output produced."
            
            return res
        
        except Exception as e:
            return f'Error: executing Python file: {str(e)}'

    except Exception as e:
        return f'Error: {str(e)}'