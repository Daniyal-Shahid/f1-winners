import traceback
import pandas as pd
import numpy as np
import fastf1
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, classification_report
from weather_forecast import normalise_weather_features

def train_model(predictor):
    """Train the gradient boosting model with enhanced features
    
    Args:
        predictor: F1Predictor instance
        
    Returns:
        bool: True if training was successful, False otherwise
    """
    try:
        # Get training data from multiple seasons
        print("\nPreparing training data...")
        data = predictor.prepare_race_data()
        
        # Use robust feature engineering instead of merges
        enhanced_data = predictor.enhance_with_performance_metrics(data)
        
        # Normalise weather features 
        enhanced_data, weather_scaler = normalise_weather_features(enhanced_data)
        predictor.weather_scaler = weather_scaler
        
        # Define expanded feature set
        features = [
            # Base features
            'QualifyingPosition', 'RoundNumber', 'Year',
            
            # Driver performance features
            'AvgPosition', 'WinRate', 'PodiumRate', 'PointsPerRace', 
            'RecentAvgPosition', 'RecentWinRate', 'RecentPodiumRate',
            
            # Team performance features
            'AvgPosition_team_stats', 'WinRate_team_stats', 
            'PointsPerRace_team_stats', 'RecentAvgPosition_team_stats'
        ]
        
        # Add weather features 
        weather_features = [col for col in enhanced_data.columns if col.startswith('Weather_')]
        features.extend(weather_features)
        
        # Make sure all features exist in the dataframe
        available_features = [f for f in features if f in enhanced_data.columns]
        print(f"\nUsing features: {available_features}")
        
        if len(available_features) < len(features):
            missing = set(features) - set(enhanced_data.columns)
            print(f"Warning: Missing these features: {missing}")
            
            # Add missing features with zeros
            for feature in missing:
                enhanced_data[feature] = 0
                available_features.append(feature)
        
        X = enhanced_data[available_features]
        y = enhanced_data['Position']  # Position 1 is the winner
        
        print("\nFeature matrix shape:", X.shape)
        print("Target vector shape:", y.shape)
        
        # Handle NaN values
        print("\nImputing missing values...")
        X = pd.DataFrame(predictor.imputer.fit_transform(X), columns=available_features)
        
        # Split the data
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42
        )
        
        # Configure a more robust model
        predictor.model = GradientBoostingClassifier(
            n_estimators=200,         # Increased for more complex features
            learning_rate=0.1,
            max_depth=5,              # Increased to capture weather interactions
            min_samples_split=10,
            min_samples_leaf=4,
            subsample=0.9,            # Added to reduce overfitting
            random_state=42
        )
        
        # Train the model
        print("\nTraining enhanced model with weather features...")
        predictor.model.fit(X_train, y_train)
        
        # Evaluate the model
        y_pred = predictor.model.predict(X_test)
        accuracy = accuracy_score(y_test, y_pred)
        print(f"\nModel accuracy: {accuracy:.2f}")
        
        # Feature importance
        print("\nFeature importance:")
        importance_data = sorted(zip(available_features, predictor.model.feature_importances_), 
                                key=lambda x: x[1], reverse=True)
        for feature, importance in importance_data:
            print(f"{feature}: {importance:.4f}")
        
        # Store feature names for prediction
        predictor.feature_names = available_features
        
        return True
        
    except Exception as e:
        print(f"\nError training model: {str(e)}")
        traceback.print_exc()
        return False
