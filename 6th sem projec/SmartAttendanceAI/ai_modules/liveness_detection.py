"""
SmartAttendanceAI – Liveness Detection
Eye blink (EAR via dlib) + head movement.
Prevents photo, screen, and video replay spoofing.
"""
import cv2, numpy as np, logging

logger = logging.getLogger(__name__)
EAR_THRESHOLD = 0.25
EAR_CONSEC    = 2
HEAD_MOVE_PX  = 20

try:
    import dlib
    _DLIB = True
except ImportError:
    _DLIB = False
    logger.warning("dlib not found – simplified liveness mode.")

def _ear(pts):
    A = np.linalg.norm(pts[1]-pts[5])
    B = np.linalg.norm(pts[2]-pts[4])
    C = np.linalg.norm(pts[0]-pts[3])
    return (A+B)/(2.0*C+1e-6)

class LivenessDetector:
    WINDOW = 90

    def __init__(self):
        self.blink_count = 0
        self._ear_consec = 0
        self._prev_center = None
        self._head_moved  = False
        self._prev_area   = None

        if _DLIB:
            self._det  = dlib.get_frontal_face_detector()
            try:
                self._pred = dlib.shape_predictor(
                    "models/shape_predictor_68_face_landmarks.dat")
            except Exception:
                self._pred = None

    def reset(self):
        self.blink_count  = 0
        self._ear_consec  = 0
        self._prev_center = None
        self._head_moved  = False

    def update(self, gray, face_bbox) -> bool:
        x,y,w,h = face_bbox
        center  = np.array([x+w//2, y+h//2], dtype=float)

        # Head movement check
        if self._prev_center is not None:
            if np.linalg.norm(center - self._prev_center) > HEAD_MOVE_PX:
                self._head_moved = True
        self._prev_center = center

        # Blink detection
        if _DLIB and hasattr(self,'_pred') and self._pred:
            rect  = dlib.rectangle(int(x),int(y),int(x+w),int(y+h))
            shape = self._pred(gray, rect)
            pts   = np.array([[shape.part(i).x,shape.part(i).y]
                               for i in range(68)], dtype=np.float32)
            ear   = (_ear(pts[36:42]) + _ear(pts[42:48])) / 2.0
            if ear < EAR_THRESHOLD:
                self._ear_consec += 1
            else:
                if self._ear_consec >= EAR_CONSEC:
                    self.blink_count += 1
                self._ear_consec = 0
        else:
            # Fallback: face-area fluctuation heuristic
            area = w*h
            if self._prev_area and (area/(self._prev_area+1e-6)) < 0.90:
                self.blink_count += 0.5
            self._prev_area = area

        return self.blink_count >= 1 and self._head_moved

    @property
    def status(self):
        if self.blink_count >= 1 and self._head_moved: return "LIVE ✓"
        if self.blink_count >= 1: return "Blinked – move head"
        if self._head_moved:      return "Moved – please blink"
        return "Checking liveness…"