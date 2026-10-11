
"use strict";

const API_BASE = "/api";

const scanForm = document.getElementById("scan-form");
const scanButton = document.getElementById("scan-button");
const scanButtonText = document.getElementById("scan-button-text");
const scanMessage = document.getElementById("scan-message");
const resultsSection = document.getElementById("results-section");
const refreshButton = document.getElementById("refresh-button");
const findingsList = document.getElementById("findings-list");
const investigationsList = document.getElementById("investigations-list");
const rawReport = document.getElementById("raw-report");

let currentScanId = null;
let currentReport = null;

async function apiRequest(path, options = {}) {
    const response = await fetch(`${API_BASE}${path}`, {
        ...options,
        headers: {
            Accept: "application/json",
            ...(options.body ? { "Content-Type": "application/json" } : {}),
            ...options.headers,
        },
    });

    const contentType = response.headers.get("content-type") || "";
    let data = null;

    if (contentType.includes("application/json")) {
        try {
            data = await response.json();
        } catch {
            throw new Error("The server returned an invalid JSON response.");
        }
    }

    if (!response.ok) {
        const detail = data?.detail;
        const message =
            typeof detail === "string"
                ? detail
                : `Request failed with HTTP ${response.status}.`;

        throw new Error(message);
    }

    return data;
}

function setMessage(message, type = "") {
    scanMessage.textContent = message;
    scanMessage.className = `message${type ? ` ${type}` : ""}`;
}

function setApiStatus(status, online) {
    const statusText = document.getElementById("api-status");
    const dot = document.querySelector(".status-dot");

    if (statusText) {
        statusText.textContent = status;
    }

    if (dot) {
        dot.classList.toggle("online", online);
        dot.classList.toggle("offline", !online);
    }
}

async function checkApiStatus() {
    try {
        const result = await apiRequest("/status");

        setApiStatus(
            result?.status === "ready" ? "API online" : "API responding",
            true
        );
    } catch {
        setApiStatus("API unavailable", false);
    }
}

function createElement(tag, className = "", text) {
    const element = document.createElement(tag);

    if (className) {
        element.className = className;
    }

    if (text !== undefined && text !== null) {
        element.textContent = String(text);
    }

    return element;
}

function formatStatus(status) {
    if (typeof status !== "string" || !status) {
        return "unknown";
    }

    return status.replaceAll("_", " ");
}

function statusClass(status) {
    const allowed = ["passed", "failed", "unrun", "inconclusive"];

    return allowed.includes(status)
        ? `status-${status}`
        : "status-inconclusive";
}

function addMetadata(container, label, value) {
    if (value === undefined || value === null || value === "") {
        return;
    }

    container.appendChild(
        createElement("span", "", `${label}: ${value}`)
    );
}

function renderFindings(findings) {
    findingsList.replaceChildren();

    document.getElementById("finding-count-label").textContent =
        `${findings.length} finding${findings.length === 1 ? "" : "s"}`;

    if (!findings.length) {
        findingsList.appendChild(
            createElement(
                "p",
                "muted",
                "No candidate findings were reported by the scanner."
            )
        );
        return;
    }

    for (const finding of findings) {
        const card = createElement("article", "finding-card");
        const topLine = createElement("div", "finding-topline");

        const rule = createElement(
            "span",
            "rule-id",
            finding.rule_id || "Unknown rule"
        );

        const severityValue = String(
            finding.severity || "unknown"
        ).toLowerCase();

        const allowedSeverities = [
            "critical",
            "high",
            "medium",
            "low",
            "unknown",
        ];

        const safeSeverity = allowedSeverities.includes(severityValue)
            ? severityValue
            : "unknown";

        const severity = createElement(
            "span",
            `severity severity-${safeSeverity}`,
            finding.severity || "Unknown severity"
        );

        topLine.append(rule, severity);

        const message = createElement(
            "p",
            "finding-message",
            finding.message || "No finding message provided."
        );

        const metadata = createElement("div", "metadata");

        addMetadata(metadata, "Tool", finding.tool);
        addMetadata(metadata, "Confidence", finding.confidence);
        addMetadata(metadata, "File", finding.file);
        addMetadata(metadata, "Line", finding.line);

        card.append(topLine, message, metadata);

        if (finding.code) {
            card.appendChild(
                createElement("code", "source-code", finding.code)
            );
        }

        findingsList.appendChild(card);
    }
}

function renderInvestigations(investigations) {
    investigationsList.replaceChildren();

    if (!investigations.length) {
        investigationsList.appendChild(
            createElement(
                "p",
                "muted",
                "No investigation records are available."
            )
        );
        return;
    }

    for (const investigation of investigations) {
        const card = createElement("article", "investigation-card");
        const finding = investigation.finding || {};

        const title = createElement(
            "h3",
            "",
            `${finding.rule_id || "Finding"} — ${finding.file || "Unknown file"
            }`
        );

        card.appendChild(title);

        const status = investigation.investigation_status || "unknown";

        const statusPill = createElement(
            "span",
            `status-pill ${statusClass(status)}`,
            formatStatus(status)
        );

        card.appendChild(statusPill);

        const assessment =
            investigation.assessment || investigation.summary;

        if (assessment) {
            card.appendChild(createElement("p", "", assessment));
        }

        const evidence = Array.isArray(investigation.evidence)
            ? investigation.evidence
            : [];

        if (evidence.length) {
            card.appendChild(
                createElement("p", "", "Collected evidence:")
            );

            const list = document.createElement("ul");

            for (const item of evidence) {
                const evidenceText =
                    typeof item === "string"
                        ? item
                        : JSON.stringify(item);

                list.appendChild(createElement("li", "", evidenceText));
            }

            card.appendChild(list);
        }

        investigationsList.appendChild(card);
    }
}

function renderProofLoop(report) {
    const findings = Array.isArray(report.findings)
        ? report.findings
        : [];

    const investigations = Array.isArray(report.investigations)
        ? report.investigations
        : [];

    const stages = [
        [
            "proof-find",
            findings.length
                ? "Findings detected"
                : "No findings reported",
        ],
        [
            "proof-investigate",
            `${report.investigations_completed ?? investigations.length} completed`,
        ],
        [
            "proof-reproduce",
            formatStatus(report.reproduction_status || "unrun"),
        ],
        [
            "proof-verify",
            `Demo fix: ${formatStatus(
                report.fix_status || "unrun"
            )} · Verify: ${formatStatus(
                report.verification_status || "unrun"
            )}`,
        ],
    ];

    for (const [id, value] of stages) {
        const element = document.getElementById(id);

        if (element) {
            element.textContent = value;
        }
    }

    document.getElementById("stat-findings").textContent =
        report.findings_count ?? findings.length;

    document.getElementById("stat-files").textContent =
        `${report.files_scanned ?? 0} / ${report.files_discovered ?? 0}`;

    document.getElementById("stat-investigations").textContent =
        report.investigations_completed ?? investigations.length;

    const status = document.getElementById("stat-status");

    status.textContent = formatStatus(report.scan_status);
    status.className = `status-value ${statusClass(report.scan_status)}`;
}

async function loadScan(scanId) {
    const report = await apiRequest(
        `/scans/${encodeURIComponent(scanId)}`
    );

    if (!report || typeof report !== "object") {
        throw new Error("The server returned an invalid scan report.");
    }

    currentReport = report;
    currentScanId = scanId;

    renderProofLoop(report);

    renderFindings(
        Array.isArray(report.findings) ? report.findings : []
    );

    renderInvestigations(
        Array.isArray(report.investigations)
            ? report.investigations
            : []
    );

    rawReport.textContent = JSON.stringify(report, null, 2);
    resultsSection.hidden = false;
    resultsSection.scrollIntoView({
        behavior: "smooth",
        block: "start",
    });
}

scanForm.addEventListener("submit", async (event) => {
    event.preventDefault();

    scanButton.disabled = true;
    scanButtonText.textContent = "Analysis running...";

    setMessage(
        "Running the configured demonstration scan. Please wait."
    );

    try {
        const payload = {
            workspace_name: document.getElementById("workspace").value,
            max_files: Number(
                document.getElementById("max-files").value
            ),
            context_lines: Number(
                document.getElementById("context-lines").value
            ),
        };

        const created = await apiRequest("/scans", {
            method: "POST",
            body: JSON.stringify(payload),
        });

        if (!created?.scan_id) {
            throw new Error("The server did not return a scan ID.");
        }

        await loadScan(created.scan_id);

        setMessage(
            `Scan finished: ${formatStatus(
                created.scan_status
            )}. ${created.findings_count} finding(s) reported.`,
            "success"
        );
    } catch (error) {
        setMessage(
            error.message || "The scan could not be completed.",
            "error"
        );
    } finally {
        scanButton.disabled = false;
        scanButtonText.textContent = "Run security analysis";
    }
});

refreshButton.addEventListener("click", async () => {
    if (!currentScanId) {
        setMessage("Run a scan before refreshing results.", "error");
        return;
    }

    refreshButton.disabled = true;

    try {
        await loadScan(currentScanId);
        setMessage("Results refreshed.", "success");
    } catch (error) {
        setMessage(
            error.message || "Could not refresh results.",
            "error"
        );
    } finally {
        refreshButton.disabled = false;
    }
});

document
    .getElementById("download-report")
    .addEventListener("click", async () => {
        if (!currentScanId || !currentReport) {
            setMessage(
                "Run a scan before downloading a report.",
                "error"
            );
            return;
        }

        const button = document.getElementById("download-report");
        button.disabled = true;

        try {
            const reportSummary = await apiRequest(
                `/scans/${encodeURIComponent(currentScanId)}/report`
            );

            const exportData = {
                ...reportSummary,
                findings: currentReport.findings || [],
                investigations: currentReport.investigations || [],
                proofloop_records: currentReport.proofloop_records || [],
                controlled_reproduction:
                    currentReport.controlled_reproduction || null,
                fix_workflow: currentReport.fix_workflow || null,
                fix_verified: currentReport.fix_verified === true,
                original_modified:
                    currentReport.original_modified ?? false,
            };

            const blob = new Blob(
                [JSON.stringify(exportData, null, 2)],
                { type: "application/json" }
            );

            const url = URL.createObjectURL(blob);
            const link = document.createElement("a");

            link.href = url;
            link.download =
                `securitysense-report-${currentScanId}.json`;

            document.body.appendChild(link);
            link.click();
            link.remove();

            URL.revokeObjectURL(url);

            setMessage("JSON report prepared for download.", "success");
        } catch (error) {
            setMessage(
                error.message || "Could not export the report.",
                "error"
            );
        } finally {
            button.disabled = false;
        }
    });

checkApiStatus();
