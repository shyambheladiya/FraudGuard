
from flask import Flask, render_template, jsonify, request, Response
from datetime import date
import csv
import io
import math

app = Flask(__name__)

HIGH_VALUE_LIMIT = 50000
DAILY_TRANSACTION_LIMIT = 4
DAILY_AMOUNT_LIMIT = 100000

transactions = [
    {"account": "A101", "amount": 5000, "date": "2026-11-04"},
    {"account": "A102", "amount": 70000, "date": "2026-11-04"},
    {"account": "A101", "amount": 3000, "date": "2026-11-04"},
    {"account": "A103", "amount": 2000, "date": "2026-11-03"},
    {"account": "A101", "amount": 4000, "date": "2026-11-04"},
    {"account": "A102", "amount": 1500, "date": "2026-11-04"},
    {"account": "A101", "amount": 90000, "date": "2026-11-04"},
    {"account": "A103", "amount": 2000, "date": "2026-11-03"},
    {"account": "A103", "amount": 2000, "date": "2026-11-04"},
    {"account": "A103", "amount": 2000, "date": "2026-11-04"},
    {"account": "A104", "amount": 4000, "date": "2026-11-04"},
]


def analyse_transactions(rows):
    accounts = {}

    for transaction in rows:
        account = transaction["account"]
        amount = transaction["amount"]
        transaction_date = transaction["date"]

        if account not in accounts:
            accounts[account] = {
                "account": account,
                "count": 0,
                "total": 0,
                "flags": [],
                "daily_activity": {}
            }

        item = accounts[account]
        item["count"] += 1
        item["total"] += amount

        if transaction_date not in item["daily_activity"]:
            item["daily_activity"][transaction_date] = {
                "count": 0,
                "total": 0
            }

        daily = item["daily_activity"][transaction_date]
        daily["count"] += 1
        daily["total"] += amount

        if amount > HIGH_VALUE_LIMIT:
            if "High Value" not in item["flags"]:
                item["flags"].append("High Value")

    for item in accounts.values():
        for daily in item["daily_activity"].values():
            if daily["count"] >= DAILY_TRANSACTION_LIMIT:
                if "Daily Frequency" not in item["flags"]:
                    item["flags"].append("Daily Frequency")

            if daily["total"] > DAILY_AMOUNT_LIMIT:
                if "Daily Amount Limit" not in item["flags"]:
                    item["flags"].append("Daily Amount Limit")

        item["max_daily_count"] = max(
            (d["count"] for d in item["daily_activity"].values()),
            default=0
        )

        item["max_daily_total"] = max(
            (d["total"] for d in item["daily_activity"].values()),
            default=0
        )

        item["status"] = (
            "Suspicious" if item["flags"] else "Safe"
        )

    return list(accounts.values())


def generate_daily_report(selected_date=None):
    grouped = {}

    for transaction in transactions:
        transaction_date = transaction["date"]

        if selected_date and transaction_date != selected_date:
            continue

        key = (transaction_date, transaction["account"])

        if key not in grouped:
            grouped[key] = {
                "date": transaction_date,
                "account": transaction["account"],
                "count": 0,
                "total": 0,
                "flags": []
            }

        grouped[key]["count"] += 1
        grouped[key]["total"] += transaction["amount"]

        if transaction["amount"] > HIGH_VALUE_LIMIT:
            if "High Value" not in grouped[key]["flags"]:
                grouped[key]["flags"].append("High Value")

    records = list(grouped.values())

    for item in records:
        if item["count"] >= DAILY_TRANSACTION_LIMIT:
            item["flags"].append("Daily Frequency")

        if item["total"] > DAILY_AMOUNT_LIMIT:
            item["flags"].append("Daily Amount Limit")

        item["status"] = (
            "Suspicious" if item["flags"] else "Safe"
        )

    records.sort(key=lambda x: (x["date"], x["account"]), reverse=True)

    return records


def valid_date(value):
    if not isinstance(value, str):
        return False

    try:
        return date.fromisoformat(value).isoformat() == value
    except ValueError:
        return False


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/api/summary")
def summary():
    accounts = analyse_transactions(transactions)

    return jsonify({
        "accounts": len(accounts),
        "transaction_count": len(transactions),
        "total_amount": sum(t["amount"] for t in transactions),
        "suspicious_count": sum(
            1 for a in accounts if a["status"] == "Suspicious"
        )
    })


@app.route("/api/transactions", methods=["GET"])
def get_transactions():
    return jsonify({
        "transactions": transactions,
        "accounts": analyse_transactions(transactions)
    })


@app.route("/api/transactions", methods=["POST"])
def add_transaction():
    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return jsonify({"error": "Invalid request data"}), 400

    account = str(data.get("account", "")).strip().upper()

    if not account or len(account) > 30:
        return jsonify({"error": "Enter a valid account ID"}), 400

    try:
        amount = float(data.get("amount"))
    except (TypeError, ValueError):
        return jsonify({"error": "Invalid amount"}), 400

    if not math.isfinite(amount) or amount <= 0:
        return jsonify({"error": "Amount must be greater than zero"}), 400

    transaction_date = data.get("date") or date.today().isoformat()

    if not valid_date(transaction_date):
        return jsonify({"error": "Invalid date. Use YYYY-MM-DD"}), 400

    new_transaction = {
        "account": account,
        "amount": amount,
        "date": transaction_date
    }

    transactions.append(new_transaction)

    return jsonify({
        "message": "Transaction added successfully",
        "transaction": new_transaction
    }), 201


@app.route("/api/daily")
def daily_report():
    selected_date = request.args.get("date", "all")

    if selected_date != "all" and not valid_date(selected_date):
        return jsonify({"error": "Invalid date filter"}), 400

    dates = sorted(
        {t["date"] for t in transactions},
        reverse=True
    )

    records = generate_daily_report(
        None if selected_date == "all" else selected_date
    )

    return jsonify({
        "selected_date": selected_date,
        "available_dates": dates,
        "records": records,
        "totals": {
            "transactions": sum(r["count"] for r in records),
            "amount": sum(r["total"] for r in records),
            "suspicious": sum(
                1 for r in records if r["status"] == "Suspicious"
            ),
            "safe": sum(
                1 for r in records if r["status"] == "Safe"
            )
        }
    })


@app.route("/api/export/csv")
def export_csv():
    selected_date = request.args.get("date", "all")

    if selected_date != "all" and not valid_date(selected_date):
        return jsonify({"error": "Invalid date filter"}), 400

    records = generate_daily_report(
        None if selected_date == "all" else selected_date
    )

    output = io.StringIO()
    writer = csv.writer(output)

    writer.writerow([
        "Date",
        "Account",
        "Daily Transactions",
        "Daily Amount",
        "Detection Flags",
        "Status"
    ])

    for item in records:
        writer.writerow([
            item["date"],
            item["account"],
            item["count"],
            item["total"],
            ", ".join(item["flags"]) or "No flags",
            item["status"]
        ])

    filename = (
        "fraudguard_all_dates.csv"
        if selected_date == "all"
        else f"fraudguard_{selected_date}.csv"
    )

    return Response(
        "\ufeff" + output.getvalue(),
        mimetype="text/csv",
        headers={
            "Content-Disposition": f'attachment; filename="{filename}"'
        }
    )


if __name__ == "__main__":
    app.run(debug=True)
