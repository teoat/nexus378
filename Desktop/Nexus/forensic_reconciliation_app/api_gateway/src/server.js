#!/usr/bin/env node

const express = require('express');
const cors = require('cors');
const helmet = require('helmet');
const compression = require('compression');
const winston = require('winston');
const { ElasticsearchTransport } = require('winston-elasticsearch');
const rateLimit = require('express-rate-limit');
const { createServer: createHttpServer } = require('http');
const { createServer: createHttpsServer } = require('https');
const fs = require('fs');
const { WebSocketServer } = require('ws');
const swaggerJSDoc = require('swagger-jsdoc');
const swaggerUi = require('swagger-ui-express');

// Import middleware and routes
const authMiddleware = require('./middleware/auth');
const errorHandler = require('./middleware/errorHandler');
const apiRoutes = require('./routes/api');
const graphqlRoutes = require('./routes/graphql');
const { metricsRouter, recordRequest } = require('./monitoring/metrics');


// Import configuration
const config = require('./config');

// Create Express app
const app = express();

// Create HTTP or HTTPS server
let server;
if (process.env.SSL_KEY_FILE && process.env.SSL_CERT_FILE) {
  const options = {
    key: fs.readFileSync(process.env.SSL_KEY_FILE),
    cert: fs.readFileSync(process.env.SSL_CERT_FILE),
  };
  server = createHttpsServer(options, app);
} else {
  server = createHttpServer(app);
}

// Create WebSocket server
const wss = new WebSocketServer({ server });

// Security middleware
app.use(helmet({
  contentSecurityPolicy: {
    directives: {
      defaultSrc: ["'self'"],
      styleSrc: ["'self'", "'unsafe-inline'"],
      scriptSrc: ["'self'"],
      imgSrc: ["'self'", "data:", "https:"],
    },
  },
  crossOriginEmbedderPolicy: false,
}));

// CORS configuration
app.use(cors({
  origin: config.corsOrigins,
  credentials: true,
  methods: ['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'],
  allowedHeaders: ['Content-Type', 'Authorization', 'X-Requested-With'],
}));

// Rate limiting
const limiter = rateLimit({
  windowMs: 15 * 60 * 1000, // 15 minutes
  max: 100, // limit each IP to 100 requests per windowMs
  message: 'Too many requests from this IP, please try again later.',
  standardHeaders: true,
  legacyHeaders: false,
});
app.use('/api/', limiter);

// Body parsing middleware
app.use(express.json({ limit: '10mb' }));
app.use(express.urlencoded({ extended: true, limit: '10mb' }));

// Compression middleware
app.use(compression());

// Logging middleware
const logger = winston.createLogger({
  level: config.logging.level,
  format: winston.format.json(),
  transports: [
    new winston.transports.Console(),
    new ElasticsearchTransport(config.logging.elasticsearch),
  ],
});

app.use((req, res, next) => {
    res.on('finish', () => {
        logger.info({
            message: 'request',
            method: req.method,
            url: req.originalUrl,
            status: res.statusCode,
            ip: req.ip,
            userAgent: req.get('user-agent'),
        });
    });
    next();
});


// Metrics endpoint
app.use(metricsRouter);

// Record request metrics
app.use(recordRequest);

// Health check endpoint
app.get('/health', (req, res) => {
  res.status(200).json({
    status: 'OK',
    timestamp: new Date().toISOString(),
    uptime: process.uptime(),
    environment: process.env.NODE_ENV || 'development'
  });
});

// API routes
app.use('/api', apiRoutes);

// Swagger API Documentation
const swaggerOptions = {
  definition: {
    openapi: '3.0.0',
    info: {
      title: 'Forensic Reconciliation API',
      version: '1.0.0',
      description: 'API documentation for the Forensic Reconciliation + Fraud Platform',
    },
    servers: [
      {
        url: 'http://localhost:8080',
        description: 'Development server'
      },
      {
        url: 'https://api.forensic-reconciliation.com',
        description: 'Production server'
      }
    ],
    components: {
      securitySchemes: {
        bearerAuth: {
          type: 'http',
          scheme: 'bearer',
          bearerFormat: 'JWT',
        }
      }
    },
    security: [{
      bearerAuth: []
    }]
  },
  apis: ['./src/routes/*.js'],
};

const swaggerSpec = swaggerJSDoc(swaggerOptions);
app.use('/api-docs', swaggerUi.serve, swaggerUi.setup(swaggerSpec));

// GraphQL routes
app.use('/graphql', graphqlRoutes);

// WebSocket connection handling
wss.on('connection', (ws, req) => {
  console.log('New WebSocket connection established');
  
  ws.on('message', (message) => {
    try {
      const data = JSON.parse(message);
      console.log('WebSocket message received:', data);
      
      // Handle different message types
      switch (data.type) {
        case 'ping':
          ws.send(JSON.stringify({ type: 'pong', timestamp: Date.now() }));
          break;
        case 'subscribe':
          // Handle subscription logic
          ws.send(JSON.stringify({ 
            type: 'subscribed', 
            channel: data.channel,
            timestamp: Date.now() 
          }));
          break;
        default:
          ws.send(JSON.stringify({ 
            type: 'error', 
            message: 'Unknown message type',
            timestamp: Date.now() 
          }));
      }
    } catch (error) {
      console.error('WebSocket message parsing error:', error);
      ws.send(JSON.stringify({ 
        type: 'error', 
        message: 'Invalid message format',
        timestamp: Date.now() 
      }));
    }
  });
  
  ws.on('close', () => {
    console.log('WebSocket connection closed');
  });
  
  ws.on('error', (error) => {
    console.error('WebSocket error:', error);
  });
});

// Error handling middleware (must be last)
app.use(errorHandler);

// 404 handler
app.use('*', (req, res) => {
  res.status(404).json({
    error: 'Route not found',
    path: req.originalUrl,
    method: req.method,
    timestamp: new Date().toISOString()
  });
});

// Start server
const HTTP_PORT = process.env.PORT || config.port || 3000;
const HTTPS_PORT = process.env.HTTPS_PORT || 8443;

if (process.env.SSL_KEY_FILE && process.env.SSL_CERT_FILE) {
  server.listen(HTTPS_PORT, () => {
    console.log(`🚀 API Gateway server running on HTTPS port ${HTTPS_PORT}`);
    console.log(`📊 Health check: https://localhost:${HTTPS_PORT}/health`);
    console.log(`🔌 WebSocket server active on wss://localhost:${HTTPS_PORT}`);
    console.log(`🌐 Environment: ${process.env.NODE_ENV || 'development'}`);
  });
} else {
  server.listen(HTTP_PORT, () => {
    console.log(`🚀 API Gateway server running on HTTP port ${HTTP_PORT}`);
    console.log(`📊 Health check: http://localhost:${HTTP_PORT}/health`);
    console.log(`🔌 WebSocket server active on ws://localhost:${HTTP_PORT}`);
    console.log(`🌐 Environment: ${process.env.NODE_ENV || 'development'}`);
  });
}

// Graceful shutdown
process.on('SIGTERM', () => {
  console.log('SIGTERM received, shutting down gracefully');
  server.close(() => {
    console.log('Process terminated');
    process.exit(0);
  });
});

process.on('SIGINT', () => {
  console.log('SIGINT received, shutting down gracefully');
  server.close(() => {
    console.log('Process terminated');
    process.exit(0);
  });
});

module.exports = { app, server, wss };
