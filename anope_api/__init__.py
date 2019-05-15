def create_instance():
    from flask import Flask
    from .config import Config
    instance = Flask(__name__)

    instance.config.from_object(Config)

    from anope_api.views.api.v0.auth import auth_bp

    instance.register_blueprint(auth_bp)
    instance.register_blueprint(auth_bp, url_prefix='/api')
    instance.register_blueprint(auth_bp, url_prefix='/api/v0')

    return instance


app = create_instance()
