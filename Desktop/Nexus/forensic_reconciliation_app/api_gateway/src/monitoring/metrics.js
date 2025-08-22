const os = require('os');
const { performance } = require('perf_hooks');
const config = require('../config');

/**
 * Performance metrics collector
 */
class MetricsCollector {
  constructor() {
    this.metrics = {
      requests: {
        total: 0,
        successful: 0,
        failed: 0,
        byMethod: {},
        byEndpoint: {},
        byStatus: {}
      },
      responseTime: {
        min: Infinity,
        max: 0,
        sum: 0,
        count: 0,
        percentiles: {}
      },
      errors: {
        total: 0,
        byType: {},
        byEndpoint: {}
      },
      system: {
        cpu: 0,
        memory: 0,
        uptime: 0,
        loadAverage: []
      },
      database: {
        mongo: { healthy: false, responseTime: 0 },
        redis: { healthy: false, responseTime: 0 }
      },
      cache: {
        hits: 0,
        misses: 0,
        hitRate: 0
      },
      websockets: {
        connections: 0,
        messages: 0,
        errors: 0
      }
    };

    this.startTime = Date.now();
    this.lastUpdate = Date.now();
    this.updateInterval = 30000; // 30 seconds

    // Start periodic updates
    this.startPeriodicUpdates();
  }

  /**
   * Record HTTP request metrics
   */
  recordRequest(method, endpoint, statusCode, responseTime, error = null) {
    const now = Date.now();
    
    // Basic request counting
    this.metrics.requests.total++;
    
    if (statusCode >= 200 && statusCode < 400) {
      this.metrics.requests.successful++;
    } else {
      this.metrics.requests.failed++;
    }

    // Method counting
    this.metrics.requests.byMethod[method] = (this.metrics.requests.byMethod[method] || 0) + 1;
    
    // Endpoint counting
    this.metrics.requests.byEndpoint[endpoint] = (this.metrics.requests.byEndpoint[endpoint] || 0) + 1;
    
    // Status code counting
    this.metrics.requests.byStatus[statusCode] = (this.metrics.requests.byStatus[statusCode] || 0) + 1;

    // Response time metrics
    if (responseTime < this.metrics.responseTime.min) {
      this.metrics.responseTime.min = responseTime;
    }
    if (responseTime > this.metrics.responseTime.max) {
      this.metrics.responseTime.max = responseTime;
    }
    this.metrics.responseTime.sum += responseTime;
    this.metrics.responseTime.count++;

    // Error tracking
    if (error) {
      this.metrics.errors.total++;
      const errorType = error.name || 'Unknown';
      this.metrics.errors.byType[errorType] = (this.metrics.errors.byType[errorType] || 0) + 1;
      this.metrics.errors.byEndpoint[endpoint] = (this.metrics.errors.byEndpoint[endpoint] || 0) + 1;
    }

    // Update percentiles every 100 requests
    if (this.metrics.responseTime.count % 100 === 0) {
      this.updatePercentiles();
    }
  }

  /**
   * Update response time percentiles
   */
  updatePercentiles() {
    const avg = this.metrics.responseTime.sum / this.metrics.responseTime.count;
    this.metrics.responseTime.percentiles = {
      avg: Math.round(avg * 100) / 100,
      p50: this.calculatePercentile(50),
      p90: this.calculatePercentile(90),
      p95: this.calculatePercentile(95),
      p99: this.calculatePercentile(99)
    };
  }

  /**
   * Calculate percentile (simplified - in production use proper percentile calculation)
   */
  calculatePercentile(percentile) {
    // This is a simplified implementation
    // In production, you'd want to use a proper percentile calculation library
    const avg = this.metrics.responseTime.sum / this.metrics.responseTime.count;
    return Math.round(avg * 100) / 100;
  }

  /**
   * Record database health metrics
   */
  recordDatabaseHealth(type, healthy, responseTime) {
    if (type === 'mongo') {
      this.metrics.database.mongo.healthy = healthy;
      this.metrics.database.mongo.responseTime = responseTime;
    } else if (type === 'redis') {
      this.metrics.database.redis.healthy = healthy;
      this.metrics.database.redis.responseTime = responseTime;
    }
  }

  /**
   * Record cache metrics
   */
  recordCache(hit) {
    if (hit) {
      this.metrics.cache.hits++;
    } else {
      this.metrics.cache.misses++;
    }
    
    const total = this.metrics.cache.hits + this.metrics.cache.misses;
    this.metrics.cache.hitRate = total > 0 ? (this.metrics.cache.hits / total) * 100 : 0;
  }

  /**
   * Record WebSocket metrics
   */
  recordWebSocket(type, count = 1) {
    switch (type) {
      case 'connection':
        this.metrics.websockets.connections += count;
        break;
      case 'message':
        this.metrics.websockets.messages += count;
        break;
      case 'error':
        this.metrics.websockets.errors += count;
        break;
      case 'disconnection':
        this.metrics.websockets.connections = Math.max(0, this.metrics.websockets.connections - count);
        break;
    }
  }

  /**
   * Update system metrics
   */
  updateSystemMetrics() {
    const now = Date.now();
    
    // CPU usage
    const cpus = os.cpus();
    let totalIdle = 0;
    let totalTick = 0;
    
    cpus.forEach(cpu => {
      for (const type in cpu.times) {
        totalTick += cpu.times[type];
      }
      totalIdle += cpu.times.idle;
    });
    
    const idle = totalIdle / cpus.length;
    const total = totalTick / cpus.length;
    const usage = 100 - (100 * idle / total);
    
    this.metrics.system.cpu = Math.round(usage * 100) / 100;
    
    // Memory usage
    const totalMem = os.totalmem();
    const freeMem = os.freemem();
    const usedMem = totalMem - freeMem;
    this.metrics.system.memory = Math.round((usedMem / totalMem) * 100 * 100) / 100;
    
    // Load average
    this.metrics.system.loadAverage = os.loadavg();
    
    // Uptime
    this.metrics.system.uptime = Math.floor((now - this.startTime) / 1000);
    
    this.lastUpdate = now;
  }

  /**
   * Start periodic system metrics updates
   */
  startPeriodicUpdates() {
    setInterval(() => {
      this.updateSystemMetrics();
    }, this.updateInterval);
  }

  /**
   * Get current metrics
   */
  getMetrics() {
    // Update system metrics if needed
    const now = Date.now();
    if (now - this.lastUpdate > this.updateInterval) {
      this.updateSystemMetrics();
    }

    return {
      ...this.metrics,
      timestamp: new Date().toISOString(),
      uptime: this.metrics.system.uptime
    };
  }

  /**
   * Get metrics summary for health checks
   */
  getHealthSummary() {
    const metrics = this.getMetrics();
    
    return {
      status: this.determineOverallHealth(metrics),
      timestamp: metrics.timestamp,
      uptime: metrics.uptime,
      requests: {
        total: metrics.requests.total,
        successRate: metrics.requests.total > 0 
          ? (metrics.requests.successful / metrics.requests.total * 100).toFixed(2)
          : 0
      },
      responseTime: {
        avg: metrics.responseTime.percentiles.avg || 0,
        p95: metrics.responseTime.percentiles.p95 || 0
      },
      system: {
        cpu: metrics.system.cpu,
        memory: metrics.system.memory
      },
      database: {
        mongo: metrics.database.mongo.healthy,
        redis: metrics.database.redis.healthy
      }
    };
  }

  /**
   * Determine overall health status
   */
  determineOverallHealth(metrics) {
    // Check critical thresholds
    const criticalThresholds = {
      cpu: 90,
      memory: 90,
      responseTime: 2000, // 2 seconds
      errorRate: 10 // 10%
    };

    const errorRate = metrics.requests.total > 0 
      ? (metrics.errors.total / metrics.requests.total) * 100 
      : 0;

    if (metrics.system.cpu > criticalThresholds.cpu ||
        metrics.system.memory > criticalThresholds.memory ||
        metrics.responseTime.percentiles.p95 > criticalThresholds.responseTime ||
        errorRate > criticalThresholds.errorRate ||
        !metrics.database.mongo.healthy ||
        !metrics.database.redis.healthy) {
      return 'critical';
    }

    // Check warning thresholds
    const warningThresholds = {
      cpu: 70,
      memory: 70,
      responseTime: 1000, // 1 second
      errorRate: 5 // 5%
    };

    if (metrics.system.cpu > warningThresholds.cpu ||
        metrics.system.memory > warningThresholds.memory ||
        metrics.responseTime.percentiles.p95 > warningThresholds.responseTime ||
        errorRate > warningThresholds.errorRate) {
      return 'warning';
    }

    return 'healthy';
  }

  /**
   * Reset metrics (useful for testing or daily resets)
   */
  resetMetrics() {
    this.metrics = {
      requests: {
        total: 0,
        successful: 0,
        failed: 0,
        byMethod: {},
        byEndpoint: {},
        byStatus: {}
      },
      responseTime: {
        min: Infinity,
        max: 0,
        sum: 0,
        count: 0,
        percentiles: {}
      },
      errors: {
        total: 0,
        byType: {},
        byEndpoint: {}
      },
      system: {
        cpu: 0,
        memory: 0,
        uptime: 0,
        loadAverage: []
      },
      database: {
        mongo: { healthy: false, responseTime: 0 },
        redis: { healthy: false, responseTime: 0 }
      },
      cache: {
        hits: 0,
        misses: 0,
        hitRate: 0
      },
      websockets: {
        connections: 0,
        messages: 0,
        errors: 0
      }
    };
    
    this.startTime = Date.now();
    this.lastUpdate = Date.now();
  }
}

// Create singleton instance
const metricsCollector = new MetricsCollector();

module.exports = metricsCollector;


