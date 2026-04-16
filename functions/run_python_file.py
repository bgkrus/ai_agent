import os
import subprocess
from google.genai import types

schema_run_python_file = types.FunctionDeclaration(
    name="run_python_file",
    description="Runs a pyhton file with the python3 interpreter. Accepts additional CLI args as an optional array.",
    parameters=types.Schema(
        type=types.Type.OBJECT,
        properties={
            "file_path": types.Schema(
                type=types.Type.STRING,
                description="The file to run, relative to the working directory.",
            ),
            "args": types.Schema(
                type=types.Type.ARRAY,
                items=types.Schema(
                    type=types.Type.STRING,
                ),
                description="An option array of string to be used as the CLI args for the Python file.",
            ),
        },
        required=["file_path"],
    ),
)

def run_python_file(working_directory, file_path, args=None):
    try:   
        working_dir_abs = os.path.abspath(working_directory)
        target_dir = os.path.normpath(os.path.join(working_dir_abs, file_path))
        valid_target_dir = os.path.commonpath([working_dir_abs, target_dir]) == working_dir_abs
        
        if not valid_target_dir:
            return f'Error: Cannot execute "{file_path}" as it is outside the permitted working directory'
        
        if not os.path.isfile(target_dir):
            return f'Error: "{file_path}" does not exist or is not a regular file'
        
        if not target_dir.endswith(".py"):
            return f'Error: "{file_path}" is not a Python file'
        
        command = ["python", target_dir]
        if args: 
            command.extend(args)
        run_command = subprocess.run(command, cwd = working_dir_abs, capture_output=True , text=True, timeout=30)

        output = []

        if run_command.returncode != 0:
            output.append(f"Process exited with code {run_command.returncode}")

        if not run_command.stdout and not run_command.stderr:
            output.append("No output produced")

        if run_command.stdout:
            output.append(f"STDOUT:\n{run_command.stdout}")
        if run_command.stderr:
            output.append(f"STDERR:\n{run_command.stderr}")

        return "\n".join(output)
    except Exception as e:
        return f"Error: executing Python file: {e}"