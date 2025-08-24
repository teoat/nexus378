# Forensic Platform Helm Chart

## Overview
This Helm chart deploys the Nexus Platform on Kubernetes, providing a complete infrastructure for digital forensics and evidence management.

## Prerequisites
- Kubernetes 1.19+
- Helm 3.0+
- Istio service mesh installed in the cluster
- Dynamic volume provisioning support
- Metrics server installed for HPA functionality

## Features
- Complete microservices architecture deployment
- Integrated monitoring stack with Prometheus and Grafana
- Automatic horizontal scaling
- Persistent storage management
- Service mesh integration with Istio
- RBAC configuration
- Health monitoring and readiness probes

## Installation

1. Add required Helm repositories:
```bash
helm repo add bitnami https://charts.bitnami.com/bitnami
helm repo add elastic https://helm.elastic.co
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm repo add grafana https://grafana.github.io/helm-charts
helm repo update
```

2. Install the chart:
```bash
helm install forensic-platform ./helm \
  --namespace forensic-platform \
  --create-namespace \
  --set global.environment=production
```

## Configuration

The following table lists the configurable parameters of the chart and their default values.

### Global Parameters

| Parameter | Description | Default |
|-----------|-------------|----------|
| `global.environment` | Environment name | `production` |
| `global.imageRegistry` | Global Docker image registry | `""` |
| `global.imagePullSecrets` | Global Docker registry secret names | `[]` |
| `global.storageClass` | Global storage class for dynamic provisioning | `standard` |

### Main Application Parameters

| Parameter | Description | Default |
|-----------|-------------|----------|
| `forensicApp.image.repository` | Image repository | `nexus` |
| `forensicApp.image.tag` | Image tag | `enhanced` |
| `forensicApp.replicaCount` | Number of replicas | `3` |
| `forensicApp.resources` | CPU/Memory resource requests/limits | See values.yaml |

### API Gateway Parameters

| Parameter | Description | Default |
|-----------|-------------|----------|
| `apiGateway.image.repository` | Image repository | `api_gateway` |
| `apiGateway.image.tag` | Image tag | `latest` |
| `apiGateway.replicaCount` | Number of replicas | `2` |

### Persistence Parameters

| Parameter | Description | Default |
|-----------|-------------|----------|
| `forensicApp.persistence.logs.size` | Size of logs PVC | `10Gi` |
| `forensicApp.persistence.uploads.size` | Size of uploads PVC | `50Gi` |
| `forensicApp.persistence.reports.size` | Size of reports PVC | `20Gi` |

### Autoscaling Parameters

| Parameter | Description | Default |
|-----------|-------------|----------|
| `autoscaling.enabled` | Enable autoscaling | `true` |
| `autoscaling.minReplicas` | Minimum replicas | `1` |
| `autoscaling.maxReplicas` | Maximum replicas | `10` |
| `autoscaling.targetCPUUtilizationPercentage` | Target CPU utilization | `80` |

### Dependencies Parameters

| Parameter | Description | Default |
|-----------|-------------|----------|
| `postgresql.enabled` | Enable PostgreSQL | `true` |
| `redis.enabled` | Enable Redis | `true` |
| `rabbitmq.enabled` | Enable RabbitMQ | `true` |
| `elasticsearch.enabled` | Enable Elasticsearch | `true` |
| `kibana.enabled` | Enable Kibana | `true` |
| `prometheus.enabled` | Enable Prometheus | `true` |
| `grafana.enabled` | Enable Grafana | `true` |

## Upgrading

To upgrade the release:
```bash
helm upgrade forensic-platform ./helm \
  --namespace forensic-platform \
  --set forensicApp.image.tag=new-version
```

## Uninstallation

To uninstall the release:
```bash
helm uninstall forensic-platform -n forensic-platform
```

## Backup and Restore

### Backup
The following data should be backed up:
- PostgreSQL data
- Elasticsearch indices
- MinIO objects
- Redis data (if persistence is enabled)
- RabbitMQ data (if persistence is enabled)

### Restore
1. Restore the backed-up data to the respective PVCs
2. Reinstall the chart pointing to the restored PVCs

## Monitoring

The platform comes with built-in monitoring:
- Prometheus for metrics collection
- Grafana for visualization
- Service and pod metrics
- Custom application metrics

Access Grafana:
```bash
kubectl port-forward svc/forensic-platform-grafana 3000:80 -n forensic-platform
```

## Troubleshooting

### Common Issues

1. Pending PVCs
- Check storage class availability
- Verify PV provisioner is running

2. Pod Startup Failures
- Check pod events: `kubectl describe pod [pod-name] -n forensic-platform`
- View logs: `kubectl logs [pod-name] -n forensic-platform`

3. Service Connectivity
- Verify service endpoints: `kubectl get endpoints -n forensic-platform`
- Check Istio gateway and virtual service configuration

## Security Considerations

1. Secrets Management
- All sensitive data is stored in Kubernetes secrets
- Use external secrets management solutions in production

2. Network Policies
- Configure network policies to restrict pod-to-pod communication
- Enable mTLS in Istio

3. RBAC
- Service accounts with minimal required permissions
- Role-based access control for all components