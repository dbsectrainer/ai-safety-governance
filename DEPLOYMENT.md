# Deployment Guide

This guide provides detailed instructions for deploying the AI Safety & Governance system in various environments.

## Prerequisites

- AWS Account with appropriate IAM permissions
- Docker (20.10.x or later)
- Kubernetes (1.20.x or later)
- kubectl configured for your cluster
- Python 3.8 or later
- AWS CLI configured

## Local Development Deployment

1. Clone the repository:
```bash
git clone https://github.com/yourusername/ai-safety-governance.git
cd ai-safety-governance
```

2. Create and activate virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: .\venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Run locally:
```bash
python src/main.py
```

## Docker Deployment

1. Build the Docker image:
```bash
docker build -t ai-safety-governance .
```

2. Run with Docker Compose:
```bash
docker-compose up --build
```

## Kubernetes Deployment

1. Configure AWS credentials:
```bash
aws configure
```

2. Update kubeconfig:
```bash
aws eks update-kubeconfig --name ai-safety-cluster --region your-region
```

3. Deploy to Kubernetes:
```bash
kubectl apply -f kubernetes/deployment.yaml
kubectl apply -f kubernetes/service.yaml
```

4. Verify deployment:
```bash
kubectl get pods
kubectl get services
```

## Production Deployment

### AWS EKS Setup

1. Create EKS cluster:
```bash
eksctl create cluster \
    --name ai-safety-cluster \
    --region your-region \
    --node-type t3.medium \
    --nodes 3
```

2. Configure AWS services:
- Set up CloudWatch logging
- Configure Prometheus monitoring
- Enable AWS X-Ray tracing

### CI/CD Pipeline

1. Configure GitHub Secrets:
- AWS_ACCESS_KEY_ID
- AWS_SECRET_ACCESS_KEY
- ECR_REGISTRY

2. Push to main branch to trigger deployment:
```bash
git push origin main
```

## Monitoring Setup

1. Access Prometheus:
```bash
kubectl port-forward svc/prometheus 9090:9090
```

2. Access CloudWatch Logs:
- Navigate to AWS CloudWatch console
- Select log group: ai-safety-governance

## Troubleshooting

### Common Issues

1. Pod startup failures:
```bash
kubectl describe pod <pod-name>
kubectl logs <pod-name>
```

2. Service connectivity:
```bash
kubectl get svc
kubectl describe svc ai-safety-governance
```

3. Configuration issues:
- Verify environment variables
- Check AWS credentials
- Validate Kubernetes configs

## Rollback Procedure

1. Find previous deployment:
```bash
kubectl rollout history deployment/ai-safety-governance
```

2. Rollback to previous version:
```bash
kubectl rollout undo deployment/ai-safety-governance
```

## Security Considerations

1. Enable AWS Security Groups
2. Configure Network Policies
3. Implement Pod Security Policies
4. Regular security audits
5. Monitor CloudWatch Logs
6. Enable AWS GuardDuty

## Performance Optimization

1. Resource Requests/Limits
2. HPA Configuration
3. Cluster Autoscaling
4. Cache Implementation
5. Load Balancer Setup

## Backup and Recovery

1. Regular State Backups
2. Database Snapshots
3. Configuration Backups
4. Disaster Recovery Plan

For additional support, please refer to the documentation or contact the development team.
