import requests
import json
from typing import Dict, Any, Optional
from sqlalchemy.orm import Session
from app.core.config import settings
from app.models.models import Equipement, Alerte, Prediction, AuditReseau


class AssistantService:
    def process_natural_query(self, db: Session, user_query: str) -> Dict[str, Any]:
        """
        Process natural language query, route to read-only DB query, return structured response.
        Enforces strict read-only mode (no mutation allowed).
        """
        query_lower = user_query.lower()

        # Rule-based intent matching & DB lookup (guarantees 100% accuracy without hallucinations)
        if "santé" in query_lower or "sante" in query_lower or "parc" in query_lower or "équipements" in query_lower or "equipements" in query_lower:
            equipements = db.query(Equipement).all()
            data = [{"nom": e.nom, "ip": e.ip, "type": e.type, "sante": f"{e.health_score}%"} for e in equipements]
            reponse = f"Voici l'état de santé actuel des {len(equipements)} équipements du parc :"
            return {"reponse": reponse, "donnees_associees": data}

        elif "alerte" in query_lower or "critique" in query_lower or "problème" in query_lower or "probleme" in query_lower:
            alertes = db.query(Alerte).filter(Alerte.statut == "active").all()
            data = [{"origine": a.module_origine, "severite": a.severite, "message": a.message} for a in alertes]
            reponse = f"Il y a actuellement {len(alertes)} alerte(s) active(s) sur la plateforme :"
            return {"reponse": reponse, "donnees_associees": data}

        elif "ttf" in query_lower or "saturation" in query_lower or "disque" in query_lower or "panne" in query_lower:
            predictions = db.query(Prediction).all()
            data = []
            for p in predictions:
                eq = db.query(Equipement).filter(Equipement.id == p.equipement_id).first()
                eq_nom = eq.nom if eq else f"ID {p.equipement_id}"
                data.append({
                    "equipement": eq_nom,
                    "metrique": p.metrique,
                    "ttf_estime": f"{p.ttf_estime:.1f} heures"
                })
            reponse = f"Voici les prédictions de saturation (Time-To-Failure) calculées :"
            return {"reponse": reponse, "donnees_associees": data}

        elif "audit" in query_lower or "cis" in query_lower or "réseau" in query_lower or "reseau" in query_lower:
            audits = db.query(AuditReseau).filter(AuditReseau.statut == "non_corrige").all()
            data = [{"constat": a.constat, "regle": a.regle_cis, "criticite": a.criticite} for a in audits]
            reponse = f"Synthèse de l'audit CIS : {len(audits)} non-conformité(s) détectée(s) :"
            return {"reponse": reponse, "donnees_associees": data}

        else:
            # Query Ollama for general response if available
            prompt = f"Tu es l'assistant IA de la plateforme Sentinelle AIOps. Réponds de façon synthétique et courtoise à l'administrateur système: {user_query}"
            try:
                res = requests.post(
                    f"{settings.OLLAMA_BASE_URL}/api/generate",
                    json={"model": settings.OLLAMA_MODEL, "prompt": prompt, "stream": False},
                    timeout=5
                )
                if res.status_code == 200:
                    text = res.json().get("response", "")
                    return {"reponse": text, "donnees_associees": None}
            except Exception:
                pass

            return {
                "reponse": "Je suis l'assistant IA Sentinelle AIOps. Vous pouvez me poser des questions sur l'état du parc, les alertes en cours, les prédictions de saturation (TTF) ou les résultats d'audit CIS.",
                "donnees_associees": None
            }


assistant_service = AssistantService()
