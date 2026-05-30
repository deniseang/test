from flask import Flask, render_template, request, jsonify, redirect, url_for
import sqlite3
import json
from datetime import date, datetime, timedelta
import os

app = Flask(__name__)
DB_PATH = os.path.join(os.path.dirname(__file__), "data.db")


def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db()
    c = conn.cursor()

    c.executescript("""
        CREATE TABLE IF NOT EXISTS chores (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            points INTEGER NOT NULL DEFAULT 10,
            earns_allowance INTEGER NOT NULL DEFAULT 1,
            active INTEGER NOT NULL DEFAULT 1
        );

        CREATE TABLE IF NOT EXISTS accomplishments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            points INTEGER NOT NULL DEFAULT 20,
            active INTEGER NOT NULL DEFAULT 1
        );

        CREATE TABLE IF NOT EXISTS privileges (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            description TEXT,
            cost INTEGER NOT NULL DEFAULT 20,
            has_duration INTEGER NOT NULL DEFAULT 0,
            active INTEGER NOT NULL DEFAULT 1
        );

        CREATE TABLE IF NOT EXISTS daily_log (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            log_date TEXT NOT NULL,
            item_type TEXT NOT NULL,
            item_id INTEGER NOT NULL,
            item_name TEXT NOT NULL,
            points INTEGER NOT NULL,
            notes TEXT,
            created_at TEXT NOT NULL DEFAULT (datetime('now'))
        );

        CREATE TABLE IF NOT EXISTS privilege_awards (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            award_date TEXT NOT NULL,
            privilege_id INTEGER NOT NULL,
            privilege_name TEXT NOT NULL,
            duration_hours REAL,
            cost INTEGER NOT NULL,
            notes TEXT,
            created_at TEXT NOT NULL DEFAULT (datetime('now'))
        );

        CREATE TABLE IF NOT EXISTS penalties (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            penalty_date TEXT NOT NULL,
            reason TEXT NOT NULL,
            points INTEGER NOT NULL,
            notes TEXT,
            created_at TEXT NOT NULL DEFAULT (datetime('now'))
        );

        CREATE TABLE IF NOT EXISTS allowance (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            allowance_date TEXT NOT NULL UNIQUE,
            amount REAL NOT NULL DEFAULT 0,
            paid INTEGER NOT NULL DEFAULT 0,
            notes TEXT
        );
    """)

    # Seed default chores if empty
    if c.execute("SELECT COUNT(*) FROM chores").fetchone()[0] == 0:
        chores = [
            ("Cleaning room", 15, 1),
            ("Cleaning plates", 10, 1),
            ("Clearing dog poop", 20, 1),
            ("Change pee pads", 10, 1),
            ("Doing laundry", 15, 1),
            ("Vacuuming", 15, 1),
            ("Taking out trash", 10, 1),
            ("Washing dishes", 10, 1),
        ]
        c.executemany("INSERT INTO chores (name, points, earns_allowance) VALUES (?, ?, ?)", chores)

    if c.execute("SELECT COUNT(*) FROM accomplishments").fetchone()[0] == 0:
        accomplishments = [
            ("Good grades / test result", 50),
            ("Completed homework on time", 20),
            ("Helped a classmate", 15),
            ("Won a competition", 60),
            ("Read a book", 20),
            ("Extra credit work", 25),
        ]
        c.executemany("INSERT INTO accomplishments (name, points) VALUES (?, ?)", accomplishments)

    if c.execute("SELECT COUNT(*) FROM privileges").fetchone()[0] == 0:
        privileges = [
            ("Mobile phone use", "Screen time on phone", 25, 1),
            ("Watch a movie", "Watch one full movie at home", 30, 0),
            ("YouTube videos", "Watch YouTube videos", 20, 1),
            ("Mobile games", "Play mobile games", 20, 1),
            ("Shopping with friends", "Go shopping with friends", 60, 0),
            ("Movie with friends", "Watch movie at cinema with friends", 70, 0),
            ("Boba tea", "One boba tea treat", 25, 0),
        ]
        c.executemany(
            "INSERT INTO privileges (name, description, cost, has_duration) VALUES (?, ?, ?, ?)",
            privileges,
        )

    conn.commit()
    conn.close()


def get_today():
    return date.today().isoformat()


def get_points_balance(for_date=None):
    conn = get_db()
    c = conn.cursor()
    if for_date is None:
        # All-time balance
        earned = c.execute(
            "SELECT COALESCE(SUM(points), 0) FROM daily_log"
        ).fetchone()[0]
        spent = c.execute(
            "SELECT COALESCE(SUM(cost), 0) FROM privilege_awards"
        ).fetchone()[0]
        deducted = c.execute(
            "SELECT COALESCE(SUM(points), 0) FROM penalties"
        ).fetchone()[0]
    else:
        earned = c.execute(
            "SELECT COALESCE(SUM(points), 0) FROM daily_log WHERE log_date <= ?", (for_date,)
        ).fetchone()[0]
        spent = c.execute(
            "SELECT COALESCE(SUM(cost), 0) FROM privilege_awards WHERE award_date <= ?", (for_date,)
        ).fetchone()[0]
        deducted = c.execute(
            "SELECT COALESCE(SUM(points), 0) FROM penalties WHERE penalty_date <= ?", (for_date,)
        ).fetchone()[0]
    conn.close()
    return earned - spent - deducted


@app.route("/")
def index():
    today = get_today()
    conn = get_db()
    c = conn.cursor()

    chores = c.execute("SELECT * FROM chores WHERE active=1 ORDER BY name").fetchall()
    accomplishments = c.execute("SELECT * FROM accomplishments WHERE active=1 ORDER BY name").fetchall()
    privileges = c.execute("SELECT * FROM privileges WHERE active=1 ORDER BY cost").fetchall()

    today_log = c.execute(
        "SELECT * FROM daily_log WHERE log_date=? ORDER BY created_at DESC", (today,)
    ).fetchall()
    today_penalties = c.execute(
        "SELECT * FROM penalties WHERE penalty_date=? ORDER BY created_at DESC", (today,)
    ).fetchall()
    today_awards = c.execute(
        "SELECT * FROM privilege_awards WHERE award_date=? ORDER BY created_at DESC", (today,)
    ).fetchall()

    # Completed chore/accomplishment IDs today
    completed_ids = {
        "chore": set(),
        "accomplishment": set(),
    }
    for row in today_log:
        completed_ids[row["item_type"]].add(row["item_id"])

    # Allowance
    allowance_row = c.execute(
        "SELECT * FROM allowance WHERE allowance_date=?", (today,)
    ).fetchone()

    conn.close()

    points_balance = get_points_balance()
    today_points = sum(r["points"] for r in today_log) - sum(r["points"] for r in today_penalties)

    return render_template(
        "index.html",
        today=today,
        chores=chores,
        accomplishments=accomplishments,
        privileges=privileges,
        today_log=today_log,
        today_penalties=today_penalties,
        today_awards=today_awards,
        completed_ids=completed_ids,
        points_balance=points_balance,
        today_points=today_points,
        allowance=allowance_row,
    )


@app.route("/log_item", methods=["POST"])
def log_item():
    data = request.json
    today = get_today()
    conn = get_db()
    c = conn.cursor()

    item_type = data["type"]  # "chore" or "accomplishment"
    item_id = data["id"]
    notes = data.get("notes", "")

    if item_type == "chore":
        row = c.execute("SELECT * FROM chores WHERE id=?", (item_id,)).fetchone()
    else:
        row = c.execute("SELECT * FROM accomplishments WHERE id=?", (item_id,)).fetchone()

    if not row:
        conn.close()
        return jsonify({"error": "Item not found"}), 404

    # Check if already logged today
    existing = c.execute(
        "SELECT id FROM daily_log WHERE log_date=? AND item_type=? AND item_id=?",
        (today, item_type, item_id),
    ).fetchone()

    if existing:
        conn.close()
        return jsonify({"error": "Already logged today"}), 400

    c.execute(
        "INSERT INTO daily_log (log_date, item_type, item_id, item_name, points, notes) VALUES (?, ?, ?, ?, ?, ?)",
        (today, item_type, item_id, row["name"], row["points"], notes),
    )

    # Auto-calculate allowance based on chore completions
    if item_type == "chore":
        chore_count = c.execute(
            "SELECT COUNT(*) FROM daily_log WHERE log_date=? AND item_type='chore'", (today,)
        ).fetchone()[0] + 1  # +1 for the one we just inserted (not committed yet, use +1)
        # $10 if at least 1 chore done (full $10 for completing any chores — split equally concept)
        # Actually give $10 fixed if they do chores today (store once)
        existing_allowance = c.execute(
            "SELECT id FROM allowance WHERE allowance_date=?", (today,)
        ).fetchone()
        if not existing_allowance:
            c.execute(
                "INSERT INTO allowance (allowance_date, amount) VALUES (?, ?)", (today, 10.0)
            )

    conn.commit()
    conn.close()

    balance = get_points_balance()
    return jsonify({"success": True, "points": row["points"], "balance": balance})


@app.route("/unlog_item", methods=["POST"])
def unlog_item():
    data = request.json
    today = get_today()
    conn = get_db()
    c = conn.cursor()

    item_type = data["type"]
    item_id = data["id"]

    c.execute(
        "DELETE FROM daily_log WHERE log_date=? AND item_type=? AND item_id=?",
        (today, item_type, item_id),
    )

    # If no more chores today, remove allowance
    if item_type == "chore":
        remaining = c.execute(
            "SELECT COUNT(*) FROM daily_log WHERE log_date=? AND item_type='chore'", (today,)
        ).fetchone()[0]
        if remaining == 0:
            c.execute("DELETE FROM allowance WHERE allowance_date=? AND paid=0", (today,))

    conn.commit()
    conn.close()
    balance = get_points_balance()
    return jsonify({"success": True, "balance": balance})


@app.route("/award_privilege", methods=["POST"])
def award_privilege():
    data = request.json
    today = get_today()
    conn = get_db()
    c = conn.cursor()

    priv_id = data["id"]
    duration = data.get("duration")
    notes = data.get("notes", "")

    priv = c.execute("SELECT * FROM privileges WHERE id=?", (priv_id,)).fetchone()
    if not priv:
        conn.close()
        return jsonify({"error": "Privilege not found"}), 404

    balance = get_points_balance()
    cost = priv["cost"]
    if duration and priv["has_duration"]:
        cost = int(priv["cost"] * float(duration))

    if balance < cost:
        conn.close()
        return jsonify({"error": f"Not enough points (need {cost}, have {balance})"}), 400

    c.execute(
        "INSERT INTO privilege_awards (award_date, privilege_id, privilege_name, duration_hours, cost, notes) VALUES (?, ?, ?, ?, ?, ?)",
        (today, priv_id, priv["name"], duration, cost, notes),
    )
    conn.commit()
    conn.close()

    balance = get_points_balance()
    return jsonify({"success": True, "cost": cost, "balance": balance})


@app.route("/add_penalty", methods=["POST"])
def add_penalty():
    data = request.json
    today = get_today()
    conn = get_db()
    c = conn.cursor()

    reason = data.get("reason", "").strip()
    points = int(data.get("points", 10))
    notes = data.get("notes", "")

    if not reason:
        conn.close()
        return jsonify({"error": "Reason is required"}), 400

    c.execute(
        "INSERT INTO penalties (penalty_date, reason, points, notes) VALUES (?, ?, ?, ?)",
        (today, reason, points, notes),
    )
    conn.commit()
    conn.close()

    balance = get_points_balance()
    return jsonify({"success": True, "balance": balance})


@app.route("/mark_allowance_paid", methods=["POST"])
def mark_allowance_paid():
    data = request.json
    today = data.get("date", get_today())
    conn = get_db()
    c = conn.cursor()
    c.execute("UPDATE allowance SET paid=1 WHERE allowance_date=?", (today,))
    conn.commit()
    conn.close()
    return jsonify({"success": True})


@app.route("/history")
def history():
    conn = get_db()
    c = conn.cursor()

    logs = c.execute(
        "SELECT * FROM daily_log ORDER BY log_date DESC, created_at DESC LIMIT 100"
    ).fetchall()
    penalties = c.execute(
        "SELECT * FROM penalties ORDER BY penalty_date DESC, created_at DESC LIMIT 50"
    ).fetchall()
    awards = c.execute(
        "SELECT * FROM privilege_awards ORDER BY award_date DESC, created_at DESC LIMIT 50"
    ).fetchall()
    allowances = c.execute(
        "SELECT * FROM allowance ORDER BY allowance_date DESC LIMIT 30"
    ).fetchall()

    conn.close()
    balance = get_points_balance()

    return render_template(
        "history.html",
        logs=logs,
        penalties=penalties,
        awards=awards,
        allowances=allowances,
        balance=balance,
    )


@app.route("/settings")
def settings():
    conn = get_db()
    c = conn.cursor()
    chores = c.execute("SELECT * FROM chores ORDER BY name").fetchall()
    accomplishments = c.execute("SELECT * FROM accomplishments ORDER BY name").fetchall()
    privileges = c.execute("SELECT * FROM privileges ORDER BY cost").fetchall()
    conn.close()
    return render_template("settings.html", chores=chores, accomplishments=accomplishments, privileges=privileges)


@app.route("/add_chore", methods=["POST"])
def add_chore():
    data = request.json
    conn = get_db()
    c = conn.cursor()
    c.execute(
        "INSERT INTO chores (name, points, earns_allowance) VALUES (?, ?, ?)",
        (data["name"], int(data["points"]), 1),
    )
    conn.commit()
    new_id = c.lastrowid
    conn.close()
    return jsonify({"success": True, "id": new_id})


@app.route("/add_accomplishment", methods=["POST"])
def add_accomplishment():
    data = request.json
    conn = get_db()
    c = conn.cursor()
    c.execute(
        "INSERT INTO accomplishments (name, points) VALUES (?, ?)",
        (data["name"], int(data["points"])),
    )
    conn.commit()
    new_id = c.lastrowid
    conn.close()
    return jsonify({"success": True, "id": new_id})


@app.route("/update_privilege", methods=["POST"])
def update_privilege():
    data = request.json
    conn = get_db()
    c = conn.cursor()
    c.execute(
        "UPDATE privileges SET cost=? WHERE id=?",
        (int(data["cost"]), int(data["id"])),
    )
    conn.commit()
    conn.close()
    return jsonify({"success": True})


@app.route("/toggle_active", methods=["POST"])
def toggle_active():
    data = request.json
    table = {"chore": "chores", "accomplishment": "accomplishments", "privilege": "privileges"}[data["type"]]
    conn = get_db()
    c = conn.cursor()
    c.execute(f"UPDATE {table} SET active = 1 - active WHERE id=?", (data["id"],))
    conn.commit()
    conn.close()
    return jsonify({"success": True})


@app.route("/api/stats")
def api_stats():
    conn = get_db()
    c = conn.cursor()
    today = get_today()
    week_ago = (date.today() - timedelta(days=6)).isoformat()

    total_points_earned = c.execute("SELECT COALESCE(SUM(points),0) FROM daily_log").fetchone()[0]
    total_spent = c.execute("SELECT COALESCE(SUM(cost),0) FROM privilege_awards").fetchone()[0]
    total_deducted = c.execute("SELECT COALESCE(SUM(points),0) FROM penalties").fetchone()[0]
    total_allowance = c.execute("SELECT COALESCE(SUM(amount),0) FROM allowance").fetchone()[0]
    unpaid_allowance = c.execute("SELECT COALESCE(SUM(amount),0) FROM allowance WHERE paid=0").fetchone()[0]

    weekly = c.execute(
        "SELECT log_date, SUM(points) as pts FROM daily_log WHERE log_date >= ? GROUP BY log_date ORDER BY log_date",
        (week_ago,),
    ).fetchall()

    conn.close()
    return jsonify({
        "balance": total_points_earned - total_spent - total_deducted,
        "total_earned": total_points_earned,
        "total_spent": total_spent,
        "total_deducted": total_deducted,
        "total_allowance": total_allowance,
        "unpaid_allowance": unpaid_allowance,
        "weekly": [{"date": r["log_date"], "points": r["pts"]} for r in weekly],
    })


if __name__ == "__main__":
    init_db()
    app.run(debug=True, host="0.0.0.0", port=5000)
