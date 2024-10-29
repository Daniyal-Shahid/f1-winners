# backend/app/routes/predict.py
from flask import Blueprint, request, jsonify
import joblib
import os

predict_bp = Blueprint("predict", __name__)

model_path = os.path.join(os.path.dirname(__file__), "../models/model.pkl")

# Only attempt to load the model if it exists
if os.path.exists(model_path) and os.path.getsize(model_path) > 0:
    model = joblib.load(model_path)
else:
    model = None

@predict_bp.route("/predict", methods=["POST"])
def predict():
    if model is None:
        return jsonify({"error": "Model not available. Train the model first."}), 503
    
    data = request.get_json()
    prediction = model.predict([data["features"]])  # Modify for actual input format
    return jsonify({"prediction": prediction.tolist()})