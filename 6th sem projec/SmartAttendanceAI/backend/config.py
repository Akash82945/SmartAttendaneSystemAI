"""SmartAttendanceAI – Configuration"""
import os

class Config:
    SECRET_KEY   = os.environ.get("SECRET_KEY", "kce_smart_attendance_secret_2024")
    DEBUG        = os.environ.get("DEBUG", "True") == "True"

    # MySQL
    MYSQL_HOST     = os.environ.get("MYSQL_HOST",     "localhost")
    MYSQL_PORT     = int(os.environ.get("MYSQL_PORT", 3306))
    MYSQL_USER     = os.environ.get("MYSQL_USER",     "root")
    MYSQL_PASSWORD = os.environ.get("MYSQL_PASSWORD", "yourpassword")
    MYSQL_DB       = os.environ.get("MYSQL_DB",       "smart_attendance_db")

    # SMTP Email Alerts
    SMTP_SERVER = os.environ.get("SMTP_SERVER", "smtp.gmail.com")
    SMTP_PORT   = int(os.environ.get("SMTP_PORT", 587))
    EMAIL_USER  = os.environ.get("EMAIL_USER",  "your_email@gmail.com")
    EMAIL_PASS  = os.environ.get("EMAIL_PASS",  "your_app_password")

    # Attendance Rules
    MIN_ATTENDANCE_PERCENTAGE = 75
    DUPLICATE_WINDOW_MINUTES  = 60

    # Paths
    BASE_DIR             = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    MODELS_DIR           = os.path.join(BASE_DIR, "models")
    DATASETS_DIR         = os.path.join(BASE_DIR, "datasets", "student_faces")
    FACE_EMBEDDINGS_PATH = os.path.join(MODELS_DIR, "face_embeddings.pkl")
    MASK_MODEL_PATH      = os.path.join(MODELS_DIR, "mask_detection_model.h5")

    # Camera
    CAMERA_INDEX          = 0
    FRAME_WIDTH           = 640
    FRAME_HEIGHT          = 480
    RECOGNITION_THRESHOLD = 0.55

    # Logging
    LOG_DIR  = os.path.join(BASE_DIR, "logs")
    LOG_FILE = os.path.join(LOG_DIR, "app.log")