from flask_smorest import Blueprint
from flask.views import MethodView

blp = Blueprint(
    "Health",
    "health",
    url_prefix="/api",
    description="Health and service status endpoints",
)

@blp.route("/health")
class HealthCheck(MethodView):
    """Health check endpoint to verify the service is running."""
    # PUBLIC_INTERFACE
    def get(self):
        """Return service health status.

        Returns:
            dict: {"status": "ok"}
        """
        return {"status": "ok"}
