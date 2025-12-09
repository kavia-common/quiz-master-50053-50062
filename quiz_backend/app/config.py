from os import getenv

class Config:
    """Base configuration for the Flask app, including OpenAPI docs settings."""
    DEBUG = getenv("FLASK_DEBUG", "0") == "1"
    TESTING = False

    # API documentation details
    API_TITLE = "Quiz Backend API"
    API_VERSION = "v1"
    OPENAPI_VERSION = "3.0.3"
    OPENAPI_URL_PREFIX = "/docs"
    OPENAPI_SWAGGER_UI_PATH = ""
    OPENAPI_SWAGGER_UI_URL = "https://cdn.jsdelivr.net/npm/swagger-ui-dist/"
