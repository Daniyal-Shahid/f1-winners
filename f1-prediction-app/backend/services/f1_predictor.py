import fastf1
import pandas as pd
import numpy as np
import logging
from datetime import datetime, timedelta
from .championship_calculator import ChampionshipCalculator

class F1Predictor:
    
    def __init__(self):
        self.current_year = datetime.now().year
        self.recent_races_cache = None
        self.last_race_cache = None
        self.cache_timestamp = None
        self.cache_duration = timedelta(hours=1)

    def get_recent_races(self, limit=5):
        """Fetch recent race results to analyze trends"""
        if (self.recent_races_cache is not None and 
            self.cache_timestamp is not None and 
            datetime.now() - self.cache_timestamp < self.cache_duration):
            return self.recent_races_cache

        current_date = datetime.now()
        current_year = current_date.year
        
        # First try current season
        season = fastf1.get_event_schedule(current_year)
        completed_races = season[pd.to_datetime(season['EventDate']).dt.tz_localize(None) < current_date]
        
        # If no races in current season, get last races from previous season
        if completed_races.empty:
            previous_year = current_year - 1
            season = fastf1.get_event_schedule(previous_year)
            completed_races = season  # Get all races from previous season
            
            # Add a flag to indicate we're using previous season data
            self.using_previous_season = True
            logging.info(f"Using data from {previous_year} season")
        else:
            self.using_previous_season = False

        processed_races = []
        for _, race in completed_races.tail(limit).iterrows():
            try:
                # Load the race session
                race_session = fastf1.get_session(
                    previous_year if self.using_previous_season else current_year,
                    race['RoundNumber'], 
                    'R'
                )
                race_session.load()
                
                # Get race results
                results = race_session.results
                
                processed_results = []
                for _, driver in results.iterrows():
                    processed_results.append({
                        'position': int(driver['Position']) if pd.notna(driver['Position']) else None,
                        'driver': f"{driver['FirstName']} {driver['LastName']}",
                        'team': driver['TeamName'],
                        'points': float(driver['Points']) if pd.notna(driver['Points']) else 0.0,
                        'grid': int(driver['GridPosition']) if pd.notna(driver['GridPosition']) else None,
                        'status': driver['Status']
                    })

                processed_races.append({
                    'name': race['EventName'],
                    'round': int(race['RoundNumber']),
                    'date': race['EventDate'].strftime('%Y-%m-%d'),
                    'results': processed_results
                })
                
            except Exception as e:
                logging.error(f"Error processing race {race['EventName']}: {str(e)}")
                continue

        self.recent_races_cache = {
            'races': processed_races,
            'using_previous_season': self.using_previous_season,
            'season_used': previous_year if self.using_previous_season else current_year
        }
        
        self.cache_timestamp = datetime.now()
        return self.recent_races_cache

    def get_driver_stats(self):
        """Calculate driver statistics from recent races"""
        races = self.get_recent_races()
        if not races:
            return None

        driver_stats = {}
        
        for race in races['races']:
            for result in race['results']:
                driver = result['driver']
                if driver not in driver_stats:
                    driver_stats[driver] = {
                        'points_total': 0,
                        'wins': 0,
                        'podiums': 0,
                        'dnfs': 0,
                        'grid_positions': [],  # Keep raw grid positions
                        'finish_positions': [], # Keep raw finish positions
                        'team': result['team']
                    }
                
                stats = driver_stats[driver]
                if result['position'] is not None:  # Only count if they finished
                    stats['points_total'] += result['points']
                    stats['finish_positions'].append(result['position'])
                    
                    if result['position'] == 1:
                        stats['wins'] += 1
                    if result['position'] <= 3:
                        stats['podiums'] += 1
                
                if 'DNF' in str(result['status']):
                    stats['dnfs'] += 1
                
                if result['grid'] is not None:
                    stats['grid_positions'].append(result['grid'])

        # Calculate averages
        for driver in driver_stats:
            stats = driver_stats[driver]
            stats['avg_grid'] = np.mean(stats['grid_positions']) if stats['grid_positions'] else None
            stats['avg_finish'] = np.mean(stats['finish_positions']) if stats['finish_positions'] else None
            
        return driver_stats

    def predict_next_race(self):
        """Predict next race winner based on recent performance"""
        recent_data = self.get_recent_races()
        if not recent_data:
            return None

        driver_stats = self.get_driver_stats()
        if not driver_stats:
            return None

        predictions = []
        for driver, stats in driver_stats.items():
            score = (
                stats['points_total'] * 0.4 +
                stats['wins'] * 10 +
                stats['podiums'] * 5 -
                stats['dnfs'] * 5 -
                (stats['avg_finish'] * 2 if stats['avg_finish'] is not None else 0)
            )
            
            predictions.append({
                'driver': driver,
                'score': score,
                'confidence': None,
                'team': stats['team'],
                'recent_stats': stats
            })

        # Sort and calculate confidence
        predictions.sort(key=lambda x: x['score'], reverse=True)
        max_score = predictions[0]['score']
        min_score = predictions[-1]['score']
        score_range = max_score - min_score

        for pred in predictions:
            pred['confidence'] = int(((pred['score'] - min_score) / score_range) * 100)

        winner_prediction = predictions[0]
        
        # Generate reasoning
        reasons = []
        stats = winner_prediction['recent_stats']
        if stats['wins'] > 0:
            reasons.append(f"Won {stats['wins']} recent races")
        if stats['podiums'] > 0:
            reasons.append(f"Secured {stats['podiums']} podiums in recent races")
        if stats['avg_grid'] is not None and stats['avg_grid'] < 3:
            reasons.append("Strong qualifying performance")
        if stats['dnfs'] == 0:
            reasons.append("Consistent reliability")
        
        # Sort predictions by confidence
        predictions.sort(key=lambda x: x['score'], reverse=True)
        
        # Get winner and top 3
        winner_prediction = predictions[0]
        other_predictions = [
            {
                'driver': p['driver'],
                'team': p['team'],
                'confidence': p['confidence']
            } for p in predictions[1:3]  # Get 2nd and 3rd place
        ]
        
        return {
            'driver': winner_prediction['driver'],
            'confidence': winner_prediction['confidence'],
            'team': winner_prediction['team'],
            'reasons': reasons,
            'other_predictions': other_predictions,  # Add other predictions
            'prediction_metadata': {
                'using_previous_season': recent_data['using_previous_season'],
                'season_used': recent_data['season_used'],
                'confidence_adjustment': 0.7 if recent_data['using_previous_season'] else 1.0
            }
        }

    def get_last_race_results(self):
        """Get the results from the most recent race"""
        races = self.get_recent_races(limit=1)
        if not races:
            return None

        last_race = races['races'][0]  # Most recent race will be first
        
        highlights = []
        results = last_race['results']
        
        # Generate highlights
        winner = next((r for r in results if r['position'] == 1), None)
        if winner:
            highlights.append(f"{winner['driver']} wins the {last_race['name']}")
        
        # Calculate overtakes for each driver
        overtakes = []
        for result in results:
            if result['position'] is not None and result['grid'] is not None:
                positions_gained = result['grid'] - result['position']
                if positions_gained > 0:  # Only count positive overtakes
                    overtakes.append({
                        'driver': result['driver'],
                        'overtakes': positions_gained,
                        'original_position': result['grid'],
                        'final_position': result['position']
                    })
        
        # Add best overtaker to highlights
        if overtakes:
            best_overtaker = max(overtakes, key=lambda x: x['overtakes'])
            highlights.append(f"{best_overtaker['driver']} gained the most positions: {best_overtaker['overtakes']} overtakes. They started from P{best_overtaker['original_position']} and finished in P{best_overtaker['final_position']}")
        
        podium_teams = set(r['team'] for r in results if r['position'] is not None and r['position'] <= 3)
        if len(podium_teams) > 1:
            highlights.append(f"Podium split between {', '.join(podium_teams)}")
        
        dnfs = [r for r in results if 'DNF' in str(r['status'])]
        if dnfs:
            dnf_drivers = ', '.join(d['driver'] for d in dnfs)
            highlights.append(f"DNFs: {dnf_drivers}")

        return {
            'name': last_race['name'],
            'results': [r for r in results if r['position'] is not None][:10],  # Top 10 finishers
            'highlights': highlights
        }

    def predict_qualifying(self):
        """Predict qualifying performance based on recent data"""
        driver_stats = self.get_driver_stats()
        if not driver_stats:
            return None

        quali_predictions = []
        for driver, stats in driver_stats.items():
            try:
                # Calculate qualifying-specific score
                quali_score = stats['points_total'] * 0.2  # Recent form still matters
                
                if stats['grid_positions']:
                    # Count pole positions
                    pole_positions = sum(1 for pos in stats['grid_positions'] if pos == 1)
                    front_rows = sum(1 for pos in stats['grid_positions'] if pos <= 3)
                    
                    quali_score += (
                        pole_positions * 15 +  # Poles
                        front_rows * 8 +      # Front row starts
                        (20 - stats['avg_grid']) * 2 if stats['avg_grid'] is not None else 0  # Average grid position bonus
                    )
                
                # Penalty for DNFs
                quali_score -= stats['dnfs'] * 3

                quali_predictions.append({
                    'driver': driver,
                    'score': float(quali_score),
                    'confidence': None,
                    'team': stats['team'],
                    'recent_stats': stats
                })
            except Exception as e:
                logging.error(f"Error calculating qualifying prediction for {driver}: {str(e)}")
                continue

        if not quali_predictions:
            return None

        # Sort and calculate confidence
        quali_predictions.sort(key=lambda x: x['score'], reverse=True)
        max_score = quali_predictions[0]['score']
        min_score = quali_predictions[-1]['score']
        score_range = max_score - min_score if max_score != min_score else 1

        # Calculate confidence for all predictions
        for pred in quali_predictions:
            try:
                confidence = ((pred['score'] - min_score) / score_range) * 100
                pred['confidence'] = int(max(0, min(100, confidence)))  # Clamp between 0 and 100
            except Exception as e:
                logging.error(f"Error calculating confidence: {str(e)}")
                pred['confidence'] = 0

        pole_prediction = quali_predictions[0]
        
        # Get other top predictions (2nd and 3rd)
        other_predictions = [
            {
                'driver': p['driver'],
                'team': p['team'],
                'confidence': p['confidence']
            } for p in quali_predictions[1:3]  # Get 2nd and 3rd place
        ]
        
        # Generate reasoning for qualifying prediction
        reasons = []
        stats = pole_prediction['recent_stats']
        
        if stats['grid_positions']:
            pole_positions = sum(1 for pos in stats['grid_positions'] if pos == 1)
            front_rows = sum(1 for pos in stats['grid_positions'] if pos <= 3)
            
            if stats['avg_grid'] is not None and stats['avg_grid'] <= 2:
                reasons.append(f"Average starting position of {stats['avg_grid']:.1f}")
            
            if pole_positions > 0:
                reasons.append(f"Secured {pole_positions} pole position{'s' if pole_positions > 1 else ''} in recent races")
            
            if front_rows > pole_positions:
                reasons.append(f"Started from front row {front_rows} times recently")
        
        if stats['dnfs'] == 0:
            reasons.append("Consistent qualifying performance")

        # Get recent data for metadata
        recent_data = self.get_recent_races()

        return {
            'driver': pole_prediction['driver'],
            'confidence': pole_prediction['confidence'],
            'team': pole_prediction['team'],
            'reasons': reasons,
            'other_predictions': other_predictions,  # Add other predictions
            'prediction_metadata': {
                'using_previous_season': recent_data['using_previous_season'],
                'season_used': recent_data['season_used'],
                'confidence_adjustment': 0.7 if recent_data['using_previous_season'] else 1.0
            }
        }

    def get_championship_standings(self):
        """Calculate current championship standings and potential winners"""
        calculator = ChampionshipCalculator()
        return calculator.calculate_championship_status()
    pass
