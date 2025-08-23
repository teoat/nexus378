const express = require('express');
const { authenticateToken, requireRole } = require('../middleware/auth');
const { createRateLimiters } = require('../middleware/security');
const { validate } = require('../middleware/validation');
const { loginSchema } = require('../validation/authValidation');
const { proxy } = require('../proxy/proxy');

const router = express.Router();
const rateLimiters = createRateLimiters();

// Apply general rate limiting to all API routes
router.use(rateLimiters.general);

// Health check endpoint (no auth required)
router.get('/health', (req, res) => {
  res.json({
    status: 'OK',
    timestamp: new Date().toISOString(),
    service: 'Forensic Reconciliation API',
    version: '1.0.0'
  });
});

// Authentication routes (stricter rate limiting)
router.use('/auth', rateLimiters.auth);
router.post('/auth/login', validate(loginSchema), require('./controllers/authController').login);
router.post('/auth/register', require('./controllers/authController').register);
router.post('/auth/refresh', require('./controllers/authController').refreshToken);
router.post('/auth/logout', authenticateToken, require('./controllers/authController').logout);
router.get('/auth/profile', authenticateToken, require('./controllers/authController').getProfile);

// Proxy all other requests to the backend service
router.use(proxy);

// 404 handler for undefined routes
router.use('*', (req, res) => {
  res.status(404).json({
    error: 'API endpoint not found',
    code: 'ENDPOINT_NOT_FOUND',
    path: req.originalUrl,
    method: req.method,
    timestamp: new Date().toISOString()
  });
});

module.exports = router;


