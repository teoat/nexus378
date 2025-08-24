const express = require('express');
const dotenv = require('dotenv');
const cors = require('cors');
const multer = require('multer');
const path = require('path');
 
 dotenv.config();
 
 const app = express();
const port = process.env.PORT || 5000;

app.use(cors());
app.use(express.json());
app.use(express.static(path.join(__dirname, '../frontend')));

const storage = multer.diskStorage({
  destination: function (req, file, cb) {
    cb(null, 'uploads/');
  },
  filename: function (req, file, cb) {
    cb(null, Date.now() + '-' + file.originalname);
  }
});

const upload = multer({ storage: storage });

app.post('/upload', upload.single('file'), (req, res) => {
  res.send({ message: 'File uploaded successfully', file: req.file });
});

app.post('/set-mode', (req, res) => {
  const { mode } = req.body;
  console.log(`Received request to set AI mode to: ${mode}`);
  let responseMessage = `AI mode successfully set to ${mode}.`;
  if (mode === 'extreme') {
    responseMessage += ' Advanced processing capabilities are now active.';
  } else if (mode === 'eco') {
    responseMessage += ' Optimized processing for predefined formats is active.';
  } else if (mode === 'guided') {
    responseMessage += ' Step-by-step guidance for standard formats is active.';
  }
  // In a real application, this would interact with FrenlyMetaAgent
  // For now, we simulate success
  res.status(200).json({ message: responseMessage });
});

// New endpoint for Extreme mode file processing
app.post('/process-file-extreme', (req, res) => {
  console.log('Received request for Extreme mode file processing.');
  // Simulate advanced processing logic here
  // In a real scenario, this would involve:
  // 1. Receiving file data (e.g., from a multipart/form-data upload)
  // 2. Calling specialized AI agents (e.g., FraudAgent, RiskAgent)
  // 3. Performing complex data analysis, pattern recognition, predictive modeling
  // 4. Storing processed data
  // 5. Returning detailed results or status updates

  const simulatedProcessingResult = {
    status: 'Processing initiated for Extreme mode',
    details: 'Advanced fraud detection, predictive analysis, and multi-agent orchestration are underway.',
    timestamp: new Date().toISOString()
  };

  res.status(200).json(simulatedProcessingResult);
});

app.get('/', (req, res) => {
  const filePath = path.join(__dirname, '../frontend', 'ingestion.html');
  console.log(`Attempting to serve: ${filePath}`);
  res.sendFile(filePath, (err) => {
    if (err) {
      console.error('Error sending file:', err);
      res.status(500).send('Error loading page');
    }
  });
});
 
 app.listen(port, () => {
   console.log(`Server is running on port: ${port}`);
});