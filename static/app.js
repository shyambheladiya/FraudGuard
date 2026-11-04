
const API = "/api";

let currentRecords = [];
let availableDates = [];

const dateFilter = document.getElementById("reportDate");
const searchInput = document.getElementById("search");
const statusFilter = document.getElementById("statusFilter");
const rows = document.getElementById("dailyRows");
const emptyMessage = document.getElementById("emptyMessage");
const message = document.getElementById("message");

function formatCurrency(value) {
    return "₹" + Number(value).toLocaleString("en-IN");
}

function formatDate(value) {
    if (value === "all") return "All Dates";

    const [year, month, day] = value.split("-").map(Number);

    return new Date(year, month - 1, day).toLocaleDateString("en-IN", {
        day: "2-digit",
        month: "short",
        year: "numeric"
    });
}


// Load the daily report from Flask
async function loadDailyReport() {
    try {
        const selectedDate = dateFilter.value || "all";

        const response = await fetch(
            `${API}/daily?date=${encodeURIComponent(selectedDate)}`
        );

        if (!response.ok) {
            throw new Error("Could not load daily report");
        }

        const data = await response.json();

        availableDates = data.available_dates || [];
        currentRecords = data.records || [];

        updateDateOptions();

        document.getElementById("reportTitle").textContent =
            `Fraud Report: ${formatDate(selectedDate)}`;

        document.getElementById("tx").textContent =
            data.totals.transactions;

        document.getElementById("tot").textContent =
            formatCurrency(data.totals.amount);

        document.getElementById("sus").textContent =
            data.totals.suspicious;

        document.getElementById("safe").textContent =
            data.totals.safe;

        renderTable();

    } catch (error) {
        console.error(error);
        message.textContent = error.message;
    }
}


// Populate date selector without losing the selection
function updateDateOptions() {
    const selected = dateFilter.value;

    dateFilter.innerHTML = "";

    const allOption = document.createElement("option");
    allOption.value = "all";
    allOption.textContent = "All Dates";
    dateFilter.appendChild(allOption);

    availableDates.forEach(date => {
        const option = document.createElement("option");
        option.value = date;
        option.textContent = formatDate(date);
        dateFilter.appendChild(option);
    });

    dateFilter.value = selected;
}


// Render the daily account table
function renderTable() {
    const search = searchInput.value.trim().toUpperCase();
    const status = statusFilter.value;

    const filtered = currentRecords.filter(record => {
        const matchesAccount =
            record.account.toUpperCase().includes(search);

        const matchesStatus =
            status === "all" || record.status === status;

        return matchesAccount && matchesStatus;
    });

    rows.replaceChildren();

    filtered.forEach(record => {
        const tr = document.createElement("tr");

        const values = [
            formatDate(record.date),
            record.account,
            record.count,
            formatCurrency(record.total),
            record.flags.length
                ? record.flags.join(", ")
                : "No flags"
        ];

        values.forEach(value => {
            const td = document.createElement("td");
            td.textContent = value;
            tr.appendChild(td);
        });

        const statusCell = document.createElement("td");
        statusCell.textContent = record.status;
        statusCell.className =
            record.status === "Safe" ? "safe" : "suspicious";

        tr.appendChild(statusCell);
        rows.appendChild(tr);
    });

    emptyMessage.hidden = filtered.length !== 0;
}


// Date selection
dateFilter.addEventListener("change", loadDailyReport);

// Search and status filters
searchInput.addEventListener("input", renderTable);
statusFilter.addEventListener("change", renderTable);


// Download selected date's CSV
document.getElementById("downloadCsv").addEventListener("click", () => {
    const selectedDate = dateFilter.value || "all";

    window.location.href =
        `${API}/export/csv?date=${encodeURIComponent(selectedDate)}`;
});


// Add transaction
document.getElementById("addTransaction").addEventListener(
    "submit",
    async event => {
        event.preventDefault();

        const account = document.getElementById("account").value.trim();
        const amount = Number(document.getElementById("amount").value);
        const transactionDate = document.getElementById("date").value;

        message.textContent = "Adding transaction...";

        try {
            const response = await fetch(`${API}/transactions`, {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify({
                    account: account,
                    amount: amount,
                    date: transactionDate
                })
            });

            const result = await response.json();

            if (!response.ok) {
                throw new Error(result.error || "Transaction failed");
            }

            message.textContent = result.message;

            event.target.reset();

            // Refresh date options and report after adding
            await loadDailyReport();

        } catch (error) {
            message.textContent = error.message;
            console.error(error);
        }
    }
);


// Initial dashboard load
loadDailyReport();
