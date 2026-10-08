"""Sentinelle AIOps — utilitaire d'horodatage UTC.

`utcnow_naive()` est le substitut direct de `datetime.utcnow()` (déprécié
depuis Python 3.12, émet un DeprecationWarning en 3.14).

Reste volontairement NAÏF (sans tzinfo) : les colonnes `DateTime` SQLite sont
sans fuseau et tout le code compare des datetimes naïfs — passer en aware
casserait les soustractions `now - horodatage` (TypeError).
Équivaut à `datetime.now(timezone.utc)` sans le tzinfo.
"""
from datetime import datetime, timezone


def utcnow_naive() -> datetime:
    return datetime.now(timezone.utc).replace(tzinfo=None)
