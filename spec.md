# SecuritySense — Technical Specification

## 1. Purpose

This document defines the technical design for SecuritySense, an AI-assisted security analysis platform centered on the ProofLoop workflow:

**Find it. Prove it. Fix it. Prove the fix.**

The implementation must preserve evidence integrity, isolate untrusted repository content, and report actual test and scanner results.

## 2. Architecture

### 2.1 Technology Stack

- Python
- FastAPI
- HTML, CSS, and vanilla JavaScript
- Bandit for deterministic Python static analysis
- pytest for automated tests
- Git and GitHub
- Free-tier public hosting, subject to current provider restrictions

Optional AI integration is permitted only if a suitable free allowance and its terms are verified. The deterministic workflow must remain usable without a model API.

### 2.2 Logical Components

1. **Scout:** discovers eligible Python files and invokes deterministic scanning.
2. **Investigator:** examines normalized findings and supporting source evidence.
3. **Reproducer:** assesses supported findings in controlled fixtures.
4. **Fix Engineer:** generates reviewable patch proposals in a disposable workspace.
5. **Verifier:** executes applicable checks and records actual outcomes.
6. **Orchestrator:** coordinates workflow stages, data handoffs, and status transitions.

The orchestrator is a coordinator, not a sixth independent AI agent.

## 3. Current Implementation Baseline

The following components have already been implemented and tested:

- `app/agents/scout.py`
- `app/scanners/bandit_runner.py`
- `app/scanners/findings.py`
- `app/scanners/scan_workspace.py`
- `tests/test_access_control.py`
- `tests/test_bandit_integration.py`
- `tests/test_bandit_runner.py`
- `tests/test_findings.py`
- `tests/test_scan_workspace.py`
- `tests/test_scout.py`
- `tests/test_scout_limit.py`

The controlled fixtures are:

- `tests/fixtures/vulnerable_app.py`
- `tests/fixtures/secure_app.py`
- `tests/fixtures/bandit_demo.py`

The current automated test suite has been reported as passing 26 tests. This is a test result, not a production-security certification.

## 4. Repository Layout

The intended structure is:

```text
securitysense/
├── app/
│   ├── main.py
│   ├── api/
│   │   └── routes.py
│   ├── core/
│   │   ├── config.py
│   │   └── orchestrator.py
│   ├── agents/
│   │   ├── scout.py
│   │   ├── investigator.py
│   │   ├── reproducer.py
│   │   ├── fix_engineer.py
│   │   └── verifier.py
│   ├── scanners/
│   │   ├── bandit_runner.py
│   │   ├── findings.py
│   │   ├── scan_workspace.py
│   │   ├── secrets_runner.py
│   │   └── dependency_runner.py
│   ├── proofloop/
│   │   ├── evidence.py
│   │   ├── patch.py
│   │   └── verification.py
│   ├── schemas/
│   │   └── findings.py
│   ├── templates/
│   │   └── index.html
│   └── static/
│       ├── css/
│       │   └── style.css
│       └── js/
│           └── app.js
├── tests/
│   ├── fixtures/
│   │   ├── vulnerable_app.py
│   │   ├── secure_app.py
│   │   └── bandit_demo.py
│   ├── test_access_control.py
│   ├── test_bandit_integration.py
│   ├── test_bandit_runner.py
│   ├── test_findings.py
│   ├── test_scan_workspace.py
│   ├── test_scout.py
│   └── test_scout_limit.py
├── docs/
│   ├── architecture.md
│   ├── security-model.md
│   └── demo-script.md
├── scope.md
├── prd.md
├── spec.md
├── requirements.txt
├── .gitignore
├── .env.example
├── README.md
└── render.yaml
```

Create modules incrementally as their phases begin. Do not create empty files en masse.

## 5. API Contract

The planned API endpoints are:

| Method | Endpoint | Purpose |
|---|---|---|
| GET | `/` | Serve the web interface |
| GET | `/health` | Return service health |
| POST | `/api/scans` | Validate and submit a scan |
| GET | `/api/scans/{scan_id}` | Retrieve scan status and summary |
| GET | `/api/scans/{scan_id}/findings` | Retrieve findings |
| GET | `/api/scans/{scan_id}/report` | Retrieve the ProofLoop report |
| POST | `/api/scans/{scan_id}/proposals` | Request a proposed fix |

These endpoints are planned contracts. They are not considered implemented until the relevant code and tests exist.

## 6. Finding Data Model

A normalized finding should support the following fields where available:

- `tool`
- `rule_id`
- `severity`
- `confidence`
- `message`
- `file`
- `line`
- `code`

Investigation and ProofLoop components may attach additional evidence and processing metadata without fabricating unavailable scanner information.

## 7. Workflow and State Reporting

The orchestrator will coordinate these stages:

1. Input validation.
2. File discovery and deterministic scanning.
3. Finding normalization.
4. Investigation.
5. Controlled reproduction, where supported.
6. Patch proposal generation.
7. Verification.
8. Report assembly.

Verification outcomes must use these states:

- `passed`
- `failed`
- `unrun`
- `inconclusive`

A stage that has not executed must not be represented as passed. Partial scanning must not be reported as complete coverage.

## 8. Security Requirements

### 8.1 Repository Input

- Accept only supported public GitHub HTTPS URLs.
- Validate the host, URL structure, redirects, and resolved network destinations.
- Apply SSRF protections.
- Enforce size, file-count, timeout, and resource limits.
- Avoid exposing internal filesystem paths or sensitive server details to users.

### 8.2 Untrusted Code

- Do not execute arbitrary submitted repository code.
- Do not invoke arbitrary build hooks or install submitted dependencies.
- Run controlled reproduction only against trusted project fixtures.
- Keep proposed patches in disposable workspaces.
- Never modify or push changes to the original repository.

### 8.3 Process Execution

- Use argument arrays rather than shell-composed commands.
- Apply timeouts.
- Validate subprocess return codes and output structures.
- Record failures honestly.
- Clean up temporary resources.

### 8.4 Application Security

- Validate API inputs.
- Apply rate limits and suitable CORS restrictions.
- Keep secrets out of frontend assets and logs.
- Treat repository comments and other source content as untrusted data.
- Avoid using untrusted source content as model instructions.

## 9. ProofLoop Evidence Model

The report should connect:

- The original finding.
- Scanner output and source location.
- Investigation observations.
- Reproduction inputs and actual results.
- Proposed patch or diff.
- Verification commands or checks and their actual outcomes.
- Remaining uncertainty and limitations.

Evidence must distinguish observed facts from explanations and hypotheses. A proposed fix is not verified merely because it appears reasonable.

## 10. Testing Strategy

### Unit Tests

- Input validation.
- File discovery and file limits.
- Finding normalization.
- Scan status and error handling.
- Evidence serialization.
- Verification status transitions.

### Integration Tests

- Bandit execution against controlled fixtures.
- End-to-end deterministic workspace scanning.
- Orchestration between implemented modules.
- Controlled vulnerable-versus-secure access-control behavior.
- Patch generation and verification when implemented.

### Acceptance Tests

- Public repository input validation.
- Traceable findings.
- Controlled reproduction.
- Reviewable patch proposals.
- Actual verification results.
- Correct handling of unrun and inconclusive checks.
- Web-interface and API workflow.
- Public deployment and documented limitations.

## 11. Runtime and Deployment

The MVP will use a Python backend and a static frontend. Temporary or in-memory scan state may be used initially, with appropriate limits and cleanup.

The selected hosting platform must be checked for current free-tier limits, supported runtime, filesystem behavior, resource constraints, and deployment requirements before use.

No paid service is mandatory for the core MVP.

## 12. Implementation Sequence

1. Phase 0 — Specifications and environment setup.
2. Phase 1 — Controlled vulnerability fixtures.
3. Phase 2 — Scout and deterministic scanning.
4. Phase 3 — Orchestrator and Investigator.
5. Phase 4 — Reproducer and ProofLoop evidence.
6. Phase 5 — Fix Engineer and Verifier.
7. Phase 6 — Frontend and API.
8. Phase 7 — Public deployment and security hardening.
9. Phase 8 — Optional enhancements.

The phase sequence and agreed scope remain fixed unless explicitly changed by the project owner.

## 13. Definition of Done

SecuritySense is ready for MVP demonstration when the end-to-end workflow produces a traceable finding, supporting evidence, controlled reproduction where supported, a reviewable proposed fix, and honest verification results.

The application must be publicly accessible, documented, and tested. Passing automated tests alone does not establish production readiness or prove the absence of security vulnerabilities.