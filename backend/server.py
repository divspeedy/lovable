from flask import Flask, request, send_from_directory, jsonify
from flask_cors import CORS
import os
import uuid
import shutil
from processing_script import aggregate_spec_from_folder

# --- App Initialization ---
app = Flask(__name__)
CORS(app)

# --- Configuration ---
# Define paths for both uploads (temporary input) and results (final output)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['RESULTS_FOLDER'] = 'results' # New config for the output directory

# Create directories if they don't exist
for folder in [app.config['UPLOAD_FOLDER'], app.config['RESULTS_FOLDER']]:
    if not os.path.exists(folder):
        os.makedirs(folder)

# --- API Endpoint ---
@app.route('/process', methods=['POST'])
def process_files_endpoint():
    """
    API endpoint to handle file uploads and processing.
    """
    # Create a unique temporary directory inside 'uploads' for the input files
    session_id = str(uuid.uuid4())
    session_folder = os.path.join(app.config['UPLOAD_FOLDER'], session_id)
    os.makedirs(session_folder)

    try:
        # --- Input Validation ---
        uploaded_files = request.files.getlist('files')
        spec_to_find = request.form.get('specNameToFind')

        if not uploaded_files:
            return jsonify({"error": "No folder/files were uploaded"}), 400
        if not spec_to_find:
            return jsonify({"error": "The 'Spec Name to Find' cannot be empty"}), 400

        # --- File Handling ---
        # Save uploaded files to the temporary session folder
        for file in uploaded_files:
            file.save(os.path.join(session_folder, os.path.basename(file.filename)))

        # --- Business Logic ---
        # Call the processing script with the input path and the output path
        result_file_path = aggregate_spec_from_folder(
            input_folder_path=session_folder,
            output_folder_path=app.config['RESULTS_FOLDER'], # Pass the results folder path
            spec_to_find=spec_to_find
        )
        
        # --- Response ---
        # Securely send the generated file from the RESULTS folder
        return send_from_directory(
            directory=app.config['RESULTS_FOLDER'], # The directory is now 'results'
            path=os.path.basename(result_file_path), # The filename of the result
            as_attachment=True
        )
    except Exception as e:
        return jsonify({"error": f"An internal error occurred: {str(e)}"}), 500
    finally:
        # --- Cleanup ---
        # The cleanup logic is now even better. It only removes the temporary
        # input folder, leaving the final file in the 'results' folder.
        if os.path.exists(session_folder):
            shutil.rmtree(session_folder)

# --- Main Entry Point ---
if __name__ == '__main__':
    app.run(debug=True, port=5000)