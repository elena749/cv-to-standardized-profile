# Build 2 — Scope

## CV-to-Standardized-Profile (n8n + LLM)

**Status:** Scope finalisiert
**Ship-Ziel:** ~10.–12. Mai 2026

---

## 1. Customer-Problem

Recruiting-Teams im Mittelstand und Konzern verbringen 10–30 Minuten pro CV mit der manuellen Übertragung in standardisierte Unternehmensprofile. Bei einem Volumen von mehreren tausend CVs/Monat sind das hunderte Stunden manuelle Arbeit pro Monat — Arbeit, die in 1–2 Minuten pro CV automatisiert werden kann, ohne Datenqualität zu opfern.

---

## 2. Customer-Persona

### Unternehmen
- **Branche:** Management-/Strategieberatung
- **Größe:** ~3.000 Mitarbeitende
- **Region:** DACH-Hauptsitz, internationale Präsenz
- **Recruiting-Modell:** Inhouse-Team. Lead-Hires (8+ Jahre Erfahrung) laufen über Executive Search.

### Recruiting-Team
- **Größe:** ~25–40 Recruiter
- **Aufteilung:** Campus Recruiting (Entry-Level) + Experienced Hire Recruiting (Mid- bis Senior-Level)
- **Tech-Affinität:** mittel — ATS-vertraut, kein Programmier-Know-how

### Bewerber-Profil
- **Career-Level:** Entry (Hochschulabsolvent), Mid (2-4 Jahre), Senior (5-8 Jahre)
- **Out-of-Scope-Rollen:** Lead-Level (8+ Jahre, Executive Search), Support-Funktionen
- **Sprache der CVs:** ~70% Deutsch, ~30% Englisch
- **Typisches CV-Profil:** akademisch (oft Promotion oder MBA), Industrie-Erfahrung in mehreren Sektoren, Methoden-Toolkit (Strategie, Operations, Digital, M&A, Performance Improvement)

### Volumen — Begründung
- ~3.000 MA × ~12% Fluktuation/Wachstum = ~400 Hires/Jahr
- × ~100 CVs/Hire (Branchen-Benchmark für Top-Strategieberatungen) = ~40.000 CVs/Jahr
- **CVs pro Monat:** ~3.500 im Schnitt, ~6.000–8.000 in Saison-Spitzen (Campus-Recruiting Herbst/Frühjahr)
- **Manuelle Bearbeitungszeit:** 10–15 Min (erfahrene Recruiter), bis zu 30 Min (Junior). Mittelwert ~15–20 Min.
- **Aktueller Engpass:** Inkonsistenz im Profil-Format zwischen Recruitern + Verzögerung in Saison-Spitzen

### ATS / System of Record
- **System:** ATS mit API-Zugang (typische Beispiele: SAP SuccessFactors, Workday, Greenhouse, oder Eigenbau-Lösung)
- **In v1:** Google Sheet als Stand-in. Spalten entsprechen einem typischen ATS-Profil-Schema. Migration zur ATS-API ist mechanisch — der letzte Pipeline-Schritt ist austauschbar.

### Use-Case in einem Satz
*"Sourcing-Recruiter in Strategieberatungen verarbeiten 3.500–8.000 CVs/Monat für Consultant-Rollen (Entry bis Senior) und brauchen standardisierte Profile in ihrem ATS, damit Hiring Manager über Standorte und Practice-Bereiche hinweg vergleichbar reviewen können."*

---

## 3. Warum dieser Build relevant ist

Drei Eigenschaften machen diesen Build für Enterprise-Kontexte relevant:

1. **API-zugängliches Zielsystem.** Output schreibt in ein ATS. Ohne API-zugängliches HR-System gibt es keine echte Wertschöpfung — daher zentral.

2. **Data Governance im Build.** Schema-Enforcement, kontrolliertes Vokabular für Skills, und Logik-Validation sorgen dafür, dass nur saubere, konsistente Daten ins Zielsystem geschrieben werden. Validation passiert at write-time, nicht at read-time — keine technische Schuld für nachgelagerte Systeme.

3. **Vorbedingung für HR-Analytics.** Standardisierte Profile sind die Voraussetzung für jede Auswertung über Snowflake oder vergleichbare Data-Plattformen. Free-Text-CVs sind nicht analysierbar; Profile mit kontrolliertem Vokabular schon.

---

## 4. ROI-Mathematik

```
3.500 CVs/Monat × 18 Min/CV     = 63.000 Min/Monat
63.000 Min ÷ 60                  = 1.050 Std/Monat
1.050 Std × 70 €/h (loaded cost) ≈ 73.500 €/Monat
× 12                             ≈ 880.000 €/Jahr
```

**Annahmen (verteidigbar):**
- 18 Min/CV: Mittelwert zwischen 10–15 (erfahren) und 30 (Junior)
- 70 €/h: Loaded Cost (Brutto-Gehalt + Lohnnebenkosten + Overhead) für Mid-Level-Recruiter in Deutschland
- 3.500 CVs/Monat: Branchen-Benchmark für Strategieberatung mit ~3.000 MA

**Saison-Spitzen-Effekt:** Bei 6.000–8.000 CVs/Monat in Campus-Saison verdoppeln sich die Einsparungen — und der Engpass wird kritisch (Bearbeitungszeit verzögert sich, Kandidaten warten zu lange, Top-Profile gehen an Konkurrenz).

---

## 5. Was v1 macht (Happy Path)

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
  - `career_level` (Entry / Mid / Senior)
  - `employment_history` (array: employer, role, start, end, responsibilities)
  - `education` (array)
  - `industries` (array, gemappt auf Taxonomie)
  - `functional_expertise` (array, gemappt auf Taxonomie)
  - `methods_and_tools` (array, gemappt auf Taxonomie)
  - `languages` (array mit proficiency)
- **Validation:** Code-basiert.
  - Schema-Check (alle Pflichtfelder vorhanden, Typen korrekt)
  - Taxonomie-Mapping (mappen oder als `unmapped` markieren)
  - Logik-Checks (Datum-Plausibilität, Employment-History ohne unmögliche Überlappungen, Total-Years vs. Summe der Stationen)
- **Output:** JSON in Google Sheet, Stand-in für ATS-API.

**Latenz-Ziel:** <2 Min pro CV (End-to-End).

---

## 6. Out-of-Scope für v1

Scope-Disziplin ist Teil des Builds. Folgende Aspekte sind bewusst ausgelassen und in der v2-Roadmap dokumentiert:

- **Multi-Page-PDF-Layout-Parsing.** Tabellen, Spalten, eingebettete Bilder werden ignoriert. Exotische Layouts → Parsing-Failure → Eintrag im Failure-Log.
- **Skills-/Expertise-Inferenz aus Job-Descriptions.** *"Senior Strategy Consultant in Pharma"* triggert nicht automatisch *"Pharma-Industrie + Strategie-Methode"* — nur explizit genannte Industries und Methods werden extrahiert.
- **Photo-/Bewerbungs-Bild-Extraktion.** CV-Foto wird ignoriert.
- **OCR auf gescannten PDFs.** Gescannter CV → Parsing-Failure.
- **Multi-Sprach-Mischung in einem CV.** Eine Sprache pro CV in v1.
- **Lead-Level-Profile (8+ Jahre).** Werden über Executive Search abgewickelt, nicht über diesen Workflow.
- **Kein UI.** Input via n8n-Trigger-Folder oder Webhook. Output via Sheet-Zeile.
- **Keine Anonymisierung / DSGVO-Pseudonymisierung.** Synthetische CVs in der Eval-Phase. Reale Daten erst in v2 mit entsprechendem Setup.

---

## 7. Definition of Done für v1

Ein Build 2 v1 ist fertig, wenn alle 7 Häkchen gesetzt sind:

1. ☐ Eine CV-Datei (PDF, DOCX, Text, DE oder EN) wird in <2 Min in eine validierte Sheet-Zeile transformiert.
2. ☐ Schema ist hart spezifiziert (JSON-Schema committed im Repo).
3. ☐ Taxonomie existiert (Industries, Functional Expertise, Methods/Tools, Languages — committed in YAML).
4. ☐ Eval-Set existiert: 20 hand-gelabelte CVs, ground-truth Profile als JSON, committed.
5. ☐ Eval-Script läuft und produziert eine Zahl (Field-Level F1 oder Exact-Match-Rate pro Feld-Kategorie).
6. ☐ **Baseline-Zahl gemessen:** zero-shot LLM ohne Schema-Enforcement, ohne Taxonomie. Im README.
7. ☐ **Pipeline-Zahl gemessen:** voller Pipeline. Im README. Schlägt Baseline.

---

## 8. Qualitäts-Marker

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

## 9. Per-Build-Disziplin

1. ✅ **SCOPE** — dieses Dokument
2. ☐ **BUILD v1** — Hygiene only: Input-Validation, Schema-Enforcement, basic Retries. Happy Path zuerst.
3. ☐ **INSTRUMENT** — Logge jeden LLM-Call: Input, Output, Latency, Token-Count, Cost.
4. ☐ **BREAK** — Red-Team-Session mit adversarialen Inputs:
   - Ambigue CVs (fehlende Daten, freelance-Wirrwarr)
   - Lange CVs (Context-Limit)
   - Leere/malformed Files, Unicode, gemischte Sprachen
   - Prompt-Injection im CV-Text
   - API-Failures (Timeouts, Rate Limits)
   - Confidently-wrong Outputs (erfundene Industries/Expertise)
5. ☐ **EVAL** — Score-Output gegen Ground Truth.
6. ☐ **v2 + MITIGATIONS** — Per Break: Fix, Mitigate, oder Accept-and-Document.
7. ☐ **COST & LATENCY** — Cost per 1.000 Runs, p50/p95 Latency.
8. ☐ **SECURITY/GOVERNANCE NOTE** — was fließt wo, was wird gespeichert, DSGVO-Einwände, Mitigations.
9. ☐ **SHIP** — README, FAILURE_LOG, CHANGELOG, Eval-Ergebnisse, Loom-Demo.

---

## 10. Konkrete nächste Aktion

**Taxonomie erstellen.** YAML-Datei, gegliedert in Kategorien, die zur Beratungs-Persona passen:

- `industries` (FinServ, Pharma, FMCG, Energy, Public Sector, Telco, Automotive, Retail, etc.)
- `functional_expertise` (Strategy, Operations, M&A, Digital Transformation, Performance Improvement, Org Design, etc.)
- `methods` (Lean Six Sigma, Design Thinking, Agile, Change Management, etc.)
- `tools` (Excel, PowerPoint, Tableau, Power BI, Alteryx, etc.)
- `languages` (mit Proficiency-Levels)
- `education_credentials` (MBA, PhD, etc.)

Committen als `taxonomy/taxonomy.yaml`. ~30–60 Min Arbeit.

**Reihenfolge danach:**

1. Schema definieren (referenziert die Taxonomie)
2. Eval-Set erstellen (20 hand-gelabelte CVs als ground-truth)
3. Pipeline bauen (n8n-Workflow)
4. Baseline messen (zero-shot)
5. Pipeline messen (voller Stack)
6. Iterate