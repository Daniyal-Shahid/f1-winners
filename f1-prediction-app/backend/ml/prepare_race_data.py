import pandas as pd
import fastf1
import traceback
from weather_forecast import get_weather_features_for_dataset

def prepare_race_data(predictor, years=None):
    """Prepare training data from FastF1 for multiple seasons
    
    Args:
        predictor: F1Predictor instance
        years (list): List of years to include (default: [2021, 2022, 2023, 2024])
        
    Returns:
        DataFrame: Processed race data
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
                
                # Extract qualifying positions WITH team name
                quali_results = quali_session.results[['DriverNumber', 'Position', 'TeamName']]
                quali_results = quali_results.rename(columns={
                    'Position': 'QualifyingPosition', 
                    'TeamName': 'Team'
                })
                
                # Get race results WITH team name
                race_results = race_session.results[['DriverNumber', 'Position', 'Points', 'TeamName']]
                race_results = race_results.rename(columns={'TeamName': 'Team'})
                
                # Convert Position columns to numeric
                quali_results['QualifyingPosition'] = pd.to_numeric(quali_results['QualifyingPosition'], errors='coerce')
                race_results['Position'] = pd.to_numeric(race_results['Position'], errors='coerce')
                
                # Merge qualifying and race data - including Team in the merge
                merged_data = pd.merge(
                    race_results, 
                    quali_results, 
                    on=['DriverNumber', 'Team'], 
                    how='outer'
                )
                
                # Add race information
                merged_data['Track'] = race['EventName']
                merged_data['RoundNumber'] = race['RoundNumber']
                merged_data['Year'] = year
                merged_data['CircuitId'] = race['OfficialEventName']
                
                all_data.append(merged_data)
                
            except Exception as e:
                print(f"Error processing race {race['EventName']}: {str(e)}")
                traceback.print_exc()
                continue
    
    if not all_data:
        raise ValueError("No race data available for training")
            
    final_data = pd.concat(all_data, ignore_index=True)
    
    # Drop rows where Position (target variable) is NaN
    final_data = final_data.dropna(subset=['Position'])
    
    # Add weather features if requested
    final_data = get_weather_features_for_dataset(final_data)
    
    print("\nFinal dataset info:")
    print(f"Total races: {len(all_data)}")
    print(f"Total data points: {len(final_data)}")
    print(f"Years included: {final_data['Year'].unique()}")
    print(f"Columns: {final_data.columns.tolist()}")
    
    return final_data