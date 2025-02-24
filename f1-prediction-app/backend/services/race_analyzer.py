import pandas as pd
import numpy as np
from datetime import datetime
import fastf1
import logging
from collections import defaultdict

class RaceAnalyzer:
    def __init__(self):
        self.cache = {}
        
    def get_driver_race_analysis(self, driver_name, race_round=None, year=None):
        """Get comprehensive race analysis for a specific driver"""
        if not year:
            year = datetime.now().year
            
        try:
            # If race_round is not specified, get the most recent race
            if race_round is None:
                schedule = fastf1.get_event_schedule(year)
                completed_races = schedule[pd.to_datetime(schedule['EventDate']) < pd.Timestamp.now()]
                if completed_races.empty:
                    # If no races this year, get last race of previous year
                    year -= 1
                    schedule = fastf1.get_event_schedule(year)
                    race_round = schedule.iloc[-1]['RoundNumber']
                else:
                    race_round = completed_races.iloc[-1]['RoundNumber']
            
            # Create cache key
            cache_key = f"{year}_{race_round}_{driver_name}"
            if cache_key in self.cache:
                return self.cache[cache_key]

            # Load race session
            session = fastf1.get_session(year, race_round, 'R')
            session.load()
            
            # Get driver's laps using the last name only
            driver_last_name = driver_name.split()[-1]
            driver_laps = session.laps.pick_driver(driver_last_name)
            
            if driver_laps.empty:
                logging.error(f"No lap data found for driver {driver_name}")
                return None
            
            analysis = {
                'lap_times': self._analyze_lap_times(driver_laps),
                'sector_performance': self._analyze_sectors(driver_laps),
                'tyre_performance': self._analyze_tyre_performance(driver_laps),
                'race_pace': self._analyze_race_pace(driver_laps, session.laps),
                'position_changes': self._analyze_position_changes(driver_laps),
                'race_summary': self._get_race_summary(session, driver_name)
            }
            
            self.cache[cache_key] = analysis
            return analysis
            
        except Exception as e:
            logging.error(f"Error analyzing race data for {driver_name}: {str(e)}")
            return None
            
    def _analyze_lap_times(self, driver_laps):
        """Analyze lap time progression"""
        valid_laps = driver_laps[driver_laps['LapTime'].notna()]
        
        lap_times_sec = valid_laps['LapTime'].dt.total_seconds()
        lap_numbers = valid_laps['LapNumber']
        
        return {
            'lap_times': lap_times_sec.tolist(),
            'lap_numbers': lap_numbers.tolist(),
            'fastest_lap': lap_times_sec.min(),
            'average_lap': lap_times_sec.mean(),
            'lap_time_trend': self._calculate_trend(lap_times_sec)
        }
        
    def _analyze_sectors(self, driver_laps):
        """Analyze sector times and consistency"""
        sectors = {}
        for sector in [1, 2, 3]:
            sector_times = driver_laps[f'Sector{sector}Time'].dt.total_seconds()
            valid_times = sector_times[sector_times.notna()]
            
            sectors[f'sector_{sector}'] = {
                'times': valid_times.tolist(),
                'best': valid_times.min(),
                'average': valid_times.mean(),
                'consistency': valid_times.std()
            }
            
        return sectors
        
    def _analyze_tyre_performance(self, driver_laps):
        """Analyze performance across different tyre compounds"""
        tyre_performance = defaultdict(list)
        
        for compound in driver_laps['Compound'].unique():
            if pd.isna(compound):
                continue
                
            compound_laps = driver_laps[driver_laps['Compound'] == compound]
            lap_times = compound_laps['LapTime'].dt.total_seconds()
            
            tyre_performance[compound] = {
                'lap_times': lap_times.tolist(),
                'lap_numbers': compound_laps['LapNumber'].tolist(),
                'average_pace': lap_times.mean(),
                'degradation': self._calculate_trend(lap_times)
            }
            
        return dict(tyre_performance)
        
    def _analyze_race_pace(self, driver_laps, all_laps):
        """Compare race pace with field average"""
        field_lap_times = all_laps['LapTime'].dt.total_seconds()
        driver_lap_times = driver_laps['LapTime'].dt.total_seconds()
        
        return {
            'driver_average': driver_lap_times.mean(),
            'field_average': field_lap_times.mean(),
            'pace_delta': driver_lap_times.mean() - field_lap_times.mean()
        }
        
    def _analyze_position_changes(self, driver_laps):
        """Track position changes throughout the race"""
        positions = driver_laps['Position'].tolist()
        lap_numbers = driver_laps['LapNumber'].tolist()
        
        return {
            'positions': positions,
            'lap_numbers': lap_numbers,
            'positions_gained': positions[0] - positions[-1] if positions else 0,
            'best_position': min(positions) if positions else None,
            'worst_position': max(positions) if positions else None
        }
        
    def _get_race_summary(self, session, driver_name):
        """Get overall race summary"""
        result = session.results.copy()
        driver_result = result[result['FullName'] == driver_name].iloc[0]
        
        return {
            'final_position': driver_result['Position'],
            'points': driver_result['Points'],
            'status': driver_result['Status'],
            'grid': driver_result['GridPosition'],
            'finish_status': driver_result['Status']
        }
        
    def _calculate_trend(self, values):
        """Calculate linear trend in data"""
        if len(values) < 2:
            return 0
            
        x = np.arange(len(values))
        z = np.polyfit(x, values, 1)
        return float(z[0])  # Return slope of trend line 