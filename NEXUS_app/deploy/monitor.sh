#!/bin/bash

set -e

# Color codes for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
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

log_section() {
    echo -e "\n${BLUE}=== $1 ===${NC}\n"
}

# Check pod health
check_pod_health() {
    log_section "Pod Health Status"
    
    # Get all pods in the namespace
    kubectl get pods -n forensic-platform -o wide
    
    # Check for pods not in Running state
    NOT_RUNNING=$(kubectl get pods -n forensic-platform --field-selector status.phase!=Running -o name)
    if [ -n "$NOT_RUNNING" ]; then
        log_warn "The following pods are not running:"
        echo "$NOT_RUNNING"
        
        # Get events for non-running pods
        for pod in $NOT_RUNNING; do
            log_warn "Events for $pod:"
            kubectl describe $pod -n forensic-platform | grep -A 10 Events:
        done
    fi
}

# Check resource usage
check_resource_usage() {
    log_section "Resource Usage"
    
    # Get resource usage for all pods
    kubectl top pods -n forensic-platform
    
    # Get resource usage for nodes
    kubectl top nodes
}

# Check HPA status
check_hpa_status() {
    log_section "HPA Status"
    
    kubectl get hpa -n forensic-platform
}

# Check service health
check_service_health() {
    log_section "Service Health"
    
    # Get all services
    kubectl get svc -n forensic-platform
    
    # Check endpoints
    kubectl get endpoints -n forensic-platform
}

# Check persistent volumes
check_volumes() {
    log_section "Persistent Volumes Status"
    
    # Get PVCs
    kubectl get pvc -n forensic-platform
    
    # Get PVs
    kubectl get pv | grep forensic-platform
}

# Check logs for errors
check_logs() {
    log_section "Recent Error Logs"
    
    # Get all pods
    PODS=$(kubectl get pods -n forensic-platform -o name)
    
    for pod in $PODS; do
        log_info "Checking logs for $pod"
        kubectl logs $pod -n forensic-platform --tail=50 | grep -i "error\|exception\|failed" || true
    done
}

# Check Istio status
check_istio() {
    log_section "Istio Status"
    
    # Check gateway status
    kubectl get gateway -n forensic-platform
    
    # Check virtual services
    kubectl get virtualservice -n forensic-platform
}

# Monitor specific service
monitor_service() {
    service=$1
    log_section "Monitoring Service: $service"
    
    # Get service details
    kubectl describe service $service -n forensic-platform
    
    # Get pods for service
    kubectl get pods -l app=$service -n forensic-platform
    
    # Get logs
    kubectl logs -l app=$service -n forensic-platform --tail=50
}

# Main monitoring process
main() {
    while true; do
        clear
        log_info "Forensic Platform Monitoring Dashboard"
        log_info "Timestamp: $(date)"
        
        # Run all checks
        check_pod_health
        check_resource_usage
        check_hpa_status
        check_service_health
        check_volumes
        check_istio
        check_logs
        
        # Wait before next update
        log_info "\nRefreshing in 30 seconds... (Press Ctrl+C to exit)"
        sleep 30
    done
}

# Parse command line arguments
if [ "$1" ]; then
    monitor_service "$1"
    exit 0
fi

# Execute main monitoring loop
main