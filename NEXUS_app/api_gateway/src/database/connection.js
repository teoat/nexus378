const mongoose = require('mongoose');
const Redis = require('ioredis');
const config = require('../config');

/**
 * MongoDB connection
 */
let mongoConnection = null;

const connectMongo = async () => {
  try {
    if (mongoConnection) {
      return mongoConnection;
    }

    const options = {
      ...config.database.options,
      bufferCommands: false,
      bufferMaxEntries: 0,
      autoIndex: config.nodeEnv === 'development',
      serverSelectionTimeoutMS: 5000,
      heartbeatFrequencyMS: 10000,
      maxPoolSize: 10,
      minPoolSize: 2,
      maxIdleTimeMS: 30000,
      connectTimeoutMS: 10000,
      socketTimeoutMS: 45000,
      family: 4, // Use IPv4, skip trying IPv6
      keepAlive: true,
      keepAliveInitialDelay: 300000, // 5 minutes
    };

    mongoConnection = await mongoose.connect(config.database.url, options);
    
    console.log('✅ MongoDB connected successfully');
    
    // Connection event handlers
    mongoose.connection.on('error', (err) => {
      console.error('❌ MongoDB connection error:', err);
    });

    mongoose.connection.on('disconnected', () => {
      console.warn('⚠️ MongoDB disconnected');
    });

    mongoose.connection.on('reconnected', () => {
      console.log('🔄 MongoDB reconnected');
    });

    // Graceful shutdown
    process.on('SIGINT', async () => {
      try {
        await mongoose.connection.close();
        console.log('MongoDB connection closed through app termination');
        process.exit(0);
      } catch (err) {
        console.error('Error during MongoDB shutdown:', err);
        process.exit(1);
      }
    });

    return mongoConnection;
  } catch (error) {
    console.error('❌ MongoDB connection failed:', error);
    throw error;
  }
};

/**
 * Redis connection
 */
let redisClient = null;

const connectRedis = async () => {
  try {
    if (redisClient) {
      return redisClient;
    }

    const redisConfig = {
      host: config.redis.host,
      port: config.redis.port,
      password: config.redis.password,
      db: config.redis.db,
      keyPrefix: config.redis.keyPrefix,
      retryDelayOnFailover: 100,
      maxRetriesPerRequest: 3,
      lazyConnect: true,
      keepAlive: 30000,
      family: 4,
      connectTimeout: 10000,
      commandTimeout: 5000,
      retryDelayOnClusterDown: 300,
      enableOfflineQueue: false,
      maxLoadingTimeout: 10000,
      enableReadyCheck: true,
      autoResubscribe: true,
      autoResendUnfulfilledCommands: true,
      lazyConnect: false,
      showFriendlyErrorStack: config.nodeEnv === 'development'
    };

    redisClient = new Redis(redisConfig);

    redisClient.on('connect', () => {
      console.log('✅ Redis connected successfully');
    });

    redisClient.on('ready', () => {
      console.log('✅ Redis ready');
    });

    redisClient.on('error', (err) => {
      console.error('❌ Redis error:', err);
    });

    redisClient.on('close', () => {
      console.warn('⚠️ Redis connection closed');
    });

    redisClient.on('reconnecting', () => {
      console.log('🔄 Redis reconnecting...');
    });

    redisClient.on('end', () => {
      console.warn('⚠️ Redis connection ended');
    });

    // Graceful shutdown
    process.on('SIGINT', async () => {
      try {
        await redisClient.quit();
        console.log('Redis connection closed through app termination');
      } catch (err) {
        console.error('Error during Redis shutdown:', err);
      }
    });

    return redisClient;
  } catch (error) {
    console.error('❌ Redis connection failed:', error);
    throw error;
  }
};

/**
 * Health check for database connections
 */
const healthCheck = async () => {
  const health = {
    timestamp: new Date().toISOString(),
    mongo: 'unknown',
    redis: 'unknown',
    overall: 'unknown'
  };

  try {
    // Check MongoDB
    if (mongoose.connection.readyState === 1) {
      await mongoose.connection.db.admin().ping();
      health.mongo = 'healthy';
    } else {
      health.mongo = 'unhealthy';
    }
  } catch (error) {
    health.mongo = 'error';
    console.error('MongoDB health check failed:', error);
  }

  try {
    // Check Redis
    if (redisClient && redisClient.status === 'ready') {
      await redisClient.ping();
      health.redis = 'healthy';
    } else {
      health.redis = 'unhealthy';
    }
  } catch (error) {
    health.redis = 'error';
    console.error('Redis health check failed:', error);
  }

  // Overall health
  if (health.mongo === 'healthy' && health.redis === 'healthy') {
    health.overall = 'healthy';
  } else if (health.mongo === 'error' || health.redis === 'error') {
    health.overall = 'unhealthy';
  } else {
    health.overall = 'degraded';
  }

  return health;
};

/**
 * Close all database connections
 */
const closeConnections = async () => {
  try {
    if (mongoConnection) {
      await mongoose.connection.close();
      console.log('MongoDB connection closed');
    }
    
    if (redisClient) {
      await redisClient.quit();
      console.log('Redis connection closed');
    }
  } catch (error) {
    console.error('Error closing database connections:', error);
  }
};

/**
 * Initialize all database connections
 */
const initializeConnections = async () => {
  try {
    console.log('🔌 Initializing database connections...');
    
    await connectMongo();
    await connectRedis();
    
    console.log('✅ All database connections initialized successfully');
    
    return {
      mongo: mongoConnection,
      redis: redisClient
    };
  } catch (error) {
    console.error('❌ Failed to initialize database connections:', error);
    throw error;
  }
};

module.exports = {
  connectMongo,
  connectRedis,
  healthCheck,
  closeConnections,
  initializeConnections,
  getMongoConnection: () => mongoConnection,
  getRedisClient: () => redisClient
};


