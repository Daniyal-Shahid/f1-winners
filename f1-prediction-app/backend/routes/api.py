from flask import Blueprint, jsonify
from services.f1_predictor import F1Predictor
from services.sentiment_analyzer import F1SentimentAnalyzer
from services.race_analyzer import RaceAnalyzer
from services.race_calendar import RaceCalendarService  # Import the new service
import logging

api_bp = Blueprint('api', __name__)
predictor = F1Predictor()
race_analyzer = RaceAnalyzer()
race_calendar_service = RaceCalendarService()  # Initialize the new service

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

@api_bp.route('/race-analysis/<driver>', methods=['GET'])
def get_race_analysis(driver):
    try:
        logging.info(f"Fetching race analysis for driver: {driver}")
        analysis = race_analyzer.get_driver_race_analysis(driver)
        
        if not analysis:
            logging.error(f"No analysis data found for driver: {driver}")
            return jsonify({
                'error': 'No analysis data found',
                'message': f'Could not find race data for driver: {driver}'
            }), 404
            
        return jsonify(analysis)
        
    except Exception as e:
        logging.error(f"Error in race analysis endpoint for {driver}: {str(e)}")
        return jsonify({
            'error': 'Internal server error',
            'message': str(e)
        }), 500

@api_bp.route('/race-calendar', methods=['GET'])
def get_race_calendar():
    """Endpoint to fetch the current season's race calendar."""
    try:
        race_calendar = race_calendar_service.get_race_calendar()
        if race_calendar:
            return jsonify(race_calendar)
        else:
            return jsonify({'error': 'Unable to fetch race calendar'}), 500
    except Exception as e:
        logging.error(f"Error in race calendar endpoint: {str(e)}")
        return jsonify({'error': str(e)}), 500