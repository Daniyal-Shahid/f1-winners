# backend/app/__init__.py
from flask import Flask, jsonify

def create_app():
    app = Flask(__name__)

    # Register predict route
    from .routes.predict import predict_bp
    app.register_blueprint(predict_bp, url_prefix="/api")

    # Define a simple root route
    @app.route("/")
    def home():
        return jsonify({"message": "Welcome to the F1 Prediction API!"})

    return app