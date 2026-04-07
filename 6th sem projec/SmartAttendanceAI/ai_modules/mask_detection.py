"""
SmartAttendanceAI – Mask Detection
MobileNetV2-based CNN. Can still recognise masked faces
via periocular region embedding in face_recognition.
"""
import cv2, numpy as np, logging, os
from backend.config import Config

logger = logging.getLogger(__name__)

class MaskDetector:
    IMG_SIZE = (224,224)
    LABELS   = ["Mask","No Mask"]

    def __init__(self):
        self.model = None
        self._load()

    def _load(self):
        if os.path.exists(Config.MASK_MODEL_PATH):
            try:
                from tensorflow.keras.models import load_model
                self.model = load_model(Config.MASK_MODEL_PATH)
                logger.info("Mask model loaded.")
            except Exception as e:
                logger.error("Mask model load error: %s", e)
        else:
            logger.warning("Mask model not found. Run train_mask_model().")

    def predict(self, face_roi: np.ndarray) -> tuple:
        if self.model is None or face_roi.size == 0:
            return "Unknown", 0.0
        try:
            img  = cv2.resize(face_roi, self.IMG_SIZE)
            img  = cv2.cvtColor(img, cv2.COLOR_BGR2RGB).astype("float32")/255.0
            preds = self.model.predict(np.expand_dims(img,0), verbose=0)[0]
            idx   = int(np.argmax(preds))
            return self.LABELS[idx], float(preds[idx])
        except Exception as e:
            logger.error("Mask predict error: %s", e)
            return "Error", 0.0

    @staticmethod
    def train_mask_model(dataset_path: str, output_path: str = None):
        """
        dataset_path/
            with_mask/    *.jpg
            without_mask/ *.jpg
        """
        import tensorflow as tf
        from tensorflow.keras import layers, models
        from tensorflow.keras.applications import MobileNetV2
        from tensorflow.keras.preprocessing.image import ImageDataGenerator

        output_path = output_path or Config.MASK_MODEL_PATH
        gen = ImageDataGenerator(rescale=1./255,rotation_range=20,
            zoom_range=0.15,horizontal_flip=True,validation_split=0.2)
        train = gen.flow_from_directory(dataset_path,target_size=(224,224),
                    batch_size=32,subset="training")
        val   = gen.flow_from_directory(dataset_path,target_size=(224,224),
                    batch_size=32,subset="validation")

        base = MobileNetV2(weights="imagenet",include_top=False,input_shape=(224,224,3))
        base.trainable = False
        model = models.Sequential([base,
            layers.GlobalAveragePooling2D(),
            layers.Dropout(0.3),
            layers.Dense(128,activation="relu"),
            layers.Dense(2,activation="softmax")])
        model.compile(optimizer="adam",loss="categorical_crossentropy",
                      metrics=["accuracy"])
        cbs = [tf.keras.callbacks.ModelCheckpoint(output_path,save_best_only=True),
               tf.keras.callbacks.EarlyStopping(patience=5,restore_best_weights=True)]
        model.fit(train,validation_data=val,epochs=20,callbacks=cbs)
        logger.info("Mask model saved to %s", output_path)