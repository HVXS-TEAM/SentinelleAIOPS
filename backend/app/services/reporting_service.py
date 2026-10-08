"""
Sentinelle AIOps - Service de reporting (étape 4).

`build_pdf_report(db, generated_by)` produit un rapport d'audit PDF (A4) en mémoire, à partir de l'état réel
de la base : synthèse, état du parc, alertes, prédictions de saturation (TTF), sécurité, conformité CIS,
recommandations. Aucun fichier n'est écrit sur le disque (pas de collision entre deux demandes simultanées)
et aucune erreur n'est avalée : si ReportLab manque, une ReportUnavailableError explicite est levée.

Le journal d'audit n'est volontairement PAS inclus : il est réservé au rôle Administrateur.
"""
import io
import os
import requests
from datetime import datetime, timedelta
from app.core.time_utils import utcnow_naive
from typing import Dict, List, Optional, Tuple
from xml.sax.saxutils import escape

from sqlalchemy.orm import Session

from app.models.models import (
    Alerte, AuditReseau, Equipement, EvenementSecurite, Prediction, SauvegardeConfig,
)

LOGO_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "assets", "sentinelle_logo_pdf.png")

RECENT_WINDOW = timedelta(hours=24)
MAX_ROWS = {"alertes": 15, "predictions": 10, "evenements": 10, "audits": 12}

# Palette Sentinelle (fond sombre + teal), adaptée à l'impression
C_DARK, C_TEAL, C_INK = "#101416", "#78D8BA", "#1B2327"
C_OK, C_WARN, C_CRIT = "#1E8E6E", "#C77700", "#C0392B"
C_ROW, C_LINE, C_MUTED = "#F3F6F5", "#D5DDDA", "#5F6B70"
CRITICITE_RANK = {"elevee": 0, "moyenne": 1, "faible": 2}
METRIC_LABELS = {"disk_percent": "Disque", "cpu_percent": "CPU", "ram_percent": "Mémoire", "bandwidth_mbps": "Bande passante"}


class ReportUnavailableError(RuntimeError):
    """ReportLab n'est pas installé dans l'environnement du back-end."""


def _e(value) -> str:
    """Échappe le texte destiné à un Paragraph ReportLab (qui interprète un mini-XML)."""
    return escape(str(value if value is not None else "-"))


def _short(text, n: int) -> str:
    text = " ".join(str(text or "-").split())
    return text if len(text) <= n else text[: n - 1] + "…"


def _fmt(dt: Optional[datetime]) -> str:
    return dt.strftime("%d/%m/%Y %H:%M") if dt else "-"


def _health_color(score: float) -> str:
    return C_OK if score >= 80 else (C_WARN if score >= 50 else C_CRIT)


def _sev_color(sev: str) -> str:
    return C_CRIT if sev == "critique" else (C_WARN if sev == "warning" else C_MUTED)


def _ttf_label(hours: float) -> str:
    if hours < 1:
        return f"{max(1, round(hours * 60))} min"
    return f"{hours:.1f} h"


class ReportingService:
    # ------------------------------------------------------------------ données
    def _collect(self, db: Session, now: datetime) -> Dict:
        since = now - RECENT_WINDOW
        equipements = db.query(Equipement).order_by(Equipement.id).all()
        names = {e.id: e.nom for e in equipements}

        alertes_actives = db.query(Alerte).filter(Alerte.statut == "active").order_by(
            Alerte.date_creation.desc()).all()
        nb_acquittees = db.query(Alerte).filter(Alerte.statut == "acquitte").count()

        latest: Dict[Tuple[int, str], Prediction] = {}
        for p in db.query(Prediction).filter(Prediction.date_calcul >= since).order_by(
                Prediction.date_calcul.desc()).all():
            latest.setdefault((p.equipement_id, p.metrique), p)
        predictions = sorted((p for p in latest.values() if p.ttf_estime < 48.0), key=lambda p: p.ttf_estime)

        events_q = db.query(EvenementSecurite).filter(EvenementSecurite.horodatage >= since)
        events = events_q.order_by(EvenementSecurite.horodatage.desc()).all()

        audits = db.query(AuditReseau).filter(AuditReseau.statut == "non_corrige").all()
        audits.sort(key=lambda a: (CRITICITE_RANK.get(a.criticite, 9), -(a.date_audit or now).timestamp()))

        backups_n = db.query(SauvegardeConfig).count()
        last_backup = db.query(SauvegardeConfig).order_by(SauvegardeConfig.date_sauvegarde.desc()).first()

        scores = [e.health_score for e in equipements]
        crit = sum(1 for a in alertes_actives if a.severite == "critique")
        warn = sum(1 for a in alertes_actives if a.severite == "warning")
        audits_high = sum(1 for a in audits if a.criticite == "elevee")
        avg = round(sum(scores) / len(scores), 1) if scores else 100.0
        low = min(scores) if scores else 100.0

        if crit > 0 or low < 50:
            niveau = "CRITIQUE"
        elif warn > 0 or avg < 80 or audits_high > 0 or predictions:
            niveau = "DÉGRADÉ"
        else:
            niveau = "NOMINAL"

        return dict(
            equipements=equipements, names=names, alertes=alertes_actives, nb_acquittees=nb_acquittees,
            crit=crit, warn=warn, predictions=predictions, events=events, audits=audits,
            audits_high=audits_high, backups_n=backups_n, last_backup=last_backup, avg=avg, niveau=niveau,
            events_crit=sum(1 for e in events if e.severite == "critique"),
        )

    def _recommendations(self, d: Dict) -> List[str]:
        recs: List[str] = []
        for p in d["predictions"][:3]:
            eq = d["names"].get(p.equipement_id, f"#{p.equipement_id}")
            metric = METRIC_LABELS.get(p.metrique, p.metrique)
            recs.append(f"<b>{_e(eq)}</b> : saturation prévue ({_e(metric.lower())}) dans {_ttf_label(p.ttf_estime)}. "
                        "Libérer ou étendre la ressource avant l'échéance.")
        brute = [e for e in d["events"] if e.type_evenement == "SSH_BRUTEFORCE"]
        if brute:
            ips = ", ".join(sorted({e.source_ip for e in brute})[:3])
            recs.append(f"Attaque par force brute SSH détectée depuis <b>{_e(ips)}</b> : bloquer la source au pare-feu "
                        "et vérifier les comptes ciblés (root, comptes de service).")
        if d["audits_high"]:
            regles = ", ".join(sorted({a.regle_cis for a in d["audits"] if a.criticite == "elevee"})[:4])
            recs.append(f"<b>{d['audits_high']}</b> non-conformité(s) CIS de criticité élevée ouvertes ({_e(regles)}) : "
                        "appliquer les correctifs proposés par le module NetDevOps.")
        low = [e for e in d["equipements"] if e.health_score < 50]
        for e in low[:2]:
            recs.append(f"<b>{_e(e.nom)}</b> présente un score de santé de {e.health_score:.0f} % : "
                        "planifier une intervention.")
        if not recs:
            recs.append("Aucune action prioritaire : le parc est nominal. Poursuivre la surveillance continue.")
        return recs

    # --------------------------------------------------------------------- PDF
    def build_pdf_report(self, db: Session, generated_by: Optional[str] = None,
                         now: Optional[datetime] = None) -> bytes:
        try:
            from reportlab.lib import colors
            from reportlab.lib.enums import TA_RIGHT
            from reportlab.lib.pagesizes import A4
            from reportlab.lib.styles import ParagraphStyle
            from reportlab.lib.units import mm
            from reportlab.pdfgen import canvas as rl_canvas
            from reportlab.platypus import (KeepTogether, Paragraph, SimpleDocTemplate, Spacer, Table,
                                            TableStyle, HRFlowable)
            from reportlab.graphics.shapes import Drawing
            from reportlab.graphics.charts.barcharts import HorizontalBarChart
        except ImportError as exc:  # pragma: no cover - dépend de l'environnement
            raise ReportUnavailableError(
                "Le module ReportLab n'est pas installé sur le serveur (pip install reportlab)."
            ) from exc

        now = now or utcnow_naive()
        d = self._collect(db, now)
        hx = colors.HexColor
        W = A4[0] - 36 * mm  # largeur utile

        # ---- styles
        body = ParagraphStyle("body", fontName="Helvetica", fontSize=9, leading=12.5, textColor=hx(C_INK))
        small = ParagraphStyle("small", parent=body, fontSize=8, leading=10.5, textColor=hx(C_MUTED))
        h1 = ParagraphStyle("h1", parent=body, fontName="Helvetica-Bold", fontSize=18, leading=22, textColor=hx(C_DARK))
        h2 = ParagraphStyle("h2", parent=body, fontName="Helvetica-Bold", fontSize=12, leading=15,
                            textColor=hx(C_DARK), spaceBefore=14, spaceAfter=2, keepWithNext=1)
        sub = ParagraphStyle("sub", parent=small, keepWithNext=1)
        cell = ParagraphStyle("cell", parent=body, fontSize=8, leading=10)
        cellb = ParagraphStyle("cellb", parent=cell, fontName="Helvetica-Bold")
        head = ParagraphStyle("head", parent=cell, fontName="Helvetica-Bold", textColor=colors.white)
        right = ParagraphStyle("right", parent=cell, alignment=TA_RIGHT)

        def section(title: str, subtitle: str = ""):
            rule = HRFlowable(width="100%", thickness=1.2, color=hx(C_TEAL), spaceAfter=5)
            rule.keepWithNext = 1          # un titre de section ne reste jamais seul en bas de page
            out = [Paragraph(_e(title), h2), rule]
            if subtitle:
                gap = Spacer(1, 4)
                gap.keepWithNext = 1
                out += [Paragraph(subtitle, sub), gap]
            return out

        def table(headers: List[str], rows: List[List], widths: List[float]):
            data = [[Paragraph(_e(h), head) for h in headers]] + rows
            t = Table(data, colWidths=widths, repeatRows=1)
            style = [
                ("BACKGROUND", (0, 0), (-1, 0), hx(C_DARK)),
                ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ("LINEBELOW", (0, 0), (-1, -1), 0.4, hx(C_LINE)),
                ("LEFTPADDING", (0, 0), (-1, -1), 5), ("RIGHTPADDING", (0, 0), (-1, -1), 5),
                ("TOPPADDING", (0, 0), (-1, -1), 4), ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
            ]
            for i in range(1, len(data)):
                if i % 2 == 0:
                    style.append(("BACKGROUND", (0, i), (-1, i), hx(C_ROW)))
            t.setStyle(TableStyle(style))
            return t

        def colored(text: str, color: str, bold=True) -> Paragraph:
            return Paragraph(f'<font color="{color}">{"<b>" if bold else ""}{_e(text)}{"</b>" if bold else ""}</font>', cell)

        def empty_note(text: str):
            return Paragraph(f'<font color="{C_OK}"><b>{_e(text)}</b></font>', body)

        story: List = []

        # ---- titre
        auteur = f" par <b>{_e(generated_by)}</b>" if generated_by else ""
        story.append(Paragraph("Rapport d'audit et de synthèse", h1))
        story.append(Paragraph(f"Généré le {_e(now.strftime('%d/%m/%Y à %H:%M'))} (UTC){auteur}. "
                               "Données : état courant du parc et dernières 24 heures.", small))
        story.append(Spacer(1, 10))

        # ---- niveau global + KPI
        niveau_color = {"NOMINAL": C_OK, "DÉGRADÉ": C_WARN, "CRITIQUE": C_CRIT}[d["niveau"]]
        pill = Table([[Paragraph(f'<font color="white"><b>NIVEAU GLOBAL : {d["niveau"]}</b></font>',
                                 ParagraphStyle("pill", parent=body, fontSize=10, alignment=1))]], colWidths=[W])
        pill.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, -1), hx(niveau_color)),
                                  ("TOPPADDING", (0, 0), (-1, -1), 6), ("BOTTOMPADDING", (0, 0), (-1, -1), 6)]))
        story += [pill, Spacer(1, 8)]

        def kpi(value: str, label: str, color: str = C_DARK):
            return [Paragraph(f'<font size="20" color="{color}"><b>{_e(value)}</b></font>',
                              ParagraphStyle("kv", parent=body, leading=24)),
                    Paragraph(_e(label), small)]

        nb_pred = len(d["predictions"])
        kpis = [
            kpi(str(len(d["equipements"])), "équipements supervisés"),
            kpi(f"{d['avg']:.0f} %", "score de santé moyen", _health_color(d["avg"])),
            kpi(str(len(d["alertes"])), "alertes actives" + (f" dont {d['crit']} critique(s)" if d["crit"] else ""),
                C_CRIT if d["crit"] else (C_WARN if d["warn"] else C_OK)),
            kpi(str(nb_pred), "saturation(s) prévue(s) sous 48 h", C_WARN if nb_pred else C_OK),
            kpi(str(len(d["audits"])), "non-conformité(s) CIS ouvertes", C_CRIT if d["audits_high"] else (C_WARN if d["audits"] else C_OK)),
            kpi(str(len(d["events"])), "événements de sécurité (24 h)", C_CRIT if d["events_crit"] else C_DARK),
        ]
        grid = Table([kpis[:3], kpis[3:]], colWidths=[W / 3] * 3)
        grid.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, -1), hx(C_ROW)),
            ("LINEABOVE", (0, 0), (-1, 0), 2, hx(C_TEAL)),
            ("BOX", (0, 0), (-1, -1), 0.5, hx(C_LINE)), ("INNERGRID", (0, 0), (-1, -1), 0.5, hx(C_LINE)),
            ("LEFTPADDING", (0, 0), (-1, -1), 10), ("TOPPADDING", (0, 0), (-1, -1), 8), ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
        ]))
        story.append(grid)

        # ---- 1. Parc
        story += section("1. État du parc informatique", "Score de santé (0-100 %) calculé à partir des audits, "
                         "événements de sécurité, prédictions de saturation et de l'occupation disque.")
        if d["equipements"]:
            n = len(d["equipements"])
            height = max(60, 22 * n + 24)
            chart = HorizontalBarChart()
            chart.x, chart.y, chart.width, chart.height = 90, 14, W / 1.0 - 130, height - 24
            chart.data = [[e.health_score for e in reversed(d["equipements"])]]
            chart.categoryAxis.categoryNames = [e.nom for e in reversed(d["equipements"])]
            chart.categoryAxis.labels.fontName = "Helvetica"
            chart.categoryAxis.labels.fontSize = 8
            chart.valueAxis.valueMin, chart.valueAxis.valueMax, chart.valueAxis.valueStep = 0, 100, 25
            chart.valueAxis.labels.fontSize = 7
            chart.valueAxis.gridStrokeColor = hx(C_LINE)
            chart.valueAxis.visibleGrid = True
            chart.barWidth = 11
            chart.bars.strokeColor = None
            for i, e in enumerate(reversed(d["equipements"])):
                chart.bars[(0, i)].fillColor = hx(_health_color(e.health_score))
            drawing = Drawing(W, height)
            drawing.add(chart)
            story.append(drawing)
            rows = [[Paragraph(f"<b>{_e(e.nom)}</b>", cell), Paragraph(_e(e.ip), cell), Paragraph(_e(e.type), cell),
                     Paragraph(_e(_short(e.os, 26)), cell), colored(f"{e.health_score:.0f} %", _health_color(e.health_score))]
                    for e in d["equipements"]]
            story.append(table(["Équipement", "Adresse IP", "Type", "Système", "Santé"], rows,
                               [W * 0.24, W * 0.20, W * 0.15, W * 0.29, W * 0.12]))
        else:
            story.append(Paragraph("Aucun équipement enregistré.", body))

        # ---- 2. Alertes
        acq = f" {d['nb_acquittees']} alerte(s) acquittée(s) non listée(s)." if d["nb_acquittees"] else ""
        story += section("2. Alertes actives", f"Triées de la plus récente à la plus ancienne.{acq}")
        if d["alertes"]:
            shown = d["alertes"][: MAX_ROWS["alertes"]]
            rows = [[colored(a.severite.upper(), _sev_color(a.severite)), Paragraph(_e(a.module_origine), cell),
                     Paragraph(_e(_short(a.message, 170)), cell), Paragraph(_e(_fmt(a.date_creation)), cell)]
                    for a in shown]
            story.append(table(["Sévérité", "Module", "Message", "Depuis"], rows,
                               [W * 0.13, W * 0.14, W * 0.55, W * 0.18]))
            if len(d["alertes"]) > len(shown):
                story.append(Paragraph(f"… et {len(d['alertes']) - len(shown)} autre(s) alerte(s) non affichée(s).", small))
        else:
            story.append(empty_note("Aucune alerte active."))

        # ---- 3. Supervision prédictive
        story += section("3. Supervision prédictive (TTF)",
                         "Dernière estimation par équipement et métrique (régression linéaire sur télémétrie récente), "
                         "saturations attendues sous 48 h.")
        if d["predictions"]:
            rows = []
            for p in d["predictions"][: MAX_ROWS["predictions"]]:
                col = C_CRIT if p.ttf_estime < 24 else C_WARN
                rows.append([Paragraph(f"<b>{_e(d['names'].get(p.equipement_id, p.equipement_id))}</b>", cell),
                             Paragraph(_e(METRIC_LABELS.get(p.metrique, p.metrique)), cell),
                             colored(_ttf_label(p.ttf_estime), col), Paragraph(_e(_fmt(p.date_calcul)), cell)])
            story.append(table(["Équipement", "Ressource", "Saturation dans", "Calculé le"], rows,
                               [W * 0.30, W * 0.22, W * 0.22, W * 0.26]))
        else:
            story.append(empty_note("Aucune saturation prévue sous 48 h."))

        # ---- 4. Sécurité
        n_by = {s: sum(1 for e in d["events"] if e.severite == s) for s in ("critique", "warning", "info")}
        story += section("4. Sécurité", f"Événements des dernières 24 h : {n_by['critique']} critique(s), "
                         f"{n_by['warning']} avertissement(s), {n_by['info']} information(s). Détection par Isolation Forest.")
        if d["events"]:
            rows = [[Paragraph(_e(_fmt(e.horodatage)), cell), Paragraph(f"<b>{_e(e.type_evenement)}</b>", cell),
                     Paragraph(_e(e.source_ip), cell), Paragraph(_e(d["names"].get(e.equipement_id, "-")), cell),
                     colored(e.severite.upper(), _sev_color(e.severite)), Paragraph(f"{e.score_anomalie:.2f}", right)]
                    for e in d["events"][: MAX_ROWS["evenements"]]]
            story.append(table(["Date", "Type", "Source", "Cible", "Sévérité", "Score"], rows,
                               [W * 0.19, W * 0.23, W * 0.18, W * 0.17, W * 0.13, W * 0.10]))
        else:
            story.append(empty_note("Aucun événement de sécurité sur les dernières 24 h."))

        # ---- 5. Conformité CIS
        by_crit = {c: sum(1 for a in d["audits"] if a.criticite == c) for c in ("elevee", "moyenne", "faible")}
        last = d["last_backup"]
        backup_txt = (f"{d['backups_n']} sauvegarde(s) de configuration ; dernière : "
                      f"{_e(d['names'].get(last.equipement_id, '-'))} le {_e(_fmt(last.date_sauvegarde))} "
                      f"(SHA-256 {_e(last.hash_integrite[:12])}…)." if last else "Aucune sauvegarde de configuration enregistrée.")
        story += section("5. Conformité réseau (CIS Benchmark)",
                         f"Non-conformités ouvertes : {by_crit['elevee']} élevée(s), {by_crit['moyenne']} moyenne(s), "
                         f"{by_crit['faible']} faible(s). {backup_txt}")
        if d["audits"]:
            crit_lbl = {"elevee": ("ÉLEVÉE", C_CRIT), "moyenne": ("MOYENNE", C_WARN), "faible": ("FAIBLE", C_MUTED)}
            rows = []
            for a in d["audits"][: MAX_ROWS["audits"]]:
                lbl, col = crit_lbl.get(a.criticite, (a.criticite.upper(), C_MUTED))
                rows.append([Paragraph(f"<b>{_e(d['names'].get(a.equipement_id, a.equipement_id))}</b>", cell),
                             Paragraph(_e(a.regle_cis), cell), colored(lbl, col),
                             Paragraph(_e(_short(a.constat, 150)), cell)])
            story.append(table(["Équipement", "Règle", "Criticité", "Constat"], rows,
                               [W * 0.20, W * 0.13, W * 0.14, W * 0.53]))
            if len(d["audits"]) > MAX_ROWS["audits"]:
                story.append(Paragraph(f"… et {len(d['audits']) - MAX_ROWS['audits']} autre(s) non-conformité(s).", small))
        else:
            story.append(empty_note("Aucune non-conformité ouverte."))

        # ---- 6. Recommandations
        recs = self._recommendations(d)
        block = section("6. Recommandations") + [Paragraph(f"•&nbsp;&nbsp;{r}", ParagraphStyle(
            "rec", parent=body, leftIndent=12, firstLineIndent=-10, spaceAfter=3)) for r in recs]
        story.append(KeepTogether(block))

        # ---- gabarit de page (en-tête sombre + logo, pied de page numéroté)
        logo_ok = os.path.exists(LOGO_PATH)
        page_w, page_h = A4
        stamp = now.strftime("%d/%m/%Y %H:%M UTC")

        def decorate(canv, doc):
            canv.saveState()
            canv.setFillColor(hx(C_DARK))
            canv.rect(0, page_h - 22 * mm, page_w, 22 * mm, stroke=0, fill=1)
            canv.setFillColor(hx(C_TEAL))
            canv.rect(0, page_h - 23.2 * mm, page_w, 1.2 * mm, stroke=0, fill=1)
            if logo_ok:
                canv.drawImage(LOGO_PATH, 14 * mm, page_h - 20 * mm, height=16 * mm, width=48 * mm,
                               preserveAspectRatio=True, anchor="w", mask="auto")
            canv.setFillColor(colors.white)
            canv.setFont("Helvetica-Bold", 11)
            canv.drawRightString(page_w - 18 * mm, page_h - 11.5 * mm, "Rapport d'audit et de synthèse")
            canv.setFont("Helvetica", 8)
            canv.setFillColor(hx(C_TEAL))
            canv.drawRightString(page_w - 18 * mm, page_h - 16.5 * mm, stamp)
            canv.restoreState()

        class NumberedCanvas(rl_canvas.Canvas):
            """Ajoute « Page i / n » : le nombre total n'est connu qu'à la fin."""

            def __init__(self, *a, **k):
                super().__init__(*a, **k)
                self._saved = []

            def showPage(self):
                self._saved.append(dict(self.__dict__))
                self._startPage()

            def save(self):
                total = len(self._saved)
                for state in self._saved:
                    self.__dict__.update(state)
                    self.setStrokeColor(hx(C_LINE))
                    self.line(18 * mm, 14 * mm, page_w - 18 * mm, 14 * mm)
                    self.setFont("Helvetica", 7.5)
                    self.setFillColor(hx(C_MUTED))
                    self.drawString(18 * mm, 10 * mm, "Sentinelle AIOps - Rapport confidentiel")
                    self.drawRightString(page_w - 18 * mm, 10 * mm, f"Page {self._pageNumber} / {total}")
                    super().showPage()
                super().save()

        buffer = io.BytesIO()
        doc = SimpleDocTemplate(
            buffer, pagesize=A4, leftMargin=18 * mm, rightMargin=18 * mm, topMargin=30 * mm, bottomMargin=20 * mm,
            title="Sentinelle AIOps - Rapport d'audit", author="Sentinelle AIOps", subject="Rapport d'audit et de synthèse",
        )
        doc.build(story, onFirstPage=decorate, onLaterPages=decorate, canvasmaker=NumberedCanvas)
        return buffer.getvalue()

    def generate_pdf_report(self, db: Session, output_path: str = "rapport_audit_sentinelle.pdf") -> str:
        """Compatibilité : écrit le rapport dans un fichier et retourne son chemin."""
        with open(output_path, "wb") as f:
            f.write(self.build_pdf_report(db))
        return output_path

    def send_discord_notification(self, webhook_url: str, message: str) -> bool:
        """Send notification via Discord Webhook."""
        try:
            res = requests.post(webhook_url, json={"content": f"🚨 **Sentinelle AIOps Alert**\n{message}"}, timeout=5)
            return res.status_code in [200, 204]
        except Exception:
            return False


reporting_service = ReportingService()
