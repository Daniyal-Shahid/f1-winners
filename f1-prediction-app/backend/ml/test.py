import fastf1

# Enable caching for faster data retrieval
fastf1.Cache.enable_cache('/Users/daniyalshahid/Desktop/personal projects/f1-winners/f1-prediction-app/backend/cache') 

# Load a specific race session (e.g., 2024 Bahrain GP - Race)
session = fastf1.get_session(2024, "Bahrain", "Race")
session.load()

# Get driver information
drivers_info = session.drivers  # List of driver numbers
print("Driver Numbers:", drivers_info)

# Get full driver details (team, name, abbreviation, etc.)
drivers_data = session.results[['Abbreviation', 'FullName', 'TeamName']]
print(drivers_data)
