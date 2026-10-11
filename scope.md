# SecuritySense — Project Scope

## 1. Project Overview

SecuritySense is a publicly accessible, AI-assisted GitHub security analysis platform designed to help developers identify security weaknesses, investigate evidence, reproduce selected vulnerabilities in a controlled environment, propose fixes, and verify those fixes.

Its defining workflow is **ProofLoop: Find it. Prove it. Fix it. Prove the fix.**

## 2. Problem Statement

Traditional security scanning tools can identify suspicious code patterns but may leave developers to determine whether a finding is exploitable, how to fix it, and whether the fix actually works.

SecuritySense aims to connect security findings with supporting evidence, controlled reproduction, reviewable patch proposals, and recorded verification results.

## 3. Core Workflow

1. **Detect:** Identify candidate security findings using deterministic scanning tools.
2. **Investigate:** Examine source locations, scanner evidence, and relevant code context.
3. **Reproduce:** Assess selected findings in a controlled test environment.
4. **Fix:** Generate a reviewable patch proposal without modifying the original repository.
5. **Verify:** Run applicable tests or security checks and record their actual results.
6. **Report:** Present findings, evidence, proposed changes, verification outcomes, and limitations.

## 4. MVP Scope

The minimum viable product will support:

- Public GitHub repositories supplied through HTTPS URLs.
- Python source-code discovery.
- Deterministic static analysis using Bandit.
- Normalized findings with rule identifiers, severity, confidence, messages, source locations, and code context where available.
- Evidence-based investigation of candidate findings.
- A controlled demonstration of broken access control.
- Vulnerable and secure demonstration implementations.
- Controlled reproduction using the project's own test fixtures.
- Reviewable fix proposals in a disposable workspace.
- Verification using applicable tests and security checks.
- A ProofLoop report with explicit verification states.
- A browser-based interface and API.
- Public hosting using free-tier services, subject to their current limits and availability.

## 5. ProofLoop Evidence Requirements

SecuritySense must distinguish between a scanner finding, a reproduced vulnerability, a proposed fix, and a verified fix.

Every reported result must reflect evidence actually obtained.

Supported verification states:

- **Passed:** The specified check ran and passed.
- **Failed:** The specified check ran and failed.
- **Unrun:** The check was not executed.
- **Inconclusive:** The available evidence does not establish a clear outcome.

A passing test does not establish that an entire application is secure. Reports must state the checks performed and relevant limitations.

## 6. Agent Responsibilities

The application will use five logical Python modules coordinated by one orchestrator:

- **Scout:** Discover eligible Python source files and initiate deterministic scanning.
- **Investigator:** Examine findings and supporting source evidence.
- **Reproducer:** Assess selected findings in a controlled environment.
- **Fix Engineer:** Propose reviewable changes without modifying the original repository.
- **Verifier:** Execute applicable checks and record their real outcomes.

These are logical modules, not five separately deployed AI services. The orchestrator coordinates their workflow and evidence handoffs.

## 7. Security and Safety Boundaries

- Treat submitted repositories and source files as untrusted input.
- Validate repository URLs and enforce protections against server-side request forgery (SSRF).
- Apply reasonable repository-size, file-count, execution-time, and request limits.
- Do not execute arbitrary submitted repository code or build hooks on the public server.
- Do not install arbitrary repository dependencies during scanning.
- Restrict vulnerability reproduction to controlled fixtures in the MVP.
- Never modify the original repository when preparing a fix proposal.
- Keep credentials and secrets out of frontend code, logs, and reports.
- Treat source comments and other repository content as untrusted data, not instructions.
- Use temporary workspaces with appropriate cleanup.
- Apply suitable API input validation, error handling, CORS restrictions, and rate limits before public deployment.

## 8. Technology Stack

- **Language:** Python
- **Backend:** FastAPI
- **Frontend:** HTML, CSS, and vanilla JavaScript
- **Static analysis:** Bandit
- **Testing:** pytest
- **Version control:** Git and GitHub
- **Hosting:** Free-tier frontend and Python backend hosting, selected after checking current limits.
- **Optional AI assistance:** A model with an available, verified free allowance may be considered. Deterministic behavior must remain available without an AI API.

No paid service is required for the core MVP.

## 9. Out of Scope for the MVP

- Executing arbitrary code from public repositories.
- Automatically merging or pushing fixes to the original repository.
- Claiming that a repository is completely secure.
- Supporting every programming language.
- Deploying multiple independent AI agents as services.
- Requiring paid model APIs, GPU infrastructure, Kubernetes, a message queue, or a vector database.
- Advanced enterprise integrations that are not necessary for the core workflow.

## 10. Acceptance Criteria

The MVP is considered functionally complete when it can:

1. Accept an eligible public GitHub repository URL.
2. Discover and scan eligible Python files within defined limits.
3. Produce findings with source locations and supporting scanner evidence.
4. Investigate a finding without inventing evidence.
5. Reproduce the controlled broken-access-control example.
6. Produce a reviewable fix proposal without modifying the original repository.
7. Run applicable verification checks and report their actual outcomes.
8. Preserve evidence linking the finding, reproduction, patch, and verification.
9. Display results through a usable web interface.
10. Be deployed at a publicly accessible URL using the selected free-tier services.
11. Document the architecture, security boundaries, setup, demonstration, and limitations.

## 11. Project Principle

SecuritySense must prioritize evidence over claims. A finding is not proof of exploitability, a proposed patch is not proof of a fix, and a passing check is not proof of complete security.