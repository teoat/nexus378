#!/bin/bash

set -e

# Color codes for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Functions
log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

wait_for_pods() {
    namespace=$1
    echo "Waiting for pods in namespace ${namespace} to be ready..."
    kubectl wait --for=condition=Ready pods --all -n "${namespace}" --timeout=300s
}

# Check required tools
check_requirements() {
    log_info "Checking requirements..."
    
    command -v kubectl >/dev/null 2>&1 || { log_error "kubectl is required but not installed."; exit 1; }
    command -v helm >/dev/null 2>&1 || { log_error "helm is required but not installed."; exit 1; }
    command -v docker >/dev/null 2>&1 || { log_error "docker is required but not installed."; exit 1; }
}

# Add Helm repositories
add_helm_repos() {
    log_info "Adding Helm repositories..."
    
    helm repo add bitnami https://charts.bitnami.com/bitnami
    helm repo add elastic https://helm.elastic.co
    helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
    helm repo add grafana https://grafana.github.io/helm-charts
    helm repo update
}

# Build and push Docker images
build_images() {
    log_info "Building Docker images..."
    
    # Build main application image
    docker build -t nexus:enhanced .
    
    # Build API Gateway image
    docker build -t api_gateway:latest ./api_gateway
    
    # Build microservices images
    docker build -t encryption-service:latest ./encryption_service
    docker build -t hash-service:latest ./hash_service
    docker build -t chain-of-custody-service:latest ./chain_of_custody_service
    docker build -t data-retention-service:latest ./data_retention_service
    docker build -t gdpr-service:latest ./gdpr_service
}

# Deploy infrastructure
deploy_infrastructure() {
    log_info "Deploying infrastructure..."
    
    # Create namespace if it doesn't exist
    kubectl create namespace forensic-platform --dry-run=client -o yaml | kubectl apply -f -
    
    # Deploy Helm chart
    helm upgrade --install forensic-platform ./helm \
        --namespace forensic-platform \
        --set global.environment=production \
        --set forensicApp.image.tag=enhanced \
        --set apiGateway.image.tag=latest \
        --wait
    
    # Wait for all pods to be ready
    wait_for_pods "forensic-platform"
}

# Verify deployment
verify_deployment() {
    log_info "Verifying deployment..."
    
    # Check pod status
    kubectl get pods -n forensic-platform
    
    # Check services
    kubectl get svc -n forensic-platform
    
    # Check Istio gateway
    kubectl get gateway -n forensic-platform
    
    # Check HPA
    kubectl get hpa -n forensic-platform
}

# Main deployment process
main() {
    log_info "Starting deployment process..."
    
    # Check requirements
    check_requirements
    
    # Add Helm repositories
    add_helm_repos
    
    # Build and push images
    build_images
    
    # Deploy infrastructure
    deploy_infrastructure
    
    # Verify deployment
    verify_deployment
    
    log_info "Deployment completed successfully!"
    log_info "Access the application at: http://localhost"
    log_info "Access Grafana at: http://localhost:3000"
    log_info "Access Kibana at: http://localhost:5601"
}

# Execute main function
main