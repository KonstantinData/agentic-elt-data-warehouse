# Datenschutzrichtlinie

Dieses Dokument beschreibt, wie personenbezogene Daten in der gesamten ELT/Analytics-Pipeline in Übereinstimmung mit der DSGVO behandelt werden.

## Rohe Eingaben

Die Pipeline nimmt rohe CSV-Dateien aus den CRM- und ERP-Systemen auf. Diese Dateien können personenbezogene Daten (PII) enthalten wie:

- `cst_firstname`, `cst_lastname` – Kundennamen
- `cst_key`, `CID` – Geschäftsidentifikatoren, die Personen eindeutig identifizieren
- `GEN`, `cst_gndr` – Geschlechtscodes
- `BDATE` – Geburtsdaten

Die rohen CSV-Dateien werden Byte-für-Byte in `artifacts/runs/<run_id>/bronze/data/` für Auditierbarkeit kopiert. Der Zugang zur Bronze-Schicht sollte nur auf autorisiertes Personal beschränkt sein.

## Pseudonymisierung und Entfernung

Während der Silver- und Gold-Phasen werden die Daten bereinigt und normalisiert, enthalten aber noch direkte Identifikatoren. Spätere Phasen (Feature Engineering, Segmentierung und Berichterstattung) dürfen keine PII preisgeben. Um dies zu erreichen:

1. **Entfernung** – direkte Namensspalten (`cst_firstname`, `cst_lastname`) werden vollständig entfernt bei der Berechnung von Kundenmerkmalen und Segmentierung.
2. **Pseudonymisierung** – Geschäftsschlüssel (`cst_key`, `CID`) werden in stabile Hashes mit einem geheimen Salt transformiert, das in einer lokalen `.env` Datei gespeichert ist. Derselbe Salt wird konsistent über Läufe angewendet, um Verknüpfbarkeit zu erhalten, ohne die ursprünglichen Identifikatoren preiszugeben.
3. **Sensible Attribute** – Geschlecht und Familienstand werden als Quasi-Identifikatoren behandelt. Sie werden in aggregierter Form für Segmentierung beibehalten (z.B. Anzahl pro Segment), aber niemals zusammen mit einem individuellen Identifikator preisgegeben.

## `data_policy.json`

Jeder Lauf produziert `artifacts/runs/<run_id>/_meta/data_policy.json`, das zusammenfasst, wie persönliche Felder behandelt wurden. Das JSON enthält:

- `personal_fields` – Liste der Spaltennamen, die als persönlich oder sensibel erkannt wurden.
- `pseudonymised` – Felder, die mit einem Salt gehasht wurden.
- `removed` – Felder, die vollständig aus nachgelagerten Ausgaben entfernt wurden.
- `salt_hash` – SHA‑256 Hash des geheimen Salts, der für Pseudonymisierung verwendet wurde (der Salt-Wert selbst wird nicht gespeichert).

Operatoren sollten die `data_policy.json` überprüfen, um Compliance und Audit-Bereitschaft sicherzustellen.