"""SmartAttendanceAI – Flask Application Factory"""
import logging, os
from flask import Flask
from backend.config import Config

os.makedirs(Config.LOG_DIR, exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[logging.FileHandler(Config.LOG_FILE), logging.StreamHandler()],
)
logger = logging.getLogger(__name__)

def create_app() -> Flask:
    app = Flask(
        __name__,
        template_folder=os.path.join(os.path.dirname(os.path.dirname(__file__)),
                                     "frontend", "templates"),
        static_folder=os.path.join(os.path.dirname(os.path.dirname(__file__)),
                                   "frontend", "static"),
    )
    app.config.from_object(Config)

    from backend.routes import main_bp
    from backend.auth   import auth_bp
    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp, url_prefix="/auth")

    logger.info("SmartAttendanceAI app started.")
    return app

if __name__ == "__main__":
    create_app().run(host="0.0.0.0", port=5000, debug=Config.DEBUG)