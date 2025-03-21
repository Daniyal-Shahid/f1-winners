import os
import openmeteo_requests
import requests
import requests_cache
import fastf1
import pandas as pd
import json
from retry_requests import retry
import traceback
import numpy as np

# Setup the Open-Meteo API client with cache and retry on error
cache_session = requests_cache.CachedSession('.cache', expire_after=3600)
retry_session = retry(cache_session, retries=5, backoff_factor=0.2)
openmeteo = openmeteo_requests.Client(session=retry_session)

def get_f1_circuits():
    """
    Get all F1 circuits data from the Jolpica-F1 API
    
    Returns:
        list: List of circuit dictionaries with location information
    """
    try:
        url = "http://api.jolpi.ca/ergast/f1/2025/circuits/"
        response = requests.get(url)
        data = response.json()
        
        # Handle the proper JSON structure
        if 'CircuitTable' in data and 'Circuits' in data['CircuitTable']:
            return data['CircuitTable']['Circuits']
        else:
            print("Unexpected API response structure:", data)
            return []
    except Exception as e:
        print(f"Error fetching circuit data: {str(e)}")
        traceback.print_exc()
        return []

def get_next_race_info():
    """
    Get information about the next race in the F1 calendar
    
    Returns:
        tuple: (next_race, circuit_data) containing race information and circuit details
    """
    try:
        # Get the next race from FastF1
        current_date = pd.Timestamp.now()
        schedule = fastf1.get_event_schedule(2025)  # Use current year for production
        race_schedule = schedule[schedule['EventName'] != 'Pre-Season Testing']
        next_races = race_schedule[race_schedule['EventDate'] > current_date]
        
        if len(next_races) == 0:  # Use len() instead of .empty for DataFrames
            print("No more races scheduled for this season")
            return None, None
        
        next_race = next_races.iloc[0]
        event_name = next_race['EventName']
        print(f"Next race: {event_name} on {next_race['EventDate']}")
        
        # Get circuit information
        circuits = get_f1_circuits()
        
        # Create a manual mapping for known mismatches
        circuit_mapping = {
            "Chinese Grand Prix": "shanghai",
            "British Grand Prix": "silverstone",
            "Monaco Grand Prix": "monaco",
            "Belgian Grand Prix": "spa",
            "Italian Grand Prix": "monza",
            "Singapore Grand Prix": "marina_bay",
            "Japanese Grand Prix": "suzuka",
            "United States Grand Prix": "americas",
            "Mexico City Grand Prix": "rodriguez",
            "São Paulo Grand Prix": "interlagos",
            "Las Vegas Grand Prix": "vegas",
            "Qatar Grand Prix": "losail",
            "Abu Dhabi Grand Prix": "yas_marina"
            # Add more mappings as needed
        }
        
        # Try to find circuit using the mapping first
        circuit_id = circuit_mapping.get(event_name)
        if circuit_id:
            # Find circuit by ID
            circuit_data = next((c for c in circuits if c['circuitId'] == circuit_id), None)
            if circuit_data:
                print(f"Found circuit using mapping: {circuit_data['circuitName']} in {circuit_data['Location']['locality']}, {circuit_data['Location']['country']}")
                return next_race, circuit_data
        
        # If no mapping or mapping didn't find a circuit, try the fuzzy matching
        circuit_data = match_circuit_to_race(next_race, circuits)
        
        if circuit_data:
            print(f"Circuit: {circuit_data['circuitName']} in {circuit_data['Location']['locality']}, {circuit_data['Location']['country']}")
            return next_race, circuit_data
        else:
            print(f"Could not find circuit data for {event_name}")
            
            # Last resort: Default coordinates for common circuits
            # This is a crude fallback but better than failing completely
            default_coords = {
                "Chinese Grand Prix": {"lat": 31.3389, "long": 121.22, "name": "Shanghai International Circuit", "locality": "Shanghai", "country": "China"},
                "British Grand Prix": {"lat": 52.0786, "long": -1.01694, "name": "Silverstone Circuit", "locality": "Silverstone", "country": "UK"},
                # Add more defaults as needed
            }
            
            if event_name in default_coords:
                coords = default_coords[event_name]
                print(f"Using default coordinates for {event_name}: {coords['name']}")
                # Create a minimal circuit data structure
                circuit_data = {
                    "circuitId": event_name.lower().replace(" ", "_"),
                    "circuitName": coords["name"],
                    "Location": {
                        "lat": str(coords["lat"]),
                        "long": str(coords["long"]),
                        "locality": coords["locality"],
                        "country": coords["country"]
                    }
                }
                return next_race, circuit_data
            
            return next_race, None
    
    except Exception as e:
        print(f"Error getting next race info: {str(e)}")
        traceback.print_exc()
        return None, None

def match_circuit_to_race(race, circuits):
    """
    Match a race to its circuit data by comparing names
    
    Args:
        race: FastF1 race information
        circuits: List of circuit dictionaries from Jolpica API
    
    Returns:
        dict: Circuit data if found, None otherwise
    """
    # Check if race is a DataFrame or Series and extract the event name
    if hasattr(race, 'EventName'):
        race_name = race['EventName']
    else:
        race_name = str(race)
    
    race_name = race_name.lower()
    
    # Special case handling for known problematic races
    if "chinese" in race_name:
        search_terms = ["shanghai", "china"]
    elif "british" in race_name:
        search_terms = ["silverstone", "uk", "great britain", "united kingdom"]
    elif "united states" in race_name or "us " in race_name:
        search_terms = ["americas", "austin", "texas", "usa"]
    else:
        # Extract key words from race name
        search_terms = [word for word in race_name.split() if len(word) > 3 and word not in ["grand", "prix"]]
    
    # Print the search terms for debugging
    print(f"Searching for circuit with terms: {search_terms}")
    
    # Try direct match on circuit names
    for circuit in circuits:
        circuit_name = circuit['circuitName'].lower()
        circuit_id = circuit['circuitId'].lower()
        
        # Check all search terms
        for term in search_terms:
            if term in circuit_name or term in circuit_id:
                print(f"Matched '{term}' in circuit: {circuit['circuitName']}")
                return circuit
            
    # Try matching by location/country
    for circuit in circuits:
        if 'Location' in circuit and 'country' in circuit['Location']:
            country = circuit['Location']['country'].lower()
            locality = circuit['Location']['locality'].lower()
            
            # Check all search terms against location
            for term in search_terms:
                if term in country or term in locality:
                    print(f"Matched '{term}' in location: {locality}, {country}")
                    return circuit
    
    # If still not found, try a broader approach
    # Convert spaces to underscores and lowercase
    normalized_race_name = race_name.replace(' ', '_').lower()
    for circuit in circuits:
        circuit_id = circuit['circuitId'].lower()
        # Get just the country name
        country = circuit['Location']['country'].lower()
        
        # Check if any part of the circuit ID is in the race name
        for part in circuit_id.split('_'):
            if part in race_name and len(part) > 3:  # Avoid short matches like "de", "of", etc.
                print(f"Matched '{part}' in race name: {race_name}")
                return circuit
                
        # Check country name against race name
        if country in race_name:
            print(f"Matched country '{country}' in race name: {race_name}")
            return circuit
    
    return None

def get_weather_forecast(latitude, longitude, days=3):
    """
    Get weather forecast data from Open-Meteo API
    
    Args:
        latitude (float): Latitude of the circuit
        longitude (float): Longitude of the circuit
        days (int): Number of forecast days to retrieve
    
    Returns:
        dict: Weather forecast data
    """
    try:
        url = "https://api.open-meteo.com/v1/forecast"
        params = {
            "latitude": latitude,
            "longitude": longitude,
            "hourly": ["temperature_2m", "relative_humidity_2m", "surface_pressure", 
                      "rain", "precipitation", "showers", "precipitation_probability", 
                      "wind_speed_10m", "wind_direction_10m", "wind_gusts_10m", 
                      "is_day", "sunshine_duration"]
        }
        responses = openmeteo.weather_api(url, params=params)
        return process_weather_data(responses)
    
    except Exception as e:
        print(f"Error getting weather forecast: {str(e)}")
        traceback.print_exc()
        return None

def process_weather_data(responses):
    """
    Process weather data from Open-Meteo API and extract F1-relevant features
    
    Args:
        responses: Open-Meteo API responses
    
    Returns:
        dict: Extracted weather features
    """
    try:
        # Process first location
        response = responses[0]
        print(f"Weather forecast for coordinates {response.Latitude()}°N {response.Longitude()}°E")
        
        # Process hourly data
        hourly = response.Hourly()
        hourly_data = {
            "date": pd.date_range(
                start=pd.to_datetime(hourly.Time(), unit="s", utc=True),
                end=pd.to_datetime(hourly.TimeEnd(), unit="s", utc=True),
                freq=pd.Timedelta(seconds=hourly.Interval()),
                inclusive="left"
            ),
            "temperature_2m": hourly.Variables(0).ValuesAsNumpy(),
            "relative_humidity_2m": hourly.Variables(1).ValuesAsNumpy(),
            "surface_pressure": hourly.Variables(2).ValuesAsNumpy(),
            "rain": hourly.Variables(3).ValuesAsNumpy(),
            "precipitation": hourly.Variables(4).ValuesAsNumpy(),
            "showers": hourly.Variables(5).ValuesAsNumpy(),
            "precipitation_probability": hourly.Variables(6).ValuesAsNumpy(),
            "wind_speed_10m": hourly.Variables(7).ValuesAsNumpy(),
            "wind_direction_10m": hourly.Variables(8).ValuesAsNumpy(),
            "wind_gusts_10m": hourly.Variables(9).ValuesAsNumpy(),
            "is_day": hourly.Variables(10).ValuesAsNumpy(),
            "sunshine_duration": hourly.Variables(11).ValuesAsNumpy()
        }
        
        # Convert to DataFrame for processing
        df = pd.DataFrame(data=hourly_data)
        
        # Calculate F1-relevant features
        features = {
            # Temperature features
            "MeanTemp": df["temperature_2m"].mean().round(1),
            "MaxTemp": df["temperature_2m"].max().round(1),
            "MinTemp": df["temperature_2m"].min().round(1),
            "TempRange": (df["temperature_2m"].max() - df["temperature_2m"].min()).round(1),
            
            # Humidity features
            "MeanHumidity": df["relative_humidity_2m"].mean().round(1),
            "MaxHumidity": df["relative_humidity_2m"].max().round(1),
            
            # Pressure features
            "MeanPressure": df["surface_pressure"].mean().round(1),
            "PressureChange": (df["surface_pressure"].max() - df["surface_pressure"].min()).round(1),
            
            # Wind features
            "MeanWindSpeed": df["wind_speed_10m"].mean().round(1),
            "MaxWindSpeed": df["wind_speed_10m"].max().round(1),
            "MaxWindGust": df["wind_gusts_10m"].max().round(1),
            
            # Wind direction as sine and cosine components
            "WindDirSin": np.sin(np.deg2rad(df["wind_direction_10m"])).mean().round(1),
            "WindDirCos": np.cos(np.deg2rad(df["wind_direction_10m"])).mean().round(1),
            
            # Precipitation features
            "TotalRainfall": df["rain"].sum().round(1),
            "MaxRainfall": df["rain"].max().round(1),
            "TotalPrecipitation": df["precipitation"].sum().round(1),
            "MeanPrecipitationProb": df["precipitation_probability"].mean().round(1),
            "MaxPrecipitationProb": df["precipitation_probability"].max().round(1),
            
            # Sunshine
            "TotalSunshine": df["sunshine_duration"].sum().round(1),
            
            # Derived weather conditions
            "RainyCondition": 1 if df["precipitation"].sum() > 0 else 0,
            "WetTrack": 1 if df["precipitation"].sum() > 1 else 0
        }
        
        # Classify weather conditions
        if features["TotalPrecipitation"] > 5:
            features["WeatherCondition"] = 4  # Heavy rain
        elif features["TotalPrecipitation"] > 0.5:
            features["WeatherCondition"] = 3  # Light rain
        elif features["MeanWindSpeed"] > 20:
            features["WeatherCondition"] = 5  # Windy
        elif features["MeanTemp"] > 30:
            features["WeatherCondition"] = 1  # Hot and dry
        elif features["MeanTemp"] < 15:
            features["WeatherCondition"] = 2  # Cold and dry
        else:
            features["WeatherCondition"] = 0  # Dry and moderate
        
        # Print weather summary
        weather_conditions = {
            0: "Dry and moderate",
            1: "Hot and dry",
            2: "Cold and dry",
            3: "Light rain",
            4: "Heavy rain",
            5: "Windy"
        }
        print(f"Weather forecast summary: {weather_conditions[features['WeatherCondition']]}")
        print(f"Average temperature: {features['MeanTemp']:.1f}°C")
        print(f"Precipitation probability: {features['MeanPrecipitationProb']:.1f}%")
        
        return features
    
    except Exception as e:
        print(f"Error processing weather data: {str(e)}")
        traceback.print_exc()
        return None

def get_race_weather_forecast():
    """
    Get weather forecast for the next F1 race
    
    Returns:
        dict: Weather features for the next race
    """
    next_race, circuit_data = get_next_race_info()
    
    # Check if next_race is None (directly, not using truth evaluation)
    if next_race is None:
        print("Could not get race information")
        return None
        
    # Check if circuit_data is None (directly, not using truth evaluation)
    if circuit_data is None:
        print("Could not get circuit information")
        return None
    
    if 'Location' not in circuit_data:
        print("Circuit data does not contain location information")
        return None
    
    # Get latitude and longitude
    latitude = float(circuit_data['Location']['lat'])
    longitude = float(circuit_data['Location']['long'])
    
    print(f"Getting weather forecast for {circuit_data['circuitName']} at coordinates {latitude}, {longitude}")
    
    # Get weather forecast
    weather_features = get_weather_forecast(latitude, longitude)
    
    if weather_features:
        # Add race information
        if hasattr(next_race, 'EventName'):
            race_name = next_race['EventName']
            race_date = next_race['EventDate'].strftime('%Y-%m-%d')
        else:
            # Fallback if next_race is not a pandas Series
            race_name = "Upcoming Race"
            race_date = "Unknown Date"
            
        weather_features['RaceName'] = race_name
        weather_features['RaceDate'] = race_date
        weather_features['CircuitName'] = circuit_data['circuitName']
        weather_features['Location'] = f"{circuit_data['Location']['locality']}, {circuit_data['Location']['country']}"
        
        return weather_features
    else:
        print("Could not get weather forecast")
        return None
    
def print_to_json(data, filename, data_folder=None):
    """Print the data to a JSON file
        
    Args:
        data (dict): Data to save
        filename (str): Name of the file (without extension)
        data_folder (str, optional): Folder to save the file. Defaults to backend/data.
    """
    if data_folder is None:
        data_folder = os.path.join(os.path.dirname(__file__), '..', 'data', 'weather')
    
    path_to_file = f"{data_folder}/{filename}.json"
    with open(path_to_file, 'w') as f:
        json.dump(str(data), f, indent=4, ensure_ascii=False)
    print(f"Data printed to {path_to_file}")


# Add __main__ function
if __name__ == "__main__":
    print("Getting F1 race weather forecast...")
    weather = get_race_weather_forecast()
    
    if weather:
        print("\nWeather forecast details:")
        for key, value in weather.items():
            if isinstance(value, float):
                print(f"{key}: {value:.2f}")
            else:
                print(f"{key}: {value}")
                
        # Save weather data to file
        print_to_json(weather, f"{weather['RaceName']}_weather")
        
    else:
        print("No weather forecast available")
        