import os
import requests
from datetime import datetime
from typing import List, Dict, Any
from sqlalchemy.orm import Session
from app.models.models import Equipement, Alerte, AuditReseau, JournalAudit


class ReportingService:
    def generate_pdf_report(self, db: Session, output_path: str = "rapport_audit_sentinelle.pdf") -> str:
        """Generate PDF audit report using ReportLab."""
        try:
            from reportlab.lib.pagesizes import letter
            from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
            from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
            from reportlab.lib import colors

            doc = SimpleDocTemplate(output_path, pagesize=letter)
            styles = getSampleStyleSheet()
            story = []

            title_style = ParagraphStyle(
                'ReportTitle',
                parent=styles['Heading1'],
                fontSize=20,
                textColor=colors.HexColor('#101416'),
                spaceAfter=12
            )
            story.append(Paragraph("Sentinelle AIOps - Rapport d'Audit & Synthèse System", title_style))
            story.append(Paragraph(f"Généré le : {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", styles['Normal']))
            story.append(Spacer(1, 16))

            # Table Equipements
            story.append(Paragraph("<b>1. État du Parc Informatique</b>", styles['Heading2']))
            equipements = db.query(Equipement).all()
            data_eq = [["Nom", "IP", "Type", "Firmware", "Score Santé"]]
            for e in equipements:
                data_eq.append([e.nom, e.ip, e.type, e.firmware or "-", f"{e.health_score}%"])

            t_eq = Table(data_eq)
            t_eq.setStyle(TableStyle([
                ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#78D8BA')),
                ('TEXTCOLOR', (0,0), (-1,0), colors.HexColor('#101416')),
                ('GRID', (0,0), (-1,-1), 0.5, colors.grey),
            ]))
            story.append(t_eq)
            story.append(Spacer(1, 16))

            # Table Alertes
            story.append(Paragraph("<b>2. Alertes Critiques Actives</b>", styles['Heading2']))
            alertes = db.query(Alerte).filter(Alerte.statut == "active").all()
            data_al = [["Module", "Sévérité", "Message"]]
            for a in alertes:
                data_al.append([a.module_origine, a.severite, a.message[:60]])

            t_al = Table(data_al if len(data_al) > 1 else [["Module", "Sévérité", "Message"], ["N/A", "N/A", "Aucune alerte active"]])
            t_al.setStyle(TableStyle([
                ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#FFB4AB')),
                ('GRID', (0,0), (-1,-1), 0.5, colors.grey),
            ]))
            story.append(t_al)

            doc.build(story)
            return output_path
        except Exception as e:
            # Fallback simple text report if PDF build fails
            with open(output_path, "w", encoding="utf-8") as f:
                f.write(f"Rapport d'audit Sentinelle AIOps\nGénéré le: {datetime.now()}\n")
            return output_path

    def send_discord_notification(self, webhook_url: str, message: str) -> bool:
        """Send notification via Discord Webhook."""
        try:
            res = requests.post(webhook_url, json={"content": f"🚨 **Sentinelle AIOps Alert**\n{message}"}, timeout=5)
            return res.status_code in [200, 204]
        except Exception:
            return False


reporting_service = ReportingService()
