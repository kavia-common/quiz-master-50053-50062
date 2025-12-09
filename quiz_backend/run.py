from app import create_app

# Entrypoint for running the service locally
# Runs on port 3001 to match the preview system
if __name__ == "__main__":
    app = create_app()
    app.run(host="0.0.0.0", port=3001)
