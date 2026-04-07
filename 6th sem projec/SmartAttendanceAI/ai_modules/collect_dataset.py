"""
SmartAttendanceAI – Face Dataset Collector
Usage: python ai_modules/collect_dataset.py --id STU001 --name "Amrit Singh" --count 150
"""
import cv2, os, argparse, logging
from backend.config import Config

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def collect(student_id: str, name: str, count: int = 150):
    save_dir = os.path.join(Config.DATASETS_DIR, student_id)
    os.makedirs(save_dir, exist_ok=True)

    cap     = cv2.VideoCapture(Config.CAMERA_INDEX)
    face_cc = cv2.CascadeClassifier(
        cv2.data.haarcascades + "haarcascade_frontalface_default.xml")
    saved, frame_id = 0, 0

    logger.info("Collecting %d images for %s (%s). Press Q to quit.", count, name, student_id)
    print(f"\n📸 Collecting dataset for: {name} [{student_id}]")
    print("► Look straight, then slowly move head left/right/up/down")
    print("► Press Q to stop early\n")

    while saved < count:
        ret, frame = cap.read()
        if not ret: break
        frame_id += 1
        gray  = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = face_cc.detectMultiScale(gray, 1.1, 5, minSize=(60, 60))

        for (x, y, w, h) in faces:
            roi  = frame[y:y+h, x:x+w]
            path = os.path.join(save_dir, f"{student_id}_{saved:04d}.jpg")
            cv2.imwrite(path, roi)
            saved += 1
            cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
            cv2.putText(frame, f"{saved}/{count}", (x, y-10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)

        cv2.putText(frame, f"Student: {name} | Saved: {saved}/{count}",
                    (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 0), 2)
        cv2.imshow("Collecting Dataset – Press Q to quit", frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release(); cv2.destroyAllWindows()
    logger.info("Saved %d images to %s", saved, save_dir)
    print(f"\n✅ Done! {saved} images saved to: {save_dir}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Collect face dataset")
    parser.add_argument("--id",    required=True,  help="Student ID e.g. STU001")
    parser.add_argument("--name",  required=True,  help="Student name")
    parser.add_argument("--count", type=int, default=150, help="Images to capture")
    args = parser.parse_args()
    collect(args.id, args.name, args.count)