from flask import Flask, render_template, request, redirect, jsonify
import sqlite3
from datetime import datetime, date, timedelta

app = Flask(__name__)
DATABASE = "fitness.db"

def init_db():
    conn = sqlite3.connect(DATABASE)
    cur = conn.cursor()

    # Check existing columns
    cur.execute("PRAGMA table_info(activities)")
    existing_cols = {row[1] for row in cur.fetchall()}

    if not existing_cols:
        # Fresh install — create table from scratch
        cur.execute("""
        CREATE TABLE activities(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            activity TEXT,
            exercise_type TEXT,
            duration INTEGER,
            calories INTEGER,
            steps INTEGER,
            date TEXT DEFAULT (date('now'))
        )
        """)
    else:
        # Migrate: rename old 'workout' column to 'activity' if needed
        if "workout" in existing_cols and "activity" not in existing_cols:
            cur.execute("""
                CREATE TABLE activities_new(
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    activity TEXT,
                    exercise_type TEXT DEFAULT 'Other',
                    duration INTEGER,
                    calories INTEGER,
                    steps INTEGER,
                    date TEXT DEFAULT (date('now'))
                )
            """)
            cur.execute("""
                INSERT INTO activities_new (id, activity, duration, calories, steps)
                SELECT id, workout, duration, calories, steps FROM activities
            """)
            cur.execute("DROP TABLE activities")
            cur.execute("ALTER TABLE activities_new RENAME TO activities")
            existing_cols = {"id", "activity", "exercise_type", "duration", "calories", "steps", "date"}

        # Migrate: add missing columns one by one
        if "activity" not in existing_cols:
            try:
                cur.execute("ALTER TABLE activities ADD COLUMN activity TEXT")
            except Exception:
                pass
        if "date" not in existing_cols:
            try:
                cur.execute("ALTER TABLE activities ADD COLUMN date TEXT DEFAULT (date('now'))")
            except Exception:
                pass
        if "exercise_type" not in existing_cols:
            try:
                cur.execute("ALTER TABLE activities ADD COLUMN exercise_type TEXT DEFAULT 'Other'")
            except Exception:
                pass

    conn.commit()
    conn.close()

init_db()

def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


@app.route("/")
def dashboard():
    conn = get_db()
    today = date.today().isoformat()
    week_start = (date.today() - timedelta(days=date.today().weekday())).isoformat()

    # Today's stats
    today_data = conn.execute(
        "SELECT * FROM activities WHERE date=?", (today,)
    ).fetchall()

    # Weekly stats
    week_data = conn.execute(
        "SELECT * FROM activities WHERE date>=?", (week_start,)
    ).fetchall()

    # All activities for recent list
    all_data = conn.execute(
        "SELECT * FROM activities ORDER BY date DESC, id DESC LIMIT 10"
    ).fetchall()

    # Weekly steps per day for chart
    weekly_steps = []
    weekly_labels = []
    for i in range(6, -1, -1):
        d = (date.today() - timedelta(days=i)).isoformat()
        row = conn.execute(
            "SELECT SUM(steps) as s FROM activities WHERE date=?", (d,)
        ).fetchone()
        weekly_steps.append(row["s"] or 0)
        weekly_labels.append((date.today() - timedelta(days=i)).strftime("%a"))

    # Activity type breakdown for chart
    type_data = conn.execute(
        "SELECT exercise_type, COUNT(*) as cnt FROM activities GROUP BY exercise_type"
    ).fetchall()

    conn.close()

    total_steps = sum(r["steps"] or 0 for r in today_data)
    total_calories = sum(r["calories"] or 0 for r in today_data)
    total_workouts = len(today_data)
    weekly_calories = sum(r["calories"] or 0 for r in week_data)
    weekly_workouts = len(week_data)

    progress = min(int((total_steps / 10000) * 100), 100)
    cal_progress = min(int((total_calories / 500) * 100), 100)
    workout_progress = min(int((total_workouts / 7) * 100), 100)

    type_labels = [r["exercise_type"] for r in type_data]
    type_counts = [r["cnt"] for r in type_data]

    return render_template("dashboard.html",
        steps=total_steps, calories=total_calories,
        workouts=total_workouts, progress=progress,
        cal_progress=cal_progress, workout_progress=workout_progress,
        weekly_calories=weekly_calories, weekly_workouts=weekly_workouts,
        activities=all_data,
        weekly_steps=weekly_steps, weekly_labels=weekly_labels,
        type_labels=type_labels, type_counts=type_counts,
        today=today
    )


@app.route("/add", methods=["GET", "POST"])
def add_activity():
    if request.method == "POST":
        activity = request.form["activity"]
        exercise_type = request.form.get("exercise_type", "Other")
        duration = request.form["duration"]
        calories = request.form["calories"]
        steps = request.form["steps"]
        date_val = request.form.get("date") or date.today().isoformat()

        conn = get_db()
        conn.execute("""
            INSERT INTO activities (activity, exercise_type, duration, calories, steps, date)
            VALUES (?,?,?,?,?,?)
        """, (activity, exercise_type, duration, calories, steps, date_val))
        conn.commit()
        conn.close()
        return redirect("/")
    return render_template("add_activity.html", today=date.today().isoformat())


@app.route("/delete/<int:activity_id>", methods=["POST"])
def delete_activity(activity_id):
    conn = get_db()
    conn.execute("DELETE FROM activities WHERE id=?", (activity_id,))
    conn.commit()
    conn.close()
    return redirect("/history")


@app.route("/history")
def history():
    conn = get_db()
    activities = conn.execute(
        "SELECT * FROM activities ORDER BY date DESC, id DESC"
    ).fetchall()
    conn.close()
    return render_template("history.html", activities=activities)


@app.route("/goals")
def goals():
    conn = get_db()
    today = date.today().isoformat()
    week_start = (date.today() - timedelta(days=date.today().weekday())).isoformat()

    today_data = conn.execute("SELECT * FROM activities WHERE date=?", (today,)).fetchall()
    week_data = conn.execute("SELECT * FROM activities WHERE date>=?", (week_start,)).fetchall()
    conn.close()

    today_steps = sum(r["steps"] or 0 for r in today_data)
    today_calories = sum(r["calories"] or 0 for r in today_data)
    today_duration = sum(r["duration"] or 0 for r in today_data)
    weekly_workouts = len(week_data)

    return render_template("goals.html",
        today_steps=today_steps, today_calories=today_calories,
        today_duration=today_duration, weekly_workouts=weekly_workouts
    )


@app.route("/profile")
def profile():
    conn = get_db()
    total = conn.execute("SELECT COUNT(*) as c FROM activities").fetchone()["c"]
    calories = conn.execute("SELECT SUM(calories) as s FROM activities").fetchone()["s"] or 0
    steps = conn.execute("SELECT SUM(steps) as s FROM activities").fetchone()["s"] or 0
    conn.close()
    return render_template("profile.html", total=total, calories=calories, steps=steps)


if __name__ == "__main__":
    app.run(debug=True)
