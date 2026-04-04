"""ISO 27001:2022 compliance control definitions.

Reference: ISO/IEC 27001:2022 Information Security Controls
"""

ISO27001_CONTROLS = {
    "A.5.1.1": {
        "name": "Policies for information security",
        "description": "Information security policy and topic-specific policies",
        "evidence": ["security_policies", "test_coverage_reports"],
        "automated": True
    },
    "A.5.1.2": {
        "name": "Policy Review",
        "description": "Review of information security policies",
        "evidence": ["policy_reviews", "approval_records"],
        "automated": True
    },
    "A.6.1.1": {
        "name": "Information Security Roles",
        "description": "Information security roles and responsibilities",
        "evidence": ["role_assignments", "org_charts"],
        "automated": True
    },
    "A.7.1.1": {
        "name": "Physical Security Perimeters",
        "description": "Physical security perimeter requirements",
        "evidence": ["environment_configs", "infrastructure_docs"],
        "automated": True
    },
    "A.8.1.1": {
        "name": "Asset Inventory",
        "description": "Inventory of assets with owners",
        "evidence": ["test_assets", "environment_configs"],
        "automated": True
    },
    "A.8.1.2": {
        "name": "Asset Ownership",
        "description": "Assets are accounted for and owned",
        "evidence": ["asset_registry", "ownership_records"],
        "automated": True
    },
    "A.9.1.1": {
        "name": "Access Control Policy",
        "description": "Information access restriction policy",
        "evidence": ["security_scan_results"],
        "automated": True
    },
    "A.9.1.2": {
        "name": "Access Rights Provisioning",
        "description": "Access rights are provisioned appropriately",
        "evidence": ["access_logs", "provisioning_records"],
        "automated": True
    },
    "A.9.4.1": {
        "name": "Information Access Restriction",
        "description": "Access to information is restricted",
        "evidence": ["security_scan_results", "access_logs"],
        "automated": True
    },
    "A.9.4.5": {
        "name": "Secure Authentication",
        "description": "Secure authentication technologies and procedures",
        "evidence": ["security_scan_results", "auth_configs"],
        "automated": True
    },
    "A.12.1.1": {
        "name": "Operational Procedures",
        "description": "Documented operating procedures",
        "evidence": ["test_procedures", "agent_logs"],
        "automated": True
    },
    "A.12.1.2": {
        "name": "Change Management",
        "description": "Changes to organization and business processes",
        "evidence": ["sprint_reports", "change_logs"],
        "automated": True
    },
    "A.12.2.1": {
        "name": "Protection from malware",
        "description": "Detection, prevention and recovery controls",
        "evidence": ["security_scan_results", "dependency_audits"],
        "automated": True
    },
    "A.12.4.1": {
        "name": "Event Logging",
        "description": "Event logs are produced, stored, protected",
        "evidence": ["agent_logs", "audit_trails"],
        "automated": True
    },
    "A.12.4.2": {
        "name": "Log Protection",
        "description": "Logs are protected from tampering",
        "evidence": ["audit_trails", "integrity_checks"],
        "automated": True
    },
    "A.12.5.1": {
        "name": "Software Installation",
        "description": "Installation of software on operational systems",
        "evidence": ["dependency_audits", "security_configs"],
        "automated": True
    },
    "A.12.6.1": {
        "name": "Vulnerability Management",
        "description": "Management of technical vulnerabilities",
        "evidence": ["security_scan_results", "vulnerability_reports"],
        "automated": True
    },
    "A.12.7.1": {
        "name": "Audit Planning",
        "description": "Information systems audit controls",
        "evidence": ["test_results", "audit_logs"],
        "automated": True
    },
    "A.14.1.1": {
        "name": "Security Requirements",
        "description": "Information security requirements included",
        "evidence": ["test_results", "security_reports"],
        "automated": True
    },
    "A.14.1.2": {
        "name": "Application Security",
        "description": "Security requirements in application services",
        "evidence": ["security_scan_results", "test_results"],
        "automated": True
    },
    "A.14.2.1": {
        "name": "Secure Development Policy",
        "description": "Secure development policy and procedures",
        "evidence": ["code_review_logs", "security_policies"],
        "automated": True
    },
    "A.14.2.8": {
        "name": "Security Testing",
        "description": "Security testing in development lifecycle",
        "evidence": ["security_scan_results", "test_results"],
        "automated": True
    }
}
