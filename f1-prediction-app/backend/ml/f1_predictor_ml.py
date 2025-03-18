import fnmatch
import os
import pathlib
import traceback
import fastf1
import pandas as pd
import numpy as np
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import LabelEncoder
from sklearn.impute import SimpleImputer
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
import warnings
import json

# Suppress warnings
warnings.filterwarnings('ignore')

class F1Predictor:
    def __init__(self):
        # Enable caching
        fastf1.Cache.enable_cache('/Users/daniyalshahid/Desktop/personal projects/f1-winners/f1-prediction-app/backend/cache')
        self.label_encoder = LabelEncoder()
        self.imputer = SimpleImputer(strategy='mean')
        self.model = GradientBoostingClassifier(
            n_estimators=100,
            learning_rate=0.1,
            max_depth=3,
            random_state=42
        )

    def prepare_race_data(self, years=None):
        """Prepare training data from FastF1 for multiple seasons
    
        Args:
            years (list): List of years to include (default: [2021, 2022, 2023, 2024])
        """
        if years is None:
            years = [2021, 2022, 2023, 2024]  # Use last 4 seasons by default
            
        all_data = []
        
        for year in years:
            print(f"\nProcessing season {year}")
            
            # Get all sessions for the year
            schedule = fastf1.get_event_schedule(year)
            
            # For current year, only use completed races
            if year == pd.Timestamp.now().year:
                completed_races = schedule[schedule['EventDate'] < pd.Timestamp.now()]
            else:
                completed_races = schedule  # Use all races for past years
            
            print(f"Processing {len(completed_races)} races for {year}")
            
            for idx, race in completed_races.iterrows():
                try:
                    print(f"Processing race: {race['EventName']}")
                    
                    # Skip if this is a testing event
                    if 'test' in race['EventName'].lower() or 'testing' in race['EventName'].lower():
                        print(f"Skipping test event: {race['EventName']}")
                        continue
                    
                    # Load the race session
                    race_session = fastf1.get_session(year, race['RoundNumber'], 'Race')
                    race_session.load()
                    
                    # Get qualifying results for grid positions
                    quali_session = fastf1.get_session(year, race['RoundNumber'], 'Qualifying')
                    quali_session.load()
                    
                    # Extract qualifying positions
                    quali_results = quali_session.results[['DriverNumber', 'Position']]
                    quali_results = quali_results.rename(columns={'Position': 'QualifyingPosition'})
                    
                    # Get race results
                    race_results = race_session.results[['DriverNumber', 'Position', 'Points']]
                    
                    # Convert Position columns to numeric
                    quali_results['QualifyingPosition'] = pd.to_numeric(quali_results['QualifyingPosition'], errors='coerce')
                    race_results['Position'] = pd.to_numeric(race_results['Position'], errors='coerce')
                    
                    # Merge qualifying and race data
                    merged_data = pd.merge(race_results, quali_results, on='DriverNumber', how='outer')
                    
                    # Add race information
                    merged_data['Track'] = race['EventName']
                    merged_data['RoundNumber'] = race['RoundNumber']
                    merged_data['Year'] = year
                    merged_data['CircuitId'] = race['OfficialEventName']  # Useful for track-specific analysis
                    
                    all_data.append(merged_data)
                    
                except Exception as e:
                    print(f"Error processing race {race['EventName']}: {str(e)}")
                    continue
        
        if not all_data:
            raise ValueError("No race data available for training")
                
        final_data = pd.concat(all_data, ignore_index=True)
        
        # Drop rows where Position (target variable) is NaN
        final_data = final_data.dropna(subset=['Position'])
        
        print("\nFinal dataset info:")
        print(f"Total races: {len(all_data)}")
        print(f"Total data points: {len(final_data)}")
        print(f"Years included: {final_data['Year'].unique()}")
        print(final_data.info())
        
        return final_data

    def train_model(self):
        """Train the gradient boosting model with multi-year data"""
        try:
            # Get training data from multiple seasons
            print("\nPreparing training data...")
            data = self.prepare_race_data()
            
            # Prepare features and target
            # Now include Year as a feature to account for season differences
            features = ['QualifyingPosition', 'RoundNumber', 'Year']  
            
            # Debug prints
            print("\nChecking features presence:")
            for feature in features:
                print(f"{feature} in columns: {feature in data.columns}")
                if feature in data.columns:
                    print(f"{feature} unique values: {data[feature].unique()}")
            
            X = data[features]
            y = data['Position']  # Position 1 is the winner
            
            print("\nFeature matrix shape:", X.shape)
            print("Target vector shape:", y.shape)
            
            # Handle NaN values in features using imputer
            print("\nImputing missing values...")
            X = pd.DataFrame(self.imputer.fit_transform(X), columns=X.columns)
            
            # Split the data
            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=0.2, random_state=42
            )
            
            print("\nTraining set shape:", X_train.shape)
            print("Test set shape:", X_test.shape)
            
            # Train the model
            print("\nTraining model...")
            self.model.fit(X_train, y_train)
            
            # Evaluate the model
            y_pred = self.model.predict(X_test)
            accuracy = accuracy_score(y_test, y_pred)
            print(f"\nModel accuracy: {accuracy:.2f}")
            
            # Feature importance
            print("\nFeature importance:")
            for feature, importance in zip(features, self.model.feature_importances_):
                print(f"{feature}: {importance:.4f}")
            
            return True
        
        except Exception as e:
            print(f"\nError training model: {str(e)}")
            traceback.print_exc()
            return False

    def predict_next_race(self):
        """Predict the winner of the next race"""
        try:
            print("\nStarting prediction for next race...")
            
            # Get current date from system
            current_date = pd.Timestamp.now()
            current_year = current_date.year
            print(f"\nCurrent date: {current_date}")
            
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
            prediction_data['Year'] = next_race['EventDate'].year  # Add year feature
            prediction_data['DriverNumber'] = pd.to_numeric(last_quali.results['DriverNumber'], errors='coerce')
            
            # Handle NaN values in prediction data
            features = ['QualifyingPosition', 'RoundNumber', 'Year']
            prediction_features = prediction_data[features]
            
            prediction_features = pd.DataFrame(self.imputer.transform(prediction_features), columns=features)
            
            # Make predictions
            predictions = self.model.predict(prediction_features)
            
            # Add predictions to the data
            prediction_data['PredictedPosition'] = predictions
            
            # Merge with current driver information
            final_predictions = pd.merge(
                prediction_data,
                drivers_df,
                on='DriverNumber',
                how='left'
            )
            
            # Sort by predicted position
            final_predictions = final_predictions.sort_values('PredictedPosition')
            
            result = {
                'race_name': next_race['EventName'],
                'race_date': next_race['EventDate'].strftime('%Y-%m-%d'),
                'predicted_winner': {
                    'name': final_predictions.iloc[0]['FullName'],
                    'team': final_predictions.iloc[0]['TeamName'],
                    'abbreviation': final_predictions.iloc[0]['Abbreviation'],
                    'position': int(final_predictions.iloc[0]['PredictedPosition'])
                },
                'top_3': [
                    {
                        'name': row['FullName'],
                        'team': row['TeamName'],
                        'abbreviation': row['Abbreviation'],
                        'position': int(row['PredictedPosition'])
                    }
                    for _, row in final_predictions.head(3).iterrows()
                ]
            }
            
            print("\nPrediction result:")
            print(f"Race: {result['race_name']} on {result['race_date']}")
            print(f"Predicted Winner: {result['predicted_winner']['name']} ({result['predicted_winner']['team']})")
            print("\nTop 3 Predictions:")
            for pos, driver in enumerate(result['top_3'], 1):
                print(f"{pos}. {driver['name']} ({driver['team']})")
            
            return result
            
        except Exception as e:
            print(f"\nError making prediction: {str(e)}")
            traceback.print_exc()
            return None
        
    def print_to_json(self, data, filename):
        """Print the data to a json file"""
        # Print the data to a json file
        path_to_file = f"/Users/daniyalshahid/Desktop/personal projects/f1-winners/f1-prediction-app/backend/data/{filename}.json"
        with open(path_to_file, 'w') as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
        print(f"Data printed to {path_to_file}")

# Usage example
if __name__ == "__main__":
    predictor = F1Predictor()
    data_folder = pathlib.Path('/Users/daniyalshahid/Desktop/personal projects/f1-winners/f1-prediction-app/backend/data')
    print("\nChecking for existing predictions...")

    # Get the next race name first (without running the full model)
    current_date = pd.Timestamp.now()
    schedule_2025 = fastf1.get_event_schedule(2025)
    race_schedule = schedule_2025[schedule_2025['EventName'] != 'Pre-Season Testing']
    next_race = race_schedule[race_schedule['EventDate'] > current_date].iloc[0]
    next_race_name = next_race['EventName']
    
    # Check if prediction already exists
    prediction_file = data_folder / f"{next_race_name}.json"
    
    if prediction_file.exists():
        print(f"\nFound existing prediction for {next_race_name}")
        print("Do you want to generate a new prediction? (y/n)")
        regenerate = input().lower()
        
        if regenerate != 'y':
            # Load and display existing prediction
            print(f"\nLoading existing prediction for {next_race_name}...")
            with open(prediction_file, 'r') as f:
                prediction = json.load(f)
            print("\nPrediction details:")
            print(f"Race: {prediction['race_name']} on {prediction['race_date']}")
            print(f"Predicted Winner: {prediction['predicted_winner']['name']} ({prediction['predicted_winner']['team']})")
            print("\nTop 3 Predictions:")
            for pos, driver in enumerate(prediction['top_3'], 1):
                print(f"{pos}. {driver['name']} ({driver['team']})")
        else:
            # Generate new prediction
            print("\n=== Starting Model Training ===")
            training_success = predictor.train_model()
            
            if training_success:
                print("\n=== Making New Predictions ===")
                prediction = predictor.predict_next_race()
                if prediction:
                    print("\nSaving new prediction to file...")
                    predictor.print_to_json(prediction, prediction['race_name'])
            else:
                print("\nTraining failed, cannot make predictions.")
    else:
        # No existing prediction found, generate new one
        print(f"\nNo existing prediction found for {next_race_name}")
        print("\n=== Starting Model Training ===")
        training_success = predictor.train_model()
        
        if training_success:
            print("\n=== Making Predictions ===")
            prediction = predictor.predict_next_race()
            if prediction:
                print("\nSaving prediction to file...")
                predictor.print_to_json(prediction, prediction['race_name'])
        else:
            print("\nTraining failed, cannot make predictions.")

