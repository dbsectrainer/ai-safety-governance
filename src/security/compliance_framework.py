import typing
from dataclasses import dataclass, field
from datetime import datetime, timedelta
import json
import logging

@dataclass
class ComplianceRule:
    """Represents a specific compliance regulation rule."""
    name: str
    description: str
    regulation: str  # e.g., 'GDPR', 'HIPAA'
    severity: str = 'medium'
    is_active: bool = True

@dataclass
class ComplianceAudit:
    """Tracks compliance audit details."""
    timestamp: datetime = field(default_factory=datetime.now)
    rules_checked: list[ComplianceRule] = field(default_factory=list)
    violations: list[dict] = field(default_factory=list)
    compliance_score: float = 100.0

class ComplianceFramework:
    """Comprehensive compliance monitoring and enforcement system."""
    
    def __init__(self, config_path: str = 'config/compliance_config.json'):
        """
        Initialize compliance framework with configurable rules.
        
        :param config_path: Path to compliance configuration file
        """
        self.logger = logging.getLogger('compliance_framework')
        self.rules: list[ComplianceRule] = self._load_rules(config_path)
    
    def _load_rules(self, config_path: str) -> list[ComplianceRule]:
        """
        Load compliance rules from configuration file.
        
        :param config_path: Path to rules configuration
        :return: List of ComplianceRule instances
        """
        try:
            with open(config_path, 'r') as f:
                rule_configs = json.load(f)
            
            return [
                ComplianceRule(
                    name=rule['name'],
                    description=rule['description'],
                    regulation=rule['regulation'],
                    severity=rule.get('severity', 'medium'),
                    is_active=rule.get('is_active', True)
                ) for rule in rule_configs
            ]
        except FileNotFoundError:
            self.logger.warning(f"Compliance config not found at {config_path}")
            return []
        except json.JSONDecodeError:
            self.logger.error(f"Invalid JSON in compliance config at {config_path}")
            return []
    
    def perform_audit(self, data: typing.Any) -> ComplianceAudit:
        """
        Perform comprehensive compliance audit on given data.
        
        :param data: Data to be audited
        :return: ComplianceAudit instance with audit results
        """
        audit = ComplianceAudit()
        
        for rule in self.rules:
            if not rule.is_active:
                continue
            
            audit.rules_checked.append(rule)
            
            # Placeholder for actual compliance checks
            # In a real implementation, each rule would have specific validation logic
            violation = self._check_rule(rule, data)
            if violation:
                audit.violations.append(violation)
                # Reduce compliance score based on violation severity
                audit.compliance_score -= self._get_severity_impact(rule.severity)
        
        return audit
    
    def _check_rule(self, rule: ComplianceRule, data: typing.Any) -> typing.Optional[dict]:
        """
        Check a specific compliance rule against data.
        
        :param rule: Compliance rule to check
        :param data: Data to validate
        :return: Violation details or None
        """
        # Placeholder implementation
        # Actual implementation would depend on specific compliance requirements
        return None
    
    def _get_severity_impact(self, severity: str) -> float:
        """
        Calculate compliance score reduction based on violation severity.
        
        :param severity: Severity of the violation
        :return: Score reduction amount
        """
        severity_map = {
            'low': 1.0,
            'medium': 5.0,
            'high': 10.0,
            'critical': 20.0
        }
        return severity_map.get(severity.lower(), 5.0)
    
    def generate_report(self, audit: ComplianceAudit) -> dict:
        """
        Generate a comprehensive compliance report.
        
        :param audit: ComplianceAudit instance
        :return: Detailed compliance report
        """
        return {
            'timestamp': audit.timestamp.isoformat(),
            'compliance_score': audit.compliance_score,
            'total_rules_checked': len(audit.rules_checked),
            'violations': audit.violations,
            'recommendations': self._generate_recommendations(audit)
        }
    
    def _generate_recommendations(self, audit: ComplianceAudit) -> list[str]:
        """
        Generate recommendations based on audit results.
        
        :param audit: ComplianceAudit instance
        :return: List of compliance improvement recommendations
        """
        recommendations = []
        
        if audit.compliance_score < 90:
            recommendations.append("Immediate compliance review recommended")
        
        for violation in audit.violations:
            recommendations.append(f"Address violation: {violation}")
        
        return recommendations

def main():
    """Example usage of ComplianceFramework."""
    compliance_framework = ComplianceFramework()
    
    # Example data to audit
    sample_data = {
        'personal_data': 'sensitive information',
        'processing_purpose': 'example purpose'
    }
    
    audit = compliance_framework.perform_audit(sample_data)
    report = compliance_framework.generate_report(audit)
    
    print(json.dumps(report, indent=2))

if __name__ == '__main__':
    main()
