# Build 2 — Scope

## CV-to-Standardized-Profile (n8n + LLM)

**Status:** Scope finalisiert
**Ship-Ziel:** ~10.–12. Mai 2026

---

## 1. Customer-Problem

Recruiting-Teams im Mittelstand verbringen 10–30 Minuten pro CV mit der manuellen Übertragung in standardisierte Unternehmensprofile. Bei einem Volumen von ~1.000 CVs/Monat sind das 250–500 Stunden manuelle Arbeit pro Monat — Arbeit, die in 1–2 Minuten pro CV automatisiert werden kann, ohne Datenqualität zu opfern.

**Zielgruppe:** Mittelständische Konzerne mit zentralisiertem Recruiting (>500 Mitarbeitende), strukturiertem Bewerber-Workflow und einem ATS als System of Record.

---

## 2. Warum dieser Build relevant ist

Drei Eigenschaften machen diesen Build für Enterprise-Kontexte relevant:

1. **API-zugängliches Zielsystem.** Output schreibt in ein ATS (in v1: Google Sheet als Stand-in für Personio, SAP SuccessFactors, Workday). Ohne API-zugängliches HR-System gibt es keine echte Wertschöpfung — daher zentral.

2. **Data Governance im Build.** Schema-Enforcement, kontrolliertes Vokabular für Skills, und Logik-Validation sorgen dafür, dass nur saubere, konsistente Daten ins Zielsystem geschrieben werden. Validation passiert at write-time, nicht at read-time — keine technische Schuld für nachgelagerte Systeme.

3. **Vorbedingung für HR-Analytics.** Standardisierte Profile sind die Voraussetzung für jede Auswertung über Snowflake oder vergleichbare Data-Plattformen. Free-Text-CVs sind nicht analysierbar; Profile mit kontrolliertem Vokabular schon.

---

## 3. Was v1 macht (Happy Path)

```
Input  →  Parsing   →  Extraction  →  Validation  →  Output
  ↓         ↓             ↓               ↓             ↓
 PDF      Text          1 LLM-Call    Schema +       Sheet
 DOCX    extraktion     → JSON        Taxonomie +   (Stand-in
 TXT     (kein LLM!)                  Logik         für ATS)
```

**Komponenten:**

- **Input:** Eine CV-Datei (PDF, DOCX, oder Text). Deutsch oder Englisch.
- **Parsing:** Text-Extraktion mit `pdf-parse` (PDF) und `mammoth` (DOCX). Kein LLM. Deterministisch und kostengünstig.
- **Extraction:** Ein LLM-Call mit Schema (Structured Outputs). Felder:
  - `name`
  - `current_role`
  - `total_years_experience`
  - `employment_history` (array: employer, role, start, end, responsibilities)
  - `education` (array)
  - `skills` (array, gemappt auf Taxonomie)
  - `languages` (array mit proficiency)
  - `certifications`
- **Validation:** Code-basiert.
  - Schema-Check (alle Pflichtfelder vorhanden, Typen korrekt)
  - Taxonomie-Mapping für Skills (mappen oder als `unmapped` markieren)
  - Logik-Checks (Datum-Plausibilität, Employment-History ohne unmögliche Überlappungen, Total-Years vs. Summe der Stationen)
- **Output:** JSON in Google Sheet, Stand-in für ATS-API.

**Latenz-Ziel:** <2 Min pro CV (End-to-End).

---

## 4. Out-of-Scope für v1

Scope-Disziplin ist Teil des Builds. Folgende Aspekte sind bewusst ausgelassen und in der v2-Roadmap dokumentiert:

- **Multi-Page-PDF-Layout-Parsing.** Tabellen, Spalten, eingebettete Bilder werden ignoriert. Exotische Layouts → Parsing-Failure → Eintrag im Failure-Log.
- **Skills-Inferenz aus Job-Descriptions.** *"Senior Backend Engineer"* triggert nicht *"Python, Java, AWS"*. Nur explizit genannte Skills werden extrahiert.
- **Photo-/Bewerbungs-Bild-Extraktion.** CV-Foto wird ignoriert.
- **OCR auf gescannten PDFs.** Gescannter CV → Parsing-Failure.
- **Multi-Sprach-Mischung in einem CV.** Eine Sprache pro CV in v1.
- **Kein UI.** Input via n8n-Trigger-Folder oder Webhook. Output via Sheet-Zeile.
- **Keine Anonymisierung / GDPR-Pseudonymisierung.** Synthetische CVs in der Eval-Phase. Reale Daten erst in v2 mit entsprechendem DSGVO-Setup.

---

## 5. Definition of Done für v1

Ein Build 2 v1 ist fertig, wenn alle 7 Häkchen gesetzt sind:

1. ☐ Eine CV-Datei (PDF, DOCX, Text, DE oder EN) wird in <2 Min in eine validierte Sheet-Zeile transformiert.
2. ☐ Schema ist hart spezifiziert (JSON-Schema committed im Repo).
3. ☐ Skills-Taxonomie existiert (~150–200 Einträge in YAML, committed).
4. ☐ Eval-Set existiert: 20 hand-gelabelte CVs, ground-truth Profile als JSON, committed.
5. ☐ Eval-Script läuft und produziert eine Zahl (Field-Level F1 oder Exact-Match-Rate pro Feld-Kategorie).
6. ☐ **Baseline-Zahl gemessen:** zero-shot LLM ohne Schema-Enforcement, ohne Taxonomie. Im README.
7. ☐ **Pipeline-Zahl gemessen:** voller Pipeline. Im README. Schlägt Baseline.

---

## 6. Qualitäts-Marker

Drei Standards, die der Build erfüllen muss, bevor er als "fertig" gilt:

### Numerische Evaluation
- Held-out Test-Set (20 CVs)
- Baseline-Zahl (zero-shot LLM ohne Pipeline)
- Pipeline-Zahl (voller Stack)
- Failure-Taxonomie im FAILURE_LOG

### Generalisierende FAILURE_LOG-Einträge
Mindestens ein Eintrag pro Build, der nicht den konkreten Bug beschreibt, sondern die Klasse von Fehlern, die er verallgemeinert.

### ROI-Transparenz im README
Konkrete Mathematik mit nachvollziehbaren Annahmen — nicht *"spart Zeit"*, sondern Volumen × Zeit pro CV × Stundensatz = monatlicher Wert. Annahmen explizit und verteidigbar.

---

## 7. Per-Build-Disziplin

1. ✅ **SCOPE** — dieses Dokument
2. ☐ **BUILD v1** — Hygiene only: Input-Validation, Schema-Enforcement, basic Retries. Happy Path zuerst.
3. ☐ **INSTRUMENT** — Logge jeden LLM-Call: Input, Output, Latency, Token-Count, Cost.
4. ☐ **BREAK** — Red-Team-Session mit adversarialen Inputs:
   - Ambigue CVs (fehlende Daten, freelance-Wirrwarr)
   - Lange CVs (Context-Limit)
   - Leere/malformed Files, Unicode, gemischte Sprachen
   - Prompt-Injection im CV-Text
   - API-Failures (Timeouts, Rate Limits)
   - Confidently-wrong Outputs (erfundene Skills)
5. ☐ **EVAL** — Score-Output gegen Ground Truth.
6. ☐ **v2 + MITIGATIONS** — Per Break: Fix, Mitigate, oder Accept-and-Document.
7. ☐ **COST & LATENCY** — Cost per 1.000 Runs, p50/p95 Latency.
8. ☐ **SECURITY/GOVERNANCE NOTE** — was fließt wo, was wird gespeichert, DSGVO-Einwände, Mitigations.
9. ☐ **SHIP** — README, FAILURE_LOG, CHANGELOG, Eval-Ergebnisse, Loom-Demo.

---

## 8. Konkrete nächste Aktion

**Skills-Taxonomie erstellen.** YAML-Datei, ~150–200 Einträge, gegliedert in Kategorien:

- `programming_languages`
- `cloud_platforms`
- `frameworks`
- `databases`
- `soft_skills`
- `languages`
- `certifications`
- `domain_expertise`

Committen als `taxonomy/skills.yaml`. ~30–60 Min Arbeit.

**Reihenfolge danach:**

1. Schema definieren (referenziert die Taxonomie)
2. Eval-Set erstellen (20 hand-gelabelte CVs als ground-truth)
3. Pipeline bauen (n8n-Workflow)
4. Baseline messen (zero-shot)
5. Pipeline messen (voller Stack)
6. Iterate