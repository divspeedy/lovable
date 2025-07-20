import os
import json
import re

def create_safe_filename(name):
    """Converts a string into a safe format for a filename."""
    s = name.replace(' ', '_').replace('/', '_')
    s = re.sub(r'(?u)[^-\w.]', '', s)
    return s

# --- MODIFIED FUNCTION SIGNATURE ---
# It now accepts separate paths for input and output.
def aggregate_spec_from_folder(input_folder_path, output_folder_path, spec_to_find):
    """
    Scans an input directory for JSON files, and stores the aggregated results
    in a new JSON file in the specified output directory.
    """
    if not os.path.isdir(input_folder_path):
        raise ValueError(f"Error: The input folder path '{input_folder_path}' does not exist.")

    results_by_iteration = {}
    files_to_process = []
    pattern = re.compile(r'llm_output_batch_(\d+)_v3\.json')

    # Read from the INPUT folder
    for filename in os.listdir(input_folder_path):
        match = pattern.match(filename)
        if match:
            iteration_num = int(match.group(1))
            files_to_process.append((iteration_num, filename))
    
    files_to_process.sort()

    if not files_to_process:
        raise FileNotFoundError("Warning: No files matching the pattern 'llm_output_batch_*_v3.json' were found.")

    for iteration_num, filename in files_to_process:
        # Construct the full path to the source file
        file_path = os.path.join(input_folder_path, filename)
        found_spec = None
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            secondary_specs = data.get('secondary_specs', [])
            for spec in secondary_specs:
                if spec_to_find in spec.get('original_names', []):
                    found_spec = spec
                    break
        except Exception as e:
            print(f"Warning: Could not process file '{filename}'. Error: {e}")
            found_spec = {"error": f"Could not process file {filename}", "details": str(e)}

        key_name = f"Iteration {iteration_num}"
        results_by_iteration[key_name] = found_spec

    # --- CRITICAL CHANGE ---
    # Create the output file in the specified OUTPUT folder path.
    safe_name = create_safe_filename(spec_to_find)
    output_filename = f"aggregated_{safe_name}_results.json"
    output_filepath = os.path.join(output_folder_path, output_filename)

    try:
        with open(output_filepath, 'w', encoding='utf-8') as f:
            json.dump(results_by_iteration, f, indent=4)
        # Return the full path to the created file
        return output_filepath
    except Exception as e:
        raise IOError(f"Error: Could not write the output file. Error: {e}")