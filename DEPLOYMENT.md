# Deployment Guide

This guide provides detailed instructions for deploying the AI Safety & Governance platform in a production environment.

## Prerequisites

### Infrastructure Requirements
- AWS Account with appropriate permissions
- Kubernetes 1.21+
- Docker 20.10+
- Helm 3.0+
- kubectl CLI tool
- AWS CLI v2

### Required Permissions
- EKS cluster administration
- ECR repository access
- CloudWatch logs access
- Secrets Manager access
- KMS key management
- IAM role management

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

### 2. EKS Cluster Setup

1. Create EKS cluster:
```bash
eksctl create cluster -f kubernetes/cluster.yaml
```

2. Configure kubectl:
```bash
aws eks update-kubeconfig --name ai-safety-cluster --region your-region
```

3. Create namespaces:
```bash
kubectl create namespace ai-safety
kubectl create namespace monitoring
kubectl create namespace logging
```

### 3. Security Configuration

1. Apply RBAC configurations:
```bash
kubectl apply -f kubernetes/rbac/
```

2. Create secrets:
```bash
kubectl create secret generic ai-safety-secrets \
  --from-file=config/secrets.env \
  --namespace ai-safety
```

3. Apply network policies:
```bash
kubectl apply -f kubernetes/network-policies/
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

### 2. Application Deployment

1. Deploy core services:
```bash
kubectl apply -f kubernetes/deployment.yaml
kubectl apply -f kubernetes/service.yaml
```

2. Verify deployment:
```bash
kubectl get pods -n ai-safety
kubectl get services -n ai-safety
```

3. Apply security policies:
```bash
kubectl apply -f kubernetes/security/
```

### 3. Post-Deployment Configuration

1. Configure monitoring:
```bash
kubectl apply -f devops/monitoring/
```

2. Setup alerts:
```bash
kubectl apply -f devops/alerts/
```

3. Configure autoscaling:
```bash
kubectl apply -f kubernetes/hpa.yaml
```

## Verification

### 1. Security Checks

1. Verify RBAC:
```bash
kubectl auth can-i --list --namespace ai-safety
```

2. Check network policies:
```bash
kubectl describe networkpolicies -n ai-safety
```

3. Verify encryption:
```bash
kubectl get pods -n ai-safety -o yaml | grep -i encryption
```

### 2. Monitoring Verification

1. Access Prometheus:
```bash
kubectl port-forward svc/prometheus-server 9090:9090 -n monitoring
```

2. Check CloudWatch logs:
```bash
aws logs describe-log-groups --log-group-prefix /ai-safety
```

### 3. Performance Testing

1. Run load tests:
```bash
kubectl apply -f tests/load-test.yaml
```

2. Monitor metrics:
```bash
kubectl port-forward svc/grafana 3000:3000 -n monitoring
```

## Maintenance

### Backup and Recovery

1. Configure backups:
```bash
kubectl apply -f kubernetes/backup/
```

2. Verify backup status:
```bash
velero backup-location get
```

### Updates and Patches

1. Update dependencies:
```bash
helm dependency update
```

2. Apply security patches:
```bash
kubectl apply -f kubernetes/security/patches/
```

### Scaling

1. Adjust HPA settings:
```bash
kubectl edit hpa ai-safety-governance-hpa -n ai-safety
```

2. Scale worker nodes:
```bash
eksctl scale nodegroup --cluster=ai-safety-cluster --nodes=3
```

## Troubleshooting

### Common Issues

1. Pod startup failures:
```bash
kubectl describe pod <pod-name> -n ai-safety
kubectl logs <pod-name> -n ai-safety
```

2. Network connectivity:
```bash
kubectl exec -it <pod-name> -n ai-safety -- ping <service-name>
```

3. Permission issues:
```bash
kubectl auth reconcile -f kubernetes/rbac/
```

### Monitoring and Debugging

1. View real-time logs:
```bash
kubectl logs -f deployment/ai-safety-governance -n ai-safety
```

2. Check metrics:
```bash
kubectl top pods -n ai-safety
```

3. Debug network policies:
```bash
kubectl exec -it <pod-name> -n ai-safety -- wget -qO- http://another-service
```

## Security Considerations

1. Regular security audits
2. Certificate rotation
3. Secret management
4. Access reviews
5. Security patch management

## Compliance

1. Maintain audit logs
2. Regular compliance checks
3. Data retention policy enforcement
4. Privacy protection verification

## Support

For production support:
1. Open GitHub issues for bug reports
2. Contact the security team for security-related issues
3. Review logs and metrics for troubleshooting
4. Consult AWS documentation for infrastructure issues
