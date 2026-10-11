# SecuritySense

**Find it. Prove it. Fix it. Prove the fix.**

SecuritySense is an AI-assisted security analysis MVP built with Python and FastAPI. It combines static analysis, finding investigation, controlled vulnerability reproduction, patch demonstration, and verification evidence in a web interface.

**Live demo:** https://securitysense.onrender.com/  
**Source code:** https://github.com/BHARGAV-RAM-09/SecuritySense

## The problem

Security scanners can identify suspicious code, but a finding alone does not show whether a specific behavior can be reproduced or whether a proposed change resolves a demonstrated problem.

SecuritySense explores an evidence-oriented workflow that keeps detection, investigation, reproduction, patching, and verification as distinct stages.

## How ProofLoop works

1. **Find:** Run Bandit against the configured Python demonstration workspace.
2. **Investigate:** Collect source context and evidence associated with each finding.
3. **Reproduce:** Run controlled access-control checks against the project's demonstration fixtures.
4. **Fix:** Generate and apply a patch to a temporary copy of the known vulnerable fixture.
5. **Verify:** Run controlled tests against the patched copy and report the observed result.

The application distinguishes statuses such as `passed`, `failed`, `unrun`, and `inconclusive`. A successful test run is evidence about the tested behavior, not proof that an entire application is secure.

## Current scope

The publicly deployed MVP scans a configured local demonstration workspace on the server. It does **not** currently support arbitrary public GitHub repository scanning.

The demonstration includes:

- A Python fixture with a deliberate Bandit-detectable issue.
- Vulnerable and secure access-control examples.
- Controlled reproduction checks.
- A temporary patch-application and verification workflow.
- A web interface for findings, investigation evidence, workflow status, and JSON report export.

The access-control fix demonstration is separate from the Bandit finding. A successful access-control verification does not mean the Bandit finding has been fixed.

## Technology stack

- Python
- FastAPI
- Uvicorn
- Bandit
- pytest
- HTML, CSS, and vanilla JavaScript
- Git and GitHub
- Render for hosting

## Run locally

### Requirements

Install Python and Git. Python 3.13.5 is configured in the current Render deployment; a compatible Python version is recommended.

### Setup

Clone the repository:

```bash
git clone https://github.com/BHARGAV-RAM-09/SecuritySense.git
cd SecuritySense
```

Create and activate a virtual environment.

**Windows PowerShell:**

```powershell
py -3.13 -m venv .venv
.\.venv\Scripts\Activate.ps1
```

Install dependencies:

```powershell
python -m pip install -r requirements.txt
```

Start the application:

```powershell
python -m uvicorn app.main:app --reload
```

Open `http://127.0.0.1:8000` in your browser.

If Python 3.13 is not installed, use an installed Python version compatible with the project's dependencies.

## Run tests

Run the full test suite:

```powershell
python -m pytest -q
```

Run the controlled fix workflow tests:

```powershell
python -m pytest tests\test_fix_workflow.py tests\test_fix_engineer.py tests\test_verifier.py tests\test_orchestrator.py -q
```

The development test suite previously passed 69 tests. Run the commands against your current checkout to verify its present state.

## API endpoints

| Method | Endpoint | Purpose |
|---|---|---|
| GET | `/health` | Application health check |
| GET | `/api/status` | API readiness |
| POST | `/api/scans` | Start a configured demonstration scan |
| GET | `/api/scans/{scan_id}` | Retrieve scan results |
| GET | `/api/scans/{scan_id}/findings` | Retrieve findings and investigation evidence |
| GET | `/api/scans/{scan_id}/report` | Retrieve a concise report |

Interactive API documentation is available at `/docs` when the application is running.

### Example scan request

```json
{
  "workspace_name": "demo",
  "max_files": 100,
  "context_lines": 3
}
```

The API accepts the configured `demo` workspace only. Scan results are stored in memory, so they are not durable across server restarts.

## Security considerations

SecuritySense is a demonstration project, not a replacement for a professional security review.

- Only configured workspaces are accepted by the scan API.
- The controlled patch workflow targets known project fixtures.
- The original access-control fixture should remain unchanged during patch verification.
- Scanner findings require investigation and interpretation.
- Verification applies only to the specific behavior and tests executed.
- In-memory scan results can disappear when the server restarts.
- Production-grade authentication, durable storage, broader rate limiting, and arbitrary repository scanning are outside the current MVP scope.

Review `docs/security-model.md` for additional details.

## Project documentation

- [`scope.md`](scope.md) — project boundaries and supported functionality.
- [`prd.md`](prd.md) — product requirements.
- [`spec.md`](spec.md) — implementation specification.
- [`docs/architecture.md`](docs/architecture.md) — architecture and data flow.
- [`docs/security-model.md`](docs/security-model.md) — security boundaries and limitations.
- [`docs/demo-script.md`](docs/demo-script.md) — presentation walkthrough.

## Roadmap

Potential future improvements, subject to scope and available time:

- Support additional languages and repository formats.
- Add stronger evidence linking findings to proposed patches.
- Improve report readability and auditability.
- Add durable storage and scan history.
- Introduce carefully sandboxed analysis for user-submitted repositories.

These are future directions, not features claimed to be implemented in the current MVP.

## License

No license is declared by this README. Add an explicit open-source license before inviting reuse or redistribution.
