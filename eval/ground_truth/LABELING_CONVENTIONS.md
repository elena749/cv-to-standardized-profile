# Labeling Conventions for Ground Truth

Dieses Dokument hält fest, wie ich beim Hand-Labeling Entscheidungen treffe, damit das Eval-Set konsistent bleibt. Wenn beim Labeln eine neue Edge-Case-Frage auftaucht, dokumentiere ich die Entscheidung hier, bevor ich weiter labele.

---

## Industries

- **Auch Praktika und Werkstudent-Tätigkeiten zählen**, wenn sie zeigen, in welchen Industries der Bewerber Erfahrung gesammelt hat. Hintergrund: zeigt Profil-Interesse über Zeit, auch wenn die Erfahrung kurz war.
- **Studienprojekte und Masterarbeiten zählen NICHT** zu Industries, auch wenn sie thematisch in einem Sektor sind.
- **Multi-Sektor-CVs:** alle erwähnten Industries werden gezählt, auch wenn nur ein einzelnes Projekt in dem Sektor stattfand.

## Functional Expertise — strenge Auslegung

- Werden NUR gezählt, wenn der Bewerber **operativ** in dem Bereich gearbeitet hat
- NICHT abzuleiten aus:
  - Erwähnungen verwandter Begriffe (*"regulierte Übernahmen"* zählt nicht als *"Risk Management"*)
  - MBA-Schwerpunkten oder Studiengängen (*"Strategy"* im MBA ≠ Strategy als Functional Expertise)
  - Branchenkenntnis allein (jemand der für Banken arbeitet, hat nicht automatisch *"Banking"* als Functional Expertise — das wäre Industry, nicht Functional)
- *"Strategy"* und *"Corporate Strategy"* / *"Growth Strategy"* werden separat gezählt, wenn beides erkennbar ist
- Wenn nur generisch *"Strategie"* erwähnt → nur *"Strategy"*

## Career Level (Standard-Pfad)

- **Entry:** 0-2 Jahre Vollzeit-Erfahrung, Hochschulabsolvent oder erste feste Stelle
- **Mid:** 2-4 Jahre Vollzeit-Erfahrung
- **Senior:** 5-8 Jahre Vollzeit-Erfahrung
- **Lead-Level (8+ Jahre):** out-of-scope, läuft über Executive Search
- **Praktika und Werkstudent-Zeiten zählen NICHT** zu den Erfahrungsjahren
- **Bei Lücken (Elternzeit, Sabbatical):** zählen auch nicht zu den Erfahrungsjahren

## Career Level für Career-Switcher

Career-Switcher (z.B. Anwalt → Beratung) werden basierend auf **Erfahrung im Ziel-Beruf (Beratung)** eingestuft, nicht auf gesamte Berufserfahrung.

- 0-2 Jahre Beratungserfahrung (egal wie viele Jahre andere Erfahrung) → Entry/Mid (typischerweise Mid mit MBA)
- 2-4 Jahre Beratungserfahrung → Mid
- 5-8 Jahre Beratungserfahrung → Senior

**Begründung:** Recruiter und Hiring Manager evaluieren Career-Level nach passendem Funktions-Kontext, nicht nach Total-Years.

**Wichtig:** `total_years_experience` bleibt aber die **Gesamtzahl** (alle Jahre, inklusive vorherige Berufe). Nur `career_level` folgt der Ziel-Beruf-Logik.

## Total Years Experience

- Berechnet aus `employment_history`, ohne Praktika und Werkstudent-Zeiten, ohne Lücken
- Bei laufenden Positionen: bis heute (Mai 2026)
- **Mathematisches Runden** auf volle Jahre: 5,4 Jahre → 5; 5,5 Jahre → 6; 8,5 Jahre → 9

## Teilzeit und Erfahrungsjahre

- Teilzeit-Tätigkeiten zählen als **Kalenderzeit**, nicht als FTE-Äquivalent
- **Begründung:** Standard in HR-Systemen, im CV wird Kalenderzeit dokumentiert. Beispiel: 4 Jahre Teilzeit (80%) zählen als 4 Jahre, nicht als 3,2 Jahre

## Employment History

- Praktika und Werkstudent-Tätigkeiten WERDEN in `employment_history` aufgenommen (zur Vollständigkeit)
- Sie zählen aber **nicht** zu `total_years_experience` und **nicht** zur Career-Level-Berechnung
- Lücken (Elternzeit, Sabbatical) werden NICHT als employment_history-Einträge aufgeführt — sie sind Lücken zwischen Einträgen

## Responsibilities

- Kurz halten: 1-3 Sätze pro Position
- Inhaltliche Schwerpunkte zusammenfassen, keine Aufzählung jeder einzelnen Aufgabe
- Bei sehr knappen CVs (cv_19): null wenn keine substantiellen Beschreibungen vorhanden

## Education

- Alle erwähnten Abschlüsse werden aufgenommen, auch der Bachelor wenn er erwähnt wird
- Wenn mehrere Abschlüsse: chronologisch absteigend (höchster/aktuellster zuerst)
- `field_of_study`: Hauptfach. Bei Schwerpunkten in Klammern z.B. *"Betriebswirtschaftslehre, Schwerpunkt Finance"*

## Education Credentials Mapping

- **MBA:** alle Bachelor-of-Business-Administration-Varianten und MBAs aller Schulen
- **Executive MBA:** explizit als EMBA gekennzeichnet
- **Master of Science:** M.Sc. in jedem Fach
- **Diplom:** alte deutsche Diplom-Abschlüsse (Diplom-Kaufmann, Diplom-Wirtschaftsingenieur, Diplom-Volkswirt)
- **Staatsexamen:** Erstes oder Zweites Juristisches Staatsexamen, Medizinisches Staatsexamen
- **PhD:** alle Promotionen (Dr. rer. pol., Dr. rer. nat., Dr. Ing., Doctor of Philosophy)
- **Master of Laws (LL.M.):** explizit als LL.M.

## Industries Mapping

- *"Banking"* und *"Asset Management"* können beide gezählt werden, wenn beide erwähnt sind
- *"Pharmaceuticals"* + *"MedTech"* + *"Healthcare"* — werden separat gezählt wenn separat erwähnt
- *"Industrial Goods"* deckt klassischen Maschinenbau und Industriefertigung ab
- *"Automotive"* nur explizit für Auto-Hersteller und -Zulieferer

## Functional Expertise Mapping

- *"M&A"* und *"Mergers and Acquisitions"* → kanonisch *"Mergers and Acquisitions"*
- *"PMI"* und *"Post-Merger Integration"* → kanonisch *"Post-Merger Integration"*
- *"Performance Improvement"* deckt Kostenoptimierung, Effizienzprogramme, Restrukturierung
- *"Digital Transformation"* nur wenn explizit erwähnt — nicht aus *"digitales Projekt"* ableiten

## Methods Mapping

- *"Lean Six Sigma"* deckt sowohl reine Lean- als auch Six-Sigma-Methoden, plus alle Belt-Stufen
- *"Agile"* + *"Scrum"* werden separat gezählt wenn beide erwähnt
- Generisches *"Projektmanagement"* mappt nicht — nur konkrete Frameworks

## Tools Mapping

- *"Excel"* → *"Microsoft Excel"*
- *"PowerPoint"* / *"PPT"* → *"Microsoft PowerPoint"*
- *"think-cell"* exakt so (mit Bindestrich, klein)
- *"Power BI"* mit Leerzeichen
- *"R"* nur wenn explizit als Tool/Sprache erwähnt — nicht aus *"R&D"* ableiten

## Skill-Levels für Tools

- **Skill-Levels werden in v1 NICHT erfasst** (z.B. *"Python (advanced)"* → nur *"Python"*)
- **Begründung:** Self-Assessments sind unzuverlässig (jeder bewertet sich anders) und nicht standardisiert
- **v2-Roadmap:** Levels nur erfassen, wenn auf standardisierten Credentials basierend (z.B. CEFR für Sprachen, Vendor-Zertifizierungen für Tools)

## Languages

- CEFR-Level direkt übernehmen wenn angegeben (z.B. *"C2"* → *"German (C2)"*)
- *"Muttersprache"* / *"Mother tongue"* / *"Native"* → Native
- *"Verhandlungssicher"* → C2
- *"Fließend"* → C1
- *"Gut"* → B2
- *"Grundkenntnisse"* / *"ein bisschen [Sprache]"* → nicht aufnehmen oder als unmapped
- **German (B2) und niedriger:** sind nicht in v1-Taxonomie (Persona-Entscheidung: deutsche Beratung erhält selten ernsthafte Bewerbungen mit Deutsch unter C1) → mappen auf `unmapped`
- Sprachen außerhalb der Taxonomie (Hindi, Niederländisch, etc.) → mappen auf `unmapped`

## Certifications

- Frei-Text, kein Mapping
- Belt-Stufen ausschreiben: *"Lean Six Sigma Green Belt"* statt *"LSS GB"*
- **Nur abgeschlossene Zertifikate** — nicht *"in Vorbereitung"* oder *"Candidate"* (z.B. *"CFA Level II Candidate"* zählt NICHT, *"CFA Level I (passed)"* zählt)

## Email, Phone, Location

- **Email:** exakt wie im CV stehend, lower-case wenn ambig
- **Phone:** im CV-Format belassen (Format variiert international)
- **Location:** *"Stadt, Land"* wenn beides angegeben, sonst nur Stadt

## Akademische Noten

- **Noten werden in v1 NICHT erfasst** (auch nicht *"summa cum laude"*, *"First Class Honours"*, *"Distinction"*, GPA-Zahlen)
- **Begründung:** Noten sind regional unterschiedlich kodiert (DE: 1.0-5.0, UK: First/Upper Second, US: 4.0-Skala) — Normalisierung ist v2-Aufwand
- **Im README dokumentiert:** für Beratungs-Recruiting sind Noten ein primärer Filter (Top-3 Firmen screenen Top-Dezil) — daher v2-Roadmap-Item

## Datums-Format

- Bevorzugt **YYYY-MM** (z.B. *"2022-03"*)
- Wenn nur Jahresangabe im CV: **YYYY** (z.B. *"2022"*)
- Bei laufenden Positionen: **end_date = null**
- Monatsnamen werden in Zahlen konvertiert (*"März"* → *"03"*, *"April"* → *"04"*)

## Bei extrem knappen CVs (z.B. cv_19)

- Felder, die nicht extrahiert werden können: **null** (für Strings) oder **leeres Array []** (für Listen)
- `name` ist Pflicht — wenn auch der Name fehlt, ist das Profil ungültig (Schema-Failure)
- `total_years_experience`: 0 wenn keine Erfahrung erkennbar (nicht null), null wenn unklar

## Bei extrem langen CVs (z.B. cv_20)

- Alle erwähnten Industries / Methods / Tools werden aufgenommen, auch wenn die Liste lang wird
- Employment History: alle Stationen, auch ältere
- Verzicht auf Konsolidierung — Ground Truth ist die *vollständige Wahrheit*, nicht eine Zusammenfassung

---

## Änderungs-Log dieses Dokuments

- **2026-05-07 (initial):** Initial version basierend auf cv_01-Labeling
- **2026-05-07 (review pass):** Ergänzungen aus cv_02-cv_18 Review:
  - Functional Expertise strenge Auslegung (cv_15: keine Halluzinationen aus verwandten Begriffen)
  - Career-Switcher-Convention (Sichtweise B: Erfahrung im Ziel-Beruf zählt)
  - Teilzeit als Kalenderzeit
  - Mathematisches Runden (8,5 → 9)
  - Skill-Levels für Tools out-of-scope für v1
  - Akademische Noten out-of-scope für v1
  - CFA Candidate weglassen, CFA passed aufnehmen
  - German B2 und niedriger als unmapped