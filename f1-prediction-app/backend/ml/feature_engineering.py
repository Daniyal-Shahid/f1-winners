import pandas as pd

def enhance_with_performance_metrics(predictor, base_data):
    """
    A more robust way to add performance metrics to the base data
    
    Args:
        predictor: F1Predictor instance
        base_data (DataFrame): The base data with DriverNumber and Team columns
    
    Returns:
        DataFrame: Enhanced data with performance metrics
    """
    # Get performance metrics
    driver_stats, team_stats = predictor.calculate_performance_metrics()
    
    # Make a copy to avoid modifying the original
    enhanced_data = base_data.copy()
    
    # Ensure DriverNumber is numeric type
    enhanced_data['DriverNumber'] = pd.to_numeric(enhanced_data['DriverNumber'], errors='coerce')
    driver_stats['DriverNumber'] = pd.to_numeric(driver_stats['DriverNumber'], errors='coerce')
    
    # Print column names for debugging
    print("\nColumns in data:", enhanced_data.columns.tolist())
    
    # Create dictionaries for faster lookups
    driver_metrics = {driver_num: {} for driver_num in driver_stats['DriverNumber']}
    for _, row in driver_stats.iterrows():
        driver_num = row['DriverNumber']
        for col in driver_stats.columns:
            if col != 'DriverNumber':
                driver_metrics[driver_num][col] = row[col]
    
    team_metrics = {team_name: {} for team_name in team_stats['Team']}
    for _, row in team_stats.iterrows():
        team_name = row['Team']
        for col in team_stats.columns:
            if col != 'Team':
                team_metrics[team_name][col] = row[col]
    
    # Add driver metrics
    for metric in driver_stats.columns:
        if metric != 'DriverNumber':
            enhanced_data[metric] = enhanced_data['DriverNumber'].apply(
                lambda x: driver_metrics.get(x, {}).get(metric, 0) if pd.notna(x) else 0
            )
    
    # Add team metrics with team_stats suffix
    if 'Team' in enhanced_data.columns:
        for metric in team_stats.columns:
            if metric != 'Team':
                enhanced_data[f"{metric}_team_stats"] = enhanced_data['Team'].apply(
                    lambda x: team_metrics.get(x, {}).get(metric, 0) if pd.notna(x) and isinstance(x, str) else 0
                )
    elif 'CurrentTeam' in enhanced_data.columns:
        enhanced_data['Team'] = enhanced_data['CurrentTeam']
        for metric in team_stats.columns:
            if metric != 'Team':
                enhanced_data[f"{metric}_team_stats"] = enhanced_data['Team'].apply(
                    lambda x: team_metrics.get(x, {}).get(metric, 0) if pd.notna(x) and isinstance(x, str) else 0
                )
    else:
        print("Warning: No Team column found, team metrics not added")
        
        # Try to add Team from driver stats
        if 'DriverNumber' in enhanced_data.columns:
            print("Adding Team from driver stats")
            enhanced_data['Team'] = enhanced_data['DriverNumber'].apply(
                lambda x: driver_metrics.get(x, {}).get('CurrentTeam', 'Unknown') if pd.notna(x) else 'Unknown'
            )
            
            # Now try to add team metrics again
            for metric in team_stats.columns:
                if metric != 'Team':
                    enhanced_data[f"{metric}_team_stats"] = enhanced_data['Team'].apply(
                        lambda x: team_metrics.get(x, {}).get(metric, 0) if pd.notna(x) and isinstance(x, str) else 0
                    )
    
    return enhanced_data 