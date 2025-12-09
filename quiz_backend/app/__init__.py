from flask import Flask
from flask_cors import CORS
from flask_smorest import Api

# Import configuration and blueprints
from .config import Config
from .routes.health import blp as health_blp
from .routes.quiz import blp as quiz_blp


# PUBLIC_INTERFACE
def create_app() -> Flask:
    """Application factory to create and configure the Flask app.

    Returns:
        Flask: A configured Flask application with CORS, OpenAPI, and registered blueprints.
    """
    app = Flask(__name__)
    app.url_map.strict_slashes = False

    # Load configuration
    app.config.from_object(Config)

    # Enable permissive CORS for development
    CORS(app, resources={r"/*": {"origins": "*"}})

    # Setup API docs with flask-smorest
    api = Api(app)
    api.register_blueprint(health_blp)
    api.register_blueprint(quiz_blp)

    # Root redirect note: We keep "/" for health to keep acceptance criteria simple.
    return app


# Keep backward compatibility for modules importing `app`
# while favoring the app factory pattern.
app = create_app()
