"""SmartAttendanceAI – Analytics"""
import logging
from database.db_connection import get_db_connection
from backend.config import Config

logger = logging.getLogger(__name__)

class AttendanceAnalytics:

    def get_low_attendance_students(self, threshold=None):
        threshold = threshold or Config.MIN_ATTENDANCE_PERCENTAGE
        try:
            conn   = get_db_connection()
            cursor = conn.cursor(dictionary=True)
            cursor.execute("""
                SELECT s.student_id,s.name,s.class,s.email,s.parent_email,
                  COUNT(CASE WHEN a.status='Present' THEN 1 END) AS present_days,
                  COUNT(*) AS total_days,
                  ROUND(COUNT(CASE WHEN a.status='Present' THEN 1 END)*100.0/
                        NULLIF(COUNT(*),0),1) AS pct
                FROM Students s
                LEFT JOIN Attendance a ON s.student_id=a.student_id
                  AND a.date>=DATE_SUB(CURDATE(),INTERVAL 30 DAY)
                GROUP BY s.student_id
                HAVING pct < %s OR pct IS NULL
                ORDER BY pct ASC
            """, (threshold,))
            rows = cursor.fetchall(); cursor.close(); conn.close()
            return rows
        except Exception as e:
            logger.error("Low attendance error: %s", e); return []

    def get_monthly_trend(self):
        try:
            conn   = get_db_connection()
            cursor = conn.cursor(dictionary=True)
            cursor.execute("""
                SELECT date, COUNT(DISTINCT student_id) AS cnt
                FROM Attendance
                WHERE MONTH(date)=MONTH(CURDATE()) AND YEAR(date)=YEAR(CURDATE())
                  AND status='Present'
                GROUP BY date ORDER BY date
            """)
            rows = cursor.fetchall(); cursor.close(); conn.close()
            return [{"date":str(r["date"]),"count":r["cnt"]} for r in rows]
        except Exception as e:
            logger.error("Monthly trend error: %s", e); return []

    def get_attendance_heatmap(self):
        try:
            conn   = get_db_connection()
            cursor = conn.cursor(dictionary=True)
            cursor.execute("""
                SELECT s.name, a.date,
                  MAX(CASE WHEN a.status='Present' THEN 1 ELSE 0 END) AS present
                FROM Students s
                LEFT JOIN Attendance a ON s.student_id=a.student_id
                  AND a.date>=DATE_SUB(CURDATE(),INTERVAL 30 DAY)
                GROUP BY s.student_id,a.date ORDER BY s.name,a.date
            """)
            rows = cursor.fetchall(); cursor.close(); conn.close()
            return [{"name":r["name"],"date":str(r["date"]),"present":r["present"]}
                    for r in rows]
        except Exception as e:
            logger.error("Heatmap error: %s", e); return []