"""
EU AI Act Compliance Framework (2025)

Implements compliance checking for the EU Artificial Intelligence Act,
including risk classification, GPAI model requirements, and transparency obligations.

Compliance with August 2025 regulations for General-Purpose AI models and
August 2026 requirements for high-risk AI systems.
"""

import typing
import json
import os
from datetime import datetime
from enum import Enum
from dataclasses import dataclass, asdict
import logging
import hashlib
from pathlib import Path


class AIRiskLevel(Enum):
    """AI system risk classification under EU AI Act"""
    UNACCEPTABLE = "unacceptable"  # Prohibited systems
    HIGH = "high"  # High-risk systems requiring strict compliance
    LIMITED = "limited"  # Limited-risk systems (transparency obligations)
    MINIMAL = "minimal"  # Minimal or no risk


class GPAICategory(Enum):
    """General-Purpose AI Model Categories"""
    STANDARD = "standard"  # Standard GPAI models
    SYSTEMIC_RISK = "systemic_risk"  # GPAI with systemic risk


@dataclass
class AISystemClassification:
    """AI System classification and metadata"""
    system_id: str
    system_name: str
    risk_level: AIRiskLevel
    use_case: str
    is_gpai: bool = False
    gpai_category: typing.Optional[GPAICategory] = None
    deployment_date: typing.Optional[str] = None
    last_assessment: typing.Optional[str] = None


@dataclass
class ComplianceRequirement:
    """Specific compliance requirement"""
    requirement_id: str
    category: str
    description: str
    applicable_risk_levels: typing.List[AIRiskLevel]
    mandatory: bool
    deadline: str
    status: str = "pending"  # pending, in_progress, compliant, non_compliant


@dataclass
class TechnicalDocumentation:
    """Technical documentation for AI systems"""
    system_id: str
    development_process: str
    training_data_summary: str
    model_architecture: str
    capabilities: typing.List[str]
    limitations: typing.List[str]
    potential_risks: typing.List[str]
    testing_procedures: str
    performance_metrics: typing.Dict[str, float]
    version: str
    last_updated: str


@dataclass
class TransparencyReport:
    """Transparency report for GPAI models"""
    model_id: str
    model_name: str
    capabilities: typing.List[str]
    limitations: typing.List[str]
    training_data_description: str
    copyright_compliance: bool
    energy_consumption: typing.Optional[float]
    carbon_footprint: typing.Optional[float]
    intended_use: str
    prohibited_uses: typing.List[str]
    risk_assessments: typing.List[str]
    report_date: str


class EUAIActCompliance:
    """
    EU AI Act Compliance Management System

    Implements requirements for:
    - Risk classification
    - GPAI model compliance (Aug 2025)
    - High-risk system compliance (Aug 2026)
    - Technical documentation
    - Transparency reporting
    - Prohibited AI practices monitoring
    """

    def __init__(self, config_path: str = 'config/eu_ai_act_config.json',
                 output_dir: str = 'compliance_reports/eu_ai_act'):
        """
        Initialize EU AI Act Compliance System

        :param config_path: Path to configuration file
        :param output_dir: Directory for compliance reports
        """
        self.config_path = config_path
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

        self.logger = logging.getLogger('eu_ai_act_compliance')
        self.logger.setLevel(logging.INFO)

        self.config = self._load_config()
        self.registered_systems: typing.Dict[str, AISystemClassification] = {}
        self.compliance_requirements = self._initialize_requirements()

    def _load_config(self) -> dict:
        """Load configuration"""
        default_config = {
            "organization_name": "Your Organization",
            "compliance_officer": "compliance@example.com",
            "auto_classification": True,
            "gpai_systemic_risk_threshold": {
                "parameters": 10_000_000_000,  # 10B parameters
                "compute_flops": 1e25
            }
        }

        try:
            if os.path.exists(self.config_path):
                with open(self.config_path, 'r') as f:
                    user_config = json.load(f)
                    default_config.update(user_config)
        except Exception as e:
            self.logger.warning(f"Could not load config, using default: {e}")

        return default_config

    def _initialize_requirements(self) -> typing.List[ComplianceRequirement]:
        """Initialize EU AI Act compliance requirements"""
        return [
            # Prohibited AI practices (Feb 2025)
            ComplianceRequirement(
                requirement_id="EUAIA-001",
                category="Prohibited Practices",
                description="Ensure no manipulative or deceptive AI techniques",
                applicable_risk_levels=[AIRiskLevel.UNACCEPTABLE],
                mandatory=True,
                deadline="2025-02-02"
            ),
            ComplianceRequirement(
                requirement_id="EUAIA-002",
                category="Prohibited Practices",
                description="No social scoring systems",
                applicable_risk_levels=[AIRiskLevel.UNACCEPTABLE],
                mandatory=True,
                deadline="2025-02-02"
            ),
            ComplianceRequirement(
                requirement_id="EUAIA-003",
                category="Prohibited Practices",
                description="No real-time biometric identification in public spaces (with exceptions)",
                applicable_risk_levels=[AIRiskLevel.UNACCEPTABLE],
                mandatory=True,
                deadline="2025-02-02"
            ),

            # GPAI requirements (Aug 2025)
            ComplianceRequirement(
                requirement_id="EUAIA-GPAI-001",
                category="GPAI Technical Documentation",
                description="Maintain technical documentation for development, training, and evaluation",
                applicable_risk_levels=[AIRiskLevel.HIGH, AIRiskLevel.LIMITED],
                mandatory=True,
                deadline="2025-08-02"
            ),
            ComplianceRequirement(
                requirement_id="EUAIA-GPAI-002",
                category="GPAI Transparency",
                description="Publish transparency reports on capabilities, limitations, and risks",
                applicable_risk_levels=[AIRiskLevel.HIGH, AIRiskLevel.LIMITED],
                mandatory=True,
                deadline="2025-08-02"
            ),
            ComplianceRequirement(
                requirement_id="EUAIA-GPAI-003",
                category="GPAI Copyright",
                description="Document copyright-protected content usage",
                applicable_risk_levels=[AIRiskLevel.HIGH, AIRiskLevel.LIMITED],
                mandatory=True,
                deadline="2025-08-02"
            ),

            # High-risk system requirements (Aug 2026)
            ComplianceRequirement(
                requirement_id="EUAIA-HR-001",
                category="High-Risk Documentation",
                description="Comprehensive technical documentation",
                applicable_risk_levels=[AIRiskLevel.HIGH],
                mandatory=True,
                deadline="2026-08-02"
            ),
            ComplianceRequirement(
                requirement_id="EUAIA-HR-002",
                category="High-Risk Risk Management",
                description="Implement robust risk management system",
                applicable_risk_levels=[AIRiskLevel.HIGH],
                mandatory=True,
                deadline="2026-08-02"
            ),
            ComplianceRequirement(
                requirement_id="EUAIA-HR-003",
                category="High-Risk Human Oversight",
                description="Implement effective human oversight mechanisms",
                applicable_risk_levels=[AIRiskLevel.HIGH],
                mandatory=True,
                deadline="2026-08-02"
            ),
            ComplianceRequirement(
                requirement_id="EUAIA-HR-004",
                category="High-Risk Accuracy",
                description="Ensure appropriate accuracy, robustness, and cybersecurity",
                applicable_risk_levels=[AIRiskLevel.HIGH],
                mandatory=True,
                deadline="2026-08-02"
            ),
            ComplianceRequirement(
                requirement_id="EUAIA-HR-005",
                category="High-Risk Logging",
                description="Maintain automatic logging capabilities",
                applicable_risk_levels=[AIRiskLevel.HIGH],
                mandatory=True,
                deadline="2026-08-02"
            ),
        ]

    def classify_ai_system(self, system_info: dict) -> AISystemClassification:
        """
        Classify AI system according to EU AI Act risk levels

        :param system_info: Dictionary with system information
        :return: AISystemClassification
        """
        system_id = system_info.get('system_id', hashlib.md5(
            system_info.get('system_name', 'unknown').encode()).hexdigest()[:16])

        # Check for prohibited practices
        if self._is_prohibited_system(system_info):
            risk_level = AIRiskLevel.UNACCEPTABLE
        # Check for high-risk applications
        elif self._is_high_risk_system(system_info):
            risk_level = AIRiskLevel.HIGH
        # Check for transparency obligations
        elif self._requires_transparency(system_info):
            risk_level = AIRiskLevel.LIMITED
        else:
            risk_level = AIRiskLevel.MINIMAL

        # Determine if it's a GPAI model
        is_gpai = system_info.get('is_general_purpose', False)
        gpai_category = None

        if is_gpai:
            gpai_category = self._classify_gpai(system_info)

        classification = AISystemClassification(
            system_id=system_id,
            system_name=system_info.get('system_name', 'Unknown'),
            risk_level=risk_level,
            use_case=system_info.get('use_case', 'Not specified'),
            is_gpai=is_gpai,
            gpai_category=gpai_category,
            deployment_date=system_info.get('deployment_date'),
            last_assessment=datetime.now().isoformat()
        )

        self.registered_systems[system_id] = classification
        self.logger.info(f"Classified system {system_id} as {risk_level.value}")

        return classification

    def _is_prohibited_system(self, system_info: dict) -> bool:
        """Check if system falls under prohibited AI practices"""
        prohibited_indicators = [
            'social_scoring',
            'manipulative_techniques',
            'real_time_biometric_surveillance',
            'emotion_recognition_workplace',
            'subliminal_manipulation'
        ]

        use_case = system_info.get('use_case', '').lower()
        return any(indicator in use_case for indicator in prohibited_indicators)

    def _is_high_risk_system(self, system_info: dict) -> bool:
        """Check if system is high-risk under EU AI Act Annex III"""
        high_risk_domains = [
            'biometric_identification',
            'critical_infrastructure',
            'education_vocational_training',
            'employment',
            'essential_services',
            'law_enforcement',
            'migration_asylum',
            'justice_democratic_processes'
        ]

        use_case = system_info.get('use_case', '').lower()
        return any(domain in use_case for domain in high_risk_domains)

    def _requires_transparency(self, system_info: dict) -> bool:
        """Check if system requires transparency obligations"""
        transparency_indicators = [
            'chatbot',
            'content_generation',
            'deepfake',
            'emotion_recognition',
            'biometric_categorization'
        ]

        use_case = system_info.get('use_case', '').lower()
        return any(indicator in use_case for indicator in transparency_indicators)

    def _classify_gpai(self, system_info: dict) -> GPAICategory:
        """Classify General-Purpose AI model"""
        params = system_info.get('parameter_count', 0)
        compute = system_info.get('training_compute_flops', 0)

        threshold_params = self.config['gpai_systemic_risk_threshold']['parameters']
        threshold_compute = self.config['gpai_systemic_risk_threshold']['compute_flops']

        if params >= threshold_params or compute >= threshold_compute:
            return GPAICategory.SYSTEMIC_RISK
        return GPAICategory.STANDARD

    def create_technical_documentation(self, system_id: str,
                                      doc_info: dict) -> TechnicalDocumentation:
        """
        Create technical documentation for AI system

        :param system_id: System identifier
        :param doc_info: Documentation information
        :return: TechnicalDocumentation
        """
        doc = TechnicalDocumentation(
            system_id=system_id,
            development_process=doc_info.get('development_process', ''),
            training_data_summary=doc_info.get('training_data_summary', ''),
            model_architecture=doc_info.get('model_architecture', ''),
            capabilities=doc_info.get('capabilities', []),
            limitations=doc_info.get('limitations', []),
            potential_risks=doc_info.get('potential_risks', []),
            testing_procedures=doc_info.get('testing_procedures', ''),
            performance_metrics=doc_info.get('performance_metrics', {}),
            version=doc_info.get('version', '1.0'),
            last_updated=datetime.now().isoformat()
        )

        # Save documentation
        doc_path = self.output_dir / f"technical_doc_{system_id}.json"
        with open(doc_path, 'w') as f:
            json.dump(asdict(doc), f, indent=2)

        self.logger.info(f"Created technical documentation for {system_id}")
        return doc

    def create_transparency_report(self, model_id: str,
                                  report_info: dict) -> TransparencyReport:
        """
        Create transparency report for GPAI model

        :param model_id: Model identifier
        :param report_info: Report information
        :return: TransparencyReport
        """
        report = TransparencyReport(
            model_id=model_id,
            model_name=report_info.get('model_name', ''),
            capabilities=report_info.get('capabilities', []),
            limitations=report_info.get('limitations', []),
            training_data_description=report_info.get('training_data_description', ''),
            copyright_compliance=report_info.get('copyright_compliance', False),
            energy_consumption=report_info.get('energy_consumption'),
            carbon_footprint=report_info.get('carbon_footprint'),
            intended_use=report_info.get('intended_use', ''),
            prohibited_uses=report_info.get('prohibited_uses', []),
            risk_assessments=report_info.get('risk_assessments', []),
            report_date=datetime.now().isoformat()
        )

        # Save report
        report_path = self.output_dir / f"transparency_report_{model_id}.json"
        with open(report_path, 'w') as f:
            json.dump(asdict(report), f, indent=2)

        self.logger.info(f"Created transparency report for {model_id}")
        return report

    def assess_compliance(self, system_id: str) -> dict:
        """
        Assess compliance status for a registered AI system

        :param system_id: System identifier
        :return: Compliance assessment results
        """
        if system_id not in self.registered_systems:
            raise ValueError(f"System {system_id} not registered")

        classification = self.registered_systems[system_id]
        applicable_requirements = [
            req for req in self.compliance_requirements
            if classification.risk_level in req.applicable_risk_levels
        ]

        assessment = {
            'system_id': system_id,
            'system_name': classification.system_name,
            'risk_level': classification.risk_level.value,
            'assessment_date': datetime.now().isoformat(),
            'total_requirements': len(applicable_requirements),
            'requirements': [],
            'compliance_score': 0,
            'critical_gaps': []
        }

        compliant_count = 0
        for req in applicable_requirements:
            req_status = {
                'requirement_id': req.requirement_id,
                'category': req.category,
                'description': req.description,
                'deadline': req.deadline,
                'status': req.status,
                'mandatory': req.mandatory
            }
            assessment['requirements'].append(req_status)

            if req.status == 'compliant':
                compliant_count += 1
            elif req.mandatory and req.status != 'compliant':
                assessment['critical_gaps'].append(req.requirement_id)

        if applicable_requirements:
            assessment['compliance_score'] = (compliant_count / len(applicable_requirements)) * 100

        # Save assessment
        assessment_path = self.output_dir / f"compliance_assessment_{system_id}_{datetime.now().strftime('%Y%m%d')}.json"
        with open(assessment_path, 'w') as f:
            json.dump(assessment, f, indent=2)

        return assessment

    def generate_compliance_report(self) -> dict:
        """
        Generate comprehensive compliance report for all systems

        :return: Compliance report
        """
        report = {
            'organization': self.config['organization_name'],
            'report_date': datetime.now().isoformat(),
            'total_systems': len(self.registered_systems),
            'systems_by_risk': {
                'unacceptable': 0,
                'high': 0,
                'limited': 0,
                'minimal': 0
            },
            'gpai_models': {
                'total': 0,
                'systemic_risk': 0,
                'standard': 0
            },
            'overall_compliance_score': 0,
            'systems': []
        }

        total_compliance = 0
        for system_id, classification in self.registered_systems.items():
            report['systems_by_risk'][classification.risk_level.value] += 1

            if classification.is_gpai:
                report['gpai_models']['total'] += 1
                if classification.gpai_category == GPAICategory.SYSTEMIC_RISK:
                    report['gpai_models']['systemic_risk'] += 1
                else:
                    report['gpai_models']['standard'] += 1

            assessment = self.assess_compliance(system_id)
            total_compliance += assessment['compliance_score']

            report['systems'].append({
                'system_id': system_id,
                'system_name': classification.system_name,
                'risk_level': classification.risk_level.value,
                'compliance_score': assessment['compliance_score'],
                'critical_gaps': len(assessment['critical_gaps'])
            })

        if self.registered_systems:
            report['overall_compliance_score'] = total_compliance / len(self.registered_systems)

        # Save report
        report_path = self.output_dir / f"eu_ai_act_compliance_report_{datetime.now().strftime('%Y%m%d')}.json"
        with open(report_path, 'w') as f:
            json.dump(report, f, indent=2)

        self.logger.info(f"Generated compliance report: {report_path}")
        return report


def main():
    """Example usage"""
    compliance_system = EUAIActCompliance()

    # Example: Register a GPAI model
    system_info = {
        'system_name': 'GPT-like Language Model',
        'use_case': 'content_generation',
        'is_general_purpose': True,
        'parameter_count': 175_000_000_000,  # 175B parameters
        'deployment_date': '2025-06-01'
    }

    classification = compliance_system.classify_ai_system(system_info)
    print(f"System classified as: {classification.risk_level.value}")

    if classification.is_gpai:
        print(f"GPAI Category: {classification.gpai_category.value}")

    # Generate compliance report
    report = compliance_system.generate_compliance_report()
    print(f"Overall compliance score: {report['overall_compliance_score']:.2f}%")


if __name__ == '__main__':
    main()
