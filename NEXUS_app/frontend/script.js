document.addEventListener('DOMContentLoaded', () => {
    console.log("Nexus script loaded.");

    const uploadForm = document.getElementById('upload-form');
    const modeSelect = document.getElementById('mode-select');
    const messageDiv = document.getElementById('message');

    if (modeSelect) {
        modeSelect.addEventListener('change', (e) => {
            const selectedMode = e.target.value;
            await sendModeToBackend(selectedMode);
        });
    }

    if (uploadForm) {
        uploadForm.addEventListener('submit', async (e) => {
            e.preventDefault();

            const formData = new FormData(uploadForm);
            const fileInput = document.getElementById('file-upload');
            const file = fileInput.files[0];

            if (!file) {
                messageDiv.textContent = 'Please select a file to upload.';
                messageDiv.style.color = 'red';
                return;
            }

            try {
                const response = await fetch('http://localhost:5002/upload', {
                    method: 'POST',
                    body: formData,
                });

                const result = await response.json();

                if (response.ok) {
                    messageDiv.textContent = `File uploaded successfully: ${result.file.originalname}`;
                    messageDiv.style.color = 'green';
                } else {
                    messageDiv.textContent = `Error: ${result.message}`;
                    messageDiv.style.color = 'red';
                }
            } catch (error) {
                console.error('Error uploading file:', error);
                messageDiv.textContent = 'An error occurred while uploading the file. Please check the console for details.';
                messageDiv.style.color = 'red';
            }
        
            async function sendModeToBackend(mode) {
                try {
                    const response = await fetch('http://localhost:5002/set-mode', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                        },
                        body: JSON.stringify({ mode: mode }),
                    });
        
                    const result = await response.json();
        
                    if (response.ok) {
                        messageDiv.textContent = `Mode set to ${mode}: ${result.message}`;
                        messageDiv.style.color = 'green';
        
                        if (mode === 'extreme') {
                            // If Extreme mode is set, initiate advanced processing
                            await initiateExtremeModeProcessing();
                        }
                    } else {
                        messageDiv.textContent = `Error setting mode to ${mode}: ${result.message}`;
                        messageDiv.style.color = 'red';
                    }
                } catch (error) {
                    console.error('Error sending mode to backend:', error);
                    messageDiv.textContent = 'An error occurred while setting the mode. Please check the console for details.';
                    messageDiv.style.color = 'red';
                }
            }
        
            async function initiateExtremeModeProcessing() {
                try {
                    messageDiv.textContent = 'Initiating Extreme mode advanced processing...';
                    messageDiv.style.color = 'orange';
        
                    const response = await fetch('http://localhost:5002/process-file-extreme', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                        },
                        body: JSON.stringify({ /* potentially send file info here later */ }),
                    });
        
                    const result = await response.json();
        
                    if (response.ok) {
                        messageDiv.textContent = `Extreme mode processing: ${result.status}. ${result.details}`;
                        messageDiv.style.color = 'green';
                    } else {
                        messageDiv.textContent = `Error in Extreme mode processing: ${result.message}`;
                        messageDiv.style.color = 'red';
                    }
                } catch (error) {
                    console.error('Error initiating Extreme mode processing:', error);
                    messageDiv.textContent = 'An error occurred during Extreme mode processing. Please check the console for details.';
                    messageDiv.style.color = 'red';
                }
            }
        });
    }
});