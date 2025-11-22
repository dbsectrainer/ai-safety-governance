"""
Model Registry and Model Cards System (2025)

Implements comprehensive model lifecycle management including:
- Model versioning and registry
- Model cards for transparency
- Data sheets for datasets
- Model governance and approval workflows

Aligned with 2025 transparency and documentation best practices.
"""

import typing
import json
from dataclasses import dataclass, asdict, field
from datetime import datetime
from enum import Enum
from pathlib import Path
import hashlib
import logging


class ModelStatus(Enum):
    """Model lifecycle status"""
    DEVELOPMENT = "development"
    TESTING = "testing"
    STAGING = "staging"
    PRODUCTION = "production"
    DEPRECATED = "deprecated"
    ARCHIVED = "archived"


class ApprovalStatus(Enum):
    """Approval workflow status"""
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    CONDITIONAL = "conditional"


@dataclass
class ModelMetadata:
    """Basic model metadata"""
    model_id: str
    model_name: str
    version: str
    description: str
    task_type: str  # classification, generation, translation, etc.
    architecture: str
    framework: str
    created_date: str
    created_by: str
    organization: str


@dataclass
class ModelPerformance:
    """Model performance metrics"""
    accuracy: typing.Optional[float] = None
    precision: typing.Optional[float] = None
    recall: typing.Optional[float] = None
    f1_score: typing.Optional[float] = None
    auc_roc: typing.Optional[float] = None

    # Additional metrics
    latency_p50_ms: typing.Optional[float] = None
    latency_p95_ms: typing.Optional[float] = None
    latency_p99_ms: typing.Optional[float] = None
    throughput_qps: typing.Optional[float] = None

    # Resource requirements
    memory_mb: typing.Optional[float] = None
    disk_mb: typing.Optional[float] = None
    gpu_required: bool = False

    custom_metrics: typing.Dict[str, float] = field(default_factory=dict)


@dataclass
class FairnessMetrics:
    """Fairness and bias metrics"""
    demographic_parity_diff: typing.Optional[float] = None
    equal_opportunity_diff: typing.Optional[float] = None
    disparate_impact_ratio: typing.Optional[float] = None

    protected_attributes: typing.List[str] = field(default_factory=list)
    fairness_assessment: str = "Not assessed"
    bias_mitigation_applied: typing.List[str] = field(default_factory=list)


@dataclass
class DataSheet:
    """Data sheet for dataset (based on Datasheets for Datasets paper)"""
    dataset_id: str
    dataset_name: str
    version: str

    # Motivation
    purpose: str
    creators: typing.List[str]
    funding: typing.Optional[str] = None

    # Composition
    instances: int
    data_types: typing.List[str] = field(default_factory=list)
    missing_data: typing.Optional[str] = None
    confidential_data: bool = False

    # Collection process
    collection_method: str
    collection_timeframe: str
    ethical_review: typing.Optional[str] = None

    # Preprocessing
    preprocessing_steps: typing.List[str] = field(default_factory=list)
    cleaning_procedures: typing.List[str] = field(default_factory=list)

    # Uses
    intended_uses: typing.List[str] = field(default_factory=list)
    prohibited_uses: typing.List[str] = field(default_factory=list)

    # Distribution
    license: str = "Unknown"
    copyright: str = "Unknown"

    # Maintenance
    maintainer: str = ""
    update_frequency: str = "Unknown"


@dataclass
class ModelCard:
    """
    Model Card for comprehensive model documentation
    Based on Model Cards for Model Reporting (Mitchell et al.)
    """
    # Basic information
    metadata: ModelMetadata

    # Model details
    model_details: typing.Dict[str, typing.Any] = field(default_factory=dict)

    # Intended use
    intended_use: typing.List[str] = field(default_factory=list)
    out_of_scope_uses: typing.List[str] = field(default_factory=list)

    # Factors (relevant factors for model behavior)
    relevant_factors: typing.List[str] = field(default_factory=list)
    evaluation_factors: typing.List[str] = field(default_factory=list)

    # Metrics
    performance_metrics: ModelPerformance = field(default_factory=ModelPerformance)
    fairness_metrics: FairnessMetrics = field(default_factory=FairnessMetrics)

    # Training data
    training_datasets: typing.List[str] = field(default_factory=list)
    training_data_sheets: typing.List[DataSheet] = field(default_factory=list)

    # Evaluation data
    evaluation_datasets: typing.List[str] = field(default_factory=list)
    evaluation_procedure: str = ""

    # Ethical considerations
    sensitive_data: bool = False
    human_life_impact: bool = False
    bias_risks: typing.List[str] = field(default_factory=list)
    mitigation_strategies: typing.List[str] = field(default_factory=list)

    # Caveats and recommendations
    limitations: typing.List[str] = field(default_factory=list)
    recommendations: typing.List[str] = field(default_factory=list)

    # Environmental impact
    carbon_footprint_kg: typing.Optional[float] = None
    energy_consumption_kwh: typing.Optional[float] = None

    # Compliance
    compliance_frameworks: typing.List[str] = field(default_factory=list)
    regulatory_approvals: typing.List[str] = field(default_factory=list)


@dataclass
class ModelVersion:
    """Model version in registry"""
    model_id: str
    version: str
    model_card: ModelCard
    status: ModelStatus
    approval_status: ApprovalStatus

    # Files and artifacts
    model_path: typing.Optional[str] = None
    config_path: typing.Optional[str] = None
    weights_hash: typing.Optional[str] = None

    # Versioning
    parent_version: typing.Optional[str] = None
    changelog: str = ""

    # Lifecycle
    created_date: str = field(default_factory=lambda: datetime.now().isoformat())
    deployed_date: typing.Optional[str] = None
    deprecated_date: typing.Optional[str] = None

    # Approval workflow
    approved_by: typing.Optional[str] = None
    approval_date: typing.Optional[str] = None
    approval_notes: str = ""

    # Metadata
    tags: typing.List[str] = field(default_factory=list)
    metadata: typing.Dict[str, typing.Any] = field(default_factory=dict)


class ModelRegistry:
    """
    Comprehensive Model Registry System

    Manages model lifecycle, versioning, documentation, and governance
    """

    def __init__(self, registry_dir: str = 'model_registry'):
        """
        Initialize Model Registry

        :param registry_dir: Directory for registry storage
        """
        self.registry_dir = Path(registry_dir)
        self.registry_dir.mkdir(parents=True, exist_ok=True)

        self.logger = logging.getLogger('model_registry')
        self.logger.setLevel(logging.INFO)

        self.models: typing.Dict[str, typing.List[ModelVersion]] = {}
        self._load_registry()

    def _load_registry(self):
        """Load existing registry from disk"""
        registry_file = self.registry_dir / 'registry_index.json'
        if registry_file.exists():
            try:
                with open(registry_file, 'r') as f:
                    data = json.load(f)
                    # Load model versions
                    for model_id, versions in data.get('models', {}).items():
                        self.models[model_id] = []
                        for version_data in versions:
                            # Reconstruct ModelVersion from dict
                            # (simplified for brevity)
                            pass
                self.logger.info(f"Loaded {len(self.models)} models from registry")
            except Exception as e:
                self.logger.error(f"Error loading registry: {e}")

    def _save_registry(self):
        """Save registry to disk"""
        registry_file = self.registry_dir / 'registry_index.json'

        registry_data = {
            'last_updated': datetime.now().isoformat(),
            'total_models': len(self.models),
            'models': {}
        }

        for model_id, versions in self.models.items():
            registry_data['models'][model_id] = [
                {
                    'version': v.version,
                    'status': v.status.value,
                    'approval_status': v.approval_status.value,
                    'created_date': v.created_date
                }
                for v in versions
            ]

        with open(registry_file, 'w') as f:
            json.dump(registry_data, f, indent=2)

    def register_model(self, model_card: ModelCard,
                      status: ModelStatus = ModelStatus.DEVELOPMENT) -> ModelVersion:
        """
        Register new model version

        :param model_card: Model card with documentation
        :param status: Initial status
        :return: ModelVersion
        """
        model_id = model_card.metadata.model_id
        version = model_card.metadata.version

        # Check if model already exists
        if model_id not in self.models:
            self.models[model_id] = []

        # Check for version conflicts
        existing_versions = [v.version for v in self.models[model_id]]
        if version in existing_versions:
            raise ValueError(
                f"Version {version} already exists for model {model_id}"
            )

        # Create model version
        model_version = ModelVersion(
            model_id=model_id,
            version=version,
            model_card=model_card,
            status=status,
            approval_status=ApprovalStatus.PENDING
        )

        self.models[model_id].append(model_version)
        self._save_registry()

        # Save model card
        self._save_model_card(model_version)

        self.logger.info(
            f"Registered model {model_id} version {version} with status {status.value}"
        )

        return model_version

    def update_status(self, model_id: str, version: str,
                     new_status: ModelStatus):
        """Update model status"""
        model_version = self._get_version(model_id, version)

        old_status = model_version.status
        model_version.status = new_status

        if new_status == ModelStatus.PRODUCTION:
            model_version.deployed_date = datetime.now().isoformat()
        elif new_status == ModelStatus.DEPRECATED:
            model_version.deprecated_date = datetime.now().isoformat()

        self._save_registry()
        self._save_model_card(model_version)

        self.logger.info(
            f"Updated {model_id} v{version} status: {old_status.value} -> {new_status.value}"
        )

    def approve_model(self, model_id: str, version: str,
                     approver: str, notes: str = "",
                     conditional: bool = False):
        """
        Approve model for deployment

        :param model_id: Model identifier
        :param version: Model version
        :param approver: Name of approver
        :param notes: Approval notes
        :param conditional: Whether approval is conditional
        """
        model_version = self._get_version(model_id, version)

        model_version.approval_status = (
            ApprovalStatus.CONDITIONAL if conditional else ApprovalStatus.APPROVED
        )
        model_version.approved_by = approver
        model_version.approval_date = datetime.now().isoformat()
        model_version.approval_notes = notes

        self._save_registry()
        self._save_model_card(model_version)

        self.logger.info(
            f"Approved {model_id} v{version} by {approver}"
        )

    def reject_model(self, model_id: str, version: str,
                    reviewer: str, reason: str):
        """Reject model"""
        model_version = self._get_version(model_id, version)

        model_version.approval_status = ApprovalStatus.REJECTED
        model_version.approved_by = reviewer
        model_version.approval_date = datetime.now().isoformat()
        model_version.approval_notes = reason

        self._save_registry()
        self._save_model_card(model_version)

        self.logger.info(
            f"Rejected {model_id} v{version} by {reviewer}: {reason}"
        )

    def get_model_card(self, model_id: str, version: str) -> ModelCard:
        """Get model card for specific version"""
        model_version = self._get_version(model_id, version)
        return model_version.model_card

    def get_latest_version(self, model_id: str,
                          status: typing.Optional[ModelStatus] = None) -> typing.Optional[ModelVersion]:
        """
        Get latest version of model

        :param model_id: Model identifier
        :param status: Optional filter by status
        :return: Latest ModelVersion or None
        """
        if model_id not in self.models:
            return None

        versions = self.models[model_id]

        if status:
            versions = [v for v in versions if v.status == status]

        if not versions:
            return None

        # Sort by created_date and return latest
        return sorted(versions, key=lambda v: v.created_date, reverse=True)[0]

    def get_production_version(self, model_id: str) -> typing.Optional[ModelVersion]:
        """Get production version of model"""
        return self.get_latest_version(model_id, status=ModelStatus.PRODUCTION)

    def list_models(self, status: typing.Optional[ModelStatus] = None) -> typing.List[dict]:
        """
        List all models in registry

        :param status: Optional filter by status
        :return: List of model summaries
        """
        models_list = []

        for model_id, versions in self.models.items():
            if status:
                versions = [v for v in versions if v.status == status]

            if versions:
                latest = sorted(versions, key=lambda v: v.created_date, reverse=True)[0]
                models_list.append({
                    'model_id': model_id,
                    'model_name': latest.model_card.metadata.model_name,
                    'latest_version': latest.version,
                    'status': latest.status.value,
                    'approval_status': latest.approval_status.value,
                    'created_date': latest.created_date,
                    'total_versions': len(versions)
                })

        return models_list

    def search_models(self, query: str) -> typing.List[dict]:
        """
        Search models by name or tags

        :param query: Search query
        :return: List of matching models
        """
        results = []
        query_lower = query.lower()

        for model_id, versions in self.models.items():
            for version in versions:
                card = version.model_card

                # Search in name, description, tags
                if (query_lower in card.metadata.model_name.lower() or
                    query_lower in card.metadata.description.lower() or
                    any(query_lower in tag.lower() for tag in version.tags)):

                    results.append({
                        'model_id': model_id,
                        'version': version.version,
                        'model_name': card.metadata.model_name,
                        'description': card.metadata.description,
                        'status': version.status.value
                    })

        return results

    def _get_version(self, model_id: str, version: str) -> ModelVersion:
        """Get specific model version"""
        if model_id not in self.models:
            raise ValueError(f"Model {model_id} not found")

        for v in self.models[model_id]:
            if v.version == version:
                return v

        raise ValueError(f"Version {version} not found for model {model_id}")

    def _save_model_card(self, model_version: ModelVersion):
        """Save model card to file"""
        model_dir = self.registry_dir / model_version.model_id
        model_dir.mkdir(exist_ok=True)

        card_path = model_dir / f"model_card_v{model_version.version}.json"

        # Convert to dict
        def to_dict(obj):
            if hasattr(obj, '__dict__'):
                result = {}
                for key, value in obj.__dict__.items():
                    if isinstance(value, Enum):
                        result[key] = value.value
                    elif isinstance(value, list):
                        result[key] = [to_dict(item) for item in value]
                    elif hasattr(value, '__dict__'):
                        result[key] = to_dict(value)
                    else:
                        result[key] = value
                return result
            return obj

        card_dict = to_dict(model_version)

        with open(card_path, 'w') as f:
            json.dump(card_dict, f, indent=2)

        self.logger.info(f"Saved model card to {card_path}")

    def generate_report(self) -> dict:
        """Generate registry summary report"""
        report = {
            'report_date': datetime.now().isoformat(),
            'total_models': len(self.models),
            'total_versions': sum(len(versions) for versions in self.models.values()),
            'by_status': {},
            'by_approval': {},
            'recently_updated': []
        }

        # Count by status
        for status in ModelStatus:
            count = sum(
                1 for versions in self.models.values()
                for v in versions if v.status == status
            )
            report['by_status'][status.value] = count

        # Count by approval
        for approval in ApprovalStatus:
            count = sum(
                1 for versions in self.models.values()
                for v in versions if v.approval_status == approval
            )
            report['by_approval'][approval.value] = count

        # Get recently updated models
        all_versions = [
            v for versions in self.models.values() for v in versions
        ]
        recent = sorted(all_versions, key=lambda v: v.created_date, reverse=True)[:10]

        report['recently_updated'] = [
            {
                'model_id': v.model_id,
                'version': v.version,
                'status': v.status.value,
                'created_date': v.created_date
            }
            for v in recent
        ]

        return report


def main():
    """Example usage"""
    registry = ModelRegistry()

    # Create model metadata
    metadata = ModelMetadata(
        model_id="sentiment-classifier-v1",
        model_name="Sentiment Analysis Classifier",
        version="1.0.0",
        description="BERT-based sentiment classification model",
        task_type="classification",
        architecture="BERT",
        framework="PyTorch",
        created_date=datetime.now().isoformat(),
        created_by="Data Science Team",
        organization="Example Corp"
    )

    # Create model card
    model_card = ModelCard(
        metadata=metadata,
        intended_use=["Sentiment analysis of product reviews", "Customer feedback classification"],
        out_of_scope_uses=["Medical diagnosis", "Legal decisions"],
        performance_metrics=ModelPerformance(
            accuracy=0.94,
            precision=0.93,
            recall=0.92,
            f1_score=0.925,
            latency_p50_ms=45.0,
            latency_p95_ms=120.0,
            throughput_qps=100.0
        ),
        limitations=["May not perform well on domain-specific jargon", "Limited to English language"],
        compliance_frameworks=["GDPR", "EU AI Act - Limited Risk"]
    )

    # Register model
    model_version = registry.register_model(model_card)
    print(f"Registered model: {model_version.model_id} v{model_version.version}")

    # Approve model
    registry.approve_model(
        model_id=metadata.model_id,
        version=metadata.version,
        approver="ML Lead",
        notes="Meets all performance and fairness criteria"
    )

    # Update to production
    registry.update_status(
        model_id=metadata.model_id,
        version=metadata.version,
        new_status=ModelStatus.PRODUCTION
    )

    # Generate report
    report = registry.generate_report()
    print(f"\nRegistry Report:")
    print(f"Total models: {report['total_models']}")
    print(f"Total versions: {report['total_versions']}")
    print(f"Production models: {report['by_status']['production']}")


if __name__ == '__main__':
    main()
