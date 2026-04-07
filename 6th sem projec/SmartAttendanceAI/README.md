# SmartAttendanceAI
### Khalsa College of Engineering and Technology
AI-Powered Smart Attendance & Classroom Monitoring System

---

## Prerequisites
- Python 3.10+
- MySQL 8.0+
- Webcam
- CMake (required for dlib)

---

## Step 1 – Clone & Setup Environment
```bash
git clone https://github.com/your-repo/SmartAttendanceAI.git
cd SmartAttendanceAI
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
```

## Step 2 – Install Dependencies
```bash
# Install CMake first (needed for dlib/face_recognition)
pip install cmake
pip install -r requirements.txt
```

## Step 3 – Setup MySQL Database
```bash
mysql -u root -p < database/schema.sql
```

## Step 4 – Configure Environment
Edit `backend/config.py` and update:
- `MYSQL_PASSWORD` → your MySQL root password
- `EMAIL_USER` / `EMAIL_PASS` → Gmail + App Password
- `CAMERA_INDEX` → 0 (default webcam) or 1 for external

## Step 5 – Collect Student Face Dataset
```bash
# For each student, run:
python ai_modules/collect_dataset.py --id STU001 --name "Amrit Singh" --count 100
python ai_modules/collect_dataset.py --id STU002 --name "Priya Kaur"  --count 100
```

## Step 6 – Train Face Recognition Model
```bash
python ai_modules/train_model.py
# Output: models/face_embeddings.pkl
```

## Step 7 – (Optional) Train Mask Detection Model
```bash
# Download mask dataset from Kaggle (Face Mask Detection Dataset)
# Place in datasets/mask_dataset/with_mask/ and datasets/mask_dataset/without_mask/
python -c "
from ai_modules.mask_detection import MaskDetector
MaskDetector.train_mask_model('datasets/mask_dataset')
"
# Output: models/mask_detection_model.h5
```

## Step 8 – Test Webcam Pipeline
```bash
python ai_modules/webcam_test.py
```

## Step 9 – Run the Application
```bash
python -m backend.app
# Open browser: http://localhost:5000
# Login: admin@kcet.ac.in / admin123
```

---

## System Architecture
