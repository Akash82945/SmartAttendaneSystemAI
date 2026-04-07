"""
SmartAttendanceAI – Face Embeddings Trainer
Reads datasets/student_faces/{student_id}/*.jpg
Generates models/face_embeddings.pkl

Usage: python ai_modules/train_model.py
"""
import os, pickle, logging
import face_recognition
from backend.config import Config

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def train():
    encodings, ids, names = [], [], []
    dataset = Config.DATASETS_DIR

    if not os.path.exists(dataset):
        logger.error("Dataset folder not found: %s", dataset)
        return

    student_dirs = [d for d in os.listdir(dataset)
                    if os.path.isdir(os.path.join(dataset, d))]

    if not student_dirs:
        logger.error("No student folders found in %s", dataset)
        return

    print(f"\n🧠 Training face recognition model...")
    print(f"   Found {len(student_dirs)} students\n")

    for sid in student_dirs:
        folder  = os.path.join(dataset, sid)
        images  = [f for f in os.listdir(folder)
                   if f.lower().endswith(('.jpg','.jpeg','.png'))]
        enc_count = 0

        for img_name in images:
            img_path = os.path.join(folder, img_name)
            try:
                img   = face_recognition.load_image_file(img_path)
                encs  = face_recognition.face_encodings(img)
                if encs:
                    encodings.append(encs[0])
                    ids.append(sid)
                    names.append(sid)   # name resolved from DB at runtime
                    enc_count += 1
            except Exception as e:
                logger.warning("Skip %s: %s", img_path, e)

        print(f"   ✓ {sid}: {enc_count}/{len(images)} encodings")

    os.makedirs(Config.MODELS_DIR, exist_ok=True)
    with open(Config.FACE_EMBEDDINGS_PATH, "wb") as f:
        pickle.dump({"encodings": encodings, "ids": ids, "names": names}, f)

    print(f"\n✅ Saved {len(encodings)} total encodings → {Config.FACE_EMBEDDINGS_PATH}")
    logger.info("Training complete. %d encodings saved.", len(encodings))

if __name__ == "__main__":
    train()