"""SmartAttendanceAI – Authentication"""
import logging
from functools import wraps
from flask import (Blueprint, render_template, request,
                   redirect, url_for, session, flash)
from database.db_connection import get_db_connection

logger  = logging.getLogger(__name__)
auth_bp = Blueprint("auth", __name__)

def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if "teacher_id" not in session:
            flash("Please log in to continue.", "warning")
            return redirect(url_for("auth.login"))
        return f(*args, **kwargs)
    return decorated

@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email    = request.form.get("email", "").strip()
        password = request.form.get("password", "").strip()
        try:
            conn   = get_db_connection()
            cursor = conn.cursor(dictionary=True)
            cursor.execute(
                "SELECT * FROM Teachers WHERE email=%s AND password=SHA2(%s,256)",
                (email, password)
            )
            teacher = cursor.fetchone()
            cursor.close(); conn.close()
            if teacher:
                session["teacher_id"]   = teacher["teacher_id"]
                session["teacher_name"] = teacher["name"]
                return redirect(url_for("main.dashboard"))
            flash("Invalid email or password.", "danger")
        except Exception as e:
            logger.error("Login error: %s", e)
            flash("Database error. Try again.", "danger")
    return render_template("login.html")

@auth_bp.route("/logout")
def logout():
    session.clear()
    flash("Logged out successfully.", "info")
    return redirect(url_for("auth.login"))