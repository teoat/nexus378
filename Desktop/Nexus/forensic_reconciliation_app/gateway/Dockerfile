# Forensic Reconciliation + Fraud Platform - API Gateway Dockerfile
# Node.js-based API gateway with GraphQL and authentication

FROM node:18-alpine

# Set environment variables
ENV NODE_ENV=development
ENV PORT=3000
ENV NPM_CONFIG_CACHE=/tmp/.npm

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apk add --no-cache \
    curl \
    git \
    python3 \
    make \
    g++ \
    && rm -rf /var/cache/apk/*

# Copy package files
COPY package*.json ./

# Install dependencies
RUN npm ci --only=production && \
    npm cache clean --force

# Copy application code
COPY . .

# Create necessary directories
RUN mkdir -p /app/logs /app/uploads /app/temp

# Create non-root user
RUN addgroup -g 1001 -S nexus && \
    adduser -S nexus -u 1001 && \
    chown -R nexus:nexus /app
USER nexus

# Expose port
EXPOSE 3000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:3000/health || exit 1

# Default command
CMD ["npm", "start"]
