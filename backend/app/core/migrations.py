"""
Sentinelle AIOps - Mini-migrations de schéma (SQLite / PostgreSQL).

`Base.metadata.create_all()` crée les tables manquantes mais n'ajoute JAMAIS
une colonne à une table déjà existante. Ce module ajoute donc, de façon
idempotente, les colonnes introduites après la première création de la base.
"""

from sqlalchemy import inspect, text


def ensure_schema(engine) -> None:
    insp = inspect(engine)
    tables = insp.get_table_names()

    # Etape 1 : lien évènement de sécurité -> équipement ciblé
    if "evenements_securite" in tables:
        cols = {c["name"] for c in insp.get_columns("evenements_securite")}
        if "equipement_id" not in cols:
            with engine.begin() as conn:
                conn.execute(text(
                    "ALTER TABLE evenements_securite "
                    "ADD COLUMN equipement_id INTEGER REFERENCES equipements(id)"
                ))
        with engine.begin() as conn:
            conn.execute(text(
                "CREATE INDEX IF NOT EXISTS ix_evenements_securite_equipement_id "
                "ON evenements_securite (equipement_id)"
            ))
