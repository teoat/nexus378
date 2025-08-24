const express = require('express');
const bodyParser = require('body-parser');
const cors = require('cors');
const bcrypt = require('bcrypt');
const jwt = require('jsonwebtoken');

const app = express();
const PORT = 5002;

// Middleware
app.use(cors());
app.use(bodyParser.json());
app.use(express.static(__dirname + '/../frontend')); // Serve static files from the frontend directory

// In-memory user store (for demonstration purposes)
const users = [];
const SECRET_KEY = 'your_jwt_secret_key'; // Replace with a strong, environment-variable-based secret in production

// Helper function to generate dummy data for charts
const generateDummyChartData = (mode) => {
    let labels, data1, data2;

    switch (mode) {
        case 'guided':
            labels = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'];
            data1 = [65, 59, 80, 81, 56, 55];
            data2 = [28, 48, 40, 19, 86, 27];
            break;
        case 'eco':
            labels = ['Q1', 'Q2', 'Q3', 'Q4'];
            data1 = [30, 45, 25, 50];
            data2 = [40, 30, 50, 20];
            break;
        case 'extreme':
            labels = ['Week 1', 'Week 2', 'Week 3', 'Week 4', 'Week 5'];
            data1 = [120, 150, 130, 160, 140];
            data2 = [80, 90, 70, 100, 85];
            break;
        default:
            labels = ['Item A', 'Item B', 'Item C', 'Item D'];
            data1 = [10, 20, 15, 25];
            data2 = [5, 15, 10, 20];
    }

    return {
        chart1: {
            labels: labels,
            datasets: [{
                label: 'Dataset 1',
                data: data1,
                backgroundColor: 'rgba(26, 188, 156, 0.6)',
                borderColor: 'rgba(26, 188, 156, 1)',
                borderWidth: 1
            }]
        },
        chart2: {
            labels: labels,
            datasets: [{
                label: 'Dataset 2',
                data: data2,
                backgroundColor: 'rgba(52, 152, 219, 0.6)',
                borderColor: 'rgba(52, 152, 219, 1)',
                borderWidth: 1,
                fill: false
            }]
        }
    };
};

// Authentication Endpoints
app.post('/register', async (req, res) => {
    const { username, password } = req.body;

    if (!username || !password) {
        return res.status(400).json({ message: 'Username and password are required' });
    }

    if (users.find(user => user.username === username)) {
        return res.status(409).json({ message: 'User already exists' });
    }

    try {
        const hashedPassword = await bcrypt.hash(password, 10);
        users.push({ username, password: hashedPassword });
        console.log('Registered users:', users); // For debugging
        res.status(201).json({ message: 'User registered successfully' });
    } catch (error) {
        res.status(500).json({ message: 'Error registering user', error: error.message });
    }
});

app.post('/login', async (req, res) => {
    const { username, password } = req.body;

    if (!username || !password) {
        return res.status(400).json({ message: 'Username and password are required' });
    }

    const user = users.find(u => u.username === username);
    if (!user) {
        return res.status(401).json({ message: 'Invalid credentials' });
    }

    try {
        const isPasswordValid = await bcrypt.compare(password, user.password);
        if (!isPasswordValid) {
            return res.status(401).json({ message: 'Invalid credentials' });
        }

        const token = jwt.sign({ username: user.username }, SECRET_KEY, { expiresIn: '1h' });
        res.status(200).json({ message: 'Login successful', token });
    } catch (error) {
        res.status(500).json({ message: 'Error logging in', error: error.message });
    }
});

// Middleware to protect routes
const authenticateToken = (req, res, next) => {
    const authHeader = req.headers['authorization'];
    const token = authHeader && authHeader.split(' ')[1];

    if (token == null) return res.sendStatus(401); // No token

    jwt.verify(token, SECRET_KEY, (err, user) => {
        if (err) return res.sendStatus(403); // Invalid token
        req.user = user;
        next();
    });
};

// API endpoint for file upload
app.post('/upload', authenticateToken, (req, res) => {
    // In a real application, handle file upload here
    // For now, just acknowledge receipt
    res.json({ message: 'File upload initiated (backend placeholder)', filename: req.body.filename });
});

// API endpoint to set the mode
app.post('/set-mode', authenticateToken, (req, res) => {
    const { mode } = req.body;
    console.log(`Mode set to: ${mode}`);
    // In a real application, this would interact with the FrenlyMetaAgent
    res.json({ message: `Mode "${mode}" received by backend.` });
});

// Placeholder for Extreme Mode processing
app.post('/process-file-extreme', authenticateToken, (req, res) => {
    const { filename } = req.body;
    console.log(`Initiating Extreme Mode processing for: ${filename}`);
    // Simulate complex AI processing
    setTimeout(() => {
        res.json({ message: `Extreme Mode processing complete for ${filename}.` });
    }, 3000);
});

// API endpoint to get visualization data
app.get('/get-visualization-data', authenticateToken, (req, res) => {
    const { mode } = req.query;
    const data = generateDummyChartData(mode);
    res.json(data);
});

// Serve the authentication page as the default route
app.get('/', (req, res) => {
    res.sendFile('auth.html', { root: __dirname + '/../frontend' });
});

// Start the server
app.listen(PORT, () => {
    console.log(`Server running on http://localhost:${PORT}`);
});