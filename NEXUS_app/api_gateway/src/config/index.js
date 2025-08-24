require('dotenv').config();

const config = {
  // Server configuration
  port: process.env.PORT || 3000,
  nodeEnv: process.env.NODE_ENV || 'development',
  
  // JWT configuration
  jwtSecret: process.env.JWT_SECRET || 'your-super-secret-jwt-key-change-in-production',
  jwtExpiresIn: process.env.JWT_EXPIRES_IN || '24h',
  jwtIssuer: process.env.JWT_ISSUER || 'forensic-reconciliation-api',
  jwtAudience: process.env.JWT_AUDIENCE || 'forensic-reconciliation-client',
  
  // CORS configuration
  corsOrigins: process.env.ALLOWED_ORIGINS 
    ? process.env.ALLOWED_ORIGINS.split(',')
    : ['http://localhost:3000', 'http://localhost:3001', 'http://localhost:8080'],
  
  // Database configuration
  database: {
    url: process.env.DATABASE_URL || 'mongodb://localhost:27017/NEXUS',
    options: {
      useNewUrlParser: true,
      useUnifiedTopology: true,
      maxPoolSize: 10,
      serverSelectionTimeoutMS: 5000,
      socketTimeoutMS: 45000,
    }
  },
  
  // Redis configuration
  redis: {
    host: process.env.REDIS_HOST || 'localhost',
    port: process.env.REDIS_PORT || 6379,
    password: process.env.REDIS_PASSWORD,
    db: process.env.REDIS_DB || 0,
    keyPrefix: 'NEXUS:'
  },
  
  // Logging configuration
  logging: {
    level: process.env.LOG_LEVEL || 'info',
    format: process.env.LOG_FORMAT || 'combined',
    file: process.env.LOG_FILE || 'logs/api-gateway.log'
  },
  
  // Rate limiting configuration
  rateLimit: {
    windowMs: 15 * 60 * 1000, // 15 minutes
    max: parseInt(process.env.RATE_LIMIT_MAX) || 100,
    message: 'Too many requests from this IP, please try again later.'
  },
  
  // File upload configuration
  upload: {
    maxFileSize: parseInt(process.env.MAX_FILE_SIZE) || 10 * 1024 * 1024, // 10MB
    allowedFileTypes: process.env.ALLOWED_FILE_TYPES 
      ? process.env.ALLOWED_FILE_TYPES.split(',')
      : ['jpg', 'jpeg', 'png', 'gif', 'pdf', 'doc', 'docx', 'txt', 'csv'],
    uploadDir: process.env.UPLOAD_DIR || 'uploads/'
  },
  
  // Security configuration
  security: {
    bcryptRounds: parseInt(process.env.BCRYPT_ROUNDS) || 12,
    sessionTimeout: parseInt(process.env.SESSION_TIMEOUT) || 24 * 60 * 60 * 1000, // 24 hours
    maxLoginAttempts: parseInt(process.env.MAX_LOGIN_ATTEMPTS) || 5,
    lockoutDuration: parseInt(process.env.LOCKOUT_DURATION) || 15 * 60 * 1000 // 15 minutes
  },
  
  // External services configuration
  services: {
    banking: {
      baseUrl: process.env.BANKING_SERVICE_URL || 'http://localhost:3001',
      apiKey: process.env.BANKING_SERVICE_API_KEY,
      timeout: parseInt(process.env.BANKING_SERVICE_TIMEOUT) || 30000
    },
    crm: {
      baseUrl: process.env.CRM_SERVICE_URL || 'http://localhost:3002',
      apiKey: process.env.CRM_SERVICE_API_KEY,
      timeout: parseInt(process.env.CRM_SERVICE_TIMEOUT) || 30000
    },
    fraud: {
      baseUrl: process.env.FRAUD_SERVICE_URL || 'http://localhost:3003',
      apiKey: process.env.FRAUD_SERVICE_API_KEY,
      timeout: parseInt(process.env.FRAUD_SERVICE_TIMEOUT) || 30000
    },
    risk: {
      baseUrl: process.env.RISK_SERVICE_URL || 'http://localhost:3004',
      apiKey: process.env.RISK_SERVICE_API_KEY,
      timeout: parseInt(process.env.RISK_SERVICE_TIMEOUT) || 30000
    }
  },
  
  // Webhook configuration
  webhooks: {
    banking: {
      secret: process.env.BANKING_WEBHOOK_SECRET,
      endpoint: '/webhooks/banking'
    },
    crm: {
      secret: process.env.CRM_WEBHOOK_SECRET,
      endpoint: '/webhooks/crm'
    },
    fraud: {
      secret: process.env.FRAUD_WEBHOOK_SECRET,
      endpoint: '/webhooks/fraud'
    },
    risk: {
      secret: process.env.RISK_WEBHOOK_SECRET,
      endpoint: '/webhooks/risk'
    }
  },
  
  // Monitoring configuration
  monitoring: {
    enabled: process.env.MONITORING_ENABLED === 'true',
    metricsPort: parseInt(process.env.METRICS_PORT) || 9090,
    healthCheckInterval: parseInt(process.env.HEALTH_CHECK_INTERVAL) || 30000, // 30 seconds
    alertThresholds: {
      cpu: parseFloat(process.env.CPU_THRESHOLD) || 80.0,
      memory: parseFloat(process.env.MEMORY_THRESHOLD) || 80.0,
      responseTime: parseInt(process.env.RESPONSE_TIME_THRESHOLD) || 1000 // 1 second
    }
  },
  
  // Feature flags
  features: {
    graphql: process.env.FEATURE_GRAPHQL !== 'false',
    websockets: process.env.FEATURE_WEBSOCKETS !== 'false',
    fileUpload: process.env.FEATURE_FILE_UPLOAD !== 'false',
    realTimeUpdates: process.env.FEATURE_REALTIME_UPDATES !== 'false',
    advancedAnalytics: process.env.FEATURE_ADVANCED_ANALYTICS !== 'false'
  }
};

// Environment-specific overrides
if (config.nodeEnv === 'production') {
  config.security.bcryptRounds = 14;
  config.rateLimit.max = 50;
  config.monitoring.enabled = true;
}

if (config.nodeEnv === 'test') {
  config.database.url = process.env.TEST_DATABASE_URL || 'mongodb://localhost:27017/forensic_reconciliation_test';
  config.redis.db = 1;
  config.logging.level = 'error';
}

// Validation
const requiredEnvVars = [
  'JWT_SECRET'
];

if (config.nodeEnv === 'production') {
  requiredEnvVars.push(
    'DATABASE_URL',
    'REDIS_PASSWORD'
  );
}

const missingVars = requiredEnvVars.filter(varName => !process.env[varName]);

if (missingVars.length > 0) {
  console.error('Missing required environment variables:', missingVars);
  if (config.nodeEnv === 'production') {
    process.exit(1);
  }
}

module.exports = config;


