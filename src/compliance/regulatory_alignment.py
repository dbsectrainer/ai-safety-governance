import typing
import json
import os
from datetime import datetime
from enum import Enum, auto
import logging
import uuid


class ComplianceStatus(Enum):
    COMPLIANT = auto()
    NON_COMPLIANT = auto()
    NEEDS_REVIEW = auto()
    ERROR = auto()


class RegulationFramework(Enum):
    GDPR = "General Data Protection Regulation"
    HIPAA = "Health Insurance Portability and Accountability Act"
    CCPA = "California Consumer Privacy Act"
    SOC2 = "Service Organization Control 2"


class ComplianceRule:
    def __init__(
        self,
        regulation: RegulationFramework,
        description: str,
        check_function: typing.Callable,
    ):
        """
        Initialize a compliance rule for a specific regulation.

        :param regulation: Regulatory framework
        :param description: Detailed description of the compliance requirement
        :param check_function: Function to validate compliance
        """
        self.id = str(uuid.uuid4())
        self.regulation = regulation
        self.description = description
        self.check_function = check_function
        self.last_checked = None
        self.status = ComplianceStatus.NEEDS_REVIEW


class ComplianceAuditTrail:
    def __init__(self, output_dir: str = "compliance_logs"):
        """
        Initialize compliance audit trail management.

        :param output_dir: Directory to store compliance audit logs
        """
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)

        # Use a per-instance logger so repeated runs in one process do not
        # accumulate handlers and duplicate audit lines.
        self.logger = logging.getLogger(f"compliance_audit.{uuid.uuid4().hex}")
        self.logger.setLevel(logging.INFO)
        self.logger.propagate = False

        # File handler for audit logs
        file_handler = logging.FileHandler(
            os.path.join(
                output_dir,
                f'compliance_audit_{datetime.now().strftime("%Y%m%d_%H%M%S_%f")}.log',
            )
        )
        formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
        file_handler.setFormatter(formatter)
        self.logger.addHandler(file_handler)


class RegulatoryAlignmentSystem:
    def __init__(
        self,
        config_path: str = "config/compliance_config.json",
        audit_trail_dir: str = "compliance_logs",
    ):
        """
        Initialize Regulatory Alignment System.

        :param config_path: Path to compliance configuration
        :param audit_trail_dir: Directory to store compliance audit logs
        """
        self.config_path = config_path
        self.config = self._load_config()

        self.compliance_rules = []
        self.audit_trail = ComplianceAuditTrail(audit_trail_dir)

        # Setup logging
        self.logger = logging.getLogger("regulatory_alignment")
        self.logger.setLevel(logging.INFO)

    def _load_config(self) -> dict:
        """
        Load compliance configuration.

        :return: Configuration dictionary
        """
        default_config = {
            "check_frequency_days": 30,
            "auto_remediation": True,
            "notification_emails": [],
            "regulations": [
                RegulationFramework.GDPR.value,
                RegulationFramework.HIPAA.value,
            ],
        }

        try:
            if os.path.exists(self.config_path):
                with open(self.config_path, "r") as f:
                    user_config = json.load(f)
                    default_config.update(user_config)
            return default_config
        except Exception as e:
            self.logger.warning(f"Could not load config, using default: {e}")
            return default_config

    def register_compliance_rule(self, rule: ComplianceRule):
        """
        Register a compliance rule for tracking and validation.

        :param rule: Compliance rule to register
        """
        self.compliance_rules.append(rule)
        self.audit_trail.logger.info(f"Registered Compliance Rule: {rule.description}")

    def run_compliance_checks(self) -> dict:
        """
        Run all registered compliance checks.

        :return: Compliance check results
        """
        results = {
            "timestamp": datetime.now().isoformat(),
            "total_rules": len(self.compliance_rules),
            "compliant_rules": 0,
            "non_compliant_rules": 0,
            "error_rules": 0,
            "rules_status": [],
        }

        for rule in self.compliance_rules:
            try:
                compliance_result = rule.check_function()
                rule.last_checked = datetime.now()

                if compliance_result:
                    rule.status = ComplianceStatus.COMPLIANT
                    results["compliant_rules"] += 1
                else:
                    rule.status = ComplianceStatus.NON_COMPLIANT
                    results["non_compliant_rules"] += 1

                results["rules_status"].append(
                    {
                        "rule_id": rule.id,
                        "regulation": rule.regulation.value,
                        "description": rule.description,
                        "status": rule.status.name,
                    }
                )

                # Log the compliance check
                self.audit_trail.logger.info(
                    f"Compliance Check: {rule.description} - {rule.status.name}"
                )

            except Exception as e:
                rule.status = ComplianceStatus.ERROR
                rule.last_checked = datetime.now()
                results["error_rules"] += 1
                results["rules_status"].append(
                    {
                        "rule_id": rule.id,
                        "regulation": rule.regulation.value,
                        "description": rule.description,
                        "status": rule.status.name,
                        "error": str(e),
                    }
                )
                self.audit_trail.logger.error(
                    f"Error in compliance check for {rule.description}: {e}"
                )

        return results

    def generate_compliance_report(self, results: dict) -> str:
        """
        Generate a detailed compliance report.

        :param results: Compliance check results
        :return: Path to generated report
        """
        report_filename = (
            f"compliance_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        )
        report_path = os.path.join(self.audit_trail.output_dir, report_filename)

        with open(report_path, "w") as f:
            json.dump(results, f, indent=2)

        self.audit_trail.logger.info(f"Generated Compliance Report: {report_path}")
        return report_path


def main():
    """
    Example usage of Regulatory Alignment System.
    """

    # Example compliance rule for data privacy
    def check_data_privacy():
        # Simulated data privacy check
        # In a real scenario, this would perform actual compliance validation
        return True

    privacy_rule = ComplianceRule(
        regulation=RegulationFramework.GDPR,
        description="Ensure data is processed with user consent",
        check_function=check_data_privacy,
    )

    # Initialize and run compliance system
    regulatory_system = RegulatoryAlignmentSystem()
    regulatory_system.register_compliance_rule(privacy_rule)

    # Run compliance checks
    results = regulatory_system.run_compliance_checks()
    regulatory_system.generate_compliance_report(results)


if __name__ == "__main__":
    main()
