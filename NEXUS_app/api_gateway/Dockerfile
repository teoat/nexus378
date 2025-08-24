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

# Stage 1: Dependencies
FROM node:18-alpine as dependencies

WORKDIR /app

COPY package*.json ./

RUN npm install --omit=dev

# Stage 2: Production
FROM node:18-alpine as production

WORKDIR /app

COPY --from=dependencies /app/node_modules ./node_modules
COPY . .

RUN addgroup -g 1001 -S nodejs && \
    adduser -S nodejs -u 1001 && \
    chown -R nodejs:nodejs /app

USER nodejs

EXPOSE 3000

HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:3000/health || exit 1

CMD ["npm", "start"]
