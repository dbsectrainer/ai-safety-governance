import boto3
import logging
from datetime import datetime, timedelta
from typing import Dict, Optional
import json
import hashlib
from botocore.exceptions import ClientError

class SecretManager:
    def __init__(self, config: Dict):
        """
        Initialize SecretManager with configuration
        
        Args:
            config: Configuration dictionary containing AWS and rotation settings
        """
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.INFO)
        
        # Initialize AWS clients
        self.secrets_client = boto3.client('secretsmanager')
        self.kms_client = boto3.client('kms')
        
        # Configure rotation settings
        self.rotation_config = config.get('rotation_config', {
            'automatic_rotation': True,
            'rotation_interval_days': 30,
            'notification_arn': None
        })
        
        # Track secret versions
        self.secret_versions = {}
        
    def create_secret(self, secret_name: str, secret_value: Dict,
                     description: str = None) -> Dict:
        """
        Create a new secret in AWS Secrets Manager
        
        Args:
            secret_name: Name of the secret
            secret_value: Dictionary containing secret values
            description: Optional description of the secret
            
        Returns:
            dict: Created secret details
        """
        try:
            # Create secret
            response = self.secrets_client.create_secret(
                Name=secret_name,
                Description=description or f"Created by SecretManager on {datetime.utcnow().isoformat()}",
                SecretString=json.dumps(secret_value),
                Tags=[
                    {
                        'Key': 'ManagedBy',
                        'Value': 'AISecretManager'
                    },
                    {
                        'Key': 'CreatedAt',
                        'Value': datetime.utcnow().isoformat()
                    }
                ]
            )
            
            # Enable rotation if configured
            if self.rotation_config['automatic_rotation']:
                self.enable_rotation(secret_name)
            
            self.logger.info(f"Created secret: {secret_name}")
            return response
            
        except ClientError as e:
            self.logger.error(f"Error creating secret {secret_name}: {str(e)}")
            raise
            
    def enable_rotation(self, secret_name: str) -> Dict:
        """Enable automatic rotation for a secret"""
        try:
            response = self.secrets_client.rotate_secret(
                SecretId=secret_name,
                RotationRules={
                    'AutomaticallyAfterDays': self.rotation_config['rotation_interval_days']
                }
            )
            
            self.logger.info(f"Enabled rotation for secret: {secret_name}")
            return response
            
        except ClientError as e:
            self.logger.error(f"Error enabling rotation for {secret_name}: {str(e)}")
            raise
            
    def get_secret(self, secret_name: str) -> Dict:
        """Get current value of a secret"""
        try:
            response = self.secrets_client.get_secret_value(
                SecretId=secret_name
            )
            
            # Track version
            self.secret_versions[secret_name] = response['VersionId']
            
            return json.loads(response['SecretString'])
            
        except ClientError as e:
            self.logger.error(f"Error retrieving secret {secret_name}: {str(e)}")
            raise
            
    def update_secret(self, secret_name: str, secret_value: Dict) -> Dict:
        """Update an existing secret"""
        try:
            response = self.secrets_client.update_secret(
                SecretId=secret_name,
                SecretString=json.dumps(secret_value)
            )
            
            self.logger.info(f"Updated secret: {secret_name}")
            return response
            
        except ClientError as e:
            self.logger.error(f"Error updating secret {secret_name}: {str(e)}")
            raise
            
    def rotate_secret(self, secret_name: str, new_value: Dict = None) -> Dict:
        """
        Manually rotate a secret
        
        Args:
            secret_name: Name of the secret to rotate
            new_value: Optional new secret value. If not provided, generates new value
            
        Returns:
            dict: Rotation details
        """
        try:
            if new_value is None:
                new_value = self._generate_secret_value()
                
            # Create new version
            response = self.secrets_client.put_secret_value(
                SecretId=secret_name,
                SecretString=json.dumps(new_value),
                VersionStages=['AWSPENDING']
            )
            
            # Verify new version
            if self._verify_secret_value(secret_name, new_value):
                # Promote to current version
                response = self.secrets_client.update_secret_version_stage(
                    SecretId=secret_name,
                    VersionStage='AWSCURRENT',
                    MoveToVersionId=response['VersionId']
                )
                
                self.logger.info(f"Rotated secret: {secret_name}")
                return response
            else:
                raise ValueError("Secret verification failed")
                
        except ClientError as e:
            self.logger.error(f"Error rotating secret {secret_name}: {str(e)}")
            raise
            
    def _generate_secret_value(self) -> Dict:
        """Generate new secret value"""
        # Implement secure secret generation logic
        return {
            'generated_at': datetime.utcnow().isoformat(),
            'value': hashlib.sha256(str(datetime.utcnow()).encode()).hexdigest()
        }
        
    def _verify_secret_value(self, secret_name: str, expected_value: Dict) -> bool:
        """Verify secret value was properly stored"""
        try:
            stored_value = self.get_secret(secret_name)
            return stored_value == expected_value
        except:
            return False
            
    def list_secrets(self) -> List[Dict]:
        """List all managed secrets"""
        try:
            response = self.secrets_client.list_secrets(
                Filters=[
                    {
                        'Key': 'tag-key',
                        'Values': ['ManagedBy']
                    }
                ]
            )
            
            return response['SecretList']
            
        except ClientError as e:
            self.logger.error(f"Error listing secrets: {str(e)}")
            raise
            
    def check_rotation_status(self, secret_name: str) -> Dict:
        """Check rotation status of a secret"""
        try:
            response = self.secrets_client.describe_secret(
                SecretId=secret_name
            )
            
            return {
                'last_rotated': response.get('LastRotatedDate'),
                'next_rotation': response.get('NextRotationDate'),
                'rotation_enabled': response.get('RotationEnabled', False),
                'rotation_rules': response.get('RotationRules', {})
            }
            
        except ClientError as e:
            self.logger.error(f"Error checking rotation status for {secret_name}: {str(e)}")
            raise
            
    def cleanup_old_versions(self, secret_name: str, 
                           keep_last_n: int = 5) -> None:
        """Clean up old versions of a secret"""
        try:
            # Get all versions
            response = self.secrets_client.list_secret_version_ids(
                SecretId=secret_name
            )
            
            versions = response['Versions']
            if len(versions) <= keep_last_n:
                return
                
            # Sort by date
            versions.sort(key=lambda x: x['CreatedDate'], reverse=True)
            
            # Delete old versions
            for version in versions[keep_last_n:]:
                self.secrets_client.delete_secret_version(
                    SecretId=secret_name,
                    VersionId=version['VersionId']
                )
                
            self.logger.info(f"Cleaned up old versions of secret: {secret_name}")
            
        except ClientError as e:
            self.logger.error(f"Error cleaning up versions for {secret_name}: {str(e)}")
            raise
