import pytest
from app.services.netdevops_service import netdevops_service


def test_audit_config_content():
    sample_config = """
    hostname SW-CORE-01
    no service password-encryption
    snmp-server community public RO
    """
    findings = netdevops_service.audit_config_content(sample_config)
    assert len(findings) >= 2
    rule_ids = [f["regle_cis"] for f in findings]
    assert any("CIS-1.1" in r for r in rule_ids)
    assert any("CIS-2.2" in r for r in rule_ids)
