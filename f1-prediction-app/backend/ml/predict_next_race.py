import json
import os
import fastf1
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
import traceback
from performance_metrics import calculate_performance_metrics
from prepare_race_data import prepare_race_data
from weather_forecast import get_weather_data, normalise_weather_features
from weather_api import get_race_weather_forecast

def predict_next_race(predictor):
    """Predict the winner of the next race using enhanced features
    
    Args:
        predictor: F1Predictor instance
        
    Returns:
        dict: Prediction results with race details and driver predictions
    """
    try:
        print("\nStarting prediction for next race...")
        
        # Get current date from system
        current_date = pd.Timestamp.now()
        current_year = current_date.year
        
        # Get the current year's schedule
        schedule = fastf1.get_event_schedule(current_year)
        
        # Filter out testing sessions and find next race
        race_schedule = schedule[schedule['EventName'] != 'Pre-Season Testing']
        next_races = race_schedule[race_schedule['EventDate'] > current_date]
        
        if next_races.empty:
            print(f"No more races in {current_year}, looking at next year")
            schedule = fastf1.get_event_schedule(current_year + 1)
            race_schedule = schedule[schedule['EventName'] != 'Pre-Season Testing']
            next_race = race_schedule.iloc[0]
        else:
            next_race = next_races.iloc[0]
        
        print(f"\nNext race: {next_race['EventName']} on {next_race['EventDate']}")
        
        # Find the most recent completed race
        completed_races = race_schedule[race_schedule['EventDate'] < current_date]
        if completed_races.empty:
            # If no races completed in current year, look at previous year's last race
            prev_year_schedule = fastf1.get_event_schedule(current_year - 1)
            last_race = prev_year_schedule.iloc[-1]
            last_race_year = current_year - 1
        else:
            last_race = completed_races.iloc[-1]
            last_race_year = current_year
            
        print(f"\nUsing data from last completed race: {last_race['EventName']} ({last_race_year})")
        
        # Load the last race session to get current driver information
        last_race_session = fastf1.get_session(last_race_year, last_race['RoundNumber'], 'Race')
        last_race_session.load()
        
        # Get driver information from the last race
        drivers_df = last_race_session.results[['DriverNumber', 'Abbreviation', 'FullName', 'TeamName']]
        drivers_df['DriverNumber'] = pd.to_numeric(drivers_df['DriverNumber'], errors='coerce')
        
        # Load qualifying session for the last race
        last_quali = fastf1.get_session(last_race_year, last_race['RoundNumber'], 'Qualifying')
        last_quali.load()
        
        # Prepare prediction data using last race's qualifying order
        prediction_data = pd.DataFrame()
        prediction_data['QualifyingPosition'] = pd.to_numeric(last_quali.results['Position'], errors='coerce')
        prediction_data['RoundNumber'] = next_race['RoundNumber']
        prediction_data['Year'] = next_race['EventDate'].year
        prediction_data['DriverNumber'] = pd.to_numeric(last_quali.results['DriverNumber'], errors='coerce')
        prediction_data['Team'] = last_quali.results['TeamName']
        
        # Add weather data for the next race if available
        weather_description = "Unknown"
        print("\nGetting real-time weather forecast for the next race...")
        try:
            # Use our weather API to get real forecast data
                weather_features = get_race_weather_forecast()
                
                check_if_weather_data_exists = os.path.exists(f"./data/weather/{next_race['EventName']}_weather.json")
                if check_if_weather_data_exists:
                    print(f"Weather data for {next_race['EventName']} found.")
                    with open(f"./data/weather/{next_race['EventName']}_weather.json", 'r') as f:
                        print(f"Weather data from file {next_race['EventName']}_weather.json loaded.")
                        weather_features = json.load(f)
                else:
                    print(f"Weather data for {next_race['EventName']} not found. Retrieving from API.")
                
                if weather_features:
                    print("Successfully retrieved weather forecast")
                    
                    # Add weather features to prediction data
                    for feature, value in weather_features.items():
                        # Only add numeric weather features to the model
                        if isinstance(value, (int, float, np.number)) and feature not in ['RaceName', 'RaceDate', 'CircuitName', 'Location']:
                            prediction_data[f'Weather_{feature}'] = value
                    
                    # Get weather description
                    weather_conditions = {
                        0: "Dry and moderate",
                        1: "Hot and dry",
                        2: "Cold and dry",
                        3: "Light rain",
                        4: "Heavy rain", 
                        5: "Windy"
                    }
                    if 'WeatherCondition' in weather_features:
                        condition = int(weather_features['WeatherCondition'])
                        weather_description = weather_conditions.get(condition, "Unknown")
                else:
                    print("Could not get weather forecast, using fallback method")
                    # Fallback to using historical weather for this track
                    similar_races = fastf1.get_event_schedule(current_year - 1)
                    similar_race = similar_races[similar_races['EventName'] == next_race['EventName']]
                    
                    if not similar_race.empty:
                        prev_race = similar_race.iloc[0]
                        from weather_forecast import get_weather_data, extract_weather_features
                        weather_data = get_weather_data(current_year - 1, prev_race['RoundNumber'])
                        if weather_data is not None:
                            weather_features = extract_weather_features(weather_data)
                            for feature, value in weather_features.items():
                                prediction_data[f'Weather_{feature}'] = value
                                
                            if 'WeatherCondition' in weather_features:
                                condition = int(weather_features['WeatherCondition'])
                                weather_description = weather_conditions.get(condition, "Unknown")
                
                # Normalise weather features
                if hasattr(predictor, 'weather_scaler') and predictor.weather_scaler is not None:
                    prediction_data, _ = normalise_weather_features(
                        prediction_data, 
                        predictor.weather_scaler, 
                        fit=False
                    )
        except Exception as e:
            print(f"Error getting weather forecast: {str(e)}")
            traceback.print_exc()
                
        # Use enhanced feature engineering
        prediction_data = predictor.enhance_with_performance_metrics(prediction_data)
        
        # Ensure we have all required features
        for feature in predictor.feature_names:
            if feature not in prediction_data.columns:
                print(f"Warning: Feature {feature} missing from prediction data. Adding with zeros.")
                prediction_data[feature] = 0
        
        # Prepare prediction features
        prediction_features = prediction_data[predictor.feature_names]
        
        # Handle missing values
        prediction_features = pd.DataFrame(
            predictor.imputer.transform(prediction_features), 
            columns=predictor.feature_names
        )
        
        # Use the trained model to predict probabilities
        driver_probabilities = predictor.model.predict_proba(prediction_features)
        
        # Create a dictionary mapping class indices to their probability values
        probability_dict = {}
        for i, class_idx in enumerate(predictor.model.classes_):
            probability_dict[class_idx] = driver_probabilities[0][i]
        
        # Make predictions
        predictions = predictor.model.predict(prediction_features)
        
        # Add predictions to the data
        prediction_data['PredictedPosition'] = predictions
        
        # Merge with driver information
        final_predictions = pd.merge(
            prediction_data[['DriverNumber', 'PredictedPosition']],
            drivers_df,
            on='DriverNumber',
            how='left'
        )
        
        # Sort by predicted position
        sorted_driver_predictions = final_predictions.sort_values('PredictedPosition').to_dict(orient='records')
        
        # Add probabilities to the result
        race_result = []
        for i, driver in enumerate(sorted_driver_predictions):
            position = driver["PredictedPosition"]
            confidence = probability_dict.get(position, 0.0) * 100  # Convert to percentage
            race_result.append({
                "position": position,
                "name": driver["FullName"],
                "team": driver["TeamName"],
                "abbreviation": driver["Abbreviation"],
                "confidence": round(confidence, 2)  # Round to 2 decimal places
            })
        
        # Identify predicted winner
        winner = next((d for d in race_result if d["position"] == 1), None)
        
        # Get top 3 drivers based on confidence, not just position
        confidence_sorted = sorted(race_result, key=lambda x: x["confidence"], reverse=True)
        top_3_by_confidence = confidence_sorted[:3]
        
        # Prepare the final prediction result
        prediction_result = {
            "race_name": next_race["EventName"],
            "race_date": next_race["EventDate"].strftime("%Y-%m-%d"),
            "weather": weather_description,
            "predicted_winner": winner,
            "top_3": top_3_by_confidence,
            "all_drivers": race_result
        }
        
        print("\nPrediction result:")
        print(f"Race: {prediction_result['race_name']} on {prediction_result['race_date']}")
        print(f"Weather: {prediction_result['weather']}")
        print(f"Predicted Winner: {prediction_result['predicted_winner']['name']} ({prediction_result['predicted_winner']['team']})")
        print("\nTop 3 Predictions:")
        for pos, driver in enumerate(prediction_result['top_3'], 1):
            print(f"{pos}. {driver['name']} ({driver['team']})")
        
        return prediction_result
        
    except Exception as e:
        print(f"\nError making prediction: {str(e)}")
        traceback.print_exc()
        return None