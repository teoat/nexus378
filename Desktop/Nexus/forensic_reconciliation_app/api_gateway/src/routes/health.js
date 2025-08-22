const express = require('express');
const { asyncHandler } = require('../middleware/errorHandler');
const { healthCheck } = require('../database/connection');
const metricsCollector = require('../monitoring/metrics');
const config = require('../config');

const router = express.Router();

/**
 * Basic health check endpoint
 */
router.get('/', asyncHandler(async (req, res) => {
  const startTime = Date.now();
  
  try {
    // Basic system health
    const systemHealth = {
      status: 'healthy',
      timestamp: new Date().toISOString(),
      uptime: process.uptime(),
      environment: config.nodeEnv,
      version: process.env.npm_package_version || '1.0.0'
    };

    res.status(200).json({
      success: true,
      data: systemHealth
    });
  } catch (error) {
    res.status(500).json({
      success: false,
      error: {
        message: 'Health check failed',
        statusCode: 500
      }
    });
  }
}));

/**
 * Detailed health check with database connections
 */
router.get('/detailed', asyncHandler(async (req, res) => {
  const startTime = Date.now();
  
  try {
    // Check database connections
    const dbHealth = await healthCheck();
    
    // Get system metrics
    const metrics = metricsCollector.getHealthSummary();
    
    // Calculate response time
    const responseTime = Date.now() - startTime;
    
    const detailedHealth = {
      status: metrics.status,
      timestamp: new Date().toISOString(),
      responseTime: `${responseTime}ms`,
      uptime: process.uptime(),
      environment: config.nodeEnv,
      version: process.env.npm_package_version || '1.0.0',
      system: {
        nodeVersion: process.version,
        platform: process.platform,
        arch: process.arch,
        memory: {
          used: Math.round(process.memoryUsage().heapUsed / 1024 / 1024),
          total: Math.round(process.memoryUsage().heapTotal / 1024 / 1024),
          external: Math.round(process.memoryUsage().external / 1024 / 1024)
        },
        cpu: metrics.system.cpu,
        memory: metrics.system.memory
      },
      database: {
        mongo: {
          status: dbHealth.mongo,
          responseTime: dbHealth.mongo === 'healthy' ? 'OK' : 'N/A'
        },
        redis: {
          status: dbHealth.redis,
          responseTime: dbHealth.redis === 'healthy' ? 'OK' : 'N/A'
        }
      },
      metrics: {
        requests: metrics.requests,
        responseTime: metrics.responseTime,
        cache: metrics.cache
      }
    };

    // Set appropriate status code based on health
    const statusCode = detailedHealth.status === 'healthy' ? 200 : 
                      detailedHealth.status === 'warning' ? 200 : 503;

    res.status(statusCode).json({
      success: true,
      data: detailedHealth
    });
  } catch (error) {
    console.error('Detailed health check failed:', error);
    
    res.status(503).json({
      success: false,
      error: {
        message: 'Health check failed',
        statusCode: 503,
        details: error.message
      }
    });
  }
}));

/**
 * Database-specific health check
 */
router.get('/database', asyncHandler(async (req, res) => {
  try {
    const dbHealth = await healthCheck();
    
    const overallStatus = (dbHealth.mongo === 'healthy' && dbHealth.redis === 'healthy') 
      ? 'healthy' : 'unhealthy';
    
    const statusCode = overallStatus === 'healthy' ? 200 : 503;
    
    res.status(statusCode).json({
      success: true,
      data: {
        status: overallStatus,
        timestamp: new Date().toISOString(),
        services: {
          mongo: {
            status: dbHealth.mongo,
            responseTime: dbHealth.mongo === 'healthy' ? 'OK' : 'N/A'
          },
          redis: {
            status: dbHealth.redis,
            responseTime: dbHealth.redis === 'healthy' ? 'OK' : 'N/A'
          }
        }
      }
    });
  } catch (error) {
    console.error('Database health check failed:', error);
    
    res.status(503).json({
      success: false,
      error: {
        message: 'Database health check failed',
        statusCode: 503,
        details: error.message
      }
    });
  }
}));

/**
 * System metrics endpoint
 */
router.get('/metrics', asyncHandler(async (req, res) => {
  try {
    const metrics = metricsCollector.getMetrics();
    
    res.status(200).json({
      success: true,
      data: metrics
    });
  } catch (error) {
    console.error('Metrics retrieval failed:', error);
    
    res.status(500).json({
      success: false,
      error: {
        message: 'Metrics retrieval failed',
        statusCode: 500,
        details: error.message
      }
    });
  }
}));

/**
 * Readiness probe for Kubernetes
 */
router.get('/ready', asyncHandler(async (req, res) => {
  try {
    const dbHealth = await healthCheck();
    const metrics = metricsCollector.getHealthSummary();
    
    // Check if the service is ready to handle requests
    const isReady = dbHealth.mongo === 'healthy' && 
                   dbHealth.redis === 'healthy' && 
                   metrics.status !== 'critical';
    
    if (isReady) {
      res.status(200).json({
        success: true,
        data: {
          status: 'ready',
          timestamp: new Date().toISOString()
        }
      });
    } else {
      res.status(503).json({
        success: false,
        error: {
          message: 'Service not ready',
          statusCode: 503,
          details: {
            mongo: dbHealth.mongo,
            redis: dbHealth.redis,
            system: metrics.status
          }
        }
      });
    }
  } catch (error) {
    console.error('Readiness check failed:', error);
    
    res.status(503).json({
      success: false,
      error: {
        message: 'Readiness check failed',
        statusCode: 503,
        details: error.message
      }
    });
  }
}));

/**
 * Liveness probe for Kubernetes
 */
router.get('/live', asyncHandler(async (req, res) => {
  try {
    // Simple liveness check - just verify the process is running
    res.status(200).json({
      success: true,
      data: {
        status: 'alive',
        timestamp: new Date().toISOString(),
        uptime: process.uptime(),
        pid: process.pid
      }
    });
  } catch (error) {
    console.error('Liveness check failed:', error);
    
    res.status(503).json({
      success: false,
      error: {
        message: 'Liveness check failed',
        statusCode: 503,
        details: error.message
      }
    });
  }
}));

/**
 * Feature flags status
 */
router.get('/features', asyncHandler(async (req, res) => {
  try {
    const features = {
      timestamp: new Date().toISOString(),
      features: config.features,
      environment: config.nodeEnv
    };
    
    res.status(200).json({
      success: true,
      data: features
    });
  } catch (error) {
    console.error('Features check failed:', error);
    
    res.status(500).json({
      success: false,
      error: {
        message: 'Features check failed',
        statusCode: 500,
        details: error.message
      }
    });
  }
}));

/**
 * Configuration status (non-sensitive)
 */
router.get('/config', asyncHandler(async (req, res) => {
  try {
    const safeConfig = {
      timestamp: new Date().toISOString(),
      environment: config.nodeEnv,
      port: config.port,
      database: {
        url: config.database.url.includes('localhost') ? config.database.url : '[REDACTED]',
        options: {
          maxPoolSize: config.database.options.maxPoolSize,
          serverSelectionTimeoutMS: config.database.options.serverSelectionTimeoutMS
        }
      },
      redis: {
        host: config.redis.host,
        port: config.redis.port,
        db: config.redis.db
      },
      rateLimit: {
        windowMs: config.rateLimit.windowMs,
        max: config.rateLimit.max
      },
      upload: {
        maxFileSize: config.upload.maxFileSize,
        allowedFileTypes: config.upload.allowedFileTypes
      },
      monitoring: {
        enabled: config.monitoring.enabled,
        metricsPort: config.monitoring.metricsPort
      }
    };
    
    res.status(200).json({
      success: true,
      data: safeConfig
    });
  } catch (error) {
    console.error('Config check failed:', error);
    
    res.status(500).json({
      success: false,
      error: {
        message: 'Config check failed',
        statusCode: 500,
        details: error.message
      }
    });
  }
}));

module.exports = router;


