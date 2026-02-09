document.addEventListener("DOMContentLoaded", () => {
    const form = document.getElementById("loanForm");
    const resultDiv = document.getElementById("result");

    form.addEventListener("submit", async (event) => {
        event.preventDefault(); // 🚨 prevent page reload

        // Read values
        const payload = {
            aadhar_number: document.getElementById("aadhar").value.trim(),
            pan_number: document.getElementById("pan").value.trim(),
            company: document.getElementById("company").value.trim(),
            experience_years: parseInt(
                document.getElementById("experience").value,
                10
            )
        };

        // Reset UI
        resultDiv.className = "result hidden";
        resultDiv.innerHTML = "";

        try {
            const response = await fetch("/loan/apply", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify(payload)
            });

            const data = await response.json();

            if (!response.ok) {
                throw data;
            }

            // SUCCESS UI
            resultDiv.className = "result success";
            resultDiv.innerHTML = `
                <strong>Decision:</strong> ${data.decision}<br/>
                <strong>Risk Score:</strong> ${data.risk_score}<br/>
                <strong>Monthly Income:</strong> ₹${data.monthly_income}
            `;
            resultDiv.classList.remove("hidden");

        } catch (error) {
            // FAILURE UI
            resultDiv.className = "result error";
            resultDiv.innerHTML =
                error?.detail?.reason || "Loan verification failed";
            resultDiv.classList.remove("hidden");
        }
    });
});
