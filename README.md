# 🏪 Kamal Billing Pro

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge&logo=python&logoColor=white"/>
  <img src="https://img.shields.io/badge/Flask-2.x-000000?style=for-the-badge&logo=flask&logoColor=white"/>
  <img src="https://img.shields.io/badge/SQLite-Database-003B57?style=for-the-badge&logo=sqlite&logoColor=white"/>
  <img src="https://img.shields.io/badge/Bluetooth-BLE-0082FC?style=for-the-badge&logo=bluetooth&logoColor=white"/>
  <img src="https://img.shields.io/badge/License-MIT-green?style=for-the-badge"/>
</p>

<p align="center">
  A fast, offline-first billing application built for <strong>Kamal Cloth House</strong> — a small retail store.<br>
  Create itemized bills, print receipts wirelessly on a Bluetooth thermal printer, and track daily revenue — all from a clean web interface running locally.
</p>

---

## ✨ Features

| Feature | Description |
|---|---|
| 🧾 **Bill Creation** | Add customer name, phone number, and unlimited line items with auto-calculated totals |
| 🖨️ **Wireless Printing** | Prints formatted ESC/POS receipts via Bluetooth to an MPT-II thermal printer |
| 💾 **Auto-Save** | Every bill is saved to a local SQLite database the moment it's created |
| 🔄 **Retry Printing** | If a print fails, retry with one click — no need to re-enter any details |
| 📋 **Bill History** | Browse all past bills with customer info, amount, and date |
| 💰 **Daily Revenue** | Pick any date to instantly see total sales and bill count for that day |
| 📱 **Responsive UI** | Clean, professional interface that works on desktop and tablet |

---

## 📸 Screenshots

> _Coming soon_

---

## 🛠️ Tech Stack

- **Backend** — Python, Flask
- **Database** — SQLite (via `sqlite3`)
- **Bluetooth** — [Bleak](https://github.com/hbldh/bleak) (BLE)
- **Receipt Printing** — ESC/POS commands + PIL for bitmap heading
- **Frontend** — Jinja2 templates, vanilla HTML / CSS / JS (no framework)

---

## 🖨️ Printer Compatibility

This app is built and tested with the **MPT-II Bluetooth thermal printer**.

The printer is discovered by Bluetooth name (`MPT-II`) using BLE scanning. Make sure:
- The printer is **powered on**
- **Bluetooth is enabled** on your machine
- On **macOS**, Terminal (or your Python runner) has **Bluetooth permission** granted under `System Settings → Privacy & Security → Bluetooth`

---

## 🚀 Getting Started

### 1. Clone the repository

```bash
git clone https://github.com/shreyjain2003/Kamal-Billing-Pro.git
cd Kamal-Billing-Pro
```

### 2. Create a virtual environment

```bash
python3 -m venv venv
source venv/bin/activate        # macOS / Linux
venv\Scripts\activate           # Windows
```

### 3. Install dependencies

```bash
pip install flask bleak pillow
```

### 4. Run the app

```bash
python app.py
```

Open your browser and go to → **http://localhost:8000**

---

## 📁 Project Structure

```
Kamal-Billing-Pro/
│
├── app.py              # Flask app — all routes and business logic
├── database.py         # DB initialisation (creates bills table)
├── printer.py          # Bluetooth BLE print logic (Bleak + ESC/POS)
├── models.py           # SQLAlchemy model definitions
│
├── templates/
│   ├── base.html           # Shared navbar + layout
│   ├── index.html          # New bill form
│   ├── history.html        # Bill history + daily revenue lookup
│   ├── print_success.html  # Receipt preview after successful print
│   └── print_error.html    # Error page with retry option
│
├── static/
│   └── style.css       # Global stylesheet
│
├── receipts/           # (gitignored) Generated receipt files
├── billing.db          # (gitignored) Local SQLite database
└── README.md
```

---

## 🔄 Bill Workflow

```
Fill in customer + items
        ↓
  Submit the form
        ↓
  Bill saved to DB  ←─── Always happens first
        ↓
  Send to printer
        ↓
  ✅ Success → Show receipt preview
  ❌ Failure → Show error + "Try Again" button (bill is already saved)
```

---

## 💰 Daily Revenue

On the History page, click **"👁️ Check Revenue"** to expand the revenue panel.  
Select any date to see:
- Total revenue (₹) for that day
- Number of bills created

No page reload — fetched live via `/revenue?date=YYYY-MM-DD`.

---

## 📄 License

This project is licensed under the [MIT License](LICENSE).

---

<p align="center">Built with ❤️ for Kamal Cloth House</p>
