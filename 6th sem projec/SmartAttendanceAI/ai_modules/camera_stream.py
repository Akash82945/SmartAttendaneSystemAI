"""
SmartAttendanceAI – Camera Stream (SSE Generator)
Full AI pipeline per frame: detect → recognise → liveness → mask → mark.
"""
import cv2, json, time, logging, requests, base64, numpy as np
from ai_modules.face_recognition_module import FaceRecognizer
from ai_modules.liveness_detection      import LivenessDetector
from ai_modules.mask_detection          import MaskDetector
from backend.config import Config

logger = logging.getLogger(__name__)

_recognizer = FaceRecognizer()
_mask_det   = MaskDetector()
_liveness   : dict[int, LivenessDetector] = {}

def _b64(frame):
    _, buf = cv2.imencode(".jpg", frame, [cv2.IMWRITE_JPEG_QUALITY, 75])
    return base64.b64encode(buf).decode()

def generate_frames_sse():
    cap = cv2.VideoCapture(Config.CAMERA_INDEX)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH,  Config.FRAME_WIDTH)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, Config.FRAME_HEIGHT)
    recently = {}   # sid → last_mark timestamp
    COOLDOWN = 300  # seconds

    try:
        while True:
            ret, frame = cap.read()
            if not ret: time.sleep(0.1); continue
            gray    = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            results = _recognizer.process_frame(frame)
            dets    = []

            for idx, res in enumerate(results):
                x,y,w,h = res["bbox"]
                if idx not in _liveness:
                    _liveness[idx] = LivenessDetector()
                ld      = _liveness[idx]
                is_live = ld.update(gray, (x,y,w,h))
                mask_lbl, mask_conf = _mask_det.predict(frame[y:y+h,x:x+w])

                sid = res["student_id"]
                if is_live and sid != "UNKNOWN":
                    now = time.time()
                    if now - recently.get(sid, 0) > COOLDOWN:
                        recently[sid] = now
                        try:
                            requests.post("http://127.0.0.1:5000/api/mark_attendance",
                                json={"student_id":sid,"subject":"General"},timeout=2)
                        except Exception: pass

                color = (0,255,0) if sid != "UNKNOWN" else (0,0,255)
                cv2.rectangle(frame,(x,y),(x+w,y+h),color,2)
                cv2.putText(frame,
                    f"{res['name']} {res['confidence']}% | {mask_lbl} | {ld.status}",
                    (x,y-10),cv2.FONT_HERSHEY_SIMPLEX,0.45,color,1)
                dets.append({"student_id":sid,"name":res["name"],
                             "confidence":res["confidence"],"mask":mask_lbl,
                             "liveness":ld.status,"bbox":[x,y,w,h]})

            yield f"data: {json.dumps({'frame':_b64(frame),'detections':dets})}\n\n"
            time.sleep(1/15)
    finally:
        cap.release(); _liveness.clear()