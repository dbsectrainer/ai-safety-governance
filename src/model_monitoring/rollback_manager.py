import logging
from typing import Dict, List, Optional
from datetime import datetime, timedelta
import json
import boto3
from dataclasses import dataclass
from enum import Enum

class RollbackTrigger(Enum):
    ACCURACY_DROP = "accuracy_drop"
    LATENCY_SPIKE = "latency_spike"
    ERROR_RATE_INCREASE = "error_rate_increase"
    DRIFT_DETECTED = "drift_detected"
    FAIRNESS_VIOLATION = "fairness_violation"
    MANUAL = "manual"

@dataclass
class ModelVersion:
    version_id: str
    s3_path: str
    deployment_time: str
    metrics: Dict
    config: Dict
    status: str

@dataclass
class RollbackEvent:
    trigger: RollbackTrigger
    old_version: str
    new_version: str
    timestamp: str
    reason: str
    metrics_before: Dict
    metrics_after: Dict
    status: str

class RollbackManager:
    def __init__(self, config: Dict):
        """
        Initialize RollbackManager
        
        Args:
            config: Configuration dictionary containing rollback settings
        """
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.INFO)
        
        # Initialize AWS clients
        self.s3_client = boto3.client('s3')
        self.sagemaker_client = boto3.client('sagemaker')
        
        # Configure settings
        self.config = config
        self.model_bucket = config['model_bucket']
        self.metrics_threshold = config.get('metrics_threshold', {
            'accuracy_drop': 0.05,
            'latency_increase': 100,  # ms
            'error_rate_increase': 0.02,
            'drift_threshold': 0.3
        })
        
        # Track versions and rollbacks
        self.model_versions = {}
        self.rollback_history = []
        
    def register_model_version(self, version_id: str, s3_path: str,
                             config: Dict, metrics: Dict) -> ModelVersion:
        """Register a new model version"""
        version = ModelVersion(
            version_id=version_id,
            s3_path=s3_path,
            deployment_time=datetime.utcnow().isoformat(),
            metrics=metrics,
            config=config,
            status='active'
        )
        
        self.model_versions[version_id] = version
        self.logger.info(f"Registered model version: {version_id}")
        
        return version
        
    def check_rollback_triggers(self, current_metrics: Dict) -> Optional[RollbackTrigger]:
        """Check if any rollback triggers are activated"""
        current_version = self._get_current_version()
        if not current_version:
            return None
            
        baseline_metrics = current_version.metrics
        
        # Check accuracy drop
        if (baseline_metrics['accuracy'] - current_metrics['accuracy'] > 
            self.metrics_threshold['accuracy_drop']):
            return RollbackTrigger.ACCURACY_DROP
            
        # Check latency spike
        if (current_metrics['latency_ms'] - baseline_metrics['latency_ms'] > 
            self.metrics_threshold['latency_increase']):
            return RollbackTrigger.LATENCY_SPIKE
            
        # Check error rate increase
        if (current_metrics['error_rate'] - baseline_metrics['error_rate'] > 
            self.metrics_threshold['error_rate_increase']):
            return RollbackTrigger.ERROR_RATE_INCREASE
            
        # Check data drift
        if current_metrics.get('drift_score', 0) > self.metrics_threshold['drift_threshold']:
            return RollbackTrigger.DRIFT_DETECTED
            
        # Check fairness violations
        if self._check_fairness_violations(current_metrics):
            return RollbackTrigger.FAIRNESS_VIOLATION
            
        return None
        
    def initiate_rollback(self, trigger: RollbackTrigger, 
                         current_metrics: Dict) -> RollbackEvent:
        """Initiate model rollback"""
        try:
            current_version = self._get_current_version()
            if not current_version:
                raise ValueError("No current version found")
                
            # Find best previous version
            previous_version = self._find_best_previous_version()
            if not previous_version:
                raise ValueError("No suitable previous version found")
                
            # Perform rollback
            rollback_event = self._perform_rollback(
                trigger,
                current_version,
                previous_version,
                current_metrics
            )
            
            # Update version statuses
            current_version.status = 'rolled_back'
            previous_version.status = 'active'
            
            # Record rollback event
            self.rollback_history.append(rollback_event)
            
            self.logger.info(
                f"Completed rollback from {current_version.version_id} "
                f"to {previous_version.version_id}"
            )
            
            return rollback_event
            
        except Exception as e:
            self.logger.error(f"Rollback failed: {str(e)}")
            raise
            
    def _perform_rollback(self, trigger: RollbackTrigger,
                         current_version: ModelVersion,
                         target_version: ModelVersion,
                         current_metrics: Dict) -> RollbackEvent:
        """Perform the actual rollback operation"""
        try:
            # Copy model artifacts
            self.s3_client.copy_object(
                Bucket=self.model_bucket,
                Key=f"models/active/model.tar.gz",
                CopySource={
                    'Bucket': self.model_bucket,
                    'Key': target_version.s3_path
                }
            )
            
            # Update SageMaker endpoint
            if self.config.get('use_sagemaker', False):
                self._update_sagemaker_endpoint(target_version)
            
            # Create rollback event
            event = RollbackEvent(
                trigger=trigger,
                old_version=current_version.version_id,
                new_version=target_version.version_id,
                timestamp=datetime.utcnow().isoformat(),
                reason=self._get_rollback_reason(trigger, current_metrics),
                metrics_before=current_metrics,
                metrics_after=target_version.metrics,
                status='completed'
            )
            
            return event
            
        except Exception as e:
            self.logger.error(f"Error during rollback: {str(e)}")
            raise
            
    def _update_sagemaker_endpoint(self, version: ModelVersion) -> None:
        """Update SageMaker endpoint to use specified model version"""
        try:
            self.sagemaker_client.update_endpoint(
                EndpointName=self.config['endpoint_name'],
                EndpointConfigName=version.config['endpoint_config_name']
            )
        except Exception as e:
            self.logger.error(f"Error updating SageMaker endpoint: {str(e)}")
            raise
            
    def _get_current_version(self) -> Optional[ModelVersion]:
        """Get current active model version"""
        active_versions = [v for v in self.model_versions.values() 
                         if v.status == 'active']
        return active_versions[0] if active_versions else None
        
    def _find_best_previous_version(self) -> Optional[ModelVersion]:
        """Find the best previous version to rollback to"""
        # Get all previous versions sorted by deployment time
        previous_versions = [
            v for v in self.model_versions.values()
            if v.status not in ['active', 'failed']
        ]
        
        if not previous_versions:
            return None
            
        # Sort by metrics (accuracy, latency, etc.)
        sorted_versions = sorted(
            previous_versions,
            key=lambda v: (
                v.metrics.get('accuracy', 0),
                -v.metrics.get('latency_ms', float('inf')),
                -v.metrics.get('error_rate', float('inf'))
            ),
            reverse=True
        )
        
        return sorted_versions[0] if sorted_versions else None
        
    def _check_fairness_violations(self, metrics: Dict) -> bool:
        """Check for fairness metric violations"""
        fairness_metrics = metrics.get('fairness_metrics', {})
        
        # Check demographic parity
        if fairness_metrics.get('demographic_parity_diff', 0) > 0.1:
            return True
            
        # Check equal opportunity
        if fairness_metrics.get('equal_opportunity_diff', 0) > 0.1:
            return True
            
        return False
        
    def _get_rollback_reason(self, trigger: RollbackTrigger,
                            metrics: Dict) -> str:
        """Generate detailed reason for rollback"""
        if trigger == RollbackTrigger.ACCURACY_DROP:
            return f"Accuracy dropped below threshold: {metrics['accuracy']:.3f}"
        elif trigger == RollbackTrigger.LATENCY_SPIKE:
            return f"Latency exceeded threshold: {metrics['latency_ms']}ms"
        elif trigger == RollbackTrigger.ERROR_RATE_INCREASE:
            return f"Error rate increased to: {metrics['error_rate']:.3f}"
        elif trigger == RollbackTrigger.DRIFT_DETECTED:
            return f"Data drift detected: {metrics.get('drift_score', 0):.3f}"
        elif trigger == RollbackTrigger.FAIRNESS_VIOLATION:
            return "Fairness metrics violated threshold"
        else:
            return "Manual rollback initiated"
            
    def get_rollback_history(self) -> List[RollbackEvent]:
        """Get history of rollback events"""
        return self.rollback_history
        
    def get_version_status(self, version_id: str) -> Optional[ModelVersion]:
        """Get status of a specific model version"""
        return self.model_versions.get(version_id)
        
    def list_versions(self) -> Dict[str, List[str]]:
        """List all model versions grouped by status"""
        versions_by_status = {}
        for version in self.model_versions.values():
            if version.status not in versions_by_status:
                versions_by_status[version.status] = []
            versions_by_status[version.status].append(version.version_id)
        return versions_by_status
