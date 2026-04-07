"""
SmartAttendanceAI – Full Pipeline Webcam Test
Tests: Face Detection → Recognition → Liveness → Mask
Press Q to quit.

Usage: python ai_modules/webcam_test.py
"""
import cv2, logging
from ai_modules.face_recognition_module import FaceRecognizer
from ai_modules.liveness_detection      import LivenessDetector
from ai_modules.mask_detection          import MaskDetector
from backend.config                     import Config

logging.basicConfig(level=logging.INFO)

def test():
    cap  = cv2.VideoCapture(Config.CAMERA_INDEX)
    rec  = FaceRecognizer()
    mask = MaskDetector()
    live = LivenessDetector()

    print("\n🎯 Webcam Test Running – Press Q to quit\n")

    while True:
        ret, frame = cap.read()
        if not ret: break

        gray    = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        results = rec.process_frame(frame)

        for r in results:
            x, y, w, h = r["bbox"]
            roi         = frame[y:y+h, x:x+w]
            mask_lbl, mask_conf = mask.predict(roi)
            is_live     = live.update(gray, (x, y, w, h))

            color = (0, 255, 0) if r["student_id"] != "UNKNOWN" else (0, 0, 255)
            cv2.rectangle(frame, (x, y), (x+w, y+h), color, 2)
            cv2.putText(frame,
                f"{r['name']} ({r['confidence']}%)",
                (x, y-30), cv2.FONT_HERSHEY_SIMPLEX, 0.55, color, 1)
            cv2.putText(frame,
                f"Mask:{mask_lbl} | {live.status}",
                (x, y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (255,255,0), 1)

        cv2.putText(frame, "SmartAttendanceAI – Webcam Test",
                    (10, 25), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (20,184,166), 2)
        cv2.imshow("Webcam Test – Press Q", frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release(); cv2.destroyAllWindows()
    print("✅ Test complete.")

if __name__ == "__main__":
    test()