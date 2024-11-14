import logging
import yaml
import json
import os
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict

import kubernetes
from kubernetes import client, config
from kubernetes.client.rest import ApiException

import git
import semver

@dataclass
class DeploymentStrategy:
    name: str
    type: str
    rollback_threshold: float
    canary_weight: Optional[float] = None
    blue_green_config: Optional[Dict] = None

@dataclass
class DeploymentMetrics:
    version: str
    success_rate: float
    error_rate: float
    response_time: float
    resource_utilization: Dict
    timestamp: str

class AdvancedDeploymentManager:
    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize Advanced Deployment Manager
        
        Args:
            config_path: Optional path to Kubernetes config
        """
        self.logger = logging.getLogger(__name__)
        
        # Load Kubernetes configuration
        try:
            if config_path:
                config.load_kube_config(config_path)
            else:
                config.load_incluster_config()
            
            self.k8s_apps_v1 = client.AppsV1Api()
            self.k8s_core_v1 = client.CoreV1Api()
        except Exception as e:
            self.logger.error(f"Kubernetes configuration error: {e}")
            raise
        
        # Git repository management
        self.repo = self._initialize_git_repository()
        
        # Deployment tracking
        self.deployment_history: List[DeploymentMetrics] = []
        self.deployment_strategies: Dict[str, DeploymentStrategy] = {}
        
        # Load deployment configurations
        self._load_deployment_strategies()
    
    def _initialize_git_repository(self) -> git.Repo:
        """
        Initialize Git repository for version tracking
        
        Returns:
            Initialized Git repository
        """
        try:
            repo_path = os.getcwd()
            return git.Repo(repo_path)
        except Exception as e:
            self.logger.error(f"Git repository initialization error: {e}")
            raise
    
    def _load_deployment_strategies(self):
        """
        Load deployment strategies from configuration
        """
        config_path = 'config/deployment_strategies.yaml'
        if os.path.exists(config_path):
            try:
                with open(config_path, 'r') as f:
                    strategies = yaml.safe_load(f)
                    for name, strategy_config in strategies.items():
                        self.deployment_strategies[name] = DeploymentStrategy(
                            name=name,
                            type=strategy_config.get('type', 'rolling-update'),
                            rollback_threshold=strategy_config.get('rollback_threshold', 0.5),
                            canary_weight=strategy_config.get('canary_weight'),
                            blue_green_config=strategy_config.get('blue_green_config')
                        )
            except Exception as e:
                self.logger.warning(f"Error loading deployment strategies: {e}")
    
    def deploy(self, service_name: str, image: str, version: str):
        """
        Deploy a new version of a service
        
        Args:
            service_name: Name of the service to deploy
            image: Docker image to deploy
            version: Version of the service
        """
        try:
            # Select deployment strategy
            strategy = self._select_deployment_strategy(service_name)
            
            # Perform deployment based on strategy
            if strategy.type == 'canary':
                self._canary_deployment(service_name, image, version, strategy)
            elif strategy.type == 'blue-green':
                self._blue_green_deployment(service_name, image, version, strategy)
            else:
                self._rolling_update_deployment(service_name, image, version)
            
            # Track deployment
            self._track_deployment(service_name, version)
        
        except Exception as e:
            self.logger.error(f"Deployment failed for {service_name}: {e}")
            raise
    
    def _select_deployment_strategy(self, service_name: str) -> DeploymentStrategy:
        """
        Select appropriate deployment strategy
        
        Args:
            service_name: Name of the service
            
        Returns:
            Selected deployment strategy
        """
        # Default to rolling update if no specific strategy defined
        return self.deployment_strategies.get(
            service_name, 
            DeploymentStrategy(
                name='default', 
                type='rolling-update', 
                rollback_threshold=0.5
            )
        )
    
    def _rolling_update_deployment(self, service_name: str, image: str, version: str):
        """
        Perform standard rolling update deployment
        
        Args:
            service_name: Name of the service
            image: Docker image to deploy
            version: Version of the service
        """
        try:
            # Get current deployment
            deployment = self.k8s_apps_v1.read_namespaced_deployment(
                name=service_name, 
                namespace='default'
            )
            
            # Update image
            deployment.spec.template.spec.containers[0].image = f"{image}:{version}"
            
            # Apply update
            self.k8s_apps_v1.patch_namespaced_deployment(
                name=service_name, 
                namespace='default', 
                body=deployment
            )
        
        except ApiException as e:
            self.logger.error(f"Rolling update failed: {e}")
            raise
    
    def _canary_deployment(self, service_name: str, image: str, version: str, strategy: DeploymentStrategy):
        """
        Perform canary deployment
        
        Args:
            service_name: Name of the service
            image: Docker image to deploy
            version: Version of the service
            strategy: Deployment strategy configuration
        """
        try:
            # Create canary deployment with reduced weight
            canary_deployment = self._create_canary_deployment(
                service_name, 
                image, 
                version, 
                strategy.canary_weight or 0.2
            )
            
            # Monitor canary deployment
            self._monitor_canary_deployment(canary_deployment, strategy)
        
        except Exception as e:
            self.logger.error(f"Canary deployment failed: {e}")
            raise
    
    def _blue_green_deployment(self, service_name: str, image: str, version: str, strategy: DeploymentStrategy):
        """
        Perform blue-green deployment
        
        Args:
            service_name: Name of the service
            image: Docker image to deploy
            version: Version of the service
            strategy: Deployment strategy configuration
        """
        try:
            # Create new (green) deployment
            green_deployment = self._create_blue_green_deployment(
                service_name, 
                image, 
                version, 
                strategy.blue_green_config
            )
            
            # Switch traffic gradually
            self._switch_traffic(green_deployment, strategy)
        
        except Exception as e:
            self.logger.error(f"Blue-green deployment failed: {e}")
            raise
    
    def _create_canary_deployment(self, service_name: str, image: str, version: str, weight: float) -> Dict:
        """
        Create canary deployment
        
        Args:
            service_name: Name of the service
            image: Docker image to deploy
            version: Version of the service
            weight: Traffic weight for canary
            
        Returns:
            Created canary deployment
        """
        # Placeholder for canary deployment creation
        return {}
    
    def _monitor_canary_deployment(self, canary_deployment: Dict, strategy: DeploymentStrategy):
        """
        Monitor canary deployment and make decisions
        
        Args:
            canary_deployment: Canary deployment details
            strategy: Deployment strategy configuration
        """
        # Implement canary monitoring logic
        pass
    
    def _create_blue_green_deployment(self, service_name: str, image: str, version: str, config: Dict) -> Dict:
        """
        Create blue-green deployment
        
        Args:
            service_name: Name of the service
            image: Docker image to deploy
            version: Version of the service
            config: Blue-green deployment configuration
            
        Returns:
            Created blue-green deployment
        """
        # Placeholder for blue-green deployment creation
        return {}
    
    def _switch_traffic(self, deployment: Dict, strategy: DeploymentStrategy):
        """
        Switch traffic between blue and green deployments
        
        Args:
            deployment: Deployment to switch to
            strategy: Deployment strategy configuration
        """
        # Implement traffic switching logic
        pass
    
    def _track_deployment(self, service_name: str, version: str):
        """
        Track deployment metrics
        
        Args:
            service_name: Name of the service
            version: Deployed version
        """
        metrics = DeploymentMetrics(
            version=version,
            success_rate=self._calculate_success_rate(service_name),
            error_rate=self._calculate_error_rate(service_name),
            response_time=self._calculate_response_time(service_name),
            resource_utilization=self._get_resource_utilization(service_name),
            timestamp=datetime.utcnow().isoformat()
        )
        
        self.deployment_history.append(metrics)
    
    def rollback(self, service_name: str, target_version: Optional[str] = None):
        """
        Rollback service to previous version
        
        Args:
            service_name: Name of the service
            target_version: Optional specific version to rollback to
        """
        try:
            # If no target version specified, find last stable version
            if not target_version:
                target_version = self._find_last_stable_version(service_name)
            
            # Perform rollback
            deployment = self.k8s_apps_v1.read_namespaced_deployment(
                name=service_name, 
                namespace='default'
            )
            
            # Update to target version
            deployment.spec.template.spec.containers[0].image = f"{service_name}:{target_version}"
            
            self.k8s_apps_v1.patch_namespaced_deployment(
                name=service_name, 
                namespace='default', 
                body=deployment
            )
            
            self.logger.info(f"Rolled back {service_name} to version {target_version}")
        
        except Exception as e:
            self.logger.error(f"Rollback failed for {service_name}: {e}")
            raise
    
    def _find_last_stable_version(self, service_name: str) -> str:
        """
        Find last stable version for rollback
        
        Args:
            service_name: Name of the service
            
        Returns:
            Last stable version
        """
        # Filter deployment history for the service
        service_history = [
            metrics for metrics in self.deployment_history 
            if metrics.success_rate > 0.95
        ]
        
        # Sort by timestamp and get the most recent stable version
        if service_history:
            return max(service_history, key=lambda x: x.timestamp).version
        
        # Fallback to previous version from Git
        return self._get_previous_git_version(service_name)
    
    def _get_previous_git_version(self, service_name: str) -> str:
        """
        Get previous version from Git history
        
        Args:
            service_name: Name of the service
            
        Returns:
            Previous version from Git
        """
        try:
            # Get previous commit
            previous_commit = self.repo.head.commit.parents[0]
            
            # Extract version from commit or tags
            # This is a simplified example and should be adapted to your versioning strategy
            return previous_commit.hexsha[:7]
        
        except Exception as e:
            self.logger.error(f"Failed to get previous Git version: {e}")
            return "latest"
    
    def _calculate_success_rate(self, service_name: str) -> float:
        """
        Calculate service success rate
        
        Args:
            service_name: Name of the service
            
        Returns:
            Success rate
        """
        # Placeholder for success rate calculation
        return 1.0
    
    def _calculate_error_rate(self, service_name: str) -> float:
        """
        Calculate service error rate
        
        Args:
            service_name: Name of the service
            
        Returns:
            Error rate
        """
        # Placeholder for error rate calculation
        return 0.0
    
    def _calculate_response_time(self, service_name: str) -> float:
        """
        Calculate service response time
        
        Args:
            service_name: Name of the service
            
        Returns:
            Average response time
        """
        # Placeholder for response time calculation
        return 0.0
    
    def _get_resource_utilization(self, service_name: str) -> Dict:
        """
        Get service resource utilization
        
        Args:
            service_name: Name of the service
            
        Returns:
            Resource utilization metrics
        """
        # Placeholder for resource utilization calculation
        return {
            'cpu': 0.0,
            'memory': 0.0
        }

class DeploymentReportGenerator:
    @staticmethod
    def generate_report(deployment_history: List[DeploymentMetrics]) -> Dict:
        """
        Generate comprehensive deployment report
        
        Args:
            deployment_history: List of deployment metrics
            
        Returns:
            Comprehensive deployment report
        """
        report = {
            'total_deployments': len(deployment_history),
            'deployment_summary': {},
            'performance_metrics': {},
            'recommendations': []
        }
        
        # Analyze deployment performance
        success_rates = [metrics.success_rate for metrics in deployment_history]
        error_rates = [metrics.error_rate for metrics in deployment_history]
        response_times = [metrics.response_time for metrics in deployment_history]
        
        report['performance_metrics'] = {
            'average_success_rate': sum(success_rates) / len(success_rates),
            'average_error_rate': sum(error_rates) / len(error_rates),
            'average_response_time': sum(response_times) / len(response_times)
        }
        
        # Generate recommendations
        if report['performance_metrics']['average_success_rate'] < 0.95:
            report['recommendations'].append(
                "Deployment success rate is low. Review deployment strategies and service configurations."
            )
        
        return report
