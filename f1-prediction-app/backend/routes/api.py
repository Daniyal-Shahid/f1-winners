from flask import Blueprint, jsonify
from services.f1_predictor import F1Predictor

api_bp = Blueprint('api', __name__)
predictor = F1Predictor()

@api_bp.route('/prediction', methods=['GET'])
def get_prediction():
    race_prediction = predictor.predict_next_race()
    quali_prediction = predictor.predict_qualifying()
    
    if race_prediction or quali_prediction:
        return jsonify({
            'prediction': {
                'race': race_prediction,
                'qualifying': quali_prediction
            }
        })
    return jsonify({'error': 'Unable to generate predictions'}), 500

@api_bp.route('/last-race', methods=['GET'])
def get_last_race():
    results = predictor.get_last_race_results()
    if results:
        return jsonify(results)
    return jsonify({'error': 'Unable to fetch last race results'}), 500

@api_bp.route('/championship', methods=['GET'])
def get_championship():
    championship_data = predictor.get_championship_standings()
    if championship_data:
        return jsonify(championship_data)
    return jsonify({'error': 'Unable to fetch championship data'}), 500
