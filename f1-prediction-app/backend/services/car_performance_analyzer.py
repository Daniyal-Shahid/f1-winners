import fastf1
import pandas as pd
import numpy as np
import logging
from datetime import datetime

class CarPerformanceAnalyzer:
    def __init__(self):
        self.performance_cache = {}
        
    def get_car_performance_data(self, year, grand_prix, session_type='Q'):
        """
        Analyze car performance data from a specific session
        
        Args:
            year (int): Season year
            grand_prix (str/int): GP round number or name
            session_type (str): 'Q' for qualifying, 'R' for race
            
        Returns:
            dict: Performance metrics by driver
        """
        cache_key = f"{year}_{grand_prix}_{session_type}"
        if cache_key in self.performance_cache:
            return self.performance_cache[cache_key]

        try:
            session = fastf1.get_session(year, grand_prix, session_type)
            session.load()
            
            performance_data = {}
            
            for driver in session.drivers:
                laps = session.laps.pick_driver(driver)
                if laps.empty:
                    continue
                    
                # Get telemetry data for fastest lap
                fastest_lap = laps.pick_fastest()
                if fastest_lap.empty:
                    continue
                    
                telemetry = fastest_lap.get_telemetry()
                
                # Calculate performance metrics
                performance_data[driver] = {
                    "top_speed": float(telemetry['Speed'].max()),
                    "avg_speed": float(telemetry['Speed'].mean()),
                    "acceleration_score": self._calculate_acceleration_score(telemetry),
                    "sector_performance": self._analyze_sector_performance(fastest_lap),
                    "tyre_management": self._analyze_tyre_management(laps)
                }
            
            self.performance_cache[cache_key] = performance_data
            return performance_data
            
        except Exception as e:
            logging.error(f"Error analyzing car performance: {str(e)}")
            return None
    
    def _calculate_acceleration_score(self, telemetry):
        """Calculate acceleration performance score"""
        try:
            # Calculate acceleration between consecutive speed measurements
            speed_diff = telemetry['Speed'].diff()
            positive_acc = speed_diff[speed_diff > 0]
            
            return float(positive_acc.mean()) if not positive_acc.empty else 0.0
        except:
            return 0.0
    
    def _analyze_sector_performance(self, lap):
        """Analyze performance in each sector"""
        try:
            # Convert timedelta to seconds for each sector
            return {
                "sector_1_time": float(lap['Sector1Time'].total_seconds()) if pd.notna(lap['Sector1Time']) else None,
                "sector_2_time": float(lap['Sector2Time'].total_seconds()) if pd.notna(lap['Sector2Time']) else None,
                "sector_3_time": float(lap['Sector3Time'].total_seconds()) if pd.notna(lap['Sector3Time']) else None
            }
        except Exception as e:
            logging.error(f"Error analyzing sector performance: {str(e)}")
            return {
                "sector_1_time": None,
                "sector_2_time": None,
                "sector_3_time": None
            }
    
    def _analyze_tyre_management(self, laps):
        """Analyze tyre management based on lap time consistency"""
        try:
            # Convert timedelta to seconds before calculations
            lap_times = laps['LapTime'].dropna().apply(lambda x: x.total_seconds())
            return {
                "lap_time_consistency": float(lap_times.std()) if not lap_times.empty else None,
                "avg_lap_time": float(lap_times.mean()) if not lap_times.empty else None
            }
        except Exception as e:
            logging.error(f"Error analyzing tyre management: {str(e)}")
            return {
                "lap_time_consistency": None,
                "avg_lap_time": None
            } 