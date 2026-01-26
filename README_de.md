# Agentic ELT Data Warehouse

🇺🇸 **[English Version](README.md)**

Dieses Repository enthält eine produktionsreife agentic ELT/Analytics-Pipeline, die LLM-Agents verwendet, um automatisch Datentransformationscode zu generieren und auszuführen. Das System demonstriert, wie KI in traditionelle Data Engineering Workflows integriert werden kann, um sich selbst anpassende Datenpipelines zu erstellen.

## 🚀 Schnellstart

### Fork & Clone
1. Forken Sie dieses Repository zu Ihrem GitHub-Account
2. Klonen Sie Ihren Fork lokal:
```bash
git clone https://github.com/YOUR_USERNAME/agentic-elt-data-warehouse.git
cd agentic-elt-data-warehouse
```

### Voraussetzungen
- **Python 3.8+** (getestet mit Python 3.12)
- **OpenAI API Key** (für LLM-Agents)
- **Git** für Versionskontrolle

### Installation

1. **Virtuelle Umgebung erstellen:**
```bash
python -m venv venv
# Windows
venv\Scripts\activate
# Linux/Mac
source venv/bin/activate
```

2. **Abhängigkeiten installieren:**
```bash
pip install -r requirements.txt
```

3. **Umgebungsvariablen einrichten:**
```bash
# Beispiel-Umgebungsdatei kopieren
cp configs\.env.example .env
# .env bearbeiten und OpenAI API Key hinzufügen
# OPENAI_API_KEY=your_api_key_here
```

### Beispieldatensatz
Das Repository enthält einen vollständigen Beispieldatensatz im `raw/` Verzeichnis:
- **CRM-Daten** (`raw/source_crm/`): Kundeninformationen, Produktdetails, Verkaufsdaten
- **ERP-Daten** (`raw/source_erp/`): Zusätzliche Kundendaten, Standortinformationen, Produktkategorien, Transaktionen

Dieser synthetische Datensatz repräsentiert die Datenstruktur eines typischen mittelständischen Unternehmens und ist sofort einsatzbereit.

## 🏃♂️ Pipeline ausführen

Führen Sie die komplette ELT-Pipeline aus:
```bash
python .\src\runs\start_run.py
```

### Was passiert
Die Pipeline führt diese Schritte automatisch aus:

1. **🥉 Bronze Layer** - Rohdatenaufnahme
   - Kopiert CSV-Dateien aus `raw/` Verzeichnissen
   - Validiert Datenintegrität mit Checksummen
   - Erstellt unveränderliche Snapshots

2. **🥈 Silver Layer** - Datenbereinigung & Standardisierung
   - LLM-Agents analysieren Datenqualitätsprobleme
   - Generieren Python-Code für Datenbereinigung
   - Führen Transformationen automatisch aus
   - Behandeln fehlende Werte, Datentypen, Formatierung

3. **🥇 Gold Layer** - Business Marts Erstellung
   - LLM-Agents entwerfen Star-Schema
   - Generieren Dimensions- und Fact-Tabellen
   - Erstellen Business-KPI-Aggregationen
   - Bauen analytics-bereite Datensätze

4. **📊 Zusammenfassungsbericht** - Ausführungszusammenfassung
   - Pipeline-Ausführungsmetriken
   - Datenqualitätsbewertungen
   - Generierte Code-Dokumentation

## 📈 Dashboard ausführen

### Streamlit Überblick

Das multipage Dashboard basiert auf Streamlit (`src/dashboard/app.py`) und lädt die neuesten Silver-Artefakte aus `artifacts/runs/<run_id>/silver/data/`. Es listet alle verfügbaren Runs, speichert die Sidebar-Filter (Datum, Produktlinien, Länder, Geschlecht usw.) im Session-State und lädt die Datensätze neu, sobald ein anderer Run gewählt wird. Jede Seite – vom Executive Overview bis zu Diagnosen und Exporten – greift auf gemeinsame Komponenten zurück, um Filter zu persistieren und den aktuellen Kontext zum Download bereitzustellen.

### Dashboard starten

Starten Sie das Dashboard, sobald mindestens ein Silver-Run abgeschlossen ist:

#### Windows

```powershell
scripts\run_dashboard.ps1
```

#### Linux/macOS

```bash
./scripts/run_dashboard.sh
```

Alternativ können Sie Streamlit direkt starten, um CLI-Flags mitzugeben:

```bash
python -m streamlit run src/dashboard/app.py
```

Das Dashboard entdeckt Artefakte unter `artifacts/runs/<run_id>/silver/data/` (mit sicherer Rückfallebene zu `artifacts/silver/<run_id>/data/`). Fehlen Runs, fordert es Sie auf, zuerst die Pipeline zu starten. Der zuerst gewählte Run ist immer der aktuellste Abschluss, aber Sie können beliebig ältere Runs zum Vergleich auswählen.

### Streamlit-Einblicke

- **Executive Overview (pages/01)** zeigt KPI-Karten, Trenddiagramme, Produktmix-Maps, Order-Signale und das Diagnostik-Panel, das die wichtigsten Kennzahlen des gewählten Silver-Runs zusammenführt.
- **Exploration Sandbox (pages/02)** bietet eine interaktive Vorschau auf die gefilterten Daten sowie Tabellen zu Top-Produkten, Top-Ländern und Top-Kunden, damit Sie Transformationslogik direkt im Dashboard überprüfen können.
- **Run Diagnostics (pages/03)** spiegelt Metadaten, Log-Informationen und fehlende Werte wider, die die Pipeline erfasst, und stellt sie in einem aufklappbaren Panel dar.
- **Exports & Context (pages/04)** erlaubt den Download des gefilterten Datensatzes als CSV sowie eines JSON-Pakets mit aktiven Filtern, Run-ID und Artefaktquelle für Audit-Zwecke.
- Die Sidebar-Filter werden über `src/dashboard/components/filters.py` konfiguriert und bleiben so lange erhalten, bis Sie sie zurücksetzen.

### Streamlit-Konfiguration und Tipps

- `.streamlit/config.toml` definiert die Light/Dark-Themen und kann angepasst werden, wenn Sie ein eigenes Farbschema benötigen.
- CLI-Optionen lassen sich über Umgebungsvariablen wie `STREAMLIT_SERVER_PORT` oder `STREAMLIT_BROWSER_GATHER_USAGE_STATS` steuern, etwa wenn der Standard-Port blockiert ist oder Sie die Nutzungsstatistik deaktivieren wollen.
- Bevor Sie den Streamlit-Dashboard neu starten, führen Sie `python .\src\runs\start_run.py` (oder den Orchestrator) erneut aus, damit frische Silver-Artefakte vorliegen; veraltete Runs zeigen stattdessen erklärenden Hinweistext.
- Verwenden Sie die Skripte `scripts/run_dashboard.ps1`/`.sh`, um den Befehl über Betriebssysteme hinweg konsistent zu halten, oder geben Sie direkt Flags wie `--server.headless true` oder `--server.address` an `python -m streamlit run`, wenn Sie das Dashboard hosten.

## 📁 Ausgabestruktur

Alle Pipeline-Ausgaben sind nach Run-ID organisiert:

```
artifacts/
├── bronze/YYYYMMDD_HHMMSS_#hash/     # Rohdaten-Snapshots
│   ├── data/*.csv                     # Kopierte Quelldateien
│   └── reports/elt_report.html        # Aufnahmebericht
├── silver/YYYYMMDD_HHMMSS_#hash/      # Bereinigte Daten
│   ├── data/*.csv                     # Standardisierte Tabellen
│   └── reports/elt_report.html        # Qualitätsbericht
├── gold/marts/YYYYMMDD_HHMMSS_#hash/  # Business Marts
│   ├── data/*.csv                     # Star-Schema-Tabellen
│   └── reports/gold_report.html       # Marts-Dokumentation
├── orchestrator/YYYYMMDD_HHMMSS_#hash/# Ausführungslogs
│   └── logs/*.log                     # Detaillierte Schritt-Logs
└── reports/YYYYMMDD_HHMMSS_#hash/     # Zusammenfassungsberichte
    ├── summary_report.md              # Menschenlesbare Zusammenfassung
    └── summary_report.json            # Maschinenlesbare Metriken
```

## 🔧 Konfigurationsoptionen

### Inkrementelle Verarbeitung
Die Pipeline erkennt automatisch unveränderte Rohdaten und überspringt die Verarbeitung, wenn keine neuen Daten verfügbar sind. Dies spart Zeit und Ressourcen bei nachfolgenden Läufen mit identischen Eingabedateien.

### Umgebungsvariablen
Wichtige Konfiguration in `.env`:
```bash
OPENAI_API_KEY=your_key_here          # Erforderlich für LLM-Agents
ORCHESTRATOR_RUN_ID=custom_run_id     # Optional: benutzerdefinierte Run-ID
```

## 🧪 Testen

Führen Sie die komplette Test-Suite aus:
```bash
pytest -q
```

Test-Kategorien:
- **Unit-Tests** - Einzelkomponenten-Tests
- **Integrationstests** - End-to-End-Pipeline-Validierung
- **Vertragstests** - Datenschema-Validierung
- **Qualitätstests** - Code-Qualität und Dokumentation

## 🏗️ Architektur

### Agentic-Komponenten
- **Draft Agents** - Analysieren Daten und generieren Transformationscode
- **Builder Agents** - Verfeinern und optimieren generierten Code
- **Quality Agents** - Validieren Code-Qualität und Performance

### Datenfluss
```
Rohdaten → Bronze (Aufnahme) → Silver (Bereinigung) → Gold (Business-Logik) → Berichte
     ↓           ↓                    ↓                    ↓
   LLM-Analyse → Code-Generierung → Ausführung → Validierung
```

### Hauptmerkmale
- **Deterministische Ausführung** - Gleiche Eingaben produzieren identische Ausgaben
- **Audit-Trail** - Vollständige Lineage-Verfolgung
- **Fehlerbehandlung** - Elegante Fehlerwiederherstellung
- **Inkrementelle Verarbeitung** - Überspringen unveränderter Daten
- **DSGVO-Konformität** - PII-Behandlung und Pseudonymisierung

## 📊 Beispieldaten-Übersicht

Der enthaltene Datensatz simuliert:
- **~1000 Kunden** über mehrere Segmente
- **~50 Produkte** in verschiedenen Kategorien
- **~5000 Verkaufstransaktionen** über Zeiträume
- **Mehrere Datenqualitätsprobleme** zum Testen der Bereinigungslogik

Daten enthalten absichtliche Qualitätsprobleme:
- Fehlende Werte
- Inkonsistente Formatierung
- Doppelte Datensätze
- Datentyp-Unstimmigkeiten

## 🔍 Monitoring & Observability

Jeder Lauf generiert umfassende Monitoring-Daten:
- **Ausführungsmetriken** - Laufzeit, Speicherverbrauch, Erfolgsraten
- **Datenqualitäts-Scores** - Vollständigkeit, Gültigkeit, Konsistenz
- **Code-Generierungslogs** - LLM-Interaktionen und Entscheidungen
- **Fehler-Tracking** - Detaillierte Fehleranalyse

## 🤝 Mitwirken

1. Repository forken
2. Feature-Branch erstellen: `git checkout -b feature/amazing-feature`
3. Änderungen committen: `git commit -m 'Add amazing feature'`
4. Zu Branch pushen: `git push origin feature/amazing-feature`
5. Pull Request öffnen

## 📝 Lizenz

Dieses Projekt ist unter der MIT-Lizenz lizenziert - siehe die [LICENSE](LICENSE) Datei für Details.

## 🆘 Fehlerbehebung

### Häufige Probleme

**Fehlender OpenAI API Key:**
```
RuntimeError: Missing OPEN_AI_KEY or OPENAI_API_KEY in .env
```
Lösung: OpenAI API Key zur `.env` Datei hinzufügen

**Import-Fehler:**
```
ModuleNotFoundError: No module named 'xyz'
```
Lösung: Sicherstellen, dass virtuelle Umgebung aktiviert und Abhängigkeiten installiert sind

**Berechtigungsfehler:**
```
PermissionError: [Errno 13] Permission denied
```
Lösung: Dateiberechtigungen prüfen und Schreibzugriff auf `artifacts/` Verzeichnis sicherstellen

### Hilfe erhalten
- Bestehende [Issues](https://github.com/YOUR_USERNAME/agentic-elt-data-warehouse/issues) prüfen
- Ausführungslogs in `artifacts/orchestrator/*/logs/` überprüfen
- Debug-Logging durch Setzen von `LOG_LEVEL=DEBUG` in `.env` aktivieren

---

**Bereit, KI-gestützte Datentechnik in Aktion zu sehen? Führen Sie `python .\src\runs\start_run.py` aus und erleben Sie die Magie! ✨**
