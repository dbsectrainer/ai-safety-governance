import unittest
import sys
import os
import json
from datetime import datetime, timedelta

# Add the project root to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from src.compliance.regulatory_alignment import (
    RegulatoryAlignmentSystem, 
    ComplianceRule, 
    RegulationFramework, 
    ComplianceStatus
)

class TestRegulatoryAlignmentSystem(unittest.TestCase):
    def setUp(self):
        """
        Set up test environment for Regulatory Alignment System.
        """
        # Use a temporary config for testing
        self.test_config_path = 'tests/test_compliance_config.json'
        with open(self.test_config_path, 'w') as f:
            json.dump({
                "check_frequency_days": 30,
                "auto_remediation": True,
                "notification_emails": ["test@example.com"]
            }, f)
        
        self.regulatory_system = RegulatoryAlignmentSystem(
            config_path=self.test_config_path
        )
    
    def tearDown(self):
        """
        Clean up test environment.
        """
        if os.path.exists(self.test_config_path):
            os.remove(self.test_config_path)
    
    def test_config_loading(self):
        """
        Test loading of compliance configuration.
        """
        config = self.regulatory_system.config
        
        self.assertIn("check_frequency_days", config)
        self.assertIn("auto_remediation", config)
        self.assertEqual(config["check_frequency_days"], 30)
        self.assertTrue(config["auto_remediation"])
    
    def test_compliance_rule_registration(self):
        """
        Test registration of compliance rules.
        """
        def mock_compliance_check():
            return True
        
        rule = ComplianceRule(
            regulation=RegulationFramework.GDPR,
            description="Test Compliance Rule",
            check_function=mock_compliance_check
        )
        
        self.regulatory_system.register_compliance_rule(rule)
        
        self.assertEqual(len(self.regulatory_system.compliance_rules), 1)
        self.assertEqual(
            self.regulatory_system.compliance_rules[0].description, 
            "Test Compliance Rule"
        )
    
    def test_compliance_checks(self):
        """
        Test running compliance checks.
        """
        def compliant_check():
            return True
        
        def non_compliant_check():
            return False
        
        compliant_rule = ComplianceRule(
            regulation=RegulationFramework.GDPR,
            description="Compliant Rule",
            check_function=compliant_check
        )
        
        non_compliant_rule = ComplianceRule(
            regulation=RegulationFramework.HIPAA,
            description="Non-Compliant Rule",
            check_function=non_compliant_check
        )
        
        self.regulatory_system.register_compliance_rule(compliant_rule)
        self.regulatory_system.register_compliance_rule(non_compliant_rule)
        
        results = self.regulatory_system.run_compliance_checks()
        
        self.assertEqual(results['total_rules'], 2)
        self.assertEqual(results['compliant_rules'], 1)
        self.assertEqual(results['non_compliant_rules'], 1)
    
    def test_compliance_report_generation(self):
        """
        Test generation of compliance reports.
        """
        def mock_check():
            return True
        
        rule = ComplianceRule(
            regulation=RegulationFramework.GDPR,
            description="Report Generation Test",
            check_function=mock_check
        )
        
        self.regulatory_system.register_compliance_rule(rule)
        results = self.regulatory_system.run_compliance_checks()
        report_path = self.regulatory_system.generate_compliance_report(results)
        
        self.assertTrue(os.path.exists(report_path))
        
        with open(report_path, 'r') as f:
            report_data = json.load(f)
        
        self.assertEqual(report_data['total_rules'], 1)
        self.assertEqual(report_data['compliant_rules'], 1)
    
    def test_error_handling(self):
        """
        Test error handling in compliance checks.
        """
        def error_check():
            raise ValueError("Simulated error")
        
        error_rule = ComplianceRule(
            regulation=RegulationFramework.CCPA,
            description="Error Handling Test",
            check_function=error_check
        )
        
        self.regulatory_system.register_compliance_rule(error_rule)
        
        # This should not raise an exception
        results = self.regulatory_system.run_compliance_checks()
        
        # Verify that the error was logged
        log_files = os.listdir(self.regulatory_system.audit_trail.output_dir)
        self.assertTrue(any('compliance_audit' in log_file for log_file in log_files))

if __name__ == '__main__':
    unittest.main()
