document.addEventListener("DOMContentLoaded", async () => {
    const sessionToken = localStorage.getItem("session_token");
    const userName = localStorage.getItem("user_name") || "User";
    const userRole = localStorage.getItem("user_role") || "customer";
    const canReview = ["admin", "reviewer"].includes(userRole);

    if (!sessionToken) {
        window.location.href = "/";
        return;
    }

    const authHeaders = {
        "X-Session-Token": sessionToken
    };

    const form = document.getElementById("loanForm");
    const resultDiv = document.getElementById("result");
    const loadingDiv = document.getElementById("loading");
    const welcomeText = document.getElementById("welcomeText");
    const historyBody = document.getElementById("historyBody");
    const emptyHistory = document.getElementById("emptyHistory");
    const totalApplications = document.getElementById("totalApplications");
    const latestDecision = document.getElementById("latestDecision");
    const avgRiskScore = document.getElementById("avgRiskScore");
    const pendingReviews = document.getElementById("pendingReviews");
    const operationsAnalytics = document.getElementById("operationsAnalytics");
    const approvalRate = document.getElementById("approvalRate");
    const approvedCount = document.getElementById("approvedCount");
    const rejectedCount = document.getElementById("rejectedCount");
    const avgTurnaround = document.getElementById("avgTurnaround");
    const reviewerPanel = document.getElementById("reviewerPanel");
    const simulatorResult = document.getElementById("simulatorResult");
    const reviewQueue = document.getElementById("reviewQueue");
    const emptyReviewQueue = document.getElementById("emptyReviewQueue");

    const simulatorControls = [
        { id: "simCreditScore", outputId: "simCreditScoreValue", formatter: formatPlain },
        { id: "simIncome", outputId: "simIncomeValue", formatter: formatCurrencyNumber },
        { id: "simLoanAmount", outputId: "simLoanAmountValue", formatter: formatCurrencyNumber },
        { id: "simExperience", outputId: "simExperienceValue", formatter: formatPlain },
        { id: "simExistingLoans", outputId: "simExistingLoansValue", formatter: formatPlain }
    ];

    welcomeText.textContent = `Welcome back, ${userName}`;

    if (canReview) {
        reviewerPanel.classList.remove("hidden");
        operationsAnalytics.classList.remove("hidden");
    } else {
        pendingReviews.textContent = "-";
    }

    simulatorControls.forEach((control) => {
        const input = document.getElementById(control.id);
        const output = document.getElementById(control.outputId);
        output.textContent = control.formatter(input.value);
        input.addEventListener("input", () => {
            output.textContent = control.formatter(input.value);
            runSimulation();
        });
    });

    form.addEventListener("submit", async (event) => {
        event.preventDefault();

        const payload = {
            aadhar_number: document.getElementById("aadhar").value.trim(),
            pan_number: document.getElementById("pan").value.trim().toUpperCase(),
            monthly_income: parseFloat(document.getElementById("income").value),
            experience_years: parseInt(document.getElementById("experience").value, 10),
            loan_amount: parseFloat(document.getElementById("loan_amount").value)
        };

        resultDiv.className = "result hidden";
        resultDiv.innerHTML = "";
        loadingDiv.classList.remove("hidden");

        try {
            const response = await fetch("/loan/apply", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    ...authHeaders
                },
                body: JSON.stringify(payload)
            });

            const data = await response.json();
            loadingDiv.classList.add("hidden");

            if (!response.ok) {
                throw data;
            }

            renderDecision(data);


await loadHistory();
await prefillSimulatorFromHistory();   
runSimulation();                       

if (canReview) {
    await loadReviewQueue();
    await loadReviewAnalytics();
}

form.reset();
        } catch (error) {
            loadingDiv.classList.add("hidden");
            if (isSessionError(error)) {
                logout();
                return;
            }
            renderError(error);
        }
    });

    await loadHistory();

await prefillSimulatorFromHistory(); 

if (canReview) {
    loadReviewQueue();
    loadReviewAnalytics();
}

runSimulation();

    function renderDecision(data) {
        const reasons = data.reasons.length
            ? data.reasons.map((reason) => `<li>${reason}</li>`).join("")
            : "<li>Profile meets all current automated checks.</li>";

        const suggestions = data.improvement_suggestions
            .map((item) => `<li>${item}</li>`)
            .join("");

        resultDiv.className = `result ${data.decision.toLowerCase()}`;
        resultDiv.innerHTML = `
            <div class="result-header">
                <h3>${data.applicant_name}</h3>
                <span class="decision-badge ${data.decision.toLowerCase()}">${data.decision}</span>
            </div>
            <div class="result-grid">
                <div><strong>Risk Score</strong><span>${data.risk_score}</span></div>
                <div><strong>Credit Score</strong><span>${data.credit_score}</span></div>
                <div><strong>Loan Ratio</strong><span>${data.loan_ratio}</span></div>
                <div><strong>Interest Rate</strong><span>${data.interest_rate}%</span></div>
            </div>
            <p class="money-line">Loan Amount: Rs.${Number(data.loan_amount).toLocaleString("en-IN")}</p>
            <p class="money-line">Monthly Income: Rs.${Number(data.monthly_income).toLocaleString("en-IN")}</p>
            <div class="advice-panel">
                <div>
                    <h4>Decision Signals</h4>
                    <ul>${reasons}</ul>
                </div>
                <div>
                    <h4>How To Improve</h4>
                    <ul>${suggestions}</ul>
                </div>
            </div>
        `;
        resultDiv.classList.remove("hidden");
    }

    function renderError(error) {
        let message = "Loan processing failed";

        if (error?.detail) {
            message = typeof error.detail === "string"
                ? error.detail
                : JSON.stringify(error.detail);
        } else if (error?.message) {
            message = error.message;
        }

        resultDiv.className = "result error";
        resultDiv.innerHTML = `<strong>Error:</strong> ${message}`;
        resultDiv.classList.remove("hidden");
    }

    async function loadHistory() {
        try {
            const response = await fetch("/loan/history", {
                headers: authHeaders
            });
            const data = await response.json();

            if (!response.ok) {
                throw data;
            }

            if (data.user?.role && data.user.role !== userRole) {
                localStorage.setItem("user_role", data.user.role);
            }

            renderHistory(data.applications || []);
        } catch (error) {
            if (isSessionError(error)) {
                logout();
                return;
            }
            historyBody.innerHTML = "";
            emptyHistory.textContent = "Unable to load application history right now.";
            emptyHistory.classList.remove("hidden");
        }
    }
async function prefillSimulatorFromHistory() {
    try {
        const response = await fetch("/loan/history", {
            headers: authHeaders
        });

        const data = await response.json();
        if (!response.ok) throw data;

        if (!data.applications || data.applications.length === 0) return;

        // ✅ ALWAYS GET LATEST RECORD
        const last = data.applications.sort(
            (a, b) => new Date(b.created_at) - new Date(a.created_at)
        )[0];

        // ✅ SET VALUES
        document.getElementById("simCreditScore").value = last.credit_score;
        document.getElementById("simIncome").value = last.monthly_income;
        document.getElementById("simLoanAmount").value = last.loan_amount;
        document.getElementById("simExperience").value = last.experience_years;
        document.getElementById("simExistingLoans").value = last.existing_loans;

        // ✅ FORCE UI + SIMULATION UPDATE
        ["simCreditScore","simIncome","simLoanAmount","simExperience","simExistingLoans"]
        .forEach(id => document.getElementById(id).dispatchEvent(new Event("input")));

    } catch (error) {
        console.log("Prefill failed", error);
    }
}



    function renderHistory(applications) {
        historyBody.innerHTML = "";

        if (!applications.length) {
            emptyHistory.textContent = "No applications yet. Submit your first loan request to build your dashboard history.";
            emptyHistory.classList.remove("hidden");
            totalApplications.textContent = "0";
            latestDecision.textContent = "-";
            avgRiskScore.textContent = "-";
            return;
        }

        emptyHistory.classList.add("hidden");

        applications.forEach((application) => {
            const formattedDate = application.created_at
                ? new Date(application.created_at).toLocaleDateString("en-IN")
                : "-";
            const displayedDecision = application.final_decision || application.decision;
            const row = document.createElement("tr");
            row.innerHTML = `
                <td>${application.applicant_name}</td>
                <td>Rs.${Number(application.loan_amount).toLocaleString("en-IN")}</td>
                <td>${application.risk_score}</td>
                <td>
                    <span class="decision-badge ${displayedDecision.toLowerCase()}">${displayedDecision}</span>
                    <div class="table-subline">${formatReviewStatus(application.review_status)}</div>
                </td>
                <td>${formattedDate}</td>
            `;
            historyBody.appendChild(row);
        });

        const riskAverage = Math.round(
            applications.reduce((sum, item) => sum + item.risk_score, 0) / applications.length
        );

        totalApplications.textContent = String(applications.length);
        latestDecision.textContent = applications[0].final_decision || applications[0].decision;
        avgRiskScore.textContent = String(riskAverage);
    }

    async function loadReviewQueue() {
        try {
            const response = await fetch("/review/queue", {
                headers: authHeaders
            });
            const data = await response.json();

            if (!response.ok) {
                throw data;
            }

            renderReviewQueue(data.cases || []);
        } catch (error) {
            if (isSessionError(error)) {
                logout();
                return;
            }
            if (error?.detail === "Reviewer access required") {
                reviewerPanel.classList.add("hidden");
                operationsAnalytics.classList.add("hidden");
                return;
            }
            reviewQueue.innerHTML = "";
            emptyReviewQueue.textContent = "Unable to load manual review queue right now.";
            emptyReviewQueue.classList.remove("hidden");
        }
    }

    function renderReviewQueue(cases) {
        reviewQueue.innerHTML = "";

        const pendingCases = cases.filter((item) => item.review_status === "PENDING_REVIEW");
        pendingReviews.textContent = String(pendingCases.length);

        if (!cases.length) {
            emptyReviewQueue.textContent = "No cases in the manual review queue.";
            emptyReviewQueue.classList.remove("hidden");
            return;
        }

        emptyReviewQueue.classList.add("hidden");

        cases.forEach((item) => {
            const card = document.createElement("div");
            card.className = "review-case";

            const notesSection = item.review_status === "PENDING_REVIEW"
                ? `
                    <textarea id="review-notes-${item.id}" class="review-notes" placeholder="Add reviewer notes and rationale"></textarea>
                    <div class="review-actions">
                        <button class="review-btn approve" data-loan-id="${item.id}" data-decision="APPROVED">Approve</button>
                        <button class="review-btn reject" data-loan-id="${item.id}" data-decision="REJECTED">Reject</button>
                    </div>
                `
                : `
                    <div class="review-summary">
                        <p><strong>Final Decision:</strong> ${item.final_decision || item.decision}</p>
                        <p><strong>Reviewed At:</strong> ${item.reviewed_at ? new Date(item.reviewed_at).toLocaleString("en-IN") : "-"}</p>
                        <p><strong>Notes:</strong> ${item.reviewer_notes || "-"}</p>
                    </div>
                `;

            card.innerHTML = `
                <div class="review-head">
                    <div>
                        <h3>${item.applicant_name}</h3>
                        <p>Application #${item.id}</p>
                    </div>
                    <div class="review-badges">
                        <span class="decision-badge review">${item.decision}</span>
                        <span class="status-pill ${item.review_status.toLowerCase()}">${formatReviewStatus(item.review_status)}</span>
                    </div>
                </div>
                <div class="review-metrics">
                    <div><span>Risk Score</span><strong>${item.risk_score}</strong></div>
                    <div><span>Credit Score</span><strong>${item.credit_score}</strong></div>
                    <div><span>Loan Amount</span><strong>Rs.${Number(item.loan_amount).toLocaleString("en-IN")}</strong></div>
                    <div><span>Loan Ratio</span><strong>${item.loan_ratio}</strong></div>
                </div>
                ${notesSection}
            `;
            reviewQueue.appendChild(card);
        });

        reviewQueue.querySelectorAll(".review-btn").forEach((button) => {
            button.addEventListener("click", async () => {
                const loanId = button.dataset.loanId;
                const finalDecision = button.dataset.decision;
                const notesField = document.getElementById(`review-notes-${loanId}`);
                const reviewerNotes = notesField.value.trim();

                if (reviewerNotes.length < 5) {
                    alert("Please add reviewer notes with at least 5 characters.");
                    return;
                }

                button.disabled = true;

                try {
                    const response = await fetch(`/review/${loanId}/decision`, {
                        method: "POST",
                        headers: {
                            "Content-Type": "application/json",
                            ...authHeaders
                        },
                        body: JSON.stringify({
                            final_decision: finalDecision,
                            reviewer_notes: reviewerNotes
                        })
                    });
                    const data = await response.json();

                    if (!response.ok) {
                        throw data;
                    }

                    await loadHistory();
                    await loadReviewQueue();
                    await loadReviewAnalytics();
                } catch (error) {
                    if (isSessionError(error)) {
                        logout();
                        return;
                    }
                    alert(error.detail || "Unable to save review decision.");
                } finally {
                    button.disabled = false;
                }
            });
        });
    }

    async function loadReviewAnalytics() {
        try {
            const response = await fetch("/review/analytics", {
                headers: authHeaders
            });
            const data = await response.json();

            if (!response.ok) {
                throw data;
            }

            approvalRate.textContent = `${data.approval_rate}%`;
            approvedCount.textContent = String(data.approved_count);
            rejectedCount.textContent = String(data.rejected_count);
            avgTurnaround.textContent = `${data.avg_review_turnaround_hours}h`;
            pendingReviews.textContent = String(data.pending_review_count);
        } catch (error) {
            if (isSessionError(error)) {
                logout();
                return;
            }
            if (error?.detail === "Reviewer access required") {
                operationsAnalytics.classList.add("hidden");
            }
        }
    }

    async function runSimulation() {
        try {
            const payload = {
                credit_score: parseInt(document.getElementById("simCreditScore").value, 10),
                monthly_income: parseFloat(document.getElementById("simIncome").value),
                existing_loans: parseInt(document.getElementById("simExistingLoans").value, 10),
                experience_years: parseInt(document.getElementById("simExperience").value, 10),
                loan_amount: parseFloat(document.getElementById("simLoanAmount").value)
            };

            const response = await fetch("/loan/simulate", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    ...authHeaders
                },
                body: JSON.stringify(payload)
            });
            const data = await response.json();

            if (!response.ok) {
                throw data;
            }

            const whyResult = data.reasons.length
                ? data.reasons.map((reason) => `<li>${reason}</li>`).join("")
                : "<li>Strong profile balance across the major risk checks.</li>";

            simulatorResult.innerHTML = `
                <div class="simulator-topline">
                    <span class="decision-badge ${data.decision.toLowerCase()}">${data.decision}</span>
                    <strong>Risk Score ${data.risk_score}</strong>
                </div>
                <div class="simulator-metrics">
                    <div><span>Loan Ratio</span><strong>${data.loan_ratio}</strong></div>
                    <div><span>Interest Rate</span><strong>${data.interest_rate}%</strong></div>
                    <div><span>Existing Loans</span><strong>${data.existing_loans}</strong></div>
                </div>
                <div class="advice-panel">
                    <div>
                        <h4>Why this result</h4>
                        <ul>${whyResult}</ul>
                    </div>
                    <div>
                        <h4>Best improvements</h4>
                        <ul>${data.improvement_suggestions.map((item) => `<li>${item}</li>`).join("")}</ul>
                    </div>
                </div>
            `;
        } catch (error) {
            if (isSessionError(error)) {
                logout();
                return;
            }
            simulatorResult.innerHTML = `
                <p class="simulator-empty">Simulation is temporarily unavailable.</p>
            `;
        }
    }

    function isSessionError(error) {
        return error?.detail === "Invalid user session" || error?.detail === "Login required";
    }

    function formatCurrencyNumber(value) {
        return Number(value).toLocaleString("en-IN");
    }

    function formatPlain(value) {
        return String(value);
    }

    function formatReviewStatus(status) {
        return String(status || "AUTO_DECIDED").replaceAll("_", " ");
    }
});

async function logout() {
    const sessionToken = localStorage.getItem("session_token");

    if (sessionToken) {
        try {
            await fetch("/auth/logout", {
                method: "POST",
                headers: {
                    "X-Session-Token": sessionToken
                }
            });
        } catch (error) {
            // Best-effort logout only.
        }
    }

    localStorage.removeItem("user_id");
    localStorage.removeItem("user_name");
    localStorage.removeItem("user_role");
    localStorage.removeItem("session_token");
    window.location.href = "/";
}

document.getElementById("contactForm")?.addEventListener("submit", async function(e) {
    e.preventDefault();

    const payload = {
        name: document.getElementById("name").value,
        email: document.getElementById("email").value,
        message: document.getElementById("message").value
    };

    const res = await fetch("/contact", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify(payload)
    });

    const data = await res.json();

    alert(data.message);
    this.reset();
});