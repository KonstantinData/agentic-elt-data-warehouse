# Runbook

Dieses Runbook bietet Anweisungen zum lokalen Ausführen der agentic ELT-Pipeline, zur Validierung von Ergebnissen und zur Fehlerbehebung häufiger Probleme. Alle Befehle sind relativ zum Projektroot.

## Voraussetzungen

- **Python 3.8+** (getestet mit Python 3.12)
- **OpenAI API Key** (für LLM-Agents)
- **Git** für Versionskontrolle

Abhängigkeiten installieren:

```bash
pip install -r requirements.txt
```

## Umgebungssetup

1. **Virtuelle Umgebung erstellen:**
```bash
python -m venv venv
# Windows
venv\Scripts\activate
# Linux/Mac
source venv/bin/activate
```

2. **Umgebungsvariablen einrichten:**
```bash
# Beispiel-Umgebungsdatei kopieren
cp configs\.env.example .env
# .env bearbeiten und OpenAI API Key hinzufügen
# OPENAI_API_KEY=your_api_key_here
```

## Pipeline ausführen

Um die komplette agentic ELT-Pipeline auszuführen:

```bash
python .\src\runs\start_run.py
```

Die Pipeline wird automatisch:
1. **🥉 Bronze Layer** - Rohe CSV-Daten aufnehmen
2. **🥈 Silver Layer** - LLM-Agents bereinigen und standardisieren Daten
3. **🥇 Gold Layer** - LLM-Agents erstellen Business Data Marts
4. **📊 Business Insights** - Executive Reports und Visualisierungen generieren

## Pipeline-Ausgabestruktur

Alle Ausgaben sind nach Run-ID organisiert:

```
artifacts/
├── bronze/YYYYMMDD_HHMMSS_#hash/     # Rohdaten-Snapshots
├── silver/YYYYMMDD_HHMMSS_#hash/      # Bereinigte Daten (neuer Zeitstempel, gleicher Suffix)
├── gold/marts/YYYYMMDD_HHMMSS_#hash/  # Business Marts (Bronze run_id für Konsistenz)
├── orchestrator/YYYYMMDD_HHMMSS_#hash/# Ausführungslogs
└── reports/YYYYMMDD_HHMMSS_#hash/     # Zusammenfassungsberichte
```

## Run-ID Logik

- **Bronze**: Generiert initiale run_id (z.B. `20260125_204110_#527f1cea`)
- **Silver**: Erstellt neue run_id mit frischem Zeitstempel aber gleichem Suffix (z.B. `20260125_204143_#527f1cea`)
- **Gold**: Verwendet Bronze run_id für Mart-Konsistenz
- **Reports**: Verwenden Orchestrator run_id

## Ergebnisse validieren

Das Repository enthält eine umfassende Test-Suite:

```bash
pytest -q
```

Tests umfassen:
- Unit-Tests für Transformationen
- Vertragstests für Ausgabe-Artefakte
- Integrationstests für End-to-End-Pipeline
- Qualitätstests für generierten Code

## Fehlerbehebung

### Häufige Probleme

**Fehlender OpenAI API Key:**
```
RuntimeError: Missing OPEN_AI_KEY or OPENAI_API_KEY in .env
```
Lösung: OpenAI API Key zur `.env` Datei hinzufügen

**Fehlende Rohdaten:**
```
FileNotFoundError: Missing required raw source directories
```
Lösung: Sicherstellen, dass `raw/source_crm` und `raw/source_erp` CSV-Dateien enthalten

**Berechtigungsfehler:**
```
PermissionError: [Errno 13] Permission denied
```
Lösung: Schreibberechtigungen für `artifacts/` Verzeichnis prüfen

**Agent-Fehler:**
- `artifacts/orchestrator/*/logs/` für detaillierte Fehlerlogs prüfen
- OpenAI API Key hat ausreichend Credits verifizieren
- LLM-Agent-Kontext in `tmp/draft_reports/` überprüfen

### Pipeline-Optionen

**LLM-Agents überspringen (für Tests):**
```bash
python .\src\runs\start_run.py --skip-llm
```

**Benutzerdefinierte Run-ID:**
```bash
set ORCHESTRATOR_RUN_ID=custom_run_id
python .\src\runs\start_run.py
```

### Inkrementelle Verarbeitung

Die Pipeline erkennt automatisch unveränderte Rohdaten und überspringt die Verarbeitung, wenn keine neuen Daten verfügbar sind, wodurch Zeit und Ressourcen gespart werden.

### Hilfe erhalten

- Ausführungslogs in `artifacts/orchestrator/*/logs/` prüfen
- Agent-Kontext in `tmp/draft_reports/` überprüfen
- Debug-Logging durch Setzen von `LOG_LEVEL=DEBUG` in `.env` aktivieren
- Bestehende [Issues](https://github.com/YOUR_USERNAME/agentic-elt-data-warehouse/issues) prüfen