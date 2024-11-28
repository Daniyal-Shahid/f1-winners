from flask import Blueprint, jsonify
from services.f1_predictor import F1Predictor
from services.sentiment_analyzer import F1SentimentAnalyzer
import logging

api_bp = Blueprint('api', __name__)
predictor = F1Predictor()

@api_bp.route('/prediction', methods=['GET'])
def get_prediction():
    try:
        race_prediction = predictor.predict_next_race()
        quali_prediction = predictor.predict_qualifying()
        
        # Debug logging
        logging.info("Race prediction sentiment data: %s", 
                    race_prediction.get('sentiment') if race_prediction else None)
        logging.info("Quali prediction sentiment data: %s", 
                    quali_prediction.get('sentiment') if quali_prediction else None)
        
        return jsonify({
            'prediction': {
                'race': race_prediction,
                'qualifying': quali_prediction
            }
        })
    except Exception as e:
        logging.error(f"Error in prediction endpoint: {str(e)}")
        return jsonify({'error': str(e)}), 500

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

@api_bp.route('/driver-sentiment/<driver_name>')
def get_driver_sentiment_details(driver_name):
    try:
        analyzer = F1SentimentAnalyzer()
        sentiment_data = analyzer.get_driver_sentiment_details(driver_name)
        return jsonify(sentiment_data)
    except Exception as e:
        logging.error(f"Error getting sentiment details: {str(e)}")
        return jsonify({'error': str(e)}), 500
