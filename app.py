from flask import Flask, render_template, request, jsonify
import asyncio
import sqlite3

from datetime import datetime
from math import ceil

from database import init_db, DB_PATH
from printer import print_receipt

init_db()

app = Flask(__name__)


# Custom Jinja2 filter: format integer as Indian number (e.g. 1,23,456)
def format_inr(value):
    try:
        value = int(value)
    except (ValueError, TypeError):
        return str(value)
    s = str(value)
    if len(s) <= 3:
        return s
    last3 = s[-3:]
    rest = s[:-3]
    groups = []
    while len(rest) > 2:
        groups.append(rest[-2:])
        rest = rest[:-2]
    if rest:
        groups.append(rest)
    groups.reverse()
    return ",".join(groups) + "," + last3


app.jinja_env.filters["format_inr"] = format_inr

RECEIPT_WIDTH = 32


def format_number(value):
    formatted = f"{value:.2f}"
    return formatted.rstrip("0").rstrip(".")


def fit_text(value, width):
    value = value.strip()
    return value[:width].ljust(width)


def format_item_line(item, qty, rate, amount):
    return (
        f"{fit_text(item, 10)}"
        f"{format_number(qty):>5}"
        f"{format_number(rate):>7}"
        f"{amount:>10}"
    )


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/print", methods=["POST"])
def print_bill():
    customer = request.form.get("customer", "")
    mobile = request.form.get("mobile", "")
    items = request.form.getlist("item[]")
    qtys = request.form.getlist("qty[]")
    rates = request.form.getlist("rate[]")

    total = 0

    bill = ""
    bill += "KAMAL CLOTH HOUSE".center(RECEIPT_WIDTH) + "\n"
    bill += "-" * RECEIPT_WIDTH + "\n"
    bill += f"Date : {datetime.now().strftime('%d-%m-%Y %I:%M %p')}\n"
    bill += f"Customer: {customer}\n\n"
    bill += f"Mobile  : {mobile}\n\n"

    bill += f"{'Item':<10}{'Qty':>5}{'Rate':>7}{'Amount':>10}\n"
    bill += "-" * RECEIPT_WIDTH + "\n"

    for item, qty, rate in zip(items, qtys, rates):
        try:
            qty = float(qty)
            rate = float(rate)

            amount = ceil(qty * rate)
            total += amount

            bill += format_item_line(item, qty, rate, amount) + "\n"
        except ValueError:
            pass

    bill += "-" * RECEIPT_WIDTH + "\n"
    bill += f"{'TOTAL':<22}{total:>10}\n"
    bill += "\nThank You\n"
    bill += "Visit Again\n\n"

    # SAVE BILL TO DATABASE
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute(
        """
        INSERT INTO bills(customer, mobile, bill_text, total, created_at)
        VALUES (?, ?, ?, ?, ?)
        """,
        (
            customer,
            mobile,
            bill,
            total,
            datetime.now().strftime("%d-%m-%Y %H:%M")
        )
    )
    bill_id = cur.lastrowid
    conn.commit()
    conn.close()

    print(f"Bill Saved Successfully. Bill No: {bill_id}")

    try:
        success = asyncio.run(print_receipt(bill))

        if success:
            return render_template(
                "print_success.html",
                bill_id=bill_id,
                bill=bill
            )

        return render_template(
            "print_error.html",
            title="Printer Not Found",
            message="Make sure the MPT-II printer is powered on and Bluetooth is enabled.",
            bill_id=bill_id,
            bill_text=bill,
            back_url="/",
            back_label="Back to Billing"
        )

    except Exception as e:
        return render_template(
            "print_error.html",
            title="Printer Error",
            message=str(e),
            bill_id=bill_id,
            bill_text=bill,
            back_url="/",
            back_label="Back to Billing"
        )


@app.route("/history")
def history():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    cur.execute("SELECT * FROM bills ORDER BY id DESC")
    bills = cur.fetchall()
    conn.close()

    total_revenue = sum(b["total"] for b in bills)

    return render_template(
        "history.html",
        bills=bills,
        total_revenue=format_inr(int(total_revenue)),
        today=datetime.now().strftime("%Y-%m-%d")
    )


@app.route("/customers")
def customers():
    """Return unique customers for autocomplete suggestions."""
    q = request.args.get("q", "").strip()
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    if q:
        cur.execute(
            """
            SELECT DISTINCT customer, mobile
            FROM bills
            WHERE customer LIKE ? OR mobile LIKE ?
            ORDER BY customer ASC
            LIMIT 10
            """,
            (f"%{q}%", f"%{q}%")
        )
    else:
        cur.execute(
            """
            SELECT DISTINCT customer, mobile
            FROM bills
            ORDER BY id DESC
            LIMIT 10
            """
        )
    rows = cur.fetchall()
    conn.close()
    return jsonify([{"customer": r["customer"], "mobile": r["mobile"]} for r in rows])


@app.route("/revenue")
def daily_revenue():
    date_str = request.args.get("date", "")
    if not date_str:
        return jsonify({"error": "date required"}), 400

    try:
        # date_str is YYYY-MM-DD; bills are stored as DD-MM-YYYY HH:MM
        dt = datetime.strptime(date_str, "%Y-%m-%d")
        date_prefix = dt.strftime("%d-%m-%Y")
        display = dt.strftime("%d %b %Y")
    except ValueError:
        return jsonify({"error": "invalid date"}), 400

    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    cur.execute(
        "SELECT total FROM bills WHERE created_at LIKE ?",
        (date_prefix + "%",)
    )
    rows = cur.fetchall()
    conn.close()

    total = sum(r["total"] for r in rows)
    return jsonify({
        "date": date_str,
        "date_display": display,
        "total": int(total),
        "count": len(rows)
    })


@app.route("/reprint/<int:bill_id>")
def reprint_bill(bill_id):
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    cur.execute("SELECT bill_text FROM bills WHERE id = ?", (bill_id,))
    bill = cur.fetchone()
    conn.close()

    if not bill:
        return render_template(
            "print_error.html",
            title="Bill Not Found",
            message=f"No bill found with ID #{bill_id}.",
            back_url="/history",
            back_label="Back to History"
        ), 404

    try:
        success = asyncio.run(print_receipt(bill["bill_text"]))

        if success:
            return render_template(
                "print_success.html",
                bill_id=bill_id,
                bill=bill["bill_text"]
            )

        return render_template(
            "print_error.html",
            title="Printer Not Found",
            message="Make sure the MPT-II printer is powered on and Bluetooth is enabled.",
            bill_id=bill_id,
            bill_text=bill["bill_text"],
            back_url="/history",
            back_label="Back to History"
        )

    except Exception as e:
        return render_template(
            "print_error.html",
            title="Printer Error",
            message=str(e),
            bill_id=bill_id,
            bill_text=bill["bill_text"],
            back_url="/history",
            back_label="Back to History"
        )

if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=8000,
        debug=True
    )
