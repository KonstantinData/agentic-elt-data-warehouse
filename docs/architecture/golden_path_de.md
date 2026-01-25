# Golden Path Architektur

Der **Golden Path** ist ein deterministischer, reproduzierbarer Workflow, der rohe CRM- und ERP-Daten in umsetzbare Insights transformiert. Er besteht aus drei Hauptschichten, die sequenziell von `src/runs/orchestrator.py` ausgeführt werden.

## Architektur-Übersicht

Die Pipeline folgt einer **Medallion-Architektur** mit drei Schichten:
- **🥉 Bronze Layer**: Rohdatenaufnahme
- **🥈 Silver Layer**: Datenbereinigung und Standardisierung  
- **🥇 Gold Layer**: Business Marts und Analytics

## Schichten

### 1. Bronze Layer (`src/runs/load_1_bronze_layer.py`)

Rohe CSV-Dateien aus `raw/source_crm` und `raw/source_erp` werden unverändert in das Run-Verzeichnis unter `artifacts/bronze/<run_id>/data/` kopiert. Der Bronze-Loader erfasst dateiweise Metadaten (Größe, Änderungszeit, SHA‑256-Checksumme) und erstellt einen HTML-Bericht, der den Ladestatus zusammenfasst. In dieser Phase finden keine Transformationen statt.

**Run-ID Format**: `YYYYMMDD_HHMMSS_#<hex>`

### 2. Silver Layer (Agentic Datenbereinigung)

Der Silver Layer verwendet **LLM-Agents**, um Daten automatisch zu bereinigen und zu standardisieren:

#### **Silver Draft Agent** (`src/agents/load_2_silver_layer_draft_agent.py`)
- Analysiert Bronze-Datenqualität
- Identifiziert Transformationsbedarfe
- Erstellt Analyseberichte

#### **Silver Builder Agent** (`src/agents/load_2_silver_layer_builder_agent.py`)
- Generiert ausführbaren Python-Code
- Implementiert Datenbereinigungslogik
- Erstellt `src/runs/load_2_silver_layer.py`

#### **Silver Runner** (`src/runs/load_2_silver_layer.py`)
- Führt generierte Transformationen aus:
  - Entfernt Whitespace und konvertiert leere Strings zu `NA`
  - Normalisiert Daten zu ISO-Format (`YYYY-MM-DD`)
  - Parst numerische Spalten und konvertiert Identifikatoren zu nullable integers
  - Harmonisiert Domain-Codes (z.B. Geschlechtswerte zu `M`/`F`/`NA`)

**Run-ID Logik**: Erstellt neue run_id mit frischem Zeitstempel aber gleichem Suffix wie Bronze
- Bronze: `20260125_204110_#527f1cea`
- Silver: `20260125_204143_#527f1cea`

### 3. Gold Layer (Agentic Business Marts)

Der Gold Layer verwendet **LLM-Agents**, um Star‑Schema Data Warehouses zu bauen:

#### **Gold Draft Agent** (`src/agents/load_3_gold_layer_draft_agent.py`)
- Analysiert Silver-Daten für Business-Muster
- Entwirft Star-Schema-Architektur
- Plant Dimensions- und Fact-Tabellen

#### **Gold Builder Agent** (`src/agents/load_3_gold_layer_builder_agent.py`)
- Generiert Data Mart Erstellungscode
- Implementiert Star-Schema-Logik
- Erstellt `src/runs/load_3_gold_layer.py`

#### **Gold Runner** (`src/runs/load_3_gold_layer.py`)
- Erstellt business-bereite Data Marts:
  - **Dimensionstabellen** – Kunden, Produkte und Standorte
  - **Fact-Tabelle** – Verkaufstransaktionen
  - **Aggregierte Marts** – Executive KPIs, Performance-Metriken
  - **Wide Tables** – angereicherte analytische Ansichten

**Run-ID Logik**: Verwendet Bronze run_id für Konsistenz über Business Marts hinweg

### 4. Business Insights Agent (`src/agents/business_insights_agent.py`)

Generiert Executive Reports und Business Intelligence:
- Analysiert Gold Data Marts für KPIs
- Erstellt stakeholder-spezifische Berichte
- Generiert Visualisierungen und Dashboards
- Produziert C-Level Executive Zusammenfassungen

## Orchestrierung

Die komplette Pipeline wird von `src/runs/orchestrator.py` orchestriert:
- Validiert Umgebung und Voraussetzungen
- Führt Schichten sequenziell aus
- Behandelt Fehler und Skip-Logik
- Generiert umfassende Ausführungsberichte
- Verwaltet run_id Konsistenz über Schichten hinweg