#!/bin/bash

# Forensic Reconciliation Platform - Optimized Build Script
# This script optimizes Docker builds using BuildKit, parallel building, and caching

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
COMPOSE_FILE="docker-compose.yml"
COMPOSE_PROD_FILE="docker-compose.prod.yml"
BUILDKIT_ENABLED=true
PARALLEL_BUILDS=4
CACHE_FROM_REGISTRY=""
PUSH_TO_REGISTRY=false

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to check prerequisites
check_prerequisites() {
    print_status "Checking prerequisites..."
    
    # Check if Docker is running
    if ! docker info > /dev/null 2>&1; then
        print_error "Docker is not running. Please start Docker and try again."
        exit 1
    fi
    
    # Check Docker version
    DOCKER_VERSION=$(docker --version | cut -d' ' -f3 | cut -d'.' -f1)
    if [ "$DOCKER_VERSION" -lt 20 ]; then
        print_warning "Docker version 20+ recommended for optimal performance"
    fi
    
    # Check if BuildKit is available
    if [ "$BUILDKIT_ENABLED" = true ]; then
        export DOCKER_BUILDKIT=1
        export COMPOSE_DOCKER_CLI_BUILD=1
        print_success "BuildKit enabled"
    fi
    
    print_success "Prerequisites check completed"
}

# Function to build cache images
build_cache_images() {
    print_status "Building cache images for better build performance..."
    
    # Build main app cache
    docker build \
        --target cache \
        --cache-from forensic_reconciliation_app:cache \
        --tag forensic_reconciliation_app:cache \
        --file Dockerfile \
        .
    
    # Build API gateway cache
    docker build \
        --target cache \
        --cache-from forensic_reconciliation_app-api_gateway:cache \
        --tag forensic_reconciliation_app-api_gateway:cache \
        --file api_gateway/Dockerfile \
        ./api_gateway
    
    print_success "Cache images built successfully"
}

# Function to build services in parallel
build_services_parallel() {
    print_status "Building services in parallel (max: $PARALLEL_BUILDS)..."
    
    # Build main application
    docker build \
        --target production \
        --cache-from forensic_reconciliation_app:cache \
        --tag forensic_reconciliation_app:latest \
        --file Dockerfile \
        . &
    
    # Build API gateway
    docker build \
        --target production \
        --cache-from forensic_reconciliation_app-api_gateway:cache \
        --tag forensic_reconciliation_app-api_gateway:latest \
        --file api_gateway/Dockerfile \
        ./api_gateway &
    
    # Wait for all builds to complete
    wait
    
    print_success "All services built successfully"
}

# Function to build with Docker Compose
build_with_compose() {
    local compose_file=$1
    local environment=$2
    
    print_status "Building with Docker Compose ($environment)..."
    
    # Build images
    docker-compose -f "$compose_file" build \
        --parallel \
        --build-arg BUILDKIT_INLINE_CACHE=1
    
    print_success "Docker Compose build completed ($environment)"
}

# Function to optimize images
optimize_images() {
    print_status "Optimizing built images..."
    
    # Remove dangling images
    docker image prune -f
    
    # Remove unused build cache
    docker builder prune -f
    
    print_success "Image optimization completed"
}

# Function to show build statistics
show_build_stats() {
    print_status "Build Statistics:"
    
    # Show image sizes
    echo "Image sizes:"
    docker images forensic_reconciliation_app* --format "table {{.Repository}}\t{{.Tag}}\t{{.Size}}"
    
    # Show disk usage
    echo -e "\nDisk usage:"
    docker system df
}

# Function to run health checks
run_health_checks() {
    print_status "Running health checks..."
    
    # Start services
    docker-compose -f "$COMPOSE_FILE" up -d
    
    # Wait for services to be ready
    sleep 30
    
    # Check service health
    docker-compose -f "$COMPOSE_FILE" ps
    
    print_success "Health checks completed"
}

# Function to show usage
show_usage() {
    echo "Usage: $0 [OPTIONS] COMMAND"
    echo ""
    echo "Commands:"
    echo "  build           Build all services with optimization"
    echo "  build-prod      Build production services"
    echo "  cache           Build cache images only"
    echo "  clean           Clean up Docker resources"
    echo "  health          Run health checks"
    echo "  stats           Show build statistics"
    echo ""
    echo "Options:"
    echo "  -f, --file     Specify compose file (default: docker-compose.yml)"
    echo "  -p, --parallel Set parallel build limit (default: 4)"
    echo "  -c, --cache    Enable/disable BuildKit cache (default: true)"
    echo "  -h, --help     Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0 build                    # Build all services"
    echo "  $0 build-prod               # Build production services"
    echo "  $0 build -p 8               # Build with 8 parallel processes"
    echo "  $0 build -f docker-compose.prod.yml  # Use production compose file"
}

# Function to clean up
cleanup() {
    print_status "Cleaning up Docker resources..."
    
    # Stop and remove containers
    docker-compose -f "$COMPOSE_FILE" down --remove-orphans
    
    # Remove unused images
    docker image prune -f
    
    # Remove unused volumes
    docker volume prune -f
    
    # Remove unused networks
    docker network prune -f
    
    # Remove build cache
    docker builder prune -f
    
    print_success "Cleanup completed"
}

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        -f|--file)
            COMPOSE_FILE="$2"
            shift 2
            ;;
        -p|--parallel)
            PARALLEL_BUILDS="$2"
            shift 2
            ;;
        -c|--cache)
            BUILDKIT_ENABLED="$2"
            shift 2
            ;;
        -h|--help)
            show_usage
            exit 0
            ;;
        build)
            COMMAND="build"
            shift
            ;;
        build-prod)
            COMMAND="build-prod"
            shift
            ;;
        cache)
            COMMAND="cache"
            shift
            ;;
        clean)
            COMMAND="clean"
            shift
            ;;
        health)
            COMMAND="health"
            shift
            ;;
        stats)
            COMMAND="stats"
            shift
            ;;
        *)
            print_error "Unknown option: $1"
            show_usage
            exit 1
            ;;
    esac
done

# Main execution
main() {
    case $COMMAND in
        build)
            check_prerequisites
            build_cache_images
            build_services_parallel
            build_with_compose "$COMPOSE_FILE" "development"
            optimize_images
            show_build_stats
            ;;
        build-prod)
            check_prerequisites
            build_cache_images
            build_services_parallel
            build_with_compose "$COMPOSE_PROD_FILE" "production"
            optimize_images
            show_build_stats
            ;;
        cache)
            check_prerequisites
            build_cache_images
            ;;
        clean)
            cleanup
            ;;
        health)
            run_health_checks
            ;;
        stats)
            show_build_stats
            ;;
        *)
            print_error "No command specified"
            show_usage
            exit 1
            ;;
    esac
}

# Run main function
main "$@"
