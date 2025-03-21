import pandas as pd
import fastf1

def calculate_performance_metrics(self, years=None):
        """
        Calculate driver and team performance metrics across multiple seasons
        to use as additional features for prediction
        
        Args:
            years (list): List of years to include (default: [2021, 2022, 2023, 2024])
        
        Returns:
            tuple: (driver_stats_df, team_stats_df) DataFrames with performance metrics
        """
        if years is None:
            years = [2021, 2022, 2023, 2024]
        
        # Initialize containers for stats
        driver_results = []
        team_results = []
        
        print("\nCalculating performance metrics for drivers and teams...")
        
        for year in years:
            print(f"Processing {year} season for performance metrics")
            schedule = fastf1.get_event_schedule(year)
            
            # For current year, only use completed races
            if year == pd.Timestamp.now().year:
                races = schedule[schedule['EventDate'] < pd.Timestamp.now()]
            else:
                races = schedule
                
            # Skip test events
            races = races[~races['EventName'].str.contains('Test|testing', case=False)]
            
            for idx, race in races.iterrows():
                try:
                    # Load race data
                    race_session = fastf1.get_session(year, race['RoundNumber'], 'Race')
                    race_session.load()
                    
                    # Extract driver performance data
                    for _, driver_data in race_session.results.iterrows():
                        driver_result = {
                            'Year': year,
                            'RoundNumber': race['RoundNumber'],
                            'Track': race['EventName'],
                            'DriverNumber': driver_data['DriverNumber'],
                            'Driver': driver_data['FullName'],
                            'Team': driver_data['TeamName'],
                            'Position': driver_data['Position'],
                            'Points': driver_data['Points'],
                            'Status': driver_data['Status'],
                            'DNF': 1 if 'dnf' in str(driver_data['Status']).lower() else 0,
                            'FinishedRace': 0 if 'dnf' in str(driver_data['Status']).lower() else 1
                        }
                        driver_results.append(driver_result)
                        
                        # Collect team results in parallel
                        team_result = {
                            'Year': year,
                            'RoundNumber': race['RoundNumber'],
                            'Track': race['EventName'],
                            'Team': driver_data['TeamName'],
                            'Position': driver_data['Position'],
                            'Points': driver_data['Points']
                        }
                        team_results.append(team_result)
                        
                except Exception as e:
                    print(f"Error processing {race['EventName']} for metrics: {str(e)}")
                    continue
        
        # Convert to DataFrames
        driver_df = pd.DataFrame(driver_results)
        team_df = pd.DataFrame(team_results)
        
        # Make sure numeric columns are proper types
        numeric_cols = ['Position', 'Points', 'DNF', 'FinishedRace']
        for col in numeric_cols:
            if col in driver_df.columns:
                driver_df[col] = pd.to_numeric(driver_df[col], errors='coerce')
        
        team_df['Points'] = pd.to_numeric(team_df['Points'], errors='coerce')
        team_df['Position'] = pd.to_numeric(team_df['Position'], errors='coerce')
        
        # Calculate driver statistics
        driver_stats = []
        
        for driver_num in driver_df['DriverNumber'].unique():
            driver_data = driver_df[driver_df['DriverNumber'] == driver_num]
            
            if len(driver_data) == 0:
                continue
                
            # Get most recent driver name and team
            recent_data = driver_data.sort_values('Year', ascending=False).iloc[0]
            driver_name = recent_data['Driver']
            current_team = recent_data['Team']
            
            # Calculate overall stats
            avg_position = driver_data['Position'].mean()
            win_rate = len(driver_data[driver_data['Position'] == 1]) / len(driver_data)
            podium_rate = len(driver_data[driver_data['Position'] <= 3]) / len(driver_data)
            points_per_race = driver_data['Points'].mean()
            dnf_rate = driver_data['DNF'].mean()
            
            # Calculate recent form (last 10 races)
            recent_races = driver_data.sort_values(['Year', 'RoundNumber'], ascending=False).head(10)
            recent_avg_position = recent_races['Position'].mean()
            recent_win_rate = len(recent_races[recent_races['Position'] == 1]) / len(recent_races)
            recent_podium_rate = len(recent_races[recent_races['Position'] <= 3]) / len(recent_races)
            recent_points_per_race = recent_races['Points'].mean()
            
            # Store metrics
            driver_stat = {
                'DriverNumber': driver_num,
                'Driver': driver_name,
                'CurrentTeam': current_team,
                'AvgPosition': avg_position,
                'WinRate': win_rate,
                'PodiumRate': podium_rate,
                'PointsPerRace': points_per_race,
                'DNFRate': dnf_rate,
                'RecentAvgPosition': recent_avg_position,
                'RecentWinRate': recent_win_rate,
                'RecentPodiumRate': recent_podium_rate,
                'RecentPointsPerRace': recent_points_per_race,
                'RacesCompleted': len(driver_data)
            }
            driver_stats.append(driver_stat)
        
        # Calculate team statistics
        team_stats = []
        
        for team_name in team_df['Team'].unique():
            team_data = team_df[team_df['Team'] == team_name]
            
            if len(team_data) == 0:
                continue
                
            # Calculate overall stats (note: each race has 2 drivers per team)
            races_count = len(team_data) / 2  # approximate number of races
            avg_position = team_data['Position'].mean()
            win_count = len(team_data[team_data['Position'] == 1])
            win_rate = win_count / races_count if races_count > 0 else 0
            podium_count = len(team_data[team_data['Position'] <= 3]) 
            podium_rate = podium_count / races_count if races_count > 0 else 0
            points_per_race = team_data.groupby(['Year', 'RoundNumber'])['Points'].sum().mean()
            
            # Calculate recent form (last 5 races = 10 driver entries)
            recent_rounds = team_data.sort_values(['Year', 'RoundNumber'], ascending=False)
            recent_rounds = recent_rounds.drop_duplicates(['Year', 'RoundNumber']).head(5)
            recent_team_data = pd.DataFrame()
            
            for _, row in recent_rounds.iterrows():
                race_data = team_data[(team_data['Year'] == row['Year']) & 
                                    (team_data['RoundNumber'] == row['RoundNumber'])]
                recent_team_data = pd.concat([recent_team_data, race_data])
            
            if len(recent_team_data) > 0:
                recent_avg_position = recent_team_data['Position'].mean()
                recent_win_rate = len(recent_team_data[recent_team_data['Position'] == 1]) / (len(recent_team_data) / 2)
                recent_points_per_race = recent_team_data.groupby(['Year', 'RoundNumber'])['Points'].sum().mean()
            else:
                recent_avg_position = avg_position
                recent_win_rate = win_rate
                recent_points_per_race = points_per_race
            
            # Store metrics
            team_stat = {
                'Team': team_name,
                'AvgPosition': avg_position,
                'WinRate': win_rate,
                'PodiumRate': podium_rate,
                'PointsPerRace': points_per_race,
                'RecentAvgPosition': recent_avg_position,
                'RecentWinRate': recent_win_rate,
                'RecentPointsPerRace': recent_points_per_race,
                'RacesCompleted': races_count
            }
            team_stats.append(team_stat)
        
        # Convert to DataFrames
        driver_stats_df = pd.DataFrame(driver_stats)
        team_stats_df = pd.DataFrame(team_stats)
        
        print(f"\nGenerated performance metrics for {len(driver_stats_df)} drivers and {len(team_stats_df)} teams")
        
        return driver_stats_df, team_stats_df