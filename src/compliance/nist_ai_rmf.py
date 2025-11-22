"""
NIST AI Risk Management Framework (AI RMF 2025)

Implements NIST AI RMF 1.0 and 2025 updates including:
- Generative AI Profile (NIST AI 600-1)
- Privacy Framework 1.1 integration
- AI security controls (SP 800-53)

Organized around four core functions: GOVERN, MAP, MEASURE, MANAGE
"""

import typing
import json
from dataclasses import dataclass, asdict, field
from datetime import datetime
from enum import Enum
from pathlib import Path
import logging


class RMFFunction(Enum):
    """NIST AI RMF Core Functions"""
    GOVERN = "govern"
    MAP = "map"
    MEASURE = "measure"
    MANAGE = "manage"


class RiskLevel(Enum):
    """Risk levels"""
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    MINIMAL = "minimal"


@dataclass
class RMFCategory:
    """RMF Category with subcategories"""
    function: RMFFunction
    category_id: str
    name: str
    description: str
    subcategories: typing.List[str] = field(default_factory=list)


@dataclass
class ImplementationStatus:
    """Implementation status for a control"""
    implemented: bool
    implementation_date: typing.Optional[str] = None
    evidence: typing.List[str] = field(default_factory=list)
    gaps: typing.List[str] = field(default_factory=list)
    notes: str = ""


@dataclass
class RiskAssessment:
    """AI Risk Assessment"""
    risk_id: str
    category: str
    description: str
    risk_level: RiskLevel
    likelihood: str  # rare, unlikely, possible, likely, almost_certain
    impact: str  # negligible, minor, moderate, major, catastrophic
    affected_stakeholders: typing.List[str]
    mitigation_controls: typing.List[str]
    residual_risk: RiskLevel
    assessment_date: str


@dataclass
class GenAIProfile:
    """
    Generative AI Profile (NIST AI 600-1)

    Additional considerations for generative AI systems
    """
    system_id: str
    is_generative: bool = False

    # CBRN (Chemical, Biological, Radiological, Nuclear) risks
    cbrn_risk_assessment: str = "Not applicable"

    # Data privacy for training
    training_data_privacy: typing.List[str] = field(default_factory=list)

    # Confabulation / hallucination risks
    confabulation_mitigation: typing.List[str] = field(default_factory=list)

    # Information integrity
    information_integrity_controls: typing.List[str] = field(default_factory=list)

    # Harmful bias and homogenization
    bias_evaluation: str = ""
    homogenization_assessment: str = ""

    # Environmental impacts
    environmental_impact_assessed: bool = False
    carbon_footprint_kg: typing.Optional[float] = None

    # Intellectual property
    ip_considerations: typing.List[str] = field(default_factory=list)


@dataclass
class NISTAIRMFAssessment:
    """Complete NIST AI RMF Assessment"""
    assessment_id: str
    system_id: str
    system_name: str
    assessment_date: str
    assessor: str

    # Function implementations
    govern_status: typing.Dict[str, ImplementationStatus] = field(default_factory=dict)
    map_status: typing.Dict[str, ImplementationStatus] = field(default_factory=dict)
    measure_status: typing.Dict[str, ImplementationStatus] = field(default_factory=dict)
    manage_status: typing.Dict[str, ImplementationStatus] = field(default_factory=dict)

    # Risk assessments
    risk_assessments: typing.List[RiskAssessment] = field(default_factory=list)

    # GenAI profile
    genai_profile: typing.Optional[GenAIProfile] = None

    # Overall metrics
    overall_compliance_score: float = 0.0
    total_categories: int = 0
    implemented_categories: int = 0

    # Recommendations
    recommendations: typing.List[str] = field(default_factory=list)


class NISTAIRMFCompliance:
    """
    NIST AI Risk Management Framework Compliance System

    Implements the four core functions:
    - GOVERN: Cultivate a culture of risk management
    - MAP: Understand AI system context
    - MEASURE: Assess and benchmark AI risks
    - MANAGE: Allocate resources to mapped risks
    """

    def __init__(self, output_dir: str = 'compliance_reports/nist_ai_rmf'):
        """
        Initialize NIST AI RMF Compliance System

        :param output_dir: Directory for reports
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

        self.logger = logging.getLogger('nist_ai_rmf')
        self.logger.setLevel(logging.INFO)

        self.categories = self._initialize_categories()

    def _initialize_categories(self) -> typing.Dict[RMFFunction, typing.List[RMFCategory]]:
        """Initialize NIST AI RMF categories and subcategories"""
        categories = {
            RMFFunction.GOVERN: [
                RMFCategory(
                    function=RMFFunction.GOVERN,
                    category_id="GOVERN-1",
                    name="Governance and Oversight",
                    description="Policies, processes, and procedures for AI governance",
                    subcategories=[
                        "GOVERN-1.1: Legal and regulatory requirements",
                        "GOVERN-1.2: Privacy and civil liberties",
                        "GOVERN-1.3: Risk management process",
                        "GOVERN-1.4: Risk tolerance",
                        "GOVERN-1.5: Organizational integration",
                        "GOVERN-1.6: Workforce diversity and expertise",
                        "GOVERN-1.7: AI risk culture"
                    ]
                ),
                RMFCategory(
                    function=RMFFunction.GOVERN,
                    category_id="GOVERN-2",
                    name="Accountability and Responsibility",
                    description="Clear assignment of roles and responsibilities",
                    subcategories=[
                        "GOVERN-2.1: Roles and responsibilities defined",
                        "GOVERN-2.2: Team diversity and expertise",
                        "GOVERN-2.3: AI design and development structure"
                    ]
                ),
                RMFCategory(
                    function=RMFFunction.GOVERN,
                    category_id="GOVERN-3",
                    name="Workforce Management",
                    description="AI system operators and practitioners are informed",
                    subcategories=[
                        "GOVERN-3.1: Workforce capability",
                        "GOVERN-3.2: Workforce training"
                    ]
                )
            ],

            RMFFunction.MAP: [
                RMFCategory(
                    function=RMFFunction.MAP,
                    category_id="MAP-1",
                    name="Context",
                    description="Context of AI system deployment established",
                    subcategories=[
                        "MAP-1.1: System purpose and use cases",
                        "MAP-1.2: Legal and regulatory requirements",
                        "MAP-1.3: Benefits and costs",
                        "MAP-1.4: Interdependent systems",
                        "MAP-1.5: Organizational risk tolerances",
                        "MAP-1.6: Value chain and ecosystem"
                    ]
                ),
                RMFCategory(
                    function=RMFFunction.MAP,
                    category_id="MAP-2",
                    name="Categorization",
                    description="AI capabilities, goals, and expected benefits categorized",
                    subcategories=[
                        "MAP-2.1: Intended purposes and prohibitions",
                        "MAP-2.2: AI system categorization",
                        "MAP-2.3: Task formulation"
                    ]
                ),
                RMFCategory(
                    function=RMFFunction.MAP,
                    category_id="MAP-3",
                    name="Impact Assessment",
                    description="Potential positive and negative impacts mapped",
                    subcategories=[
                        "MAP-3.1: Potential benefits",
                        "MAP-3.2: Negative impacts to individuals and groups",
                        "MAP-3.3: Potential impacts to ecosystems",
                        "MAP-3.4: Risks and benefits of data usage",
                        "MAP-3.5: Risks from data quality and suitability"
                    ]
                ),
                RMFCategory(
                    function=RMFFunction.MAP,
                    category_id="MAP-4",
                    name="Risk Identification",
                    description="Potential risks and impacts mapped",
                    subcategories=[
                        "MAP-4.1: Potential harms identified",
                        "MAP-4.2: Internal and external risks",
                        "MAP-4.3: All categories of risk"
                    ]
                ),
                RMFCategory(
                    function=RMFFunction.MAP,
                    category_id="MAP-5",
                    name="Impact Analysis",
                    description="Likelihood and magnitude of impacts analyzed",
                    subcategories=[
                        "MAP-5.1: Model transparency and explainability",
                        "MAP-5.2: Impact analysis methodology"
                    ]
                )
            ],

            RMFFunction.MEASURE: [
                RMFCategory(
                    function=RMFFunction.MEASURE,
                    category_id="MEASURE-1",
                    name="Test and Evaluation",
                    description="Test, evaluation, validation, and verification",
                    subcategories=[
                        "MEASURE-1.1: Appropriate methods selected",
                        "MEASURE-1.2: Test and evaluation plan",
                        "MEASURE-1.3: Ongoing monitoring"
                    ]
                ),
                RMFCategory(
                    function=RMFFunction.MEASURE,
                    category_id="MEASURE-2",
                    name="Performance Assessment",
                    description="AI system performance assessed",
                    subcategories=[
                        "MEASURE-2.1: Accuracy metrics",
                        "MEASURE-2.2: Adversarial robustness",
                        "MEASURE-2.3: Bias and fairness metrics",
                        "MEASURE-2.4: Uncertainty quantification",
                        "MEASURE-2.5: Explainability and transparency",
                        "MEASURE-2.6: Data quality",
                        "MEASURE-2.7: Environmental impact",
                        "MEASURE-2.8: Computational performance",
                        "MEASURE-2.9: Safety metrics",
                        "MEASURE-2.10: Security metrics",
                        "MEASURE-2.11: Privacy metrics",
                        "MEASURE-2.12: Value alignment",
                        "MEASURE-2.13: Feedback mechanisms"
                    ]
                ),
                RMFCategory(
                    function=RMFFunction.MEASURE,
                    category_id="MEASURE-3",
                    name="Risk Tracking",
                    description="Identified risks tracked over time",
                    subcategories=[
                        "MEASURE-3.1: Metrics tracked",
                        "MEASURE-3.2: Risk tracking process",
                        "MEASURE-3.3: Feedback from deployment"
                    ]
                ),
                RMFCategory(
                    function=RMFFunction.MEASURE,
                    category_id="MEASURE-4",
                    name="Trustworthiness",
                    description="AI system trustworthiness characteristics assessed",
                    subcategories=[
                        "MEASURE-4.1: Validation data representativeness",
                        "MEASURE-4.2: Accuracy claims substantiated",
                        "MEASURE-4.3: Explainability and interpretability"
                    ]
                )
            ],

            RMFFunction.MANAGE: [
                RMFCategory(
                    function=RMFFunction.MANAGE,
                    category_id="MANAGE-1",
                    name="Risk Response",
                    description="Risk response plans and strategies",
                    subcategories=[
                        "MANAGE-1.1: Response plan developed",
                        "MANAGE-1.2: Treatment of risks",
                        "MANAGE-1.3: Effectiveness of treatment",
                        "MANAGE-1.4: Incident response plan"
                    ]
                ),
                RMFCategory(
                    function=RMFFunction.MANAGE,
                    category_id="MANAGE-2",
                    name="Risk Resources",
                    description="Resources allocated to manage risks",
                    subcategories=[
                        "MANAGE-2.1: Resources allocated",
                        "MANAGE-2.2: Monitoring mechanisms",
                        "MANAGE-2.3: Improvement mechanisms",
                        "MANAGE-2.4: Risk communication"
                    ]
                ),
                RMFCategory(
                    function=RMFFunction.MANAGE,
                    category_id="MANAGE-3",
                    name="Risk Awareness",
                    description="Awareness of AI risks communicated",
                    subcategories=[
                        "MANAGE-3.1: Risks communicated to stakeholders",
                        "MANAGE-3.2: Feedback mechanisms established"
                    ]
                ),
                RMFCategory(
                    function=RMFFunction.MANAGE,
                    category_id="MANAGE-4",
                    name="Documentation",
                    description="AI system risks documented",
                    subcategories=[
                        "MANAGE-4.1: Risk documentation",
                        "MANAGE-4.2: Transparency documentation",
                        "MANAGE-4.3: Change management"
                    ]
                )
            ]
        }

        return categories

    def create_assessment(self, system_id: str, system_name: str,
                         assessor: str, is_generative: bool = False) -> NISTAIRMFAssessment:
        """
        Create new NIST AI RMF assessment

        :param system_id: System identifier
        :param system_name: System name
        :param assessor: Name of assessor
        :param is_generative: Whether system is generative AI
        :return: NISTAIRMFAssessment
        """
        assessment_id = f"NIST-RMF-{system_id}-{datetime.now().strftime('%Y%m%d')}"

        assessment = NISTAIRMFAssessment(
            assessment_id=assessment_id,
            system_id=system_id,
            system_name=system_name,
            assessment_date=datetime.now().isoformat(),
            assessor=assessor
        )

        # Add GenAI profile if applicable
        if is_generative:
            assessment.genai_profile = GenAIProfile(
                system_id=system_id,
                is_generative=True
            )

        self.logger.info(f"Created NIST AI RMF assessment {assessment_id}")
        return assessment

    def assess_category(self, assessment: NISTAIRMFAssessment,
                       function: RMFFunction, category_id: str,
                       implemented: bool, evidence: typing.List[str] = None,
                       gaps: typing.List[str] = None, notes: str = ""):
        """
        Assess implementation of a specific category

        :param assessment: Assessment object
        :param function: RMF function
        :param category_id: Category ID (e.g., "GOVERN-1.1")
        :param implemented: Whether category is implemented
        :param evidence: Evidence of implementation
        :param gaps: Identified gaps
        :param notes: Additional notes
        """
        status = ImplementationStatus(
            implemented=implemented,
            implementation_date=datetime.now().isoformat() if implemented else None,
            evidence=evidence or [],
            gaps=gaps or [],
            notes=notes
        )

        # Store in appropriate function dict
        if function == RMFFunction.GOVERN:
            assessment.govern_status[category_id] = status
        elif function == RMFFunction.MAP:
            assessment.map_status[category_id] = status
        elif function == RMFFunction.MEASURE:
            assessment.measure_status[category_id] = status
        elif function == RMFFunction.MANAGE:
            assessment.manage_status[category_id] = status

    def add_risk_assessment(self, assessment: NISTAIRMFAssessment,
                           risk: RiskAssessment):
        """Add risk assessment to overall assessment"""
        assessment.risk_assessments.append(risk)

    def calculate_compliance_score(self, assessment: NISTAIRMFAssessment) -> float:
        """
        Calculate overall compliance score

        :param assessment: Assessment object
        :return: Compliance score (0-100)
        """
        all_statuses = (
            list(assessment.govern_status.values()) +
            list(assessment.map_status.values()) +
            list(assessment.measure_status.values()) +
            list(assessment.manage_status.values())
        )

        if not all_statuses:
            return 0.0

        implemented_count = sum(1 for status in all_statuses if status.implemented)
        total_count = len(all_statuses)

        assessment.total_categories = total_count
        assessment.implemented_categories = implemented_count
        assessment.overall_compliance_score = (implemented_count / total_count) * 100

        return assessment.overall_compliance_score

    def generate_recommendations(self, assessment: NISTAIRMFAssessment) -> typing.List[str]:
        """
        Generate recommendations based on assessment

        :param assessment: Assessment object
        :return: List of recommendations
        """
        recommendations = []

        # Check each function
        functions_status = {
            'GOVERN': assessment.govern_status,
            'MAP': assessment.map_status,
            'MEASURE': assessment.measure_status,
            'MANAGE': assessment.manage_status
        }

        for function_name, statuses in functions_status.items():
            if not statuses:
                recommendations.append(
                    f"HIGH PRIORITY: Begin implementation of {function_name} function controls"
                )
                continue

            implemented = sum(1 for s in statuses.values() if s.implemented)
            total = len(statuses)

            if implemented / total < 0.5:
                recommendations.append(
                    f"MEDIUM PRIORITY: Improve {function_name} function coverage "
                    f"({implemented}/{total} implemented)"
                )

            # Collect gaps
            for category_id, status in statuses.items():
                if status.gaps:
                    recommendations.append(
                        f"Address gaps in {category_id}: {', '.join(status.gaps)}"
                    )

        # GenAI specific recommendations
        if assessment.genai_profile and assessment.genai_profile.is_generative:
            if not assessment.genai_profile.confabulation_mitigation:
                recommendations.append(
                    "CRITICAL: Implement confabulation/hallucination mitigation controls "
                    "for generative AI system"
                )

            if not assessment.genai_profile.environmental_impact_assessed:
                recommendations.append(
                    "Assess and document environmental impact of generative AI system"
                )

        # Risk-based recommendations
        high_risks = [
            r for r in assessment.risk_assessments
            if r.risk_level in [RiskLevel.CRITICAL, RiskLevel.HIGH]
        ]

        if high_risks:
            recommendations.append(
                f"URGENT: Address {len(high_risks)} critical/high risks identified"
            )

        assessment.recommendations = recommendations
        return recommendations

    def export_assessment(self, assessment: NISTAIRMFAssessment) -> Path:
        """
        Export assessment to file

        :param assessment: Assessment object
        :return: Path to exported file
        """
        filename = f"{assessment.assessment_id}.json"
        filepath = self.output_dir / filename

        # Convert to dict
        def to_dict(obj):
            if hasattr(obj, '__dict__'):
                result = {}
                for key, value in obj.__dict__.items():
                    if isinstance(value, Enum):
                        result[key] = value.value
                    elif isinstance(value, list):
                        result[key] = [to_dict(item) for item in value]
                    elif isinstance(value, dict):
                        result[key] = {k: to_dict(v) for k, v in value.items()}
                    elif hasattr(value, '__dict__'):
                        result[key] = to_dict(value)
                    else:
                        result[key] = value
                return result
            return obj

        assessment_dict = to_dict(assessment)

        with open(filepath, 'w') as f:
            json.dump(assessment_dict, f, indent=2)

        self.logger.info(f"Exported assessment to {filepath}")
        return filepath


def main():
    """Example usage"""
    rmf = NISTAIRMFCompliance()

    # Create assessment
    assessment = rmf.create_assessment(
        system_id="chatbot-v1",
        system_name="Customer Service Chatbot",
        assessor="AI Governance Team",
        is_generative=True
    )

    # Assess some categories
    rmf.assess_category(
        assessment,
        RMFFunction.GOVERN,
        "GOVERN-1.1",
        implemented=True,
        evidence=["AI governance policy document", "Legal review completed"],
        notes="Fully compliant with organizational policies"
    )

    rmf.assess_category(
        assessment,
        RMFFunction.MAP,
        "MAP-1.1",
        implemented=True,
        evidence=["Use case documentation", "Stakeholder requirements"],
        notes="Purpose and use cases clearly defined"
    )

    rmf.assess_category(
        assessment,
        RMFFunction.MEASURE,
        "MEASURE-2.3",
        implemented=False,
        gaps=["No fairness metrics established", "Bias testing incomplete"],
        notes="Bias and fairness assessment needed"
    )

    # Add risk assessment
    risk = RiskAssessment(
        risk_id="RISK-001",
        category="Fairness and Bias",
        description="Potential demographic bias in customer service responses",
        risk_level=RiskLevel.MEDIUM,
        likelihood="possible",
        impact="moderate",
        affected_stakeholders=["Customers", "Customer service team"],
        mitigation_controls=["Bias testing", "Fairness constraints"],
        residual_risk=RiskLevel.LOW,
        assessment_date=datetime.now().isoformat()
    )
    rmf.add_risk_assessment(assessment, risk)

    # Calculate compliance
    score = rmf.calculate_compliance_score(assessment)
    print(f"Compliance score: {score:.2f}%")

    # Generate recommendations
    recommendations = rmf.generate_recommendations(assessment)
    print("\nRecommendations:")
    for rec in recommendations:
        print(f"- {rec}")

    # Export
    filepath = rmf.export_assessment(assessment)
    print(f"\nAssessment exported to: {filepath}")


if __name__ == '__main__':
    main()
