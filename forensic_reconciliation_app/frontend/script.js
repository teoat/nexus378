document.addEventListener('DOMContentLoaded', () => {
    const fileInput = document.getElementById('fileInput');
    const uploadButton = document.getElementById('uploadButton');
    const fileList = document.getElementById('fileList');
    const messageDiv = document.getElementById('messageDiv');
    const modeSelect = document.getElementById('modeSelect');

    let uploadedFiles = [];

    // Initialize Chart.js instances globally so they can be updated
    const ctx1 = document.getElementById('myChart1').getContext('2d');
    const myChart1 = new Chart(ctx1, {
        type: 'bar',
        data: {
            labels: [], // Will be populated dynamically
            datasets: [{
                label: 'Category Distribution',
                data: [], // Will be populated dynamically
                backgroundColor: 'rgba(75, 192, 192, 0.6)',
                borderColor: 'rgba(75, 192, 192, 1)',
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                y: {
                    beginAtZero: true
                }
            }
        }
    });

    const ctx2 = document.getElementById('myChart2').getContext('2d');
    const myChart2 = new Chart(ctx2, {
        type: 'line',
        data: {
            labels: [], // Will be populated dynamically
            datasets: [{
                label: 'Trend Over Time',
                data: [], // Will be populated dynamically
                fill: false,
                borderColor: 'rgb(255, 99, 132)',
                tension: 0.1
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                y: {
                    beginAtZero: true
                }
            }
        }
    });

    uploadButton.addEventListener('click', async () => {
        const files = fileInput.files;
        if (files.length === 0) {
            showMessage('Please select files to upload.', 'error');
            return;
        }

        const formData = new FormData();
        for (let i = 0; i < files.length; i++) {
            formData.append('files', files[i]);
        }

        const token = getToken();
        if (!token) {
            logout(); // Redirect to login if no token
            return;
        }

        try {
            const response = await fetch('http://localhost:5002/upload', {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${token}`
                },
                body: formData,
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const result = await response.json();
            uploadedFiles = [...uploadedFiles, ...result.uploadedFiles];
            displayFiles();
            showMessage(result.message, 'success');
        } catch (error) {
            console.error('Error uploading files:', error);
            showMessage(`Error uploading files: ${error.message}`, 'error');
        }
    });

    function displayFiles() {
        fileList.innerHTML = '';
        if (uploadedFiles.length === 0) {
            fileList.innerHTML = '<p>No files uploaded yet.</p>';
            return;
        }

        uploadedFiles.forEach((file, index) => {
            const fileDiv = document.createElement('div');
            fileDiv.innerHTML = `
                <span>${file.originalname} (${(file.size / 1024).toFixed(2)} KB)</span>
                <button data-index="${index}">Remove</button>
            `;
            fileList.appendChild(fileDiv);
        });

        fileList.querySelectorAll('button').forEach(button => {
            button.addEventListener('click', (event) => {
                const index = event.target.dataset.index;
                uploadedFiles.splice(index, 1);
                displayFiles();
                showMessage('File removed.', 'info');
            });
        });
    }

    function showMessage(message, type) {
        messageDiv.textContent = message;
        messageDiv.className = `message ${type}`;
        messageDiv.style.display = 'block';
        setTimeout(() => {
            messageDiv.style.display = 'none';
        }, 5000);
    }

    modeSelect.addEventListener('change', async (event) => {
        const selectedMode = event.target.value;
        await sendModeToBackend(selectedMode);
    });

    async function sendModeToBackend(mode) {
        const token = getToken();
        if (!token) {
            logout(); // Redirect to login if no token
            return;
        }

        try {
            const response = await fetch('http://localhost:5002/set-mode', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${token}`
                },
                body: JSON.stringify({ mode }),
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const result = await response.json();
            showMessage(result.message, 'success');

            if (mode === 'Extreme') {
                await initiateExtremeModeProcessing();
            }

            // After setting mode, fetch and update visualizations
            await fetchAndRenderVisualizations(mode);

        } catch (error) {
            console.error('Error setting mode:', error);
            showMessage(`Error setting mode: ${error.message}`, 'error');
        }
    }

    async function initiateExtremeModeProcessing() {
        const token = getToken();
        if (!token) {
            logout(); // Redirect to login if no token
            return;
        }

        try {
            showMessage('Initiating Extreme mode processing...', 'info');
            const response = await fetch('http://localhost:5002/process-file-extreme', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${token}`
                },
                body: JSON.stringify({ files: uploadedFiles.map(f => f.originalname) }), // Send file names for processing
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const result = await response.json();
            showMessage(result.status + ' ' + result.details, 'success');
            console.log('Extreme mode processing result:', result);

        } catch (error) {
            console.error('Error initiating Extreme mode processing:', error);
            showMessage(`Error initiating Extreme mode processing: ${error.message}`, 'error');
        }
    }

    async function fetchAndRenderVisualizations(mode) {
        const token = getToken();
        if (!token) {
            logout(); // Redirect to login if no token
            return;
        }

        try {
            showMessage(`Fetching visualization data for ${mode} mode...`, 'info');
            const response = await fetch(`http://localhost:5002/get-visualization-data?mode=${mode}`, {
                headers: {
                    'Authorization': `Bearer ${token}`
                }
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const data = await response.json();
            console.log('Visualization data received:', data);

            // Update Chart 1 (Bar Chart)
            myChart1.data.labels = data.chart1.labels;
            myChart1.data.datasets[0].data = data.chart1.data;
            myChart1.data.datasets[0].label = data.chart1.label || 'Category Distribution';
            myChart1.update();

            // Update Chart 2 (Line Chart)
            myChart2.data.labels = data.chart2.labels;
            myChart2.data.datasets[0].data = data.chart2.data;
            myChart2.data.datasets[0].label = data.chart2.label || 'Trend Over Time';
            myChart2.update();

            showMessage('Visualizations updated successfully!', 'success');

        } catch (error) {
            console.error('Error fetching or rendering visualizations:', error);
            showMessage(`Error fetching or rendering visualizations: ${error.message}`, 'error');
        }
    }

    // Function to get JWT token from localStorage
    function getToken() {
        return localStorage.getItem('token');
    }

    // Function to handle logout
    function logout() {
        localStorage.removeItem('token');
        window.location.href = 'auth.html';
    }

    // Event listener for logout button
    const logoutButton = document.getElementById('logoutButton');
    if (logoutButton) {
        logoutButton.addEventListener('click', logout);
    }

    // Initial display of files (if any were pre-loaded or persisted)
    displayFiles();
});