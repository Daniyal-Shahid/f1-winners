"""Common utilities and shared functions to avoid circular imports"""
import pandas as pd
import numpy as np
import fastf1
import traceback
import os
import json

def setup_fastf1_cache(cache_path=None):
    """Set up the FastF1 cache"""
    if cache_path is None:
        cache_path = './cache'
    fastf1.Cache.enable_cache(cache_path)

def save_to_json(data, file_path):
    """Save data to a JSON file"""
    with open(file_path, 'w') as f:
        json.dump(data, f, indent=4, ensure_ascii=False)
    print(f"Data saved to {file_path}")

def load_from_json(file_path):
    """Load data from a JSON file"""
    if os.path.exists(file_path):
        with open(file_path, 'r') as f:
            return json.load(f)
    return None

# Weather condition mapping that can be used across modules
WEATHER_CONDITIONS = {
    0: "Dry and moderate",
    1: "Hot and dry",
    2: "Cold and dry",
    3: "Light rain",
    4: "Heavy rain", 
    5: "Windy"
}

# Add any other shared functions or constants here 