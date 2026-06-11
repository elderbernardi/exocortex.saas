---
title: SOP-002: Running Preflight Checks and Validation
created: 2026-06-11
updated: 2026-06-11
nature: workflows
type: workflow
tags: [dev, exocortex, qa, workflow, checklist]
confidence: high
---

# SOP-002: Running Preflight Checks and Validation

This Standard Operating Procedure (SOP) describes how to execute the automated quality validation suites before committing changes or preparing a release.

---

## 1. Quick Development Checklist (`checklist.py`)

Run this command locally during active development and prior to git commit.

### Command
```bash
python3 .agent/scripts/checklist.py .
```

### Checks Performed
*   **Security**: Scans codebase for plain-text secrets and vulnerabilities.
*   **Code Quality**: Executes linters and checks TypeScript/Python typing structures.
*   **Schema Validation**: Verifies database constraints and schema descriptors.
*   **Test Suite**: Runs the unit and integration test blocks.
*   **UX Audit**: Scans active styles against the design system guidelines.
*   **SEO Check**: Assesses standard page metadata and semantic heading structures.

---

## 2. Complete Pre-Deployment Suite (`verify_all.py`)

Run this command prior to deploying code to staging or production. This requires a running development or staging server to execute E2E and visual profiles.

### Command
```bash
python3 .agent/scripts/verify_all.py . --url http://localhost:3000
```

### Checks Performed
Includes all checks from `checklist.py`, plus:
*   **Lighthouse**: Audits Core Web Vitals (LCP, FID, CLS, INP) performance.
*   **Playwright E2E**: Executes complete browser testing flows.
*   **Bundle Analysis**: Verifies bundle sizes and detects bloating dependencies.
*   **Mobile Audit**: Validates mobile layout responsiveness and touch targets.
*   **i18n Check**: Detects hardcoded strings lacking localization keys.

---

## 3. Dedicated Security Scanning

For automated CI pipeline validation or high-security changes:
```bash
python3 .agent/skills/vulnerability-scanner/scripts/security_scan.py
```
This isolates code patterns against OWASP vulnerabilities and checks supply-chain dependencies.

---

## 4. Troubleshooting and Resolution Flow

If any check fails:

1.  **Security / Lint Blocker**: Fix these immediately. Git commit hooks will reject files with active lint or secret leaks.
2.  **Schema Desync**: Update local migrations and verify database schema descriptions.
3.  **Test Suite Failure**: Review test outputs and refactor logic. Do not bypass assertions.
4.  **UX / taste Warning**: Adjust alignment grids or remove repeating generic layouts.
