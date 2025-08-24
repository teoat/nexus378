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

# Check if namespace exists
check_namespace() {
    kubectl get namespace forensic-platform >/dev/null 2>&1
    return $?
}

# Cleanup persistent volumes
cleanup_pvs() {
    log_info "Cleaning up persistent volumes..."
    
    # Get all PVs associated with the namespace
    PVS=$(kubectl get pv -o json | jq -r '.items[] | select(.spec.claimRef.namespace == "forensic-platform") | .metadata.name')
    
    for pv in $PVS; do
        log_info "Deleting PV: $pv"
        kubectl delete pv "$pv" --force --grace-period=0
    done
}

# Remove Helm releases
remove_helm_releases() {
    log_info "Removing Helm releases..."
    
    # List all Helm releases in the namespace
    RELEASES=$(helm list -n forensic-platform -q)
    
    for release in $RELEASES; do
        log_info "Uninstalling Helm release: $release"
        helm uninstall "$release" -n forensic-platform
    done
}

# Delete namespace and resources
delete_namespace() {
    log_info "Deleting namespace and associated resources..."
    
    # Delete the namespace
    kubectl delete namespace forensic-platform --force --grace-period=0
    
    # Wait for namespace deletion
    while kubectl get namespace forensic-platform >/dev/null 2>&1; do
        log_info "Waiting for namespace deletion..."
        sleep 5
    done
}

# Cleanup Docker images
cleanup_docker_images() {
    log_info "Cleaning up Docker images..."
    
    # List of images to remove
    IMAGES=(
        "nexus:enhanced"
        "api_gateway:latest"
        "encryption-service:latest"
        "hash-service:latest"
        "chain-of-custody-service:latest"
        "data-retention-service:latest"
        "gdpr-service:latest"
    )
    
    for image in "${IMAGES[@]}"; do
        if docker images | grep -q "$(echo $image | cut -d: -f1)"; then
            log_info "Removing Docker image: $image"
            docker rmi "$image" || true
        fi
    done
}

# Main cleanup process
main() {
    log_warn "This script will remove all forensic platform resources, including data. Are you sure? (y/N)"
    read -r response
    
    if [[ "$response" =~ ^([yY][eE][sS]|[yY])+$ ]]; then
        # Check if namespace exists
        if check_namespace; then
            # Remove Helm releases first
            remove_helm_releases
            
            # Cleanup PVs
            cleanup_pvs
            
            # Delete namespace
            delete_namespace
        else
            log_warn "Namespace 'forensic-platform' not found, skipping Kubernetes cleanup"
        fi
        
        # Cleanup Docker images
        cleanup_docker_images
        
        log_info "Cleanup completed successfully!"
    else
        log_info "Cleanup cancelled"
    fi
}

# Execute main function
main