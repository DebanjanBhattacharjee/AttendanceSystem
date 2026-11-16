# Student Attendance System

A small web app to add students, mark them Present or Absent for a date, and review the records later.
Saved attendance is **read-only**: there is no edit or delete anywhere, and SQLite triggers block changes even from raw SQL.

**Stack:** Python 3.9+, Flask, SQLite (built into Python), HTML, CSS, JavaScript.

## Run it (VS Code)

```bash
# 1. Create and activate a virtual environment
python -m venv .venv
.venv\Scripts\activate          # Windows
source .venv/bin/activate       # macOS / Linux

# 2. Install dependencies
pip install -r requirements.txt

# 3. Start the app
python app.py
```

Open http://127.0.0.1:5000. In VS Code, press `Ctrl+Shift+P`, choose **Python: Select Interpreter**, and pick the `.venv` one.

## Project structure

```
app.py            Flask routes and database logic
schema.sql        Tables and the read-only triggers
templates/        HTML (Jinja2)
static/css/       Styles
static/js/        Small front-end helpers
instance/         Created on first run, holds attendance.db (ignored by Git)
```

## Push to GitHub

```bash
git init
git add .
git commit -m "Initial commit: student attendance system"
git branch -M main
git remote add origin https://github.com/<your-username>/<repo-name>.git
git push -u origin main
```
