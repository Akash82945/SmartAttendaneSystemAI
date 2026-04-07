"""
SmartAttendanceAI – Face Detection
OpenCV DNN (SSD ResNet-10) with Haar fallback.
Supports multi-face, low-light (CLAHE), various angles.
"""
import cv2, numpy as np, logging, os

logger = logging.getLogger(__name__)
PROTOTXT    = os.path.join(os.path.dirname(__file__), "deploy.prototxt")
CAFFEMODEL  = os.path.join(os.path.dirname(__file__), "res10_300x300_ssd_iter_140000.caffemodel")

class FaceDetector:
    CONFIDENCE_THRESHOLD = 0.5

    def __init__(self):
        self.net  = None
        self.haar = None
        self._load()

    def _load(self):
        if os.path.exists(PROTOTXT) and os.path.exists(CAFFEMODEL):
            try:
                self.net = cv2.dnn.readNetFromCaffe(PROTOTXT, CAFFEMODEL)
                logger.info("DNN face detector loaded."); return
            except Exception as e:
                logger.warning("DNN failed (%s) – Haar fallback.", e)
        cascade = cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
        self.haar = cv2.CascadeClassifier(cascade)
        logger.info("Haar Cascade loaded.")

    def detect(self, frame: np.ndarray) -> list:
        return self._dnn(frame) if self.net else self._haar(frame)

    def _dnn(self, frame):
        h, w = frame.shape[:2]
        blob = cv2.dnn.blobFromImage(
            cv2.resize(frame,(300,300)), 1.0, (300,300), (104.,177.,123.))
        self.net.setInput(blob)
        dets = self.net.forward()
        boxes = []
        for i in range(dets.shape[2]):
            if dets[0,0,i,2] > self.CONFIDENCE_THRESHOLD:
                b = (dets[0,0,i,3:7] * np.array([w,h,w,h])).astype(int)
                x1,y1,x2,y2 = max(0,b[0]),max(0,b[1]),min(w,b[2]),min(h,b[3])
                boxes.append((x1,y1,x2-x1,y2-y1))
        return boxes

    def _haar(self, frame):
        gray  = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
        gray  = clahe.apply(gray)
        faces = self.haar.detectMultiScale(gray, 1.1, 5, minSize=(30,30))
        return list(faces) if len(faces) > 0 else []

    @staticmethod
    def draw_boxes(frame, boxes, label="", color=(0,255,0)):
        for (x,y,w,h) in boxes:
            cv2.rectangle(frame,(x,y),(x+w,y+h),color,2)
            if label:
                cv2.putText(frame,label,(x,y-10),
                            cv2.FONT_HERSHEY_SIMPLEX,0.6,color,2)
        return frame