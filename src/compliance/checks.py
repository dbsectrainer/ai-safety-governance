"""Configuration-level compliance rules used by the API.

These checks validate that the platform's declared compliance controls are
configured with defensible values. They are not a legal certification and do
not inspect runtime data-plane behaviour.
"""

from typing import Any, Dict, List

from .regulatory_alignment import ComplianceRule, RegulationFramework


def _threshold(config: Dict[str, Any], framework: str, name: str) -> Any:
    values = config.get("compliance_thresholds", {}).get(framework, {})
    if isinstance(values, dict):
        return values.get(name)
    return None


def build_configuration_rules(config: Dict[str, Any]) -> List[ComplianceRule]:
    """Build one configuration rule per supported regulatory framework."""

    def gdpr_breach_notification() -> bool:
        notification_emails = config.get("notification_emails") or []
        window = _threshold(config, "gdpr", "data_breach_notification")
        return bool(notification_emails) and isinstance(window, (int, float)) and window <= 72

    def hipaa_breach_reporting() -> bool:
        window = _threshold(config, "hipaa", "breach_reporting")
        access_logging = _threshold(config, "hipaa", "access_logs")
        return (
            isinstance(window, (int, float))
            and window <= 60
            and isinstance(access_logging, (int, float))
            and access_logging >= 100
        )

    def ccpa_data_deletion() -> bool:
        window = _threshold(config, "ccpa", "data_deletion_requests")
        opt_out = _threshold(config, "ccpa", "opt_out_mechanism")
        return (
            isinstance(window, (int, float))
            and window <= 45
            and isinstance(opt_out, (int, float))
            and opt_out >= 100
        )

    return [
        ComplianceRule(
            regulation=RegulationFramework.GDPR,
            description=(
                "GDPR configuration: breach notification window <= 72 hours and "
                "compliance escalation contacts configured"
            ),
            check_function=gdpr_breach_notification,
        ),
        ComplianceRule(
            regulation=RegulationFramework.HIPAA,
            description=(
                "HIPAA configuration: breach reporting <= 60 days and 100% access-logging "
                "coverage declared"
            ),
            check_function=hipaa_breach_reporting,
        ),
        ComplianceRule(
            regulation=RegulationFramework.CCPA,
            description=(
                "CCPA configuration: data-deletion response <= 45 days and opt-out "
                "mechanism declared"
            ),
            check_function=ccpa_data_deletion,
        ),
    ]
