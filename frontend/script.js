document.addEventListener('DOMContentLoaded', () => {
    // --- Element References ---
    const specNameInput = document.getElementById('specName');
    const folderInput = document.getElementById('folderInput');
    const processBtn = document.getElementById('processBtn');
    const fileInfo = document.getElementById('file-info');
    const statusDiv = document.getElementById('status');

    // --- State ---
    let selectedFiles = [];
    const API_URL = 'http://127.0.0.1:5000/process'; // Best practice: Define API URL as a constant

    // --- Functions ---
    const updateButtonState = () => {
        processBtn.disabled = !(specNameInput.value.trim() !== '' && selectedFiles.length > 0);
    };

    const handleFolderSelection = (event) => {
        selectedFiles = Array.from(event.target.files);
        fileInfo.textContent = selectedFiles.length > 0 ? `${selectedFiles.length} files selected.` : 'No folder selected';
        updateButtonState();
    };

    const processFolder = async () => {
        // 1. Prepare UI for processing
        statusDiv.textContent = 'Processing... Please wait.';
        statusDiv.className = 'status status-processing';
        processBtn.disabled = true;

        // 2. Prepare data for the API
        const formData = new FormData();
        formData.append('specNameToFind', specNameInput.value);
        selectedFiles.forEach(file => {
            formData.append('files', file);
        });

        // 3. Call the API and handle the response
        try {
            const response = await fetch(API_URL, {
                method: 'POST',
                body: formData,
            });

            if (response.ok) {
                // Handle successful file download
                const blob = await response.blob();
                const disposition = response.headers.get('Content-Disposition');
                let filename = 'aggregated_results.json';
                if (disposition && disposition.includes('attachment')) {
                    const filenameMatch = /filename="([^"]+)"/.exec(disposition);
                    if (filenameMatch && filenameMatch[1]) filename = filenameMatch[1];
                }

                const a = document.createElement('a');
                a.href = window.URL.createObjectURL(blob);
                a.download = filename;
                document.body.appendChild(a);
                a.click();
                a.remove();
                
                statusDiv.textContent = `Success! Your file '${filename}' has been downloaded.`;
                statusDiv.className = 'status status-success';
            } else {
                // Handle server-side errors
                const errorData = await response.json();
                statusDiv.textContent = `Error: ${errorData.error}`;
                statusDiv.className = 'status status-error';
            }
        } catch (error) {
            // Handle network or connection errors
            console.error('Fetch API Error:', error);
            statusDiv.textContent = 'Connection Failed. Is the backend server running?';
            statusDiv.className = 'status status-error';
        } finally {
            // 4. Re-enable the UI
            updateButtonState();
        }
    };

    // --- Event Listeners ---
    specNameInput.addEventListener('input', updateButtonState);
    folderInput.addEventListener('change', handleFolderSelection);
    processBtn.addEventListener('click', processFolder);
});