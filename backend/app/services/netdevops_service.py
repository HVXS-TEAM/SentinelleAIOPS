import requests
import json
import re
from datetime import datetime
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session
from app.core.config import settings
from app.models.models import AuditReseau, SauvegardeConfig, Equipement, Alerte


class NetDevOpsService:
    CIS_RULES = [
        {
            "id": "CIS-1.1",
            "name": "Password Encryption",
            "pattern": r"^\s*service password-encryption",
            "negative_match": True,  # Alert if line starting with service password-encryption is NOT found
            "criticite": "elevee",
            "constat": "Mots de passe utilisateur non chiffrés en mémoire (service password-encryption manquant)",
            "fix": "service password-encryption"
        },
        {
            "id": "CIS-2.2",
            "name": "SNMP v1/v2 Non Sécurisé",
            "pattern": r"snmp-server community (public|private)",
            "negative_match": False,  # Alert if pattern IS found
            "criticite": "elevee",
            "constat": "Communauté SNMP v1/v2 par défaut (public/private) activée",
            "fix": "no snmp-server community public RO\nno snmp-server community private RW"
        },
        {
            "id": "CIS-3.1",
            "name": "Bannière Légale MOTD",
            "pattern": r"^\s*banner motd",
            "negative_match": True,
            "criticite": "moyenne",
            "constat": "Absence de bannière légale d'avertissement (banner motd)",
            "fix": "banner motd # ACCES RESTREINT AUX PERSONNES AUTORISEES ONLY #"
        }
    ]

    def audit_config_content(self, config_text: str) -> List[Dict[str, Any]]:
        """Static rule check based on CIS Benchmark patterns."""
        results = []
        for rule in self.CIS_RULES:
            match = re.search(rule["pattern"], config_text, re.MULTILINE | re.IGNORECASE)
            is_failing = (not match) if rule["negative_match"] else bool(match)
            if is_failing:
                results.append({
                    "regle_cis": f"{rule['id']} - {rule['name']}",
                    "constat": rule["constat"],
                    "criticite": rule["criticite"],
                    "correctif_propose": rule["fix"]
                })
        return results

    def query_ollama_audit(self, config_text: str) -> Optional[Dict[str, Any]]:
        """
        Query local Ollama LLM for structured CIS Audit recommendation.
        Returns parsed JSON or None if Ollama is unreachable.
        """
        prompt = f"""Tu es un expert en cybersécurité réseau Cisco. Analyse la configuration suivante selon le référentiel CIS Benchmark.
Structure ta réponse obligatoirement en JSON strict avec les clés: "constat", "regle_cis", "criticite", "correctif_propose".

Configuration:
```
{config_text[:2000]}
```
"""
        try:
            response = requests.post(
                f"{settings.OLLAMA_BASE_URL}/api/generate",
                json={
                    "model": settings.OLLAMA_MODEL,
                    "prompt": prompt,
                    "stream": False,
                    "format": "json"
                },
                timeout=5
            )
            if response.status_code == 200:
                data = response.json()
                return json.loads(data.get("response", "{}"))
        except Exception:
            # Ollama offline fallback to static rules
            pass
        return None

    def run_full_audit(self, db: Session, equipement_id: int, config_text: str) -> List[AuditReseau]:
        """Run audit against config text, save backups and audit logs."""
        import hashlib
        hash_val = hashlib.sha256(config_text.encode('utf-8')).hexdigest()

        # Save configuration backup
        backup = SauvegardeConfig(
            equipement_id=equipement_id,
            contenu=config_text,
            hash_integrite=hash_val,
            date_sauvegarde=datetime.utcnow()
        )
        db.add(backup)

        audits_db = []
        static_findings = self.audit_config_content(config_text)

        # Try LLM enhancement
        llm_finding = self.query_ollama_audit(config_text)
        if llm_finding and "constat" in llm_finding:
            static_findings.append({
                "regle_cis": llm_finding.get("regle_cis", "CIS-LLM-01"),
                "constat": llm_finding["constat"],
                "criticite": llm_finding.get("criticite", "moyenne"),
                "correctif_propose": llm_finding.get("correctif_propose", "")
            })

        for item in static_findings:
            audit = AuditReseau(
                equipement_id=equipement_id,
                constat=item["constat"],
                regle_cis=item["regle_cis"],
                criticite=item["criticite"],
                correctif_propose=item["correctif_propose"],
                statut="non_corrige",
                date_audit=datetime.utcnow()
            )
            db.add(audit)
            audits_db.append(audit)

        db.commit()
        return audits_db


netdevops_service = NetDevOpsService()
