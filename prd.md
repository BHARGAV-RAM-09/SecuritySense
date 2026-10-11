# SecuritySense — Product Requirements Document (PRD)

## 1. Product Summary

**Product name:** SecuritySense

**Core differentiator:** ProofLoop — Find it. Prove it. Fix it. Prove the fix.

SecuritySense is an AI-assisted security analysis platform that connects static-analysis findings to source evidence, controlled reproduction, proposed remediation, and actual verification results.

## 2. Target Users

- Developers who want to understand and remediate security findings.
- Students learning secure coding and application security.
- Small development teams seeking an accessible security-analysis workflow.
- Reviewers who need traceable evidence for findings and proposed fixes.

## 3. User Problem

Developers may receive static-analysis alerts without enough context to understand the issue, assess whether it is reproducible, choose a safe correction, or verify that the correction works.

SecuritySense aims to make this workflow traceable rather than presenting scanner output as a complete security assessment.

## 4. Product Goals

1. Accept a supported public GitHub repository URL.
2. Identify eligible Python source files and scan them using deterministic tools.
3. Present normalized findings with source locations and available evidence.
4. Investigate candidate findings using relevant code context.
5. Demonstrate controlled reproduction for the broken-access-control example.
6. Generate reviewable patch proposals without changing the original repository.
7. Run applicable verification checks and record their results.
8. Provide a readable ProofLoop report through a web interface.
9. Deploy the MVP at a publicly accessible URL using free-tier services.

## 5. Non-Goals

The MVP will not:

- Guarantee that an application is secure.
- Execute arbitrary submitted repository code on the public server.
- Automatically merge or push proposed changes to an original repository.
- Support every programming language.
- Require a paid model API.
- Depend on GPU infrastructure, Kubernetes, a vector database, or a distributed task queue.
- Treat AI-generated explanations as verified security evidence.

## 6. Core User Journey

1. The user submits a public GitHub HTTPS repository URL.
2. The backend validates the input and applies repository and resource limits.
3. Scout discovers eligible Python files.
4. Bandit scans the selected files.
5. SecuritySense normalizes findings and records scanner evidence.
6. Investigator examines the relevant finding and source context.
7. Reproducer evaluates supported findings in a controlled fixture.
8. Fix Engineer proposes a patch in a disposable workspace.
9. Verifier runs applicable tests or security checks.
10. The application displays the finding, evidence, proposed fix, verification results, and limitations.

Unsupported reproduction or verification steps must be explicitly marked as unrun or inconclusive.

## 7. Functional Requirements

### FR-01: Repository Input

- Accept public GitHub repository URLs over HTTPS.
- Reject malformed or unsupported URLs.
- Apply protections against SSRF and unauthorized network destinations.
- Enforce repository size, file-count, and processing limits.

### FR-02: Python File Discovery

- Discover eligible `.py` files.
- Exclude configured directories such as `.git`, `.venv`, `venv`, `node_modules`, and Python cache directories.
- Enforce a configurable maximum file count.
- Report whether discovery was truncated.

### FR-03: Deterministic Scanning

- Invoke Bandit through a controlled subprocess.
- Enforce a timeout.
- Validate scanner output before using it.
- Record scan failures without falsely reporting successful coverage.
- Normalize findings into a consistent structure.

### FR-04: Finding Representation

Each normalized finding should include, where available:

- Scanner or tool name.
- Rule identifier.
- Severity and confidence.
- Finding message.
- Source file and line number.
- Relevant code context.
- Supporting evidence.
- Processing and verification status.

Missing information must not be fabricated.

### FR-05: Investigation

- Examine the selected finding and relevant source context.
- Distinguish observed facts from hypotheses.
- Explain why the evidence supports or does not support the candidate finding.
- Avoid presenting an AI-generated explanation as proof by itself.

### FR-06: Controlled Reproduction

- Support the project's controlled broken-access-control demonstration.
- Use isolated test fixtures.
- Record the actual test result.
- Do not execute arbitrary repository code to reproduce a vulnerability.

### FR-07: Patch Proposal

- Produce a reviewable patch or proposed code change.
- Preserve the original repository.
- Keep proposed changes in a disposable workspace.
- Describe the intended correction and its limitations.
- Do not claim that a proposal fixes a vulnerability before verification.

### FR-08: Verification

- Run applicable tests or security checks.
- Record which checks ran and their actual outcomes.
- Distinguish passed, failed, unrun, and inconclusive results.
- Preserve relevant evidence for the report.

### FR-09: ProofLoop Report

The report should connect:

1. Candidate finding.
2. Source and scanner evidence.
3. Investigation.
4. Reproduction result, when supported.
5. Proposed patch.
6. Verification results.
7. Limitations and outstanding checks.

### FR-10: Web Interface and API

- Provide a browser-based workflow.
- Expose API endpoints for health checks, scan submission, scan status, findings, reports, and patch proposals.
- Return understandable validation and processing errors.
- Avoid exposing credentials, secrets, or internal sensitive details.

### FR-11: Public Deployment

- Provide a publicly accessible application URL.
- Use free-tier services for the core MVP, subject to current provider restrictions.
- Configure production security controls before exposing the application.
- Document deployment and operational limitations.

## 8. Non-Functional Requirements

### Security

- Treat submitted source code and repository content as untrusted.
- Validate inputs and restrict network access.
- Never expose credentials in the frontend.
- Avoid unrestricted command execution.
- Apply timeouts and resource limits.
- Use appropriate temporary-workspace cleanup.
- Treat repository content as data, not as instructions to the application.

### Reliability

- Report scanner and processing failures explicitly.
- Avoid marking incomplete scans as fully completed.
- Preserve actual verification outcomes.
- Ensure one file's scanner failure does not silently invalidate the status of the entire scan.

### Usability

- Use clear labels and source locations.
- Explain technical findings in understandable language.
- Make proposed changes reviewable.
- Clearly distinguish confirmed evidence from hypotheses.

### Maintainability

- Separate discovery, scanning, investigation, reproduction, remediation, and verification.
- Keep modules independently testable.
- Use automated tests for important behavior.
- Document the architecture and security boundaries.

## 9. Technology Requirements

- Python
- FastAPI
- HTML, CSS, vanilla JavaScript
- Git and GitHub
- Bandit
- pytest
- Free-tier hosting for the backend and frontend, subject to availability and limits

Optional AI assistance may be added only if its free allowance and terms are verified. The core deterministic workflow must not depend on a paid API.

## 10. Acceptance Criteria

The MVP must demonstrate that it can:

- Accept and validate an eligible public repository URL.
- Discover and scan eligible Python files.
- Identify a supported security finding with source evidence.
- Record investigation results without inventing evidence.
- Reproduce the controlled broken-access-control example.
- Generate a proposed fix without modifying the original repository.
- Execute applicable verification checks.
- Report honest verification statuses.
- Present the end-to-end ProofLoop in a web interface.
- Run at a public URL.
- Pass automated tests for core functionality.
- Include setup instructions, architecture documentation, security limitations, and a demonstration script.

## 11. Success Measures

The project will be evaluated on:

- Correctness of deterministic findings.
- Traceability between findings and evidence.
- Reliability of controlled reproduction.
- Quality and reviewability of patch proposals.
- Accuracy of verification reporting.
- Security boundaries around untrusted repositories.
- End-to-end usability.
- Successful public deployment and documentation.

No numerical performance or accuracy target is assumed until it is explicitly defined and measured.