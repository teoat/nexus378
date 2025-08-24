#!/bin/bash

# Enhanced Nexus Platform Build Script
# Supports Docker Compose and Kubernetes deployment with comprehensive logging

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Configuration
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$SCRIPT_DIR"
COMPOSE_FILE="$PROJECT_ROOT/docker-compose.enhanced.yml"
COMPOSE_PROD_FILE="$PROJECT_ROOT/docker-compose.prod.yml"
K8S_DIR="$PROJECT_ROOT/k8s"
BUILDKIT_ENABLED=true
PARALLEL_BUILDS=4
LOG_LEVEL="INFO"
LOG_FILE="$PROJECT_ROOT/build.log"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")

# Function to print colored output with timestamp
print_log() {
    local level=$1
    local message=$2
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    
    case $level in
        "INFO")
            echo -e "${BLUE}[${timestamp}] [INFO]${NC} $message" | tee -a "$LOG_FILE"
            ;;
        "SUCCESS")
            echo -e "${GREEN}[${timestamp}] [SUCCESS]${NC} $message" | tee -a "$LOG_FILE"
            ;;
        "WARNING")
            echo -e "${YELLOW}[${timestamp}] [WARNING]${NC} $message" | tee -a "$LOG_FILE"
            ;;
        "ERROR")
            echo -e "${RED}[${timestamp}] [ERROR]${NC} $message" | tee -a "$LOG_FILE"
            ;;
        "DEBUG")
            if [ "$LOG_LEVEL" = "DEBUG" ]; then
                echo -e "${PURPLE}[${timestamp}] [DEBUG]${NC} $message" | tee -a "$LOG_FILE"
            fi
            ;;
        *)
            echo -e "${CYAN}[${timestamp}] [LOG]${NC} $message" | tee -a "$LOG_FILE"
            ;;
    esac
}

# Function to log command execution
log_command() {
    local command="$1"
    print_log "DEBUG" "Executing: $command"
    eval "$command"
}

# Function to check prerequisites
check_prerequisites() {
    print_log "INFO" "Checking prerequisites..."
    
    # Check if Docker is running
    if ! docker info > /dev/null 2>&1; then
        print_log "ERROR" "Docker is not running. Please start Docker and try again."
        exit 1
    fi
    
    # Check Docker version
    DOCKER_VERSION=$(docker --version | cut -d' ' -f3 | cut -d'.' -f1)
    if [ "$DOCKER_VERSION" -lt 20 ]; then
        print_log "WARNING" "Docker version 20+ recommended for optimal performance"
    fi
    
    # Check if kubectl is available (for Kubernetes deployment)
    if command -v kubectl &> /dev/null; then
        KUBECTL_AVAILABLE=true
        print_log "INFO" "Kubernetes CLI (kubectl) detected"
    else
        KUBECTL_AVAILABLE=false
        print_log "WARNING" "Kubernetes CLI (kubectl) not found. Kubernetes deployment will be skipped."
    fi
    
    # Check if BuildKit is available
    if [ "$BUILDKIT_ENABLED" = true ]; then
        export DOCKER_BUILDKIT=1
        export COMPOSE_DOCKER_CLI_BUILD=1
        print_log "SUCCESS" "BuildKit enabled"
    fi
    
    print_log "SUCCESS" "Prerequisites check completed"
}

# Function to build cache images
build_cache_images() {
    print_log "INFO" "Building cache images for better build performance..."
    
    # Build main app cache
    log_command "docker build --target cache --cache-from nexus:cache --tag nexus:cache --file Dockerfile ."
    
    # Build API gateway cache
    log_command "docker build --target cache --cache-from nexus-api_gateway:cache --tag nexus-api_gateway:cache --file api_gateway/Dockerfile ./api_gateway"
    
    print_log "SUCCESS" "Cache images built successfully"
}

# Function to build services in parallel
build_services_parallel() {
    print_log "INFO" "Building services in parallel (max: $PARALLEL_BUILDS)..."
    
    # Build main application
    docker build \
        --target production \
        --cache-from nexus:cache \
        --tag nexus:enhanced \
        --file Dockerfile \
        . &
    
    # Build API gateway
    docker build \
        --target production \
        --cache-from nexus-api_gateway:cache \
        --tag nexus-api_gateway:enhanced \
        --file api_gateway/Dockerfile \
        ./api_gateway &
    
    # Wait for all builds to complete
    wait
    
    print_log "SUCCESS" "All services built successfully"
}

# Function to build with Docker Compose
build_with_compose() {
    local compose_file=$1
    local environment=$2
    
    print_log "INFO" "Building with Docker Compose ($environment)..."
    
    # Build images
    log_command "docker-compose -f \"$compose_file\" build --parallel --build-arg BUILDKIT_INLINE_CACHE=1"
    
    print_log "SUCCESS" "Docker Compose build completed ($environment)"
}

# Function to deploy to Kubernetes
deploy_to_kubernetes() {
    if [ "$KUBECTL_AVAILABLE" = false ]; then
        print_log "WARNING" "Skipping Kubernetes deployment - kubectl not available"
        return
    fi
    
    print_log "INFO" "Deploying to Kubernetes..."
    
    # Check if we're connected to a cluster
    if ! kubectl cluster-info &> /dev/null; then
        print_log "ERROR" "Not connected to Kubernetes cluster. Please configure kubectl."
        return 1
    fi
    
    # Create namespace and monitoring stack
    print_log "INFO" "Creating namespace and monitoring stack..."
    log_command "kubectl apply -f \"$K8S_DIR/namespace.yaml\""
    log_command "kubectl apply -f \"$K8S_DIR/monitoring-stack.yaml\""
    
    # Wait for monitoring stack to be ready
    print_log "INFO" "Waiting for monitoring stack to be ready..."
    log_command "kubectl wait --for=condition=ready pod -l app=prometheus -n monitoring --timeout=300s"
    log_command "kubectl wait --for=condition=ready pod -l app=grafana -n monitoring --timeout=300s"
    
    # Deploy main application
    print_log "INFO" "Deploying main application..."
    log_command "kubectl apply -f \"$K8S_DIR/forensic-app-deployment.yaml\""
    
    # Wait for application to be ready
    print_log "INFO" "Waiting for application to be ready..."
    log_command "kubectl wait --for=condition=ready pod -l app=forensic-app -n forensic-platform --timeout=300s"
    
    print_log "SUCCESS" "Kubernetes deployment completed"
    
    # Show deployment status
    print_log "INFO" "Deployment status:"
    log_command "kubectl get pods -n forensic-platform"
    log_command "kubectl get services -n forensic-platform"
    log_command "kubectl get pods -n monitoring"
}

# Function to run health checks
run_health_checks() {
    local deployment_type=$1
    
    print_log "INFO" "Running health checks for $deployment_type deployment..."
    
    if [ "$deployment_type" = "docker" ]; then
        # Docker health checks
        log_command "docker-compose -f \"$COMPOSE_FILE\" ps"
        log_command "docker-compose -f \"$COMPOSE_FILE\" logs --tail=50"
    elif [ "$deployment_type" = "kubernetes" ]; then
        # Kubernetes health checks
        if [ "$KUBECTL_AVAILABLE" = true ]; then
            log_command "kubectl get pods -n forensic-platform"
            log_command "kubectl get pods -n monitoring"
            log_command "kubectl describe pods -n forensic-platform"
        fi
    fi
    
    print_log "SUCCESS" "Health checks completed"
}

# Function to show build statistics
show_build_stats() {
    print_log "INFO" "Build Statistics:"
    
    # Show image sizes
    echo "Image sizes:" | tee -a "$LOG_FILE"
    log_command "docker images nexus* --format \"table {{.Repository}}\t{{.Tag}}\t{{.Size}}\""
    
    # Show disk usage
    echo -e "\nDisk usage:" | tee -a "$LOG_FILE"
    log_command "docker system df"
    
    # Show resource usage
    echo -e "\nResource usage:" | tee -a "$LOG_FILE"
    log_command "docker stats --no-stream --format \"table {{.Container}}\t{{.CPUPerc}}\t{{.MemUsage}}\t{{.NetIO}}\""
}

# Function to optimize images
optimize_images() {
    print_log "INFO" "Optimizing built images..."
    
    # Remove dangling images
    log_command "docker image prune -f"
    
    # Remove unused build cache
    log_command "docker builder prune -f"
    
    # Remove unused volumes
    log_command "docker volume prune -f"
    
    print_log "SUCCESS" "Image optimization completed"
}

# Function to create backup
create_backup() {
    print_log "INFO" "Creating backup of current state..."
    
    local backup_dir="$PROJECT_ROOT/backups/backup_$TIMESTAMP"
    mkdir -p "$backup_dir"
    
    # Backup Docker images
    docker save nexus:enhanced -o "$backup_dir/forensic-app.tar"
    docker save nexus-api_gateway:enhanced -o "$backup_dir/api-gateway.tar"
    
    # Backup configuration files
    cp -r "$PROJECT_ROOT/k8s" "$backup_dir/"
    cp "$COMPOSE_FILE" "$backup_dir/"
    cp "$COMPOSE_PROD_FILE" "$backup_dir/"
    
    # Backup logs
    if [ -f "$LOG_FILE" ]; then
        cp "$LOG_FILE" "$backup_dir/"
    fi
    
    print_log "SUCCESS" "Backup created in $backup_dir"
}

# Function to show usage
show_usage() {
    echo "Enhanced Nexus Platform Build Script"
    echo ""
    echo "Usage: $0 [OPTIONS] COMMAND"
    echo ""
    echo "Commands:"
    echo "  build           Build all services with optimization"
    echo "  build-prod      Build production services"
    echo "  build-cache     Build cache images only"
    echo "  deploy-k8s      Deploy to Kubernetes"
    echo "  deploy-docker   Deploy with Docker Compose"
    echo "  health          Run health checks"
    echo "  stats           Show build statistics"
    echo "  backup          Create backup of current state"
    echo "  clean           Clean up resources"
    echo ""
    echo "Options:"
    echo "  -f, --file     Specify compose file"
    echo "  -p, --parallel Set parallel build limit (default: 4)"
    echo "  -c, --cache    Enable/disable BuildKit cache (default: true)"
    echo "  -l, --log      Set log level (INFO, DEBUG, default: INFO)"
    echo "  -h, --help     Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0 build                    # Build all services"
    echo "  $0 deploy-k8s               # Deploy to Kubernetes"
    echo "  $0 build -p 8               # Build with 8 parallel processes"
    echo "  $0 build -l DEBUG           # Build with debug logging"
}

# Function to clean up
cleanup() {
    print_log "INFO" "Cleaning up resources..."
    
    # Stop and remove containers
    if [ -f "$COMPOSE_FILE" ]; then
        log_command "docker-compose -f \"$COMPOSE_FILE\" down --remove-orphans"
    fi
    
    # Remove unused images
    log_command "docker image prune -f"
    
    # Remove unused volumes
    log_command "docker volume prune -f"
    
    # Remove unused networks
    log_command "docker network prune -f"
    
    # Remove build cache
    log_command "docker builder prune -f"
    
    print_log "SUCCESS" "Cleanup completed"
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
        -l|--log)
            LOG_LEVEL="$2"
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
        build-cache)
            COMMAND="build-cache"
            shift
            ;;
        deploy-k8s)
            COMMAND="deploy-k8s"
            shift
            ;;
        deploy-docker)
            COMMAND="deploy-docker"
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
        backup)
            COMMAND="backup"
            shift
            ;;
        clean)
            COMMAND="clean"
            shift
            ;;
        *)
            print_log "ERROR" "Unknown option: $1"
            show_usage
            exit 1
            ;;
    esac
done

# Initialize logging
echo "=== Enhanced Build Log - $(date) ===" > "$LOG_FILE"

# Main execution
main() {
    print_log "INFO" "Starting enhanced build process..."
    print_log "INFO" "Project root: $PROJECT_ROOT"
    print_log "INFO" "Log file: $LOG_FILE"
    print_log "INFO" "Log level: $LOG_LEVEL"
    
    case $COMMAND in
        build)
            check_prerequisites
            build_cache_images
            build_services_parallel
            build_with_compose "$COMPOSE_FILE" "development"
            optimize_images
            show_build_stats
            create_backup
            ;;
        build-prod)
            check_prerequisites
            build_cache_images
            build_services_parallel
            build_with_compose "$COMPOSE_PROD_FILE" "production"
            optimize_images
            show_build_stats
            create_backup
            ;;
        build-cache)
            check_prerequisites
            build_cache_images
            ;;
        deploy-k8s)
            check_prerequisites
            deploy_to_kubernetes
            run_health_checks "kubernetes"
            ;;
        deploy-docker)
            check_prerequisites
            build_with_compose "$COMPOSE_FILE" "development"
            run_health_checks "docker"
            ;;
        health)
            run_health_checks "docker"
            ;;
        stats)
            show_build_stats
            ;;
        backup)
            create_backup
            ;;
        clean)
            cleanup
            ;;
        *)
            print_log "ERROR" "No command specified"
            show_usage
            exit 1
            ;;
    esac
    
    print_log "SUCCESS" "Enhanced build process completed successfully!"
}

# Run main function
main "$@"
