const config = require('../config');

/**
 * Custom error class for API errors
 */
class ApiError extends Error {
  constructor(statusCode, message, isOperational = true, stack = '') {
    super(message);
    this.statusCode = statusCode;
    this.isOperational = isOperational;
    this.timestamp = new Date().toISOString();
    
    if (stack) {
      this.stack = stack;
    } else {
      Error.captureStackTrace(this, this.constructor);
    }
  }
}

/**
 * Error handler middleware
 */
const errorHandler = (err, req, res, next) => {
  let error = { ...err };
  error.message = err.message;

  // Log error
  console.error('Error:', {
    message: err.message,
    stack: err.stack,
    url: req.url,
    method: req.method,
    ip: req.ip,
    userAgent: req.get('User-Agent'),
    timestamp: new Date().toISOString()
  });

  // Mongoose bad ObjectId
  if (err.name === 'CastError') {
    const message = 'Resource not found';
    error = new ApiError(404, message);
  }

  // Mongoose duplicate key
  if (err.code === 11000) {
    const field = Object.keys(err.keyValue)[0];
    const message = `Duplicate field value: ${field}. Please use another value.`;
    error = new ApiError(400, message);
  }

  // Mongoose validation error
  if (err.name === 'ValidationError') {
    const message = Object.values(err.errors).map(val => val.message).join(', ');
    error = new ApiError(400, message);
  }

  // JWT errors
  if (err.name === 'JsonWebTokenError') {
    const message = 'Invalid token. Please log in again.';
    error = new ApiError(401, message);
  }

  if (err.name === 'TokenExpiredError') {
    const message = 'Token expired. Please log in again.';
    error = new ApiError(401, message);
  }

  // Multer file upload errors
  if (err.code === 'LIMIT_FILE_SIZE') {
    const message = `File too large. Maximum size is ${config.upload.maxFileSize / (1024 * 1024)}MB.`;
    error = new ApiError(400, message);
  }

  if (err.code === 'LIMIT_FILE_COUNT') {
    const message = 'Too many files. Please upload fewer files.';
    error = new ApiError(400, message);
  }

  if (err.code === 'LIMIT_UNEXPECTED_FILE') {
    const message = 'Unexpected file field.';
    error = new ApiError(400, message);
  }

  // Rate limit errors
  if (err.status === 429) {
    const message = 'Too many requests. Please try again later.';
    error = new ApiError(429, message);
  }

  // GraphQL errors
  if (err.extensions && err.extensions.code) {
    const graphqlErrorMap = {
      'GRAPHQL_VALIDATION_FAILED': { status: 400, message: 'GraphQL validation failed' },
      'BAD_USER_INPUT': { status: 400, message: 'Invalid input data' },
      'UNAUTHENTICATED': { status: 401, message: 'Authentication required' },
      'FORBIDDEN': { status: 403, message: 'Access denied' },
      'NOT_FOUND': { status: 404, message: 'Resource not found' },
      'INTERNAL_SERVER_ERROR': { status: 500, message: 'Internal server error' }
    };

    const graphqlError = graphqlErrorMap[err.extensions.code];
    if (graphqlError) {
      error = new ApiError(graphqlError.status, graphqlError.message);
    }
  }

  // Default error
  if (!error.statusCode) {
    error.statusCode = 500;
    error.message = 'Internal Server Error';
  }

  // Send error response
  const errorResponse = {
    success: false,
    error: {
      message: error.message,
      statusCode: error.statusCode,
      timestamp: error.timestamp,
      path: req.originalUrl,
      method: req.method
    }
  };

  // Include stack trace in development
  if (config.nodeEnv === 'development') {
    errorResponse.error.stack = error.stack;
  }

  // Include additional details for validation errors
  if (error.statusCode === 400 && error.details) {
    errorResponse.error.details = error.details;
  }

  res.status(error.statusCode).json(errorResponse);
};

/**
 * 404 handler for undefined routes
 */
const notFound = (req, res, next) => {
  const error = new ApiError(404, `Route ${req.originalUrl} not found`);
  next(error);
};

/**
 * Async error wrapper
 */
const asyncHandler = (fn) => (req, res, next) => {
  Promise.resolve(fn(req, res, next)).catch(next);
};

/**
 * Error logger
 */
const errorLogger = (err, req, res, next) => {
  // Log error to file or external service
  const errorLog = {
    timestamp: new Date().toISOString(),
    level: 'error',
    message: err.message,
    stack: err.stack,
    url: req.url,
    method: req.method,
    ip: req.ip,
    userAgent: req.get('User-Agent'),
    userId: req.user?.id || 'anonymous',
    requestId: req.id || 'unknown'
  };

  // In production, you might want to send this to a logging service
  if (config.nodeEnv === 'production') {
    // TODO: Send to external logging service (e.g., Loggly, Papertrail)
    console.error('Production Error Log:', JSON.stringify(errorLog));
  } else {
    console.error('Development Error Log:', errorLog);
  }

  next(err);
};

/**
 * Graceful shutdown error handler
 */
const gracefulShutdown = (server) => {
  return (signal) => {
    console.log(`\n${signal} received. Shutting down gracefully...`);
    
    server.close(() => {
      console.log('HTTP server closed');
      process.exit(0);
    });

    // Force close after 10 seconds
    setTimeout(() => {
      console.error('Could not close connections in time, forcefully shutting down');
      process.exit(1);
    }, 10000);
  };
};

module.exports = {
  ApiError,
  errorHandler,
  notFound,
  asyncHandler,
  errorLogger,
  gracefulShutdown
};


