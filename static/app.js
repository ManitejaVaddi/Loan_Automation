document.addEventListener("DOMContentLoaded", () => {
    const form = document.getElementById("loanForm");
    const resultDiv = document.getElementById("result");
    const loadingDiv = document.getElementById("loading");

    form.addEventListener("submit", async (event) => {
        event.preventDefault();

        const payload = {
            aadhar_number: document.getElementById("aadhar").value.trim(),
            pan_number: document.getElementById("pan").value.trim().toUpperCase(),
            monthly_income: parseFloat(
    document.getElementById("income").value
            ),
            experience_years: parseInt(
                document.getElementById("experience").value,
                10
            ),
            loan_amount: parseFloat(
                document.getElementById("loan_amount").value
            )
        };

        // Reset UI
        resultDiv.className = "result hidden";
        resultDiv.innerHTML = "";
        loadingDiv.classList.remove("hidden");

        try {
            const response = await fetch("/loan/apply", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify(payload)
            });

            const data = await response.json();
            loadingDiv.classList.add("hidden");

            if (!response.ok) {
                throw data;
            }

            // ✅ SUCCESS UI (FIXED TEMPLATE STRING)
            resultDiv.className = "result success";

            resultDiv.innerHTML = `
                <h3>Loan Decision: ${data.decision}</h3>
                <p><strong>Risk Score:</strong> ${data.risk_score}</p>
                <p><strong>Loan Amount:</strong> ₹${data.loan_amount}</p>
                <p><strong>Monthly Income:</strong> ₹${data.monthly_income}</p>
                <p><strong>Credit Score:</strong> ${data.credit_score}</p>

                <p><strong>Reasons:</strong></p>
                <ul>
                    ${data.reasons.map(reason => `<li>${reason}</li>`).join("")}
                </ul>
            `;

            resultDiv.classList.remove("hidden");

        } catch (error) {
            loadingDiv.classList.add("hidden");

            resultDiv.className = "result error";

            let message = "Loan processing failed";

            if (error?.detail) {
                message = typeof error.detail === "string"
                    ? error.detail
                    : JSON.stringify(error.detail);
            }
            else if (error?.message) {
    message = error.message;
}

            resultDiv.innerHTML = `<strong>Error:</strong> ${message}`;
            resultDiv.classList.remove("hidden");
        }
    });
});