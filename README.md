
# FraudGuard - Daily Fraud Detection Dashboard

FraudGuard is a Python Flask-based transaction monitoring dashboard that analyses financial transactions and identifies potentially suspicious account activity.

## Features

- Daily transaction monitoring
- Account-wise transaction analysis
- High-value transaction detection
- Daily transaction frequency detection
- Daily amount threshold detection
- Suspicious and safe account classification
- Date-wise filtering
- CSV report export
- Add new transactions through the dashboard

## Technology Stack

- Python
- Flask
- HTML
- CSS
- JavaScript
- REST API
- CSV

## Fraud Detection Rules

| Rule | Condition |
|---|---|
| High Value | Single transaction above ₹50,000 |
| Daily Frequency | 4 or more transactions per account per day |
| Daily Amount | Daily account total above ₹1,00,000 |

These are configurable demonstration rules, not validated banking fraud standards.

## Project Structure

```text
Fraudguard_project/
├── app.py
├── requirements.txt
├── README.md
├── .gitignore
├── templates/
│   └── index.html
└── static/
    ├── style.css
    └── app.js
```

## Installation and Setup

### 1. Clone the repository

```bash
git clone YOUR_GITHUB_REPOSITORY_URL
cd FraudGuard
```

### 2. Create a virtual environment

```bash
py -m venv .venv
```

### 3. Activate it on Windows

```bash
.venv\Scripts\activate
```

### 4. Install dependencies

```bash
py -m pip install -r requirements.txt
```

### 5. Run the application

```bash
py app.py
```

### 6. Open in your browser

```text
http://127.0.0.1:5000
```

## Important Notes

- This is an educational portfolio project.
- It uses demonstration transaction data.
- Transactions are currently stored in memory and reset when the server restarts.
- Detection rules are simple threshold-based rules, not a production-grade fraud detection system.
