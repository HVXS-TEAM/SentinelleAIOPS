import pytest
from app.services.security_service import security_service


def test_parse_auth_log_line():
    line = "Feb 08 14:32:10 srv-auth sshd[1234]: Failed password for root from 198.51.100.45 port 54321 ssh2"
    parsed = security_service.parse_auth_log_line(line)
    assert parsed is not None
    assert parsed["source_ip"] == "198.51.100.45"
    assert parsed["utilisateur"] == "root"
    assert parsed["type_evenement"] == "SSH_AUTH_FAILURE"


def test_parse_non_auth_line():
    line = "Feb 08 14:32:10 srv-auth systemd[1]: Started Periodic Background Jobs."
    parsed = security_service.parse_auth_log_line(line)
    assert parsed is None
