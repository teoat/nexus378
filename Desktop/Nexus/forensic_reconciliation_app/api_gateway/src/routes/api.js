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

/**
 * @swagger
 * /api/health:
 *   get:
 *     summary: Health check endpoint
 *     description: Returns the health status of the API gateway.
 *     tags: [Health]
 *     responses:
 *       200:
 *         description: API is healthy.
 *         content:
 *           application/json:
 *             schema:
 *               type: object
 *               properties:
 *                 status:
 *                   type: string
 *                   example: OK
 *                 timestamp:
 *                   type: string
 *                   format: date-time
 */
router.get('/health', (req, res) => {
  res.json({
    status: 'OK',
    timestamp: new Date().toISOString(),
    service: 'Forensic Reconciliation API',
    version: '1.0.0'
  });
});

/**
 * @swagger
 * tags:
 *   name: Authentication
 *   description: User authentication and profile management
 */

/**
 * @swagger
 * /api/auth/login:
 *   post:
 *     summary: User login
 *     description: Authenticate a user and receive JWT tokens.
 *     tags: [Authentication]
 *     requestBody:
 *       required: true
 *       content:
 *         application/json:
 *           schema:
 *             type: object
 *             properties:
 *               email:
 *                 type: string
 *                 format: email
 *               password:
 *                 type: string
 *                 format: password
 *     responses:
 *       200:
 *         description: Successful login.
 *       401:
 *         description: Invalid credentials.
 */

// Authentication routes (stricter rate limiting)
router.use('/auth', rateLimiters.auth);
router.post('/auth/login', validate(loginSchema), require('./controllers/authController').login);
router.post('/auth/register', require('./controllers/authController').register);
router.post('/auth/refresh', require('./controllers/authController').refreshToken);
router.post('/auth/logout', authenticateToken, require('./controllers/authController').logout);
router.get('/auth/profile', authenticateToken, require('./controllers/authController').getProfile);

/**
 * @swagger
 * /api/v1/ai/reconciliation/process:
 *   post:
 *     summary: Process a batch of records for reconciliation
 *     description: Submits a batch of records to the AI reconciliation agent.
 *     tags: [AI Services]
 *     security:
 *       - bearerAuth: []
 *     requestBody:
 *       required: true
 *       content:
 *         application/json:
 *           schema:
 *             type: object
 *             properties:
 *               records:
 *                 type: array
 *                 items:
 *                   type: object
 *     responses:
 *       200:
 *         description: Batch accepted for processing.
 *       401:
 *         description: Unauthorized.
 */

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


