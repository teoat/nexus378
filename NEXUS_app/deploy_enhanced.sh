#!/bin/bash

# Enhanced Nexus Platform Deployment Script
# Comprehensive deployment with monitoring, logging, and health checks

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
LOG_FILE="$PROJECT_ROOT/deploy.log"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")

# Deployment options
DEPLOYMENT_TYPE="docker"  # docker, kubernetes, hybrid
ENVIRONMENT="development"  # development, staging, production
ENABLE_MONITORING=true
ENABLE_LOGGING=true
ENABLE_BACKUP=true
ROLLBACK_ENABLED=true
HEALTH_CHECK_INTERVAL=30
MAX_HEALTH_CHECK_ATTEMPTS=10

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
            echo -e "${PURPLE}[${timestamp}] [DEBUG]${NC} $message" | tee -a "$LOG_FILE"
            ;;
        *)
            echo -e "${CYAN}[${timestamp}] [LOG]${NC} $message" | tee -a "$LOG_FILE"
            ;;
    esac
}

# Function to check prerequisites
check_prerequisites() {
    print_log "INFO" "Checking deployment prerequisites..."
    
    # Check Docker
    if ! docker info > /dev/null 2>&1; then
        print_log "ERROR" "Docker is not running. Please start Docker and try again."
        exit 1
    fi
    
    # Check Docker Compose
    if ! command -v docker-compose &> /dev/null; then
        print_log "ERROR" "Docker Compose is not installed. Please install Docker Compose."
        exit 1
    fi
    
    # Check Kubernetes (if needed)
    if [ "$DEPLOYMENT_TYPE" = "kubernetes" ] || [ "$DEPLOYMENT_TYPE" = "hybrid" ]; then
        if ! command -v kubectl &> /dev/null; then
            print_log "ERROR" "Kubernetes CLI (kubectl) is not installed. Please install kubectl."
            exit 1
        fi
        
        if ! kubectl cluster-info &> /dev/null; then
            print_log "ERROR" "Not connected to Kubernetes cluster. Please configure kubectl."
            exit 1
        fi
    fi
    
    # Check required files
    if [ ! -f "$COMPOSE_FILE" ]; then
        print_log "ERROR" "Docker Compose file not found: $COMPOSE_FILE"
        exit 1
    fi
    
    if [ ! -d "$K8S_DIR" ]; then
        print_log "ERROR" "Kubernetes directory not found: $K8S_DIR"
        exit 1
    fi
    
    print_log "SUCCESS" "Prerequisites check completed"
}

# Function to create backup
create_backup() {
    if [ "$ENABLE_BACKUP" = false ]; then
        print_log "INFO" "Backup disabled, skipping..."
        return
    fi
    
    print_log "INFO" "Creating backup of current deployment..."
    
    local backup_dir="$PROJECT_ROOT/backups/deployment_$TIMESTAMP"
    mkdir -p "$backup_dir"
    
    # Backup Docker images
    if docker images | grep -q "nexus"; then
        docker save nexus:enhanced -o "$backup_dir/forensic-app.tar"
        print_log "INFO" "Backed up forensic app image"
    fi
    
    if docker images | grep -q "nexus-api_gateway"; then
        docker save nexus-api_gateway:enhanced -o "$backup_dir/api-gateway.tar"
        print_log "INFO" "Backed up API gateway image"
    fi
    
    # Backup configuration files
    cp -r "$K8S_DIR" "$backup_dir/"
    cp "$COMPOSE_FILE" "$backup_dir/"
    cp "$COMPOSE_PROD_FILE" "$backup_dir/"
    
    # Backup logs
    if [ -f "$LOG_FILE" ]; then
        cp "$LOG_FILE" "$backup_dir/"
    fi
    
    # Create backup manifest
    cat > "$backup_dir/backup-manifest.txt" << EOF
Backup created: $(date)
Deployment type: $DEPLOYMENT_TYPE
Environment: $ENVIRONMENT
Images backed up: $(ls -1 "$backup_dir"/*.tar 2>/dev/null | wc -l)
Configuration files: $(find "$backup_dir" -name "*.yaml" -o -name "*.yml" | wc -l)
EOF
    
    print_log "SUCCESS" "Backup created in $backup_dir"
}

# Function to deploy with Docker Compose
deploy_docker() {
    print_log "INFO" "Deploying with Docker Compose ($ENVIRONMENT)..."
    
    local compose_file="$COMPOSE_FILE"
    if [ "$ENVIRONMENT" = "production" ]; then
        compose_file="$COMPOSE_PROD_FILE"
    fi
    
    # Stop existing services
    print_log "INFO" "Stopping existing services..."
    docker-compose -f "$compose_file" down --remove-orphans || true
    
    # Build and start services
    print_log "INFO" "Building and starting services..."
    docker-compose -f "$compose_file" up -d --build
    
    # Wait for services to be ready
    print_log "INFO" "Waiting for services to be ready..."
    sleep 30
    
    print_log "SUCCESS" "Docker Compose deployment completed"
}

# Function to deploy to Kubernetes
deploy_kubernetes() {
    print_log "INFO" "Deploying to Kubernetes..."
    
    # Create namespace and monitoring stack
    print_log "INFO" "Creating namespace and monitoring stack..."
    kubectl apply -f "$K8S_DIR/namespace.yaml"
    kubectl apply -f "$K8S_DIR/monitoring-stack.yaml"
    
    # Wait for monitoring stack to be ready
    print_log "INFO" "Waiting for monitoring stack to be ready..."
    kubectl wait --for=condition=ready pod -l app=prometheus -n monitoring --timeout=300s || true
    kubectl wait --for=condition=ready pod -l app=grafana -n monitoring --timeout=300s || true
    
    # Deploy main application
    print_log "INFO" "Deploying main application..."
    kubectl apply -f "$K8S_DIR/forensic-app-deployment.yaml"
    
    # Wait for application to be ready
    print_log "INFO" "Waiting for application to be ready..."
    kubectl wait --for=condition=ready pod -l app=forensic-app -n forensic-platform --timeout=300s || true
    
    print_log "SUCCESS" "Kubernetes deployment completed"
}

# Function to run health checks
run_health_checks() {
    print_log "INFO" "Running health checks..."
    
    local attempts=0
    local healthy=false
    
    while [ $attempts -lt $MAX_HEALTH_CHECK_ATTEMPTS ] && [ "$healthy" = false ]; do
        attempts=$((attempts + 1))
        print_log "INFO" "Health check attempt $attempts/$MAX_HEALTH_CHECK_ATTEMPTS"
        
        if [ "$DEPLOYMENT_TYPE" = "docker" ] || [ "$DEPLOYMENT_TYPE" = "hybrid" ]; then
            # Docker health checks
            if docker-compose -f "$COMPOSE_FILE" ps | grep -q "Up"; then
                print_log "SUCCESS" "Docker services are running"
                healthy=true
            else
                print_log "WARNING" "Some Docker services are not running"
                sleep $HEALTH_CHECK_INTERVAL
            fi
        fi
        
        if [ "$DEPLOYMENT_TYPE" = "kubernetes" ] || [ "$DEPLOYMENT_TYPE" = "hybrid" ]; then
            # Kubernetes health checks
            if kubectl get pods -n forensic-platform 2>/dev/null | grep -q "Running"; then
                print_log "SUCCESS" "Kubernetes pods are running"
                healthy=true
            else
                print_log "WARNING" "Some Kubernetes pods are not running"
                sleep $HEALTH_CHECK_INTERVAL
            fi
        fi
    done
    
    if [ "$healthy" = true ]; then
        print_log "SUCCESS" "All health checks passed"
        return 0
    else
        print_log "ERROR" "Health checks failed after $MAX_HEALTH_CHECK_ATTEMPTS attempts"
        return 1
    fi
}

# Function to show deployment status
show_deployment_status() {
    print_log "INFO" "Deployment Status:"
    
    if [ "$DEPLOYMENT_TYPE" = "docker" ] || [ "$DEPLOYMENT_TYPE" = "hybrid" ]; then
        echo "=== Docker Services ===" | tee -a "$LOG_FILE"
        docker-compose -f "$COMPOSE_FILE" ps | tee -a "$LOG_FILE"
        
        echo -e "\n=== Docker Resource Usage ===" | tee -a "$LOG_FILE"
        docker stats --no-stream --format "table {{.Container}}\t{{.CPUPerc}}\t{{.MemUsage}}\t{{.NetIO}}" | tee -a "$LOG_FILE"
    fi
    
    if [ "$DEPLOYMENT_TYPE" = "kubernetes" ] || [ "$DEPLOYMENT_TYPE" = "hybrid" ]; then
        echo -e "\n=== Kubernetes Pods ===" | tee -a "$LOG_FILE"
        kubectl get pods -n forensic-platform | tee -a "$LOG_FILE"
        
        echo -e "\n=== Kubernetes Services ===" | tee -a "$LOG_FILE"
        kubectl get services -n forensic-platform | tee -a "$LOG_FILE"
        
        echo -e "\n=== Monitoring Stack ===" | tee -a "$LOG_FILE"
        kubectl get pods -n monitoring | tee -a "$LOG_FILE"
    fi
}

# Function to rollback deployment
rollback_deployment() {
    if [ "$ROLLBACK_ENABLED" = false ]; then
        print_log "WARNING" "Rollback disabled, cannot rollback"
        return
    fi
    
    print_log "WARNING" "Rolling back deployment..."
    
    # Find latest backup
    local latest_backup=$(ls -t "$PROJECT_ROOT/backups"/deployment_* 2>/dev/null | head -1)
    
    if [ -z "$latest_backup" ]; then
        print_log "ERROR" "No backup found for rollback"
        return 1
    fi
    
    print_log "INFO" "Rolling back to: $latest_backup"
    
    # Restore Docker images if available
    if [ -f "$latest_backup/forensic-app.tar" ]; then
        docker load -i "$latest_backup/forensic-app.tar"
        print_log "INFO" "Restored forensic app image"
    fi
    
    if [ -f "$latest_backup/api-gateway.tar" ]; then
        docker load -i "$latest_backup/api-gateway.tar"
        print_log "INFO" "Restored API gateway image"
    fi
    
    # Restart services
    if [ "$DEPLOYMENT_TYPE" = "docker" ] || [ "$DEPLOYMENT_TYPE" = "hybrid" ]; then
        docker-compose -f "$COMPOSE_FILE" restart
    fi
    
    if [ "$DEPLOYMENT_TYPE" = "kubernetes" ] || [ "$DEPLOYMENT_TYPE" = "hybrid" ]; then
        kubectl rollout restart deployment/forensic-app -n forensic-platform
    fi
    
    print_log "SUCCESS" "Rollback completed"
}

# Function to show usage
show_usage() {
    echo "Enhanced Nexus Platform Deployment Script"
    echo ""
    echo "Usage: $0 [OPTIONS] COMMAND"
    echo ""
    echo "Commands:"
    echo "  deploy          Deploy the platform"
    echo "  status          Show deployment status"
    echo "  health          Run health checks"
    echo "  rollback        Rollback to previous deployment"
    echo "  backup          Create backup of current deployment"
    echo "  clean           Clean up deployment"
    echo ""
    echo "Options:"
    echo "  -t, --type      Deployment type: docker, kubernetes, hybrid (default: docker)"
    echo "  -e, --env       Environment: development, staging, production (default: development)"
    echo "  -m, --monitor   Enable/disable monitoring (default: true)"
    echo "  -l, --logging   Enable/disable logging (default: true)"
    echo "  -b, --backup    Enable/disable backup (default: true)"
    echo "  -r, --rollback  Enable/disable rollback (default: true)"
    echo "  -h, --help      Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0 deploy                           # Deploy with default settings"
    echo "  $0 deploy -t kubernetes             # Deploy to Kubernetes"
    echo "  $0 deploy -t hybrid -e production   # Hybrid deployment in production"
    echo "  $0 status                           # Show deployment status"
    echo "  $0 rollback                         # Rollback to previous deployment"
}

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        -t|--type)
            DEPLOYMENT_TYPE="$2"
            shift 2
            ;;
        -e|--env)
            ENVIRONMENT="$2"
            shift 2
            ;;
        -m|--monitor)
            ENABLE_MONITORING="$2"
            shift 2
            ;;
        -l|--logging)
            ENABLE_LOGGING="$2"
            shift 2
            ;;
        -b|--backup)
            ENABLE_BACKUP="$2"
            shift 2
            ;;
        -r|--rollback)
            ROLLBACK_ENABLED="$2"
            shift 2
            ;;
        -h|--help)
            show_usage
            exit 0
            ;;
        deploy)
            COMMAND="deploy"
            shift
            ;;
        status)
            COMMAND="status"
            shift
            ;;
        health)
            COMMAND="health"
            shift
            ;;
        rollback)
            COMMAND="rollback"
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
echo "=== Enhanced Deployment Log - $(date) ===" > "$LOG_FILE"

# Main execution
main() {
    print_log "INFO" "Starting enhanced deployment process..."
    print_log "INFO" "Deployment type: $DEPLOYMENT_TYPE"
    print_log "INFO" "Environment: $ENVIRONMENT"
    print_log "INFO" "Monitoring enabled: $ENABLE_MONITORING"
    print_log "INFO" "Logging enabled: $ENABLE_LOGGING"
    print_log "INFO" "Backup enabled: $ENABLE_BACKUP"
    print_log "INFO" "Rollback enabled: $ROLLBACK_ENABLED"
    
    case $COMMAND in
        deploy)
            check_prerequisites
            create_backup
            
            if [ "$DEPLOYMENT_TYPE" = "docker" ] || [ "$DEPLOYMENT_TYPE" = "hybrid" ]; then
                deploy_docker
            fi
            
            if [ "$DEPLOYMENT_TYPE" = "kubernetes" ] || [ "$DEPLOYMENT_TYPE" = "hybrid" ]; then
                deploy_kubernetes
            fi
            
            run_health_checks
            show_deployment_status
            ;;
        status)
            show_deployment_status
            ;;
        health)
            run_health_checks
            ;;
        rollback)
            rollback_deployment
            ;;
        backup)
            create_backup
            ;;
        clean)
            print_log "INFO" "Cleaning up deployment..."
            if [ "$DEPLOYMENT_TYPE" = "docker" ] || [ "$DEPLOYMENT_TYPE" = "hybrid" ]; then
                docker-compose -f "$COMPOSE_FILE" down --remove-orphans --volumes
            fi
            if [ "$DEPLOYMENT_TYPE" = "kubernetes" ] || [ "$DEPLOYMENT_TYPE" = "hybrid" ]; then
                kubectl delete namespace forensic-platform --ignore-not-found=true
                kubectl delete namespace monitoring --ignore-not-found=true
            fi
            print_log "SUCCESS" "Cleanup completed"
            ;;
        *)
            print_log "ERROR" "No command specified"
            show_usage
            exit 1
            ;;
    esac
    
    print_log "SUCCESS" "Enhanced deployment process completed successfully!"
}

# Run main function
main "$@"
