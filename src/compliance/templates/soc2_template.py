"""SOC 2 Type II compliance control definitions.

Reference: AICPA Trust Services Criteria
"""

SOC2_CONTROLS = {
    "CC1.1": {
        "name": "Control Environment",
        "description": "Entity demonstrates commitment to integrity and ethical values",
        "evidence": ["code_review_logs", "test_results", "agent_audit_trail"],
        "automated": True
    },
    "CC1.2": {
        "name": "Board Oversight",
        "description": "Board of directors demonstrates independence from management",
        "evidence": ["governance_docs", "sprint_reports"],
        "automated": True
    },
    "CC2.1": {
        "name": "Communication",
        "description": "Entity communicates internally about objectives",
        "evidence": ["sprint_reports", "test_plans"],
        "automated": True
    },
    "CC2.2": {
        "name": "Internal Communication",
        "description": "Entity communicates internally about matters affecting internal control",
        "evidence": ["agent_logs", "test_execution_logs"],
        "automated": True
    },
    "CC3.1": {
        "name": "Risk Assessment",
        "description": "Entity specifies objectives with sufficient clarity",
        "evidence": ["risk_assessments", "defect_density_data"],
        "automated": True
    },
    "CC3.2": {
        "name": "Risk Identification",
        "description": "Entity identifies risks to achievement of objectives",
        "evidence": ["historical_analyses", "sprint_reports"],
        "automated": True
    },
    "CC4.1": {
        "name": "Monitoring Activities",
        "description": "Entity selects and develops ongoing evaluations",
        "evidence": ["test_execution_logs", "release_certifications"],
        "automated": True
    },
    "CC4.2": {
        "name": "Remediation",
        "description": "Entity evaluates and communicates deficiencies",
        "evidence": ["defect_reports", "release_notes"],
        "automated": True
    },
    "CC5.1": {
        "name": "Control Activities",
        "description": "Entity selects and develops control activities",
        "evidence": ["automated_test_results", "security_scan_results"],
        "automated": True
    },
    "CC5.2": {
        "name": "Technology Controls",
        "description": "Entity deploys control activities through technology",
        "evidence": ["ci_cd_logs", "security_scan_results"],
        "automated": True
    },
    "CC6.1": {
        "name": "Logical Access",
        "description": "Entity implements logical access security",
        "evidence": ["security_scan_results", "zap_scan_reports"],
        "automated": True
    },
    "CC6.2": {
        "name": "Access Rights",
        "description": "Entity assigns and manages access rights",
        "evidence": ["access_logs", "security_configs"],
        "automated": True
    },
    "CC6.3": {
        "name": "Access Removal",
        "description": "Entity removes access when appropriate",
        "evidence": ["access_logs", "deprovisioning_records"],
        "automated": True
    },
    "CC6.6": {
        "name": "Security Events",
        "description": "Entity implements controls to prevent or detect unauthorized activity",
        "evidence": ["security_scan_results", "vulnerability_reports"],
        "automated": True
    },
    "CC7.1": {
        "name": "Vulnerability Management",
        "description": "Entity identifies and evaluates vulnerabilities",
        "evidence": ["security_scan_results", "dependency_audits"],
        "automated": True
    },
    "CC7.2": {
        "name": "Vulnerability Response",
        "description": "Entity monitors system components for anomalies",
        "evidence": ["security_reports", "incident_logs"],
        "automated": True
    },
    "CC8.1": {
        "name": "Change Management",
        "description": "Entity manages changes to entity-level controls",
        "evidence": ["sprint_reports", "change_logs"],
        "automated": True
    },
    "CC8.2": {
        "name": "Change Authorization",
        "description": "Entity authorizes, designs, develops, and implements changes",
        "evidence": ["code_review_logs", "ci_cd_logs"],
        "automated": True
    },
    "CC9.1": {
        "name": "Operations",
        "description": "Entity manages operational processes",
        "evidence": ["deployment_logs", "release_notes"],
        "automated": True
    }
}
