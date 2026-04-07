"""SmartAttendanceAI – Email Alert (SMTP)"""
import smtplib, logging
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from database.db_connection import get_db_connection
from backend.config import Config

logger = logging.getLogger(__name__)

class EmailAlert:

    def _send(self, to, subject, html):
        msg = MIMEMultipart("alternative")
        msg["From"]    = Config.EMAIL_USER
        msg["To"]      = to
        msg["Subject"] = subject
        msg.attach(MIMEText(html,"html"))
        try:
            with smtplib.SMTP(Config.SMTP_SERVER, Config.SMTP_PORT) as s:
                s.ehlo(); s.starttls()
                s.login(Config.EMAIL_USER, Config.EMAIL_PASS)
                s.sendmail(Config.EMAIL_USER, to, msg.as_string())
            logger.info("Alert sent to %s", to)
        except Exception as e:
            logger.error("Email error to %s: %s", to, e)

    def send_low_attendance_alert(self, student_id, pct):
        try:
            conn   = get_db_connection()
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT * FROM Students WHERE student_id=%s", (student_id,))
            s = cursor.fetchone(); cursor.close(); conn.close()
            if not s: return

            subject = f"⚠️ Low Attendance Alert – {s['name']}"
            body = f"""
            <html><body style="font-family:Arial,sans-serif;background:#0f0f0f;padding:20px">
            <div style="max-width:580px;margin:auto;background:#1a1a1a;border-radius:12px;
                        padding:32px;border:1px solid #333">
              <h2 style="color:#f97316">⚠️ Low Attendance Warning</h2>
              <p style="color:#ccc">Dear <b style="color:#fff">{s['name']}</b>,</p>
              <p style="color:#ccc">Your current attendance is
                <b style="color:#ef4444;font-size:1.4em">{pct}%</b> —
                below the required <b>75%</b> threshold.</p>
              <p style="color:#ccc">Please contact your class teacher immediately.</p>
              <hr style="border-color:#333"/>
              <p style="color:#666;font-size:12px">
                Khalsa College of Engineering and Technology<br>
                SmartAttendanceAI – Automated Alert System
              </p>
            </div></body></html>"""

            for email in filter(None,[s.get("email"),s.get("parent_email")]):
                self._send(email, subject, body)

            # Log
            conn   = get_db_connection()
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO AlertLogs (student_id,alert_type,message) VALUES (%s,'LowAttendance',%s)",
                (student_id, f"Attendance {pct}% below 75%"))
            conn.commit(); cursor.close(); conn.close()
        except Exception as e:
            logger.error("Alert error: %s", e)