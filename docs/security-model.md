# SecuritySense Security Model

## 1. Purpose

This document describes the security boundaries, safeguards, and limitations of the current SecuritySense MVP.

SecuritySense analyzes a configured demonstration workspace. It is not a general-purpose scanner for arbitrary public GitHub repositories.

## 2. Assets to protect

- Application availability and integrity.
- Server filesystem and source code.
- Scan results and investigation evidence.
- Temporary files created during patch verification.
- Scanner subprocess execution.
- Configuration and any future credentials or API keys.

## 3. Trust boundaries

### Browser to API

The browser submits a scan request and receives scan results. The server validates the request rather than trusting client-supplied workspace paths.

### API to filesystem

The API accepts the configured `demo` workspace only. It does not expose an endpoint that accepts arbitrary filesystem paths for scanning.

### Orchestrator to scanner

The scanner processes files in the approved workspace and uses execution limits implemented by the scanning components.

### Patch workflow to test execution

The controlled patch workflow targets a known access-control fixture. It applies changes to a temporary copy and verifies the patched behavior without intentionally overwriting the original fixture.

### Analysis results to browser

Results are returned as JSON. The frontend uses DOM text APIs for scanner messages and evidence rather than treating those values as HTML markup.

## 4. Existing safeguards

The current implementation includes these controls:

- Pydantic validation of scan request fields.
- An allowlist for the configured demonstration workspace.
- File discovery and scan limits.
- Workspace path checks in relevant components.
- Controlled patching of a known fixture.
- Temporary-file-based patch verification.
- Test execution limits.
- Explicit `passed`, `failed`, `unrun`, and `inconclusive` status handling.
- In-memory scan result access protected by a lock.
- Frontend text rendering for findings and evidence.

These safeguards reduce specific risks but do not establish that every possible attack path has been eliminated.

## 5. Important limitations and risks

### No arbitrary repository scanning

The current MVP does not fetch and analyze arbitrary GitHub repositories. This restriction reduces exposure to malicious repositories, unsafe build steps, dependency installation, and untrusted source execution.

### No general sandbox

The controlled demonstration must not be treated as a sandbox for arbitrary code. Expanding to user-submitted repositories requires a separately designed isolation boundary.

### In-memory results

Scan results are stored in process memory. They may disappear after a restart and are not a durable audit history.

### Availability and abuse controls

The current implementation should not be assumed to provide production-grade authentication, distributed rate limiting, or multi-tenant isolation.

### Verification scope

A passing controlled test proves only that the tested behavior passed under the executed conditions. It does not establish that the entire application or every reported finding is secure.

### Separate fix demonstration

The access-control patch workflow operates on a known fixture. Its successful result does not imply that a separate Bandit finding has been fixed.

## 6. Recommended safeguards before broader deployment

Before supporting arbitrary repositories or sensitive production workloads, implement and validate:

1. Authentication and authorization where required.
2. Rate limiting and request-level resource budgets.
3. Strict subprocess timeouts and process cleanup.
4. Isolated, disposable workers for untrusted repository analysis.
5. No execution of arbitrary repository build scripts or dependency installation in the application process.
6. Safe temporary-directory handling and cleanup.
7. Secret redaction in logs and reports.
8. Restricted outbound network access to mitigate SSRF and data exfiltration.
9. Durable storage with access controls and retention policies.
10. Security testing, dependency review, monitoring, and incident-response procedures.

These are recommendations for future hardening, not claims that every control is already implemented.

## 7. Security reporting principles

SecuritySense should:

- Distinguish scanner output from confirmed behavior.
- Attach evidence to findings where available.
- Avoid claiming exploitability without supporting evidence.
- Mark unexecuted checks as `unrun`.
- Mark uncertain results as `inconclusive`.
- Report verification only for tests that actually ran.
- Preserve the distinction between a demonstration patch and a fix for a particular finding.

## 8. Responsible use

Use the current application only within its implemented scope. Do not interpret demonstration results as a comprehensive security audit or use the MVP to execute untrusted repository code.