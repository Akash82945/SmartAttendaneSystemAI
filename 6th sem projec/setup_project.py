import os

# Project ka main folder name
root_dir = 'SmartAttendanceAI'

# Saare folders aur files ki list
structure = [
    'frontend/templates/login.html',
    'frontend/templates/dashboard.html',
    'frontend/templates/students.html',
    'frontend/templates/live.html',
    'frontend/templates/reports.html',
    'frontend/static/css/style.css',
    'frontend/static/js/dashboard.js',
    'backend/__init__.py',
    'backend/app.py',
    'backend/config.py',
    'backend/routes.py',
    'backend/auth.py',
    'ai_modules/__init__.py',
    'ai_modules/face_detection.py',
    'ai_modules/face_recognition_module.py',
    'ai_modules/liveness_detection.py',
    'ai_modules/mask_detection.py',
    'ai_modules/camera_stream.py',
    'ai_modules/collect_dataset.py',
    'ai_modules/train_model.py',
    'ai_modules/webcam_test.py',
    'database/__init__.py',
    'database/db_connection.py',
    'database/schema.sql',
    'models/face_embeddings.pkl',
    'models/mask_detection_model.h5',
    'analytics/__init__.py',
    'analytics/attendance_analytics.py',
    'alerts/__init__.py',
    'alerts/email_alert.py',
    'datasets/student_faces/STU001/.gitkeep', # Folder create karne ke liye
    'logs/app.log',
    'requirements.txt',
    'README.md'
]

def create_structure():
    for path in structure:
        # Full path banayein
        full_path = os.path.join(root_dir, path)
        # Folder path nikaalein
        folder = os.path.dirname(full_path)
        
        # Agar folder nahi hai toh banayein
        if not os.path.exists(folder):
            os.makedirs(folder)
            print(f"Folder ban gaya: {folder}")
            
        # Khali file create karein
        with open(full_path, 'w') as f:
            pass
        print(f"File ban gayi: {full_path}")

if __name__ == "__main__":
    create_structure()
    print("\nProject structure successfully create ho gaya hai!")