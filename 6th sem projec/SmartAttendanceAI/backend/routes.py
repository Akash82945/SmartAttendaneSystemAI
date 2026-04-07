"""SmartAttendanceAI – Route Handlers"""
import csv, io, json, logging
from datetime import date
from flask import (Blueprint, render_template, request, redirect,
                   url_for, session, flash, jsonify, Response)
from backend.auth       import login_required
from database.db_connection import get_db_connection
from analytics.attendance_analytics import AttendanceAnalytics
from alerts.email_alert import EmailAlert

logger      = logging.getLogger(__name__)
main_bp     = Blueprint("main", __name__)
analytics   = AttendanceAnalytics()
email_alert = EmailAlert()

# ── Home Dashboard ─────────────────────────────────────────────────────────────
@main_bp.route("/")
@main_bp.route("/dashboard")
@login_required
def dashboard():
    try:
        conn   = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT COUNT(*) AS total FROM Students")
        total = cursor.fetchone()["total"]
        today = date.today().isoformat()
        cursor.execute(
            "SELECT COUNT(DISTINCT student_id) AS p FROM Attendance "
            "WHERE date=%s AND status='Present'", (today,)
        )
        present = cursor.fetchone()["p"]
        pct = round(present / total * 100, 1) if total else 0
        cursor.execute("""
            SELECT date, COUNT(DISTINCT student_id) AS cnt
            FROM Attendance
            WHERE date >= DATE_SUB(CURDATE(), INTERVAL 7 DAY) AND status='Present'
            GROUP BY date ORDER BY date
        """)
        trend = cursor.fetchall()
        cursor.close(); conn.close()
        return render_template("dashboard.html",
            total_students=total, today_present=present, attendance_pct=pct,
            trend=json.dumps([{"date": str(r["date"]), "count": r["cnt"]} for r in trend]),
            teacher_name=session.get("teacher_name", "Teacher"))
    except Exception as e:
        logger.error("Dashboard error: %s", e)
        return render_template("dashboard.html",
            total_students=0, today_present=0, attendance_pct=0, trend="[]")

# ── Students CRUD ──────────────────────────────────────────────────────────────
@main_bp.route("/students")
@login_required
def students():
    conn   = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM Students ORDER BY name")
    rows = cursor.fetchall()
    cursor.close(); conn.close()
    return render_template("students.html", students=rows)

@main_bp.route("/students/add", methods=["POST"])
@login_required
def add_student():
    d = request.form
    try:
        conn   = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO Students (student_id,name,class,email,parent_email) "
            "VALUES (%s,%s,%s,%s,%s)",
            (d["student_id"], d["name"], d["class"], d["email"], d["parent_email"])
        )
        conn.commit(); cursor.close(); conn.close()
        flash(f"Student {d['name']} added.", "success")
    except Exception as e:
        logger.error("Add student: %s", e)
        flash("Error adding student.", "danger")
    return redirect(url_for("main.students"))

@main_bp.route("/students/delete/<sid>", methods=["POST"])
@login_required
def delete_student(sid):
    try:
        conn   = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM Students WHERE student_id=%s", (sid,))
        conn.commit(); cursor.close(); conn.close()
        flash("Student deleted.", "success")
    except Exception as e:
        logger.error("Delete: %s", e); flash("Error deleting.", "danger")
    return redirect(url_for("main.students"))

# ── Live Attendance ────────────────────────────────────────────────────────────
@main_bp.route("/live")
@login_required
def live():
    return render_template("live.html")

@main_bp.route("/api/live_feed")
@login_required
def live_feed():
    from ai_modules.camera_stream import generate_frames_sse
    return Response(generate_frames_sse(), mimetype="text/event-stream")

@main_bp.route("/api/mark_attendance", methods=["POST"])
def mark_attendance():
    data       = request.get_json()
    student_id = data.get("student_id")
    subject    = data.get("subject", "General")
    try:
        conn   = get_db_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT id FROM Attendance
            WHERE student_id=%s AND date=CURDATE() AND subject=%s
              AND TIMESTAMPDIFF(MINUTE,CONCAT(date,' ',time),NOW()) < 60
        """, (student_id, subject))
        if cursor.fetchone():
            cursor.close(); conn.close()
            return jsonify({"status": "duplicate"})
        cursor.execute(
            "INSERT INTO Attendance (student_id,date,time,subject,status) "
            "VALUES (%s,CURDATE(),CURTIME(),%s,'Present')",
            (student_id, subject)
        )
        conn.commit()
        cursor.execute(
            "SELECT COUNT(*) AS p FROM Attendance "
            "WHERE student_id=%s AND status='Present' "
            "AND date>=DATE_SUB(CURDATE(),INTERVAL 30 DAY)", (student_id,)
        )
        pct = round(cursor.fetchone()["p"] / 30 * 100, 1)
        cursor.close(); conn.close()
        if pct < 75:
            email_alert.send_low_attendance_alert(student_id, pct)
        return jsonify({"status": "marked", "attendance_pct": pct})
    except Exception as e:
        logger.error("Mark attendance: %s", e)
        return jsonify({"status": "error"}), 500

# ── Reports ────────────────────────────────────────────────────────────────────
@main_bp.route("/reports")
@login_required
def reports():
    conn   = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT s.student_id,s.name,s.class,a.subject,a.time,a.status
        FROM Attendance a JOIN Students s ON a.student_id=s.student_id
        WHERE a.date=CURDATE() ORDER BY a.time DESC
    """)
    daily = cursor.fetchall()
    cursor.execute("""
        SELECT s.name,s.class,
               COUNT(CASE WHEN a.status='Present' THEN 1 END) AS present_days,
               COUNT(*) AS total_days
        FROM Attendance a JOIN Students s ON a.student_id=s.student_id
        WHERE MONTH(a.date)=MONTH(CURDATE()) AND YEAR(a.date)=YEAR(CURDATE())
        GROUP BY s.student_id ORDER BY present_days DESC
    """)
    monthly = cursor.fetchall()
    cursor.execute("""
        SELECT subject,
               COUNT(CASE WHEN status='Present' THEN 1 END) AS present,
               COUNT(*) AS total
        FROM Attendance WHERE MONTH(date)=MONTH(CURDATE())
        GROUP BY subject
    """)
    subject_wise = cursor.fetchall()
    cursor.close(); conn.close()
    low = analytics.get_low_attendance_students()
    return render_template("reports.html",
        daily=daily, monthly=monthly,
        subject_wise=subject_wise, low_attendance=low)

# ── Export CSV ─────────────────────────────────────────────────────────────────
@main_bp.route("/export/csv")
@login_required
def export_csv():
    conn   = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("""
        SELECT s.student_id,s.name,s.class,a.date,a.time,a.subject,a.status
        FROM Attendance a JOIN Students s ON a.student_id=s.student_id
        ORDER BY a.date DESC,a.time DESC
    """)
    rows = cursor.fetchall(); cursor.close(); conn.close()
    out  = io.StringIO()
    w    = csv.DictWriter(out, fieldnames=["student_id","name","class","date","time","subject","status"])
    w.writeheader(); w.writerows(rows); out.seek(0)
    return Response(out.getvalue(), mimetype="text/csv",
        headers={"Content-Disposition": "attachment;filename=attendance.csv"})

# ── Analytics APIs ─────────────────────────────────────────────────────────────
@main_bp.route("/api/analytics/monthly")
@login_required
def monthly_analytics():
    return jsonify(analytics.get_monthly_trend())

@main_bp.route("/api/analytics/heatmap")
@login_required
def heatmap_analytics():
    return jsonify(analytics.get_attendance_heatmap())