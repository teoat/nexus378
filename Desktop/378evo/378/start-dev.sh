#!/bin/bash
echo "Starting all services..."
docker-compose up -d
echo "Starting frontend and backend..."
npm-run-all --parallel start:frontend start:backend