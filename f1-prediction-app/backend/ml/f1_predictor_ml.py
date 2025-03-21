import os
import pathlib
import fastf1
import pandas as pd
import warnings
import json
import traceback
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.preprocessing import LabelEncoder
from sklearn.impute import SimpleImputer

# Import module functions
from prepare_race_data import prepare_race_data
from performance_metrics import calculate_performance_metrics
from train_model import train_model
from predict_next_race import predict_next_race
from feature_engineering import enhance_with_performance_metrics

# Suppress warnings
warnings.filterwarnings('ignore')

class F1Predictor:
    def __init__(self, cache_path=None):
        """Initialise the F1 prediction model
        
        Args:
            cache_path (str, optional): Path to FastF1 cache. Defaults to './cache'.
        """
        # Enable caching
        if cache_path is None:
            cache_path = '/Users/daniyalshahid/Desktop/personal projects/f1-winners/f1-prediction-app/backend/cache'
        
        fastf1.Cache.enable_cache(cache_path)
        
        # Initialise model components
        self.label_encoder = LabelEncoder()
        self.imputer = SimpleImputer(strategy='mean')
        self.model = GradientBoostingClassifier(
            n_estimators=100,
            learning_rate=0.1,
            max_depth=3,
            random_state=42
        )
        self.feature_names = []  # Will be populated during training
        self.weather_scaler = None  # Will be populated during training

    def prepare_race_data(self, years=None):
        """Prepare training data from FastF1 for multiple seasons
    
        Args:
            years (list): List of years to include (default: [2021, 2022, 2023, 2024])
            
        Returns:
            DataFrame: Processed race data
        """
        return prepare_race_data(self, years)
    
    def calculate_performance_metrics(self, years=None):
        """Calculate performance metrics for drivers and teams
        
        Args:
            years (list): List of years to include
        
        Returns:
            tuple: (driver_stats, team_stats) DataFrames
        """
        return calculate_performance_metrics(self, years)

    def train_model(self):
        """Train the gradient boosting model with enhanced features
        
        Returns:
            bool: True if training was successful, False otherwise
        """
        return train_model(self)
        
    def predict_next_race(self):
        """Predict the winner of the next race using enhanced features
        
        Returns:
            dict: Prediction results with race details and driver predictions
        """
        return predict_next_race(self)
    
    def enhance_with_performance_metrics(self, base_data):
        """Add performance metrics to the base data
        
        Args:
            base_data (DataFrame): The base data with DriverNumber and Team columns
        
        Returns:
            DataFrame: Enhanced data with performance metrics
        """
        return enhance_with_performance_metrics(self, base_data)
        
    def print_to_json(self, data, filename, data_folder=None):
        """Print the data to a JSON file
        
        Args:
            data (dict): Data to save
            filename (str): Name of the file (without extension)
            data_folder (str, optional): Folder to save the file. Defaults to backend/data.
        """
        if data_folder is None:
            data_folder = os.path.join(os.path.dirname(__file__), '..', 'data')
        
        path_to_file = f"{data_folder}/{filename}.json"
        with open(path_to_file, 'w') as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
        print(f"Data printed to {path_to_file}")


def main():
    """Main entry point for the F1 prediction application"""
    predictor = F1Predictor()
    data_folder = pathlib.Path('/Users/daniyalshahid/Desktop/personal projects/f1-winners/f1-prediction-app/backend/data')
    print("\nChecking for existing predictions...")

    try:
        # Get the next race name (without running the full model)
        current_date = pd.Timestamp.now()
        schedule_2025 = fastf1.get_event_schedule(2025)
        race_schedule = schedule_2025[schedule_2025['EventName'] != 'Pre-Season Testing']
        next_races = race_schedule[race_schedule['EventDate'] > current_date]
                
        if next_races.empty:
            print("No more races scheduled for this season")
            return
                
        next_race = next_races.iloc[0]
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
                generate_new_prediction(predictor, next_race_name)
        else:
            print(f"\nNo existing prediction found for {next_race_name}")
            generate_new_prediction(predictor, next_race_name)
                
    except Exception as e:
        print(f"Error during prediction process: {str(e)}")
        traceback.print_exc()


def generate_new_prediction(predictor, race_name):
    """Generate and save a new prediction
    
    Args:
        predictor (F1Predictor): Predictor instance
        race_name (str): Race name for filename
    """
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


if __name__ == "__main__":
    main()

