# Artefakte: Ausgabe-Vertrag

## Umfang
- Definiert das Artefakt-Modell, Layout und Lebenszyklus für `artifacts/`.
- Beschreibt nicht, wie Artefakte produziert werden; siehe Runner- und ADR-Dokumentation.

## Garantien
- Artefakte sind unveränderliche, run-bezogene Ausgaben unter `artifacts/<layer>/<run_id>/...`.
- `run_id` verknüpft Ausgaben mit einer einzigen Ausführung und wird niemals wiederverwendet.
- Artefakte sind nur Ausgaben; sie werden nicht als Eingaben für Geschäftslogik verwendet.

## Nicht-Ziele
- Speicherung roher Eingabedaten (siehe `raw/`).
- Beschreibung der Layer-Transformationslogik (siehe `src/` und ADRs).

## Artefakt-Typen und Zweck
- **Layer-Ausgaben:** Bronze-, Silver-, Gold-Run-Verzeichnisse.
- **Orchestrator-Ausgaben:** Ausführungslogs und Zusammenfassungsberichte.
- **Cross-Layer-Berichte:** konsolidierte Diagnostik und Rollups.
- **Ephemere Artefakte:** layer-lokale temporäre Ausgaben (nur unter `tmp/` erlaubt).

## Verzeichnis-Layout-Regeln
```
artifacts/
├── bronze/<run_id>/
│   ├── data/
│   └── reports/
├── silver/<run_id>/
│   ├── data/
│   ├── reports/
│   └── tmp/        # ephemer, nicht-autoritativ
├── gold/
│   ├── planning/<run_id>/
│   │   ├── data/
│   │   └── reports/
│   └── marts/<run_id>/
│       ├── _meta/
│       ├── data/
│       ├── reports/
│       └── run_log.txt
├── orchestrator/<run_id>/
│   └── logs/
└── reports/<run_id>/
    └── summary_report.*
```

## Aufbewahrungsrichtlinie
- Artefakte für Audit und Reproduzierbarkeit aufbewahren, bis explizit gelöscht.
- Löschungen müssen dokumentiert und wiederholbar sein (automatisiert oder runbook-gesteuert).

## Versionierungsstrategie
- `run_id` ist die Versionsgrenze für Ausgaben.
- Wiederholungsläufe erstellen eine neue `run_id`; Überschreiben vorheriger Läufe ist verboten.

## Beziehung zu `run_id`
- `run_id` muss einen einzigen Ausführungskontext eindeutig identifizieren.
- `run_id` verknüpft mit der Herkunft von Code, Konfiguration und Eingaben.

## Reproduzierbar vs. Ephemer
- **Reproduzierbar:** `data/`, `reports/`, `_meta/`, und `run_log.txt` für einen Lauf.
- **Ephemer:** `tmp/` Verzeichnisse (müssen jederzeit sicher löschbar sein).

## Eigentümerschaft und Verantwortlichkeiten
- Repository-Maintainer besitzen Artefakt-Richtlinie und Aufbewahrungsdurchsetzung.
- Pipeline-Operatoren besitzen Bereinigungsautomatisierung und Verifikation.

## Links
- **Upstream:** ADRs für run_id und Artefakt-Richtlinie: `docs/adr/0003-run-id-and-artifact-layout.md`, `docs/adr/0010-artifacts-versioning-policy.md`.
- **Downstream:** Layer-Verträge: `bronze/README.md`, `silver/README.md`, `gold/README.md`.