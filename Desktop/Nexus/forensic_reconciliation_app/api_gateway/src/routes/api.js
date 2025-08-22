const express = require('express');
const { authenticateToken, requireRole } = require('../middleware/auth');
const { createRateLimiters } = require('../middleware/security');

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
router.post('/auth/login', require('./controllers/authController').login);
router.post('/auth/register', require('./controllers/authController').register);
router.post('/auth/refresh', require('./controllers/authController').refreshToken);
router.post('/auth/logout', authenticateToken, require('./controllers/authController').logout);
router.get('/auth/profile', authenticateToken, require('./controllers/authController').getProfile);

// User management routes
router.use('/users', authenticateToken);
router.get('/users', requireRole(['ADMIN', 'ANALYST']), require('./controllers/userController').getUsers);
router.get('/users/:id', requireRole(['ADMIN', 'ANALYST']), require('./controllers/userController').getUser);
router.post('/users', requireRole(['ADMIN']), require('./controllers/userController').createUser);
router.put('/users/:id', requireRole(['ADMIN']), require('./controllers/userController').updateUser);
router.delete('/users/:id', requireRole(['ADMIN']), require('./controllers/userController').deleteUser);
router.patch('/users/:id/status', requireRole(['ADMIN']), require('./controllers/userController').changeUserStatus);

// Transaction routes
router.use('/transactions', authenticateToken);
router.get('/transactions', requireRole(['ADMIN', 'ANALYST', 'INVESTIGATOR']), require('./controllers/transactionController').getTransactions);
router.get('/transactions/:id', requireRole(['ADMIN', 'ANALYST', 'INVESTIGATOR']), require('./controllers/transactionController').getTransaction);
router.post('/transactions', requireRole(['ADMIN', 'ANALYST']), require('./controllers/transactionController').createTransaction);
router.put('/transactions/:id', requireRole(['ADMIN', 'ANALYST']), require('./controllers/transactionController').updateTransaction);
router.patch('/transactions/:id/suspicious', requireRole(['ADMIN', 'ANALYST', 'INVESTIGATOR']), require('./controllers/transactionController').markSuspicious);
router.get('/transactions/account/:accountNumber', requireRole(['ADMIN', 'ANALYST', 'INVESTIGATOR']), require('./controllers/transactionController').getTransactionsByAccount);

// Fraud detection routes
router.use('/fraud', authenticateToken);
router.get('/fraud/indicators', requireRole(['ADMIN', 'ANALYST', 'INVESTIGATOR']), require('./controllers/fraudController').getFraudIndicators);
router.get('/fraud/indicators/:id', requireRole(['ADMIN', 'ANALYST', 'INVESTIGATOR']), require('./controllers/fraudController').getFraudIndicator);
router.post('/fraud/indicators', requireRole(['ADMIN', 'ANALYST', 'INVESTIGATOR']), require('./controllers/fraudController').createFraudIndicator);
router.put('/fraud/indicators/:id', requireRole(['ADMIN', 'ANALYST']), require('./controllers/fraudController').updateFraudIndicator);
router.get('/fraud/patterns', requireRole(['ADMIN', 'ANALYST', 'INVESTIGATOR']), require('./controllers/fraudController').getFraudPatterns);
router.post('/fraud/patterns/analyze', requireRole(['ADMIN', 'ANALYST', 'INVESTIGATOR']), require('./controllers/fraudController').analyzePatterns);

// Risk assessment routes
router.use('/risk', authenticateToken);
router.get('/risk/assessments', requireRole(['ADMIN', 'ANALYST', 'INVESTIGATOR']), require('./controllers/riskController').getRiskAssessments);
router.get('/risk/assessments/:entityId', requireRole(['ADMIN', 'ANALYST', 'INVESTIGATOR']), require('./controllers/riskController').getRiskAssessment);
router.post('/risk/assessments', requireRole(['ADMIN', 'ANALYST']), require('./controllers/riskController').createRiskAssessment);
router.put('/risk/assessments/:entityId', requireRole(['ADMIN', 'ANALYST']), require('./controllers/riskController').updateRiskAssessment);
router.get('/risk/scores', requireRole(['ADMIN', 'ANALYST', 'INVESTIGATOR']), require('./controllers/riskController').getRiskScores);
router.post('/risk/scores/calculate', requireRole(['ADMIN', 'ANALYST']), require('./controllers/riskController').calculateRiskScore);

// Evidence processing routes
router.use('/evidence', authenticateToken);
router.get('/evidence/files', requireRole(['ADMIN', 'ANALYST', 'INVESTIGATOR']), require('./controllers/evidenceController').getEvidenceFiles);
router.get('/evidence/files/:id', requireRole(['ADMIN', 'ANALYST', 'INVESTIGATOR']), require('./controllers/evidenceController').getEvidenceFile);
router.post('/evidence/files/upload', rateLimiters.upload, requireRole(['ADMIN', 'ANALYST', 'INVESTIGATOR']), require('./controllers/evidenceController').uploadEvidenceFile);
router.post('/evidence/files/:id/process', requireRole(['ADMIN', 'ANALYST']), require('./controllers/evidenceController').processEvidenceFile);
router.get('/evidence/files/:id/metadata', requireRole(['ADMIN', 'ANALYST', 'INVESTIGATOR']), require('./controllers/evidenceController').getFileMetadata);
router.get('/evidence/files/:id/hash', requireRole(['ADMIN', 'ANALYST', 'INVESTIGATOR']), require('./controllers/evidenceController').getFileHash);

// Reconciliation routes
router.use('/reconciliation', authenticateToken);
router.get('/reconciliation/jobs', requireRole(['ADMIN', 'ANALYST', 'INVESTIGATOR']), require('./controllers/reconciliationController').getReconciliationJobs);
router.get('/reconciliation/jobs/:id', requireRole(['ADMIN', 'ANALYST', 'INVESTIGATOR']), require('./controllers/reconciliationController').getReconciliationJob);
router.post('/reconciliation/jobs', requireRole(['ADMIN', 'ANALYST']), require('./controllers/reconciliationController').createReconciliationJob);
router.post('/reconciliation/jobs/:id/start', requireRole(['ADMIN', 'ANALYST']), require('./controllers/reconciliationController').startReconciliationJob);
router.post('/reconciliation/jobs/:id/stop', requireRole(['ADMIN', 'ANALYST']), require('./controllers/reconciliationController').stopReconciliationJob);
router.get('/reconciliation/jobs/:id/results', requireRole(['ADMIN', 'ANALYST', 'INVESTIGATOR']), require('./controllers/reconciliationController').getJobResults);
router.get('/reconciliation/jobs/:id/status', requireRole(['ADMIN', 'ANALYST', 'INVESTIGATOR']), require('./controllers/reconciliationController').getJobStatus);

// Analytics and reporting routes
router.use('/analytics', authenticateToken);
router.get('/analytics/dashboard', requireRole(['ADMIN', 'ANALYST', 'INVESTIGATOR']), require('./controllers/analyticsController').getDashboard);
router.get('/analytics/transactions/summary', requireRole(['ADMIN', 'ANALYST', 'INVESTIGATOR']), require('./controllers/analyticsController').getTransactionSummary);
router.get('/analytics/fraud/trends', requireRole(['ADMIN', 'ANALYST', 'INVESTIGATOR']), require('./controllers/analyticsController').getFraudTrends);
router.get('/analytics/risk/distribution', requireRole(['ADMIN', 'ANALYST', 'INVESTIGATOR']), require('./controllers/analyticsController').getRiskDistribution);
router.post('/analytics/reports/generate', requireRole(['ADMIN', 'ANALYST']), require('./controllers/analyticsController').generateReport);
router.get('/analytics/reports/:id', requireRole(['ADMIN', 'ANALYST', 'INVESTIGATOR']), require('./controllers/analyticsController').getReport);

// System monitoring routes
router.use('/monitoring', authenticateToken);
router.get('/monitoring/health', requireRole(['ADMIN']), require('./controllers/monitoringController').getSystemHealth);
router.get('/monitoring/performance', requireRole(['ADMIN']), require('./controllers/monitoringController').getPerformanceMetrics);
router.get('/monitoring/logs', requireRole(['ADMIN']), require('./controllers/monitoringController').getSystemLogs);
router.get('/monitoring/alerts', requireRole(['ADMIN', 'ANALYST']), require('./controllers/monitoringController').getSystemAlerts);
router.post('/monitoring/alerts/:id/acknowledge', requireRole(['ADMIN', 'ANALYST']), require('./controllers/monitoringController').acknowledgeAlert);

// Webhook endpoints
router.use('/webhooks', rateLimiters.general);
router.post('/webhooks/banking', require('./controllers/webhookController').handleBankingWebhook);
router.post('/webhooks/crm', require('./controllers/webhookController').handleCRMWebhook);
router.post('/webhooks/fraud', require('./controllers/webhookController').handleFraudWebhook);
router.post('/webhooks/risk', require('./controllers/webhookController').handleRiskWebhook);

// File upload routes
router.use('/upload', authenticateToken, rateLimiters.upload);
router.post('/upload/evidence', requireRole(['ADMIN', 'ANALYST', 'INVESTIGATOR']), require('./controllers/uploadController').uploadEvidence);
router.post('/upload/documents', requireRole(['ADMIN', 'ANALYST']), require('./controllers/uploadController').uploadDocuments);
router.post('/upload/images', requireRole(['ADMIN', 'ANALYST', 'INVESTIGATOR']), require('./controllers/uploadController').uploadImages);

// Search and filtering routes
router.use('/search', authenticateToken);
router.get('/search/transactions', requireRole(['ADMIN', 'ANALYST', 'INVESTIGATOR']), require('./controllers/searchController').searchTransactions);
router.get('/search/users', requireRole(['ADMIN', 'ANALYST']), require('./controllers/searchController').searchUsers);
router.get('/search/evidence', requireRole(['ADMIN', 'ANALYST', 'INVESTIGATOR']), require('./controllers/searchController').searchEvidence);
router.get('/search/fraud', requireRole(['ADMIN', 'ANALYST', 'INVESTIGATOR']), require('./controllers/searchController').searchFraud);

// Export routes
router.use('/export', authenticateToken);
router.get('/export/transactions', requireRole(['ADMIN', 'ANALYST']), require('./controllers/exportController').exportTransactions);
router.get('/export/fraud-report', requireRole(['ADMIN', 'ANALYST']), require('./controllers/exportController').exportFraudReport);
router.get('/export/risk-assessment', requireRole(['ADMIN', 'ANALYST']), require('./controllers/exportController').exportRiskAssessment);
router.get('/export/evidence-summary', requireRole(['ADMIN', 'ANALYST']), require('./controllers/exportController').exportEvidenceSummary);

// Configuration routes
router.use('/config', authenticateToken);
router.get('/config/system', requireRole(['ADMIN']), require('./controllers/configController').getSystemConfig);
router.put('/config/system', requireRole(['ADMIN']), require('./controllers/configController').updateSystemConfig);
router.get('/config/features', requireRole(['ADMIN', 'ANALYST']), require('./controllers/configController').getFeatureFlags);
router.put('/config/features', requireRole(['ADMIN']), require('./controllers/configController').updateFeatureFlags);

// Audit log routes
router.use('/audit', authenticateToken);
router.get('/audit/logs', requireRole(['ADMIN']), require('./controllers/auditController').getAuditLogs);
router.get('/audit/logs/:id', requireRole(['ADMIN']), require('./controllers/auditController').getAuditLog);
router.get('/audit/activity', requireRole(['ADMIN', 'ANALYST']), require('./controllers/auditController').getUserActivity);
router.get('/audit/changes', requireRole(['ADMIN']), require('./controllers/auditController').getSystemChanges);

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


