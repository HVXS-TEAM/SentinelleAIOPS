"""
Vérification live de l'étape 4 : rapport PDF réel. Le back-end doit tourner sur http://localhost:8000.
Usage :  python verif_etape4.py      (dure environ 15 s)
Le rapport obtenu après injection des 3 scénarios de démo est conservé dans "rapport_verif_etape4.pdf"
(dossier courant) : ouvre-le pour le contrôler visuellement.
"""
import io
import os
import sys

import requests

API = "http://localhost:8000/api/v1"
PWD = {"tech": os.environ.get("SENTINELLE_PASSWORD", "TechPass2026!"), "visiteur": "VisitorPass2026!"}
OUT_FILE = "rapport_verif_etape4.pdf"
ok_all = True


def check(label, cond, detail=""):
    global ok_all
    ok_all &= bool(cond)
    print(f"  [{'OK' if cond else 'ECHEC'}] {label} {detail}")


def bearer(user):
    r = requests.post(f"{API}/auth/login", data={"username": user, "password": PWD[user]}, timeout=10)
    return {"Authorization": f"Bearer {r.json()['access_token']}"}


def get_pdf(headers=None):
    return requests.get(f"{API}/admin/generate-pdf-report", headers=headers, timeout=30)


def text_of(data: bytes):
    try:
        from pypdf import PdfReader
    except ImportError:
        return None
    return "\n".join(p.extract_text() for p in PdfReader(io.BytesIO(data)).pages)


print("1) Contrôle d'accès")
check("sans jeton -> 401", get_pdf().status_code == 401)
check("visiteur -> 403", get_pdf(bearer("visiteur")).status_code == 403)

print("2) Rapport après injection des 3 scénarios de démo")
h = bearer("tech")
requests.post(f"{API}/simulation/reset", headers=h, timeout=15)
for sc in ("inject-bruteforce", "stress-disk", "cis-flaw"):
    requests.post(f"{API}/simulation/{sc}", headers=h, timeout=15)
r = get_pdf(h)
check("réponse 200", r.status_code == 200, f"({r.status_code})")
check("type application/pdf", r.headers.get("content-type") == "application/pdf")
check("téléchargement nommé rapport_sentinelle_*.pdf", 'filename="rapport_sentinelle_' in r.headers.get("content-disposition", ""))
check("vrai PDF (en-tête %PDF, fin %%EOF, > 5 Ko)", r.content.startswith(b"%PDF-") and r.content.rstrip().endswith(b"%%EOF") and len(r.content) > 5000, f"({len(r.content)} octets)")
with open(OUT_FILE, "wb") as f:
    f.write(r.content)
txt = text_of(r.content)
if txt is None:
    print("  [--] contenu non vérifié (pypdf absent : pip install pypdf)")
else:
    for expected in ("Rapport d'audit et de synthèse", "NIVEAU GLOBAL", "par tech", "SSH_BRUTEFORCE", "198.51.100.45", "SRV-APP-01", "CIS-1.1"):
        check(f"le rapport contient « {expected} »", expected in txt)

print("3) Après reset : le rapport reflète l'état réel")
requests.post(f"{API}/simulation/reset", headers=h, timeout=15)
r2 = get_pdf(h)
check("réponse 200 et PDF valide", r2.status_code == 200 and r2.content.startswith(b"%PDF-"))
txt2 = text_of(r2.content)
if txt2 is not None:
    check("l'attaque simulée a disparu du rapport", "198.51.100.45" not in txt2)

print(f"\nRapport de démonstration conservé : {os.path.abspath(OUT_FILE)}")
print("RESULTAT :", "TOUT EST OK" if ok_all else "DES VERIFICATIONS ONT ECHOUE")
sys.exit(0 if ok_all else 1)
