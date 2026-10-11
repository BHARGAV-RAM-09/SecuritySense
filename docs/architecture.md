# SecuritySense Architecture

## 1. Overview

SecuritySense is a Python-based security analysis MVP built with FastAPI. It coordinates static analysis, investigation, controlled reproduction, patch application, and verification through a web interface.

The current deployment uses a configured demonstration workspace. It does not execute arbitrary public GitHub repositories.

## 2. Architecture

```text
                    User / Browser
                          |
                          v
                  FastAPI Web App
                  /             \
                 v               v
          Static Frontend      REST API
          HTML/CSS/JS              |
                                   v
                           Scan Orchestrator
                                   |
                    +--------------+--------------+
                    |              |              |
                    v              v              v
                 Scout         Bandit Scanner   Investigator
                    |              |              |
                    +--------------+--------------+
                                   |
                                   v
                           Finding Records
                                   |
                                   v
                           ProofLoop Evidence
                                   |
                   +---------------+---------------+
                   |               |               |
                   v               v               v
              Reproduction    Patch Workflow    Verification
                   |               |               |
                   +---------------+---------------+
                                   |
                                   v
                          JSON Scan Results
                                   |
                                   v
                            Browser Report
```

## 3. Application components

### FastAPI application

`app/main.py` initializes the web application, serves the frontend, and exposes the health endpoint.

### REST API

`app/api/routes.py` validates scan requests, enforces the configured demonstration workspace, coordinates analysis, and exposes scan results and reports.

The current API stores scan results in an in-memory dictionary protected by a lock. Results are not durable and may disappear after a process restart.

### Scout

`app/agents/scout.py` discovers eligible Python files within the allowed workspace and applies file-selection limits.

### Static scanner

`app/scanners/bandit_runner.py` runs Bandit against the controlled workspace.

`app/scanners/findings.py` normalizes scanner output.

`app/scanners/scan_workspace.py` coordinates scanning and records scan status and failures.

### Investigator

`app/agents/investigator.py` collects source context for reported findings while applying workspace path restrictions.

Investigation evidence helps explain a finding; it does not independently prove exploitability.

### Controlled reproducer

`app/agents/reproducer.py` executes predefined access-control checks against the project's demonstration fixtures.

The checks demonstrate the difference between a vulnerable example and a secure example. Their results apply only to those controlled examples.

### ProofLoop evidence

`app/proofloop/evidence.py` constructs evidence records and tracks verification-related status without treating missing evidence as success.

### Fix workflow

`app/proofloop/patch.py` prepares a patch for the known demonstration fixture.

`app/proofloop/apply_patch.py` applies changes to a separate temporary file rather than overwriting the original fixture.

`app/proofloop/fix_workflow.py` coordinates the controlled patch and verification demonstration.

### Verifier

`app/agents/verifier.py` runs the configured test verification process with execution limits.

The controlled workflow generates tests for the patched access-control example. A passing result is evidence for those tests only.

### Frontend

`app/templates/index.html` defines the page structure.

`app/static/css/style.css` defines the visual styling.

`app/static/js/app.js` submits scan requests, displays findings and evidence, shows workflow status, and exports JSON reports.

## 4. End-to-end data flow

1. The user submits a scan request through the browser.
2. FastAPI validates the request and accepts only the configured `demo` workspace.
3. The orchestrator discovers files and runs the static scanner.
4. Findings are investigated using source context.
5. The system records evidence and runs controlled access-control reproduction checks.
6. For approved project paths, the separate access-control patch workflow can create a temporary patched copy and verify it.
7. The API stores the resulting scan record in memory.
8. The frontend retrieves the record and displays its findings, evidence, statuses, and JSON export.

## 5. Important workflow distinction

The static scanner's findings and the access-control fix demonstration are separate activities.

For example, a Bandit finding can be reported while the controlled access-control patch workflow passes. This does not mean that the Bandit finding was fixed.

SecuritySense preserves these distinctions through separate finding records, reproduction results, patch statuses, and verification statuses.

## 6. Deployment

The repository includes `render.yaml` for the Render web service configuration.

The hosted application is available at:

- Application: https://securitysense.onrender.com/
- API health: https://securitysense.onrender.com/health
- API readiness: https://securitysense.onrender.com/api/status
- Interactive API documentation: https://securitysense.onrender.com/docs

The service uses in-memory state, so scan history should not be considered persistent.

## 7. Current limitations

- Scanning is restricted to the configured demonstration workspace.
- Arbitrary public GitHub repository scanning is not implemented.
- The reproduction workflow covers controlled access-control fixtures.
- Patch verification does not establish the security of the entire application.
- Scan records are stored in memory rather than durable storage.
- The current MVP is a demonstration and is not a substitute for a full security audit.
