# 0003 – Run ID & Artefakt-Layout

*Status:* Akzeptiert

## Kontext

Die agentic ELT-Pipeline generiert Logs, Ausgaben und Metadaten über mehrere Schichten (Bronze, Silver, Gold). Ohne eine konsistente Struktur werden Fehlerbehebung und Audits teuer und unzuverlässig. Jede Schicht hat spezifische run_id Generierungslogik, die dokumentiert werden muss.

## Entscheidung

Jede Pipeline-Ausführung erhält eine eindeutige **Run ID** nach dem Muster `YYYYMMDD_HHMMSS_#<hex>`. Artefakte werden in einer konsistenten Verzeichnisstruktur gespeichert, die nach Run ID und Schicht organisiert ist.

### Run ID Generierungslogik

- **Bronze Layer**: Generiert initiale run_id mit Zeitstempel und zufälligem Hex-Suffix
  - Format: `20260125_204110_#527f1cea`
  - Ort: `artifacts/bronze/<run_id>/`

- **Silver Layer**: Erstellt neue run_id mit frischem Zeitstempel aber **gleichem Suffix** wie Bronze
  - Format: `20260125_204143_#527f1cea` (neuer Zeitstempel, gleicher `#527f1cea`)
  - Ort: `artifacts/silver/<silver_run_id>/`
  - Zweck: Erhält Lineage bei gleichzeitiger Ermöglichung mehrerer Silver-Läufe pro Bronze

- **Gold Layer**: Verwendet **Bronze run_id** für Konsistenz über Business Marts hinweg
  - Format: `20260125_204110_#527f1cea` (gleich wie Bronze)
  - Ort: `artifacts/gold/marts/<bronze_run_id>/`
  - Zweck: Stellt sicher, dass Business Marts konsistent gruppiert sind

- **Orchestrator**: Generiert eigene run_id für Ausführungsverfolgung
  - Ort: `artifacts/orchestrator/<orchestrator_run_id>/`
  - Enthält Logs für alle Pipeline-Schritte

### Verzeichnisstruktur

```
artifacts/
├── bronze/<run_id>/
│   ├── data/*.csv
│   └── reports/elt_report.html
├── silver/<silver_run_id>/
│   ├── data/*.csv
│   └── reports/elt_report.html
├── gold/marts/<bronze_run_id>/
│   ├── data/*.csv
│   └── reports/gold_report.html
├── orchestrator/<orchestrator_run_id>/
│   └── logs/*.log
└── reports/<orchestrator_run_id>/
    ├── summary_report.md
    └── team_reports/*.md
```

## Begründung

* **Auditierbarkeit:** Ergebnisse können zu spezifischen Läufen über alle Schichten verfolgt werden
* **Lineage-Verfolgung:** Suffix-Konsistenz ermöglicht Bronze→Silver→Gold Nachverfolgbarkeit
* **Operative Effizienz:** Logs und Ausgaben sind schnell auffindbar
* **Compliance-Bereitschaft:** Unterstützt Aufbewahrungs- und Audit-Anforderungen
* **Multi-Run-Unterstützung:** Ermöglicht mehrere Silver-Läufe pro Bronze ohne Konflikte

## Konsequenzen

* Alle Jobs müssen Namens- und Speicherkonventionen befolgen
* Verbessert langfristige Observability und SLA-Berichterstattung
* Ermöglicht inkrementelle Verarbeitung und Datenlineage-Verfolgung
* Unterstützt agentic Pipeline-Debugging und Fehlerbehebung