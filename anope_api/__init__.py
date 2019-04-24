def create_instance():
    from flask import Flask
    from .config import Config
    instance = Flask(__name__)

    instance.config.from_object(Config)

    from anope_api.views.auth import auth_bp
    instance.register_blueprint(auth_bp)

    return instance


app = create_instance()
