"""
SmartAttendanceAI – Face Recognition
128-d face_recognition embeddings + cosine distance.
Multi-face simultaneous recognition.
"""
import os, pickle, logging
import numpy as np, face_recognition, cv2
from backend.config import Config

logger = logging.getLogger(__name__)

class FaceRecognizer:
    def __init__(self):
        self.known_encodings: list = []
        self.known_ids:       list = []
        self.known_names:     list = []
        self._load()

    def _load(self):
        path = Config.FACE_EMBEDDINGS_PATH
        if not os.path.exists(path):
            logger.warning("No embeddings at %s – run train_model.py first.", path)
            return
        try:
            with open(path,"rb") as f:
                d = pickle.load(f)
            self.known_encodings = d.get("encodings",[])
            self.known_ids       = d.get("ids",[])
            self.known_names     = d.get("names",[])
            logger.info("Loaded %d encodings.", len(self.known_encodings))
        except Exception as e:
            logger.error("Embedding load error: %s", e)

    def reload(self):
        self._load()

    def recognize(self, rgb_frame, face_location) -> tuple:
        """Returns (student_id, name, confidence_pct)"""
        if not self.known_encodings:
            return "UNKNOWN","Unknown",0.0
        enc = face_recognition.face_encodings(rgb_frame, [face_location])
        if not enc:
            return "UNKNOWN","Unknown",0.0
        dists    = face_recognition.face_distance(self.known_encodings, enc[0])
        best_idx = int(np.argmin(dists))
        best_d   = float(dists[best_idx])
        if best_d < Config.RECOGNITION_THRESHOLD:
            return (self.known_ids[best_idx],
                    self.known_names[best_idx],
                    round((1-best_d)*100, 1))
        return "UNKNOWN","Unknown",0.0

    def process_frame(self, bgr_frame) -> list[dict]:
        """Detect & recognise all faces. Returns list of dicts."""
        small = cv2.resize(bgr_frame,(0,0),fx=0.5,fy=0.5)
        rgb   = cv2.cvtColor(small, cv2.COLOR_BGR2RGB)
        locs  = face_recognition.face_locations(rgb, model="hog")
        out   = []
        for loc in locs:
            top,right,bottom,left = [v*2 for v in loc]
            sid,name,conf = self.recognize(
                cv2.cvtColor(bgr_frame, cv2.COLOR_BGR2RGB),
                (top//2,right//2,bottom//2,left//2))
            out.append({"student_id":sid,"name":name,"confidence":conf,
                        "bbox":(left,top,right-left,bottom-top)})
        return out