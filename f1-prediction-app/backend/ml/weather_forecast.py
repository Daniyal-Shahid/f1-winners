import pandas as pd
import numpy as np
import fastf1
import traceback
from sklearn.preprocessing import StandardScaler

def get_weather_data(year, round_number, session_type='Race'):
    """ 
    Get weather data for a specific race
    
    Args:
        year (int): Year of the race
        round_number (int): Round number of the race
        session_type (str): Session type ('Race', 'Qualifying', etc.)

    Returns:
        dict: Aggregated weather features for the race
    """
    try:
        # Get the race session
        session = fastf1.get_session(year, round_number, session_type)
        session.load()
        
        # Get weather data
        weather_data = session.weather_data
        
        if weather_data is None or weather_data.empty:
            print(f"No weather data found for {year} round {round_number}")
            return create_default_weather_features()
        
        # Process and return aggregated weather features
        return extract_weather_features(weather_data)
        
    except Exception as e:
        print(f"Error getting weather data: {str(e)}")
        traceback.print_exc()
        return create_default_weather_features()

def extract_weather_features(weather_data):
    """
    Extract relevant weather features from weather data
    
    Args:
        weather_data (DataFrame): Raw weather data

    Returns:
        dict: Aggregated weather features
    """
    # Ensure we have the needed columns
    required_columns = ['AirTemp', 'Humidity', 'Pressure', 'WindSpeed', 'WindDirection', 'Rainfall']
    
    # Check which columns are available
    available_columns = [col for col in required_columns if col in weather_data.columns]
    
    if not available_columns:
        print("No usable weather columns found")
        return create_default_weather_features()
    
    # Initialize features dictionary
    features = {}
    
    # Process available columns
    if 'AirTemp' in available_columns:
        features['MeanTemp'] = weather_data['AirTemp'].mean()
        features['MaxTemp'] = weather_data['AirTemp'].max()
        features['MinTemp'] = weather_data['AirTemp'].min()
        features['TempRange'] = features['MaxTemp'] - features['MinTemp']
    
    if 'Humidity' in available_columns:
        features['MeanHumidity'] = weather_data['Humidity'].mean()
        features['MaxHumidity'] = weather_data['Humidity'].max()
    
    if 'Pressure' in available_columns:
        features['MeanPressure'] = weather_data['Pressure'].mean()
        features['PressureChange'] = weather_data['Pressure'].max() - weather_data['Pressure'].min()
    
    if 'WindSpeed' in available_columns:
        features['MeanWindSpeed'] = weather_data['WindSpeed'].mean()
        features['MaxWindSpeed'] = weather_data['WindSpeed'].max()
    
    if 'WindDirection' in available_columns:
        # Convert wind direction to sine and cosine components for circular feature
        rad = np.deg2rad(weather_data['WindDirection'])
        features['WindDirSin'] = np.sin(rad).mean()
        features['WindDirCos'] = np.cos(rad).mean()
    
    if 'Rainfall' in available_columns:
        features['TotalRainfall'] = weather_data['Rainfall'].sum()
        features['MaxRainfall'] = weather_data['Rainfall'].max()
        features['RainyCondition'] = 1 if features['TotalRainfall'] > 0 else 0
    
    # Derived weather conditions
    features['WetTrack'] = 1 if ('TotalRainfall' in features and features['TotalRainfall'] > 0) else 0
    
    # Classify weather conditions
    features['WeatherCondition'] = classify_weather_condition(features)
    
    return features

def classify_weather_condition(features):
    """
    Classify weather into categories based on features
    
    Args:
        features (dict): Weather features

    Returns:
        int: Weather condition category
            0: Dry and moderate
            1: Hot and dry
            2: Cold and dry
            3: Light rain
            4: Heavy rain
            5: Windy
    """
    # Default to dry and moderate
    condition = 0
    
    if 'TotalRainfall' in features:
        if features['TotalRainfall'] > 2.0:
            condition = 4  # Heavy rain
        elif features['TotalRainfall'] > 0:
            condition = 3  # Light rain
    
    if 'MeanWindSpeed' in features and features['MeanWindSpeed'] > 20:
        condition = 5  # Windy takes precedence if very windy
    
    if condition == 0 and 'MeanTemp' in features:  # Only classify temperature if it's dry
        if features['MeanTemp'] > 30:
            condition = 1  # Hot
        elif features['MeanTemp'] < 15:
            condition = 2  # Cold
    
    return condition

def create_default_weather_features():
    """
    Create default weather features when data is not available
    
    Returns:
        dict: Default weather features
    """
    return {
        'MeanTemp': 22.0,         # Average temperature
        'MaxTemp': 25.0,
        'MinTemp': 20.0,
        'TempRange': 5.0,
        'MeanHumidity': 50.0,
        'MaxHumidity': 60.0,
        'MeanPressure': 1013.0,
        'PressureChange': 2.0,
        'MeanWindSpeed': 10.0,
        'MaxWindSpeed': 15.0,
        'WindDirSin': 0.0,
        'WindDirCos': 1.0,
        'TotalRainfall': 0.0,
        'MaxRainfall': 0.0,
        'RainyCondition': 0,
        'WetTrack': 0,
        'WeatherCondition': 0     # Default: dry and moderate
    }

def get_weather_features_for_dataset(race_data):
    """
    Get weather features for a dataset of races
    
    Args:
        race_data (DataFrame): DataFrame with Year and RoundNumber columns

    Returns:
        DataFrame: Original data with added weather features
    """
    print("\nExtracting weather features for dataset...")
    result_data = race_data.copy()
    
    # Initialize weather feature columns
    weather_features = create_default_weather_features()
    for feature in weather_features:
        result_data[f'Weather_{feature}'] = None
    
    # Group by Year and RoundNumber to process each race once
    for (year, round_num), group in race_data.groupby(['Year', 'RoundNumber']):
        print(f"Getting weather for {year} round {round_num}")
        
        # Get weather features for this race
        weather = get_weather_data(year, round_num)
        
        # Update rows for this race with weather features
        race_indices = group.index
        for feature, value in weather.items():
            result_data.loc[race_indices, f'Weather_{feature}'] = value
    
    # Convert to numeric and fill missing values
    for feature in weather_features:
        result_data[f'Weather_{feature}'] = pd.to_numeric(result_data[f'Weather_{feature}'], errors='coerce')
        # If any values are still missing, fill with defaults
        if result_data[f'Weather_{feature}'].isna().any():
            result_data[f'Weather_{feature}'].fillna(weather_features[feature], inplace=True)
    
    print(f"Added {len(weather_features)} weather features to dataset")
    return result_data

def normalise_weather_features(data, scaler=None, fit=True):
    """
    Normalise weather features to have zero mean and unit variance
    
    Args:
        data (DataFrame): Data with weather features
        scaler (StandardScaler, optional): Pre-fitted scaler to use
        fit (bool): Whether to fit the scaler on this data

    Returns:
        tuple: (DataFrame with normalised features, fitted scaler)
    """
    # Get list of weather feature columns
    weather_cols = [col for col in data.columns if col.startswith('Weather_')]
    
    if not weather_cols:
        print("No weather features found to normalize")
        return data, None
    
    # Create new scaler if not provided
    if scaler is None:
        scaler = StandardScaler()
    
    # Extract features to normalise
    features_to_normalise = data[weather_cols].copy()
    
    # Fit or transform
    if fit:
        normalised_features = scaler.fit_transform(features_to_normalise)
    else:
        normalised_features = scaler.transform(features_to_normalise)
    
    # Replace original features with normalised ones
    data_normalised = data.copy()
    data_normalised[weather_cols] = normalised_features
    
    return data_normalised, scaler