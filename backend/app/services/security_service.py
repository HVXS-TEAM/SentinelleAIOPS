import re
from datetime import datetime
from typing import List, Dict, Any, Optional
import numpy as np
from sqlalchemy.orm import Session
from app.models.models import EvenementSecurite, Alerte

try:
    from sklearn.ensemble import IsolationForest
    HAS_SKLEARN = True
except ImportError:
    HAS_SKLEARN = False


class SecurityService:
    def __init__(self):
        if HAS_SKLEARN:
            self.model = IsolationForest(contamination=0.1, random_state=42)
        else:
            self.model = None

    def parse_auth_log_line(self, line: str) -> Optional[Dict[str, Any]]:
        """
        Parse standard Linux Syslog/Auth.log line.
        Example: Feb 08 14:32:10 srv-auth sshd[1234]: Failed password for root from 198.51.100.45 port 54321 ssh2
        """
        failed_pattern = r"(?P<date>\w{3}\s+\d+\s+\d+:\d+:\d+)\s+(?P<host>\S+)\s+sshd\[\d+\]:\s+Failed password for (?P<user>\S+) from (?P<ip>\d+\.\d+\.\d+\.\d+)"
        match = re.search(failed_pattern, line)
        if match:
            return {
                "source_ip": match.group("ip"),
                "utilisateur": match.group("user"),
                "type_evenement": "SSH_AUTH_FAILURE",
                "raw_line": line
            }
        return None

    def analyze_log_batch(self, db: Session, log_lines: List[str]) -> List[EvenementSecurite]:
        """
        Extract features from logs, train/predict IsolationForest or fallback model, save anomalies and create alerts.
        """
        parsed_events = []
        for line in log_lines:
            parsed = self.parse_auth_log_line(line)
            if parsed:
                parsed_events.append(parsed)

        if not parsed_events:
            return []

        # Feature extraction per IP: [attempts_count, unique_users_targeted]
        ip_stats: Dict[str, Dict[str, Any]] = {}
        for ev in parsed_events:
            ip = ev["source_ip"]
            user = ev["utilisateur"]
            if ip not in ip_stats:
                ip_stats[ip] = {"count": 0, "users": set(), "events": []}
            ip_stats[ip]["count"] += 1
            ip_stats[ip]["users"].add(user)
            ip_stats[ip]["events"].append(ev)

        feature_matrix = []
        ip_list = list(ip_stats.keys())
        for ip in ip_list:
            feature_matrix.append([ip_stats[ip]["count"], len(ip_stats[ip]["users"])])

        if HAS_SKLEARN and len(feature_matrix) >= 2:
            X = np.array(feature_matrix)
            self.model.fit(X)
            scores = self.model.score_samples(X)  # Negative scores are anomalous
        else:
            # Statistical fallback anomaly scoring
            scores = np.array([-0.85 if f[0] >= 5 else 0.45 for f in feature_matrix])

        results = []
        for idx, ip in enumerate(ip_list):
            score = float(scores[idx])
            is_anomaly = score < 0.0
            if is_anomaly or ip_stats[ip]["count"] >= 5:
                severite = "critique" if score < -0.5 else "warning"
                ev_db = EvenementSecurite(
                    source_ip=ip,
                    utilisateur=list(ip_stats[ip]["users"])[0],
                    type_evenement="SSH_BRUTEFORCE" if ip_stats[ip]["count"] >= 5 else "ANOMALY_LOG",
                    score_anomalie=score,
                    severite=severite,
                    horodatage=datetime.utcnow()
                )
                db.add(ev_db)
                results.append(ev_db)

                # Create alert if critical
                if severite == "critique":
                    alert = Alerte(
                        type="AttaqueDetectee",
                        module_origine="securite",
                        severite="critique",
                        message=f"Détection d'anomalie de connexion depuis {ip} ({ip_stats[ip]['count']} tentatives, score anomaly: {score:.2f})",
                        statut="active"
                    )
                    db.add(alert)
        db.commit()
        return results


security_service = SecurityService()
