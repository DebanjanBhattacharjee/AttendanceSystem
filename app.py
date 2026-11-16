"""Student Attendance System - Flask + SQLite.

Run:  python app.py   ->  http://127.0.0.1:5000
"""
import os
import sqlite3
from datetime import date
from pathlib import Path

from flask import Flask, flash, g, redirect, render_template, request, url_for

BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "instance" / "attendance.db"

app = Flask(__name__)
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "dev-only-change-me")


# ---------- Database helpers ----------
def get_db():
    if "db" not in g:
        g.db = sqlite3.connect(DB_PATH)
        g.db.row_factory = sqlite3.Row
        g.db.execute("PRAGMA foreign_keys = ON")
    return g.db


@app.teardown_appcontext
def close_db(_exc):
    db = g.pop("db", None)
    if db is not None:
        db.close()


def init_db():
    DB_PATH.parent.mkdir(exist_ok=True)
    with sqlite3.connect(DB_PATH) as conn:
        conn.executescript((BASE_DIR / "schema.sql").read_text(encoding="utf-8"))


def parse_date(value, default=None):
    """Return a 'YYYY-MM-DD' string if valid, otherwise the default."""
    try:
        return date.fromisoformat(value).isoformat()
    except (TypeError, ValueError):
        return default


# ---------- Routes ----------
@app.route("/")
def index():
    students = get_db().execute(
        "SELECT id, name, created_at FROM students ORDER BY name"
    ).fetchall()
    return render_template("index.html", students=students)


@app.post("/students")
def add_student():
    name = " ".join(request.form.get("name", "").split())  # trim extra spaces
    if not name:
        flash("Enter a student name.", "error")
    elif len(name) > 80:
        flash("Name must be 80 characters or fewer.", "error")
    else:
        try:
            db = get_db()
            db.execute("INSERT INTO students (name) VALUES (?)", (name,))
            db.commit()
            flash(f"{name} added.", "success")
        except sqlite3.IntegrityError:
            flash(f"{name} is already on the list.", "error")
    return redirect(url_for("index"))


@app.route("/mark", methods=["GET", "POST"])
def mark():
    today = date.today().isoformat()
    selected = parse_date(request.values.get("date"), today)

    if selected > today:
        flash("You can't mark attendance for a future date.", "error")
        return redirect(url_for("mark"))

    db = get_db()

    if request.method == "POST":
        saved = 0
        for s in db.execute("SELECT id FROM students").fetchall():
            status = request.form.get(f"status_{s['id']}")
            if status in ("Present", "Absent"):
                # INSERT OR IGNORE: an existing record is never overwritten
                cur = db.execute(
                    "INSERT OR IGNORE INTO attendance (student_id, date, status) "
                    "VALUES (?, ?, ?)",
                    (s["id"], selected, status),
                )
                saved += cur.rowcount
        db.commit()
        if saved:
            flash(f"Saved attendance for {saved} student(s) on {selected}.", "success")
        else:
            flash("Nothing to save. Pick Present or Absent for at least one student.", "error")
        return redirect(url_for("mark", date=selected))

    rows = db.execute(
        """
        SELECT s.id, s.name, a.status
        FROM students s
        LEFT JOIN attendance a ON a.student_id = s.id AND a.date = ?
        ORDER BY s.name
        """,
        (selected,),
    ).fetchall()
    pending = sum(1 for r in rows if r["status"] is None)
    return render_template("mark.html", rows=rows, selected=selected, today=today, pending=pending)


@app.route("/records")
def records():
    db = get_db()
    students = db.execute("SELECT id, name FROM students ORDER BY name").fetchall()

    date_from = parse_date(request.args.get("date_from"), "")
    date_to = parse_date(request.args.get("date_to"), "")
    student_id = request.args.get("student_id", type=int)

    where, params = [], []
    if date_from:
        where.append("a.date >= ?")
        params.append(date_from)
    if date_to:
        where.append("a.date <= ?")
        params.append(date_to)
    if student_id:
        where.append("a.student_id = ?")
        params.append(student_id)
    clause = ("WHERE " + " AND ".join(where)) if where else ""

    log = db.execute(
        f"""
        SELECT a.date, s.name, a.status
        FROM attendance a JOIN students s ON s.id = a.student_id
        {clause}
        ORDER BY a.date DESC, s.name
        """,
        params,
    ).fetchall()

    summary = db.execute(
        f"""
        SELECT s.name,
               SUM(a.status = 'Present') AS present,
               SUM(a.status = 'Absent')  AS absent,
               COUNT(*)                  AS total,
               ROUND(100.0 * SUM(a.status = 'Present') / COUNT(*), 1) AS percent
        FROM attendance a JOIN students s ON s.id = a.student_id
        {clause}
        GROUP BY s.id
        ORDER BY s.name
        """,
        params,
    ).fetchall()

    return render_template(
        "records.html",
        students=students,
        log=log,
        summary=summary,
        date_from=date_from,
        date_to=date_to,
        student_id=student_id,
    )


init_db()

if __name__ == "__main__":
    app.run(debug=True)
