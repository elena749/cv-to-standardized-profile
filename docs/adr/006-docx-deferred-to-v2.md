# ADR-006: DOCX support deferred to v2

## Status
Accepted

## Date
2026-05-08

## Context

The eval set contains 20 CVs across three formats: 10 PDF, 8 DOCX, 2 TXT. The pipeline must process all three to fully cover the eval set and reflect realistic consulting-recruiting input volume (DOCX dominates in this domain).

DOCX cannot be passed directly to an LLM via n8n's standard OpenAI node — as of May 2026, the node's file input is limited to PDF. DOCX requires either (a) a conversion service that extracts text, (b) a switch to OpenAI's Responses API (which does support DOCX natively as of February 2026) via custom HTTP-Request, or (c) self-hosted infrastructure with mammoth or similar.

## Options considered

### Option 1: OpenAI Responses API with native DOCX file input
n8n version 1.117.0+ exposes the Responses API as a separate operation. The Responses API can accept DOCX files directly via the Files API + file_id reference. However, n8n's V2 OpenAI node only exposes PDF as a file type in the message-input — DOCX cannot be selected through the UI. Workaround: build the Responses API call via raw HTTP-Request node.

Compliance: file goes to OpenAI (US). Same trade-off as any US-vendor path.

### Option 2: AWS Textract Frankfurt
AWS's text-extraction service running in the Frankfurt region. EU data residency. Standard enterprise DPA. US CLOUD Act still applies because AWS is US-incorporated.

Setup complexity: AWS account, IAM user with Textract permissions, credential setup in n8n via the native AWS node or HTTP-Request.

### Option 3: AWS European Sovereign Cloud Textract
Launched January 2026. Physically and logically separate from commercial AWS regions. EU-incorporated entity, EU-resident personnel, designed to exclude US CLOUD Act exposure. Textract is in the initial service list.

Setup complexity: high. Enterprise onboarding, separate account from commercial AWS, separate IAM partition. Not practical for solo-developer setup in a single session.

### Option 4: CloudConvert
US-based conversion API. 25 free conversions/day. Native n8n node available. Files uploaded to CloudConvert servers; retention per CloudConvert policy.

Compliance: US vendor, no EU residency on free tier, US CLOUD Act applies.

### Option 5: Defer DOCX to v2
Ship the pipeline with PDF + TXT support (14 of 20 eval CVs). Document the four conversion paths as v2-trigger options. The compliance tier of the chosen path becomes a customer-driven decision rather than a pipeline default.

## Decision

Option 5 (defer to v2).

## Rationale

Three reasons:

1. **Phase discipline.** Phase 1 (happy-path end-to-end) must close cleanly before Phase 4 (format expansion) begins. Phase 2 (eval against ground truth) and Phase 3 (instrumentation) must run on the existing pipeline first to surface failure modes. Expanding formats before measurement means building on an unmeasured foundation, and when failures emerge in Phase 2, two pipelines need fixing instead of one.

2. **Compliance-tier choice should be customer-driven.** All four DOCX options have legitimate use cases — different compliance tiers fit different customers. Pre-empting the choice in v1 commits to one compliance position; deferring keeps the architecture open. The README documents the four-path trade-off explicitly so the choice can be made when the customer is known.

3. **The 14-CV eval subset is statistically sufficient.** 10 PDF + 2 TXT + 2 deliberate edge cases provide variation across complexity levels, formats, lengths, and languages. Phase 2 results from this subset are valid measurements of the existing pipeline. DOCX coverage is not a precondition for Phase 2.

The cost of deferring is real: the eval set is partially unused in v1, and the loom demo cannot show DOCX processing. The cost of not deferring is larger: convention drift on architectural decisions, divided attention across formats, and the risk that DOCX setup consumes the time budgeted for Phase 2 measurement.

## Consequences

**Immediate:**
- v1 ships with PDF and TXT only
- README documents DOCX-deferral with the four-path table for future tier selection
- Pending list in README explicitly tracks DOCX as a v2 item

**Downstream:**
- Phase 2 eval runs on 14 of 20 CVs; the 8 DOCX CVs become a v2 eval-set extension
- When a customer is identified for production deployment, the compliance tier determines the conversion path
- Architecture invariant: all four DOCX paths plug into the existing pipeline between the file-type router and the OpenAI extraction node — adding DOCX in v2 is additive, not a rebuild
- The decision to defer is itself a signal in technical due diligence — phase discipline is valued more highly than feature completeness by experienced reviewers

**Revisit trigger:**
- After Phase 2 eval completes, evaluate whether the 14-CV measurement is sufficient or whether DOCX coverage is needed for statistical confidence
- When a customer's compliance tier is identified, select among the four paths and implement
- When n8n's OpenAI node exposes DOCX as a file type for the Responses API (currently PDF-only), Option 1 becomes the simplest path and may bypass the need for a separate conversion service entirely