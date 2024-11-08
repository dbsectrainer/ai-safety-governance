# Deployment Guide

This guide provides comprehensive instructions for deploying the AI Safety & Governance platform in production environments.

## Prerequisites

### Infrastructure Requirements
- AWS Account with appropriate permissions
- Kubernetes 1.21+
- Docker 20.10+
- Helm 3.0+
- FluxCD
- Istio 1.12+
- Chaos Mesh
- kubectl CLI tool
- AWS CLI v2

### Required Permissions
- EKS cluster administration
- ECR repository access
- CloudWatch logs access
- Secrets Manager access
- KMS key management
- IAM role management
- SageMaker deployment permissions

## Environment Setup

### 1. AWS Configuration

1. Configure AWS CLI:
```bash
aws configure
```

2. Create required IAM roles:
```bash
aws iam create-role --role-name ai-safety-eks-role --assume-role-policy-document file://config/aws_config.json
```

3. Create KMS keys for encryption:
```bash
aws kms create-key --description "AI Safety Encryption Key"
```

4. Configure Secrets Manager:
```bash
aws secretsmanager create-secret --name ai-safety-secrets \
  --description "AI Safety Platform Secrets" \
  --secret-string file://config/secrets.json
```

### 2. GitOps Setup

1. Install FluxCD:
```bash
flux install

# Bootstrap Git repository
flux bootstrap github \
  --owner=$GITHUB_USER \
  --repository=ai-safety-governance \
  --branch=main \
  --path=./kubernetes/flux
```

2. Configure Flux sources:
```bash
flux create source git ai-safety-governance \
  --url=https://github.com/$GITHUB_USER/ai-safety-governance \
  --branch=main \
  --interval=1m
```

### 3. Service Mesh Setup

1. Install Istio:
```bash
istioctl install -f kubernetes/service-mesh/istio-config.yaml

# Enable injection
kubectl label namespace ai-safety istio-injection=enabled
```

2. Configure mTLS:
```bash
kubectl apply -f kubernetes/service-mesh/mtls-policy.yaml
```

3. Setup monitoring:
```bash
kubectl apply -f kubernetes/service-mesh/monitoring/
```

### 4. Chaos Engineering Setup

1. Install Chaos Mesh:
```bash
helm repo add chaos-mesh https://charts.chaos-mesh.org
helm install chaos-mesh chaos-mesh/chaos-mesh \
  --namespace=chaos-testing \
  --create-namespace \
  --values=kubernetes/chaos/values.yaml
```

2. Configure chaos experiments:
```bash
kubectl apply -f kubernetes/chaos/chaos-mesh.yaml
```

## Deployment Steps

### 1. Infrastructure Components

1. Deploy monitoring stack:
```bash
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm install prometheus prometheus-community/kube-prometheus-stack \
  --namespace monitoring \
  --values devops/monitoring/prometheus_config.yaml
```

2. Configure logging:
```bash
kubectl apply -f devops/logging/cloudwatch_config.json
```

3. Setup secret rotation:
```bash
kubectl apply -f kubernetes/security/secret-rotation/
```

### 2. Core Services Deployment

1. Deploy model monitoring:
```bash
kubectl apply -f kubernetes/model-monitoring/
```

2. Deploy security services:
```bash
kubectl apply -f kubernetes/security/
```

3. Deploy privacy protection:
```bash
kubectl apply -f kubernetes/privacy/
```

### 3. A/B Testing Setup

1. Configure A/B testing framework:
```bash
kubectl apply -f kubernetes/ab-testing/
```

2. Setup experiment tracking:
```bash
kubectl apply -f kubernetes/ab-testing/tracking/
```

### 4. Model Rollback Configuration

1. Configure rollback manager:
```bash
kubectl apply -f kubernetes/model-rollback/
```

2. Setup monitoring triggers:
```bash
kubectl apply -f kubernetes/model-rollback/triggers/
```

## Verification

### 1. Infrastructure Verification

1. Check GitOps sync:
```bash
flux get kustomizations
```

2. Verify service mesh:
```bash
istioctl analyze
```

3. Test chaos experiments:
```bash
kubectl apply -f kubernetes/chaos/test-experiment.yaml
```

### 2. Security Verification

1. Verify mTLS:
```bash
istioctl authn tls-check
```

2. Check secret rotation:
```bash
kubectl get secretproviderclass
```

3. Verify network policies:
```bash
kubectl describe networkpolicies -n ai-safety
```

### 3. Monitoring Verification

1. Access Grafana:
```bash
kubectl port-forward svc/grafana 3000:3000 -n monitoring
```

2. Check Prometheus metrics:
```bash
kubectl port-forward svc/prometheus-server 9090:9090 -n monitoring
```

## Production Considerations

### High Availability
1. Multi-zone deployment
2. Pod anti-affinity
3. Horizontal pod autoscaling
4. Node auto-scaling
5. Database replication

### Security Hardening
1. Regular security audits
2. Certificate rotation
3. Secret rotation
4. Network policy reviews
5. Compliance checks

### Monitoring & Alerting
1. Set up alert rules
2. Configure on-call rotations
3. Implement incident response
4. Enable audit logging
5. Configure metric retention

### Backup & Recovery
1. Regular state backups
2. Disaster recovery testing
3. Data retention policies
4. Backup verification
5. Recovery procedures

## Troubleshooting

### Common Issues

1. GitOps sync issues:
```bash
flux logs --all-namespaces
```

2. Service mesh problems:
```bash
istioctl proxy-status
istioctl proxy-config all
```

3. Chaos testing issues:
```bash
kubectl logs -n chaos-testing -l app.kubernetes.io/component=controller-manager
```

### Performance Issues

1. Check resource usage:
```bash
kubectl top pods -n ai-safety
```

2. Monitor service mesh:
```bash
istioctl dashboard envoy
```

3. Analyze metrics:
```bash
kubectl port-forward -n monitoring svc/grafana 3000:3000
```

## Maintenance

### Regular Updates
1. Update dependencies
2. Patch security vulnerabilities
3. Rotate certificates
4. Update compliance checks
5. Refresh chaos tests

### Scaling
1. Adjust resource limits
2. Configure auto-scaling
3. Optimize performance
4. Monitor capacity
5. Plan for growth

## Support

For production support:
1. Check logs and metrics
2. Review documentation
3. Open GitHub issues
4. Contact security team
