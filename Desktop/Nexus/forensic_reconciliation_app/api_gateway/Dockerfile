# Multi-stage Dockerfile for API Gateway
# Stage 1: Base Node.js environment
FROM node:18-alpine as base

# Set environment variables
ENV NODE_ENV=production \
    NPM_CONFIG_CACHE=/tmp/npm-cache \
    NPM_CONFIG_PREFER_OFFLINE=true

# Install system dependencies
RUN apk add --no-cache \
    curl \
    dumb-init

# Create app user
RUN addgroup -g 1001 -S nodejs && \
    adduser -S nodejs -u 1001

# Stage 2: Dependencies
FROM base as dependencies

# Copy package files first for better caching
COPY package*.json ./

# Install dependencies
RUN npm ci --only=production && npm cache clean --force

# Stage 3: Development (for testing and debugging)
FROM dependencies as development

# Install development dependencies
RUN npm ci && npm cache clean --force

# Copy source code
COPY . /app/
WORKDIR /app

# Change ownership to app user
RUN chown -R nodejs:nodejs /app
USER nodejs

# Expose port
EXPOSE 3000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:3000/health || exit 1

# Default command
CMD ["npm", "run", "dev"]

# Stage 4: Production
FROM dependencies as production

# Copy source code
COPY . /app/
WORKDIR /app

# Remove development files
RUN rm -rf \
    .git \
    .github \
    .vscode \
    node_modules/.cache \
    coverage \
    .nyc_output \
    .eslintcache \
    *.log \
    .env.local \
    .env.development

# Create necessary directories
RUN mkdir -p /app/logs /app/uploads

# Change ownership to app user
RUN chown -R nodejs:nodejs /app
USER nodejs

# Expose port
EXPOSE 3000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:3000/health || exit 1

# Default command
CMD ["dumb-init", "npm", "start"]

# Stage 5: Cache (for build optimization)
FROM base as cache
COPY package*.json ./
RUN npm ci --only=production && npm cache clean --force
