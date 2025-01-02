import fastf1
import pandas as pd
import numpy as np
import logging
from datetime import datetime, timedelta
from .championship_calculator import ChampionshipCalculator
from .sentiment_analyzer import F1SentimentAnalyzer
from .car_performance_analyzer import CarPerformanceAnalyzer
import requests
import time
from requests.exceptions import HTTPError
from concurrent.futures import ThreadPoolExecutor, as_completed

class F1Predictor:
    
    def __init__(self):
        self.current_year = datetime.now().year
        self.recent_races_cache = None
        self.last_race_cache = None
        self.cache_timestamp = None
        self.cache_duration = timedelta(hours=1)
        self.sentiment_analyzer = F1SentimentAnalyzer()
        self.performance_analyzer = CarPerformanceAnalyzer()

    def get_recent_races(self, limit=5):
        if (self.recent_races_cache is not None and 
            self.cache_timestamp is not None and 
            datetime.now() - self.cache_timestamp < self.cache_duration):
            return self.recent_races_cache

        current_date = datetime.now()
        current_year = current_date.year
        
        season = fastf1.get_event_schedule(current_year)
        completed_races = season[pd.to_datetime(season['EventDate']).dt.tz_localize(None) < current_date]
        
        if completed_races.empty:
            previous_year = current_year - 1
            season = fastf1.get_event_schedule(previous_year)
            completed_races = season
            self.using_previous_season = True
            logging.info(f"Using data from {previous_year} season")
        else:
            self.using_previous_season = False

        def process_race(race):
            try:
                race_session = fastf1.get_session(
                    previous_year if self.using_previous_season else current_year,
                    race['RoundNumber'], 
                    'R'
                )
                race_session.load()
                results = race_session.results
                processed_results = [{
                    'position': int(driver['Position']) if pd.notna(driver['Position']) else None,
                    'driver': f"{driver['FirstName']} {driver['LastName']}",
                    'team': driver['TeamName'],
                    'points': float(driver['Points']) if pd.notna(driver['Points']) else 0.0,
                    'grid': int(driver['GridPosition']) if pd.notna(driver['GridPosition']) else None,
                    'status': driver['Status']
                } for _, driver in results.iterrows()]
                return {
                    'name': race['EventName'],
                    'round': int(race['RoundNumber']),
                    'date': race['EventDate'].strftime('%Y-%m-%d'),
                    'results': processed_results
                }
            except Exception as e:
                logging.error(f"Error processing race {race['EventName']}: {str(e)}")
                return None

        with ThreadPoolExecutor() as executor:
            futures = [executor.submit(process_race, race) for _, race in completed_races.tail(limit).iterrows()]
            processed_races = [future.result() for future in as_completed(futures) if future.result() is not None]

        self.recent_races_cache = {
            'races': processed_races,
            'using_previous_season': self.using_previous_season,
            'season_used': previous_year if self.using_previous_season else current_year
        }
        
        self.cache_timestamp = datetime.now()
        return self.recent_races_cache

    def get_driver_stats(self):
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
                        'grid_positions': [],
                        'finish_positions': [],
                        'team': result['team']
                    }
                
                stats = driver_stats[driver]
                if result['position'] is not None:
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

        # Convert lists to numpy arrays for efficient calculations
        for driver in driver_stats:
            stats = driver_stats[driver]
            stats['grid_positions'] = np.array(stats['grid_positions'])
            stats['finish_positions'] = np.array(stats['finish_positions'])
            stats['avg_grid'] = np.mean(stats['grid_positions']) if stats['grid_positions'].size > 0 else None
            stats['avg_finish'] = np.mean(stats['finish_positions']) if stats['finish_positions'].size > 0 else None
            
        return driver_stats

    def predict_next_race(self):
        """Predict next race winner based on recent performance"""
        recent_data = self.get_recent_races()
        if not recent_data:
            return None

        driver_stats = self.get_driver_stats()
        if not driver_stats:
            return None

        # Get performance data from last race
        last_race = recent_data['races'][0]
        performance_data = self.performance_analyzer.get_car_performance_data(
            recent_data['season_used'],
            last_race['round']
        )

        predictions = []
        for driver, stats in driver_stats.items():
            score = (
                stats['points_total'] * 0.4 +
                stats['wins'] * 10 +
                stats['podiums'] * 5 -
                stats['dnfs'] * 5 -
                (stats['avg_finish'] * 2 if stats['avg_finish'] is not None else 0)
            )
            
            # Add performance metrics to score if available
            if performance_data and driver in performance_data:
                perf = performance_data[driver]
                score += (
                    perf['top_speed'] * 0.01 +
                    perf['acceleration_score'] * 2 +
                    (20 - perf['tyre_management']['lap_time_consistency']) * 0.5
                    if perf['tyre_management']['lap_time_consistency'] is not None else 0
                )
            
            predictions.append({
                'driver': driver,
                'score': score,
                'team': stats['team'],
                'recent_stats': stats
            })

        predictions = self._calculate_prediction_confidence(predictions)
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

        return self._format_prediction_response(
            winner_prediction,
            predictions[1:3],  # 2nd and 3rd place
            reasons,
            recent_data
        )

    def format_time_delta(self, seconds):
        """Format time delta in F1 style (m:ss.fff)"""
        if seconds is None:
            return None
        
        minutes = int(seconds // 60)
        remaining_seconds = seconds % 60
        
        if minutes > 0:
            return f"{minutes}:{remaining_seconds:06.3f}"
        else:
            return f"{remaining_seconds:.3f}"

    def get_last_race_results(self):
        """Get the results from the most recent race with time gaps"""
        # Check if cache needs refresh
        if (self.last_race_cache is not None and 
            self.cache_timestamp is not None and 
            datetime.now() - self.cache_timestamp < self.cache_duration):
            return self.last_race_cache

        races = self.get_recent_races(limit=1)
        if not races:
            return None

        try:
            # Load the race session
            race_session = fastf1.get_session(
                races['season_used'],
                races['races'][0]['round'],
                'R'
            )
            race_session.load()
            
            # Get the fastest lap
            fastest_lap = race_session.laps.pick_fastest(only_by_time=False)
            fastest_lap_driver = fastest_lap['Driver'] if not fastest_lap.empty else None
            fastest_lap_time = fastest_lap['LapTime'].total_seconds() if not fastest_lap.empty else None
            
            # Get race results and calculate time gaps
            results = race_session.results
            processed_results = []
            
            leader_time = None
            for _, driver in results.iterrows():
                if int(driver['Position']) == 1:
                    leader_time = driver['Time']
                    break

            for _, driver in results.iterrows():
                # Calculate gap to leader
                if pd.notna(driver['Time']) and leader_time is not None:
                    gap_to_leader = (driver['Time'] - leader_time).total_seconds()
                else:
                    gap_to_leader = None

                is_fastest_lap = fastest_lap_driver == driver['Abbreviation']
                
                # Format the fastest lap time in F1 style
                formatted_fastest_lap = self.format_time_delta(fastest_lap_time) if is_fastest_lap else None
                formatted_gap = self.format_time_delta(gap_to_leader) if gap_to_leader is not None else None

                processed_results.append({
                    'position': int(driver['Position']) if pd.notna(driver['Position']) else None,
                    'driver': f"{driver['FirstName']} {driver['LastName']}",
                    'team': driver['TeamName'],
                    'points': float(driver['Points']) if pd.notna(driver['Points']) else 0.0,
                    'grid': int(driver['GridPosition']) if pd.notna(driver['GridPosition']) else None,
                    'status': driver['Status'],
                    'gap_to_leader': formatted_gap,
                    'fastest_lap': is_fastest_lap,
                    'fastest_lap_time': formatted_fastest_lap
                })

            # Generate highlights
            highlights = []
            winner = next((r for r in processed_results if r['position'] == 1), None)
            if winner:
                highlights.append(f"{winner['driver']} wins the {races['races'][0]['name']}")
            
            # Add fastest lap highlight
            fastest_lap_driver_result = next((r for r in processed_results if r['fastest_lap']), None)
            if fastest_lap_driver_result and fastest_lap_time:
                formatted_time = self.format_time_delta(fastest_lap_time)
                highlights.append(f"Fastest Lap: {fastest_lap_driver_result['driver']} ({formatted_time})")
            
            # Calculate overtakes
            overtakes = []
            for result in processed_results:
                if result['position'] is not None and result['grid'] is not None:
                    positions_gained = result['grid'] - result['position']
                    if positions_gained > 0:
                        overtakes.append({
                            'driver': result['driver'],
                            'overtakes': positions_gained,
                            'original_position': result['grid'],
                            'final_position': result['position']
                        })
            
            if overtakes:
                best_overtaker = max(overtakes, key=lambda x: x['overtakes'])
                highlights.append(
                    f"{best_overtaker['driver']} gained the most positions: {best_overtaker['overtakes']} places "
                    f"(P{best_overtaker['original_position']} → P{best_overtaker['final_position']})"
                )
                
            # Add lost positions highlight
                
            lost_positions = [r for r in processed_results if r['position'] is not None and r['grid'] is not None and r['position'] > r['grid']]
            lost_positions_most = max(lost_positions, key=lambda x: x['position'] - x['grid'])
            if lost_positions:
                highlights.append(f"{lost_positions_most['driver']} lost the most positions: {lost_positions_most['grid'] - lost_positions_most['position']} places "
                                 f"(P{lost_positions_most['grid']} → P{lost_positions_most['position']})")
            
            # Add DNF information
            dnfs = [r for r in processed_results if 'DNF' in str(r['status'])]
            if dnfs:
                dnf_drivers = ', '.join(d['driver'] for d in dnfs)
                highlights.append(f"DNFs: {dnf_drivers}")

            race_data = {
                'name': races['races'][0]['name'],
                'results': [r for r in processed_results if r['position'] is not None][:10],  # Top 10 finishers
                'highlights': highlights,
                'total_laps': race_session.total_laps
            }
            
            # Update cache
            self.last_race_cache = race_data
            self.cache_timestamp = datetime.now()
            
            return race_data
            
        except Exception as e:
            logging.error(f"Error processing race results: {str(e)}")
            return None

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
                    'team': stats['team'],
                    'recent_stats': stats
                })
            except Exception as e:
                logging.error(f"Error calculating qualifying prediction for {driver}: {str(e)}")
                continue

        if not quali_predictions:
            return None

        # Calculate confidence scores and sort predictions
        quali_predictions = self._calculate_prediction_confidence(quali_predictions)
        
        # Get the pole prediction and other top predictions
        pole_prediction = quali_predictions[0]
        
        # Generate reasoning
        reasons = []
        stats = pole_prediction['recent_stats']
        
        if stats['grid_positions']:
            pole_positions = sum(1 for pos in stats['grid_positions'] if pos == 1)
            if pole_positions > 0:
                reasons.append(f"Secured {pole_positions} pole positions in recent races")
            
            front_rows = sum(1 for pos in stats['grid_positions'] if pos <= 3)
            if front_rows > 0:
                reasons.append(f"Qualified in top three {front_rows} times recently")
            
            if stats['avg_grid'] is not None and stats['avg_grid'] < 4:
                reasons.append(f"Strong average qualifying position of P{stats['avg_grid']:.1f}")
        
        if stats['dnfs'] == 0:
            reasons.append("Consistent reliability in recent races")

        # Get recent data for metadata
        recent_data = self.get_recent_races()
        
        return self._format_prediction_response(
            pole_prediction,
            quali_predictions[1:3],  # 2nd and 3rd place
            reasons,
            recent_data
        )

    def get_championship_standings(self):
        """Calculate current championship standings and potential winners"""
        calculator = ChampionshipCalculator()
        return calculator.calculate_championship_status()
    pass

    def _calculate_confidence_score(self, score, all_scores):
        """
        Calculate a confidence percentage for a given score within a set of scores.
        
        Args:
            score (float): The score to calculate confidence for
            all_scores (list): List of all scores to compare against
            
        Returns:
            int: Confidence score between 0 and 100
        """
        try:
            if not all_scores:
                return 0
                
            max_score = max(all_scores)
            min_score = min(all_scores)
            score_range = max_score - min_score if max_score != min_score else 1
            
            confidence = ((score - min_score) / score_range) * 100
            return int(max(0, min(100, confidence)))  # Clamp between 0 and 100
            
        except Exception as e:
            logging.error(f"Error calculating confidence score: {str(e)}")
            return 0

    def _calculate_prediction_confidence(self, predictions):
        """
        Calculate confidence scores for a list of predictions.
        Sorts predictions by score and adds confidence values.
        
        Args:
            predictions (list): List of prediction dictionaries with 'score' key
            
        Returns:
            list: Sorted predictions with added confidence scores
        """
        if not predictions:
            return []
            
        try:
            # Sort predictions by score
            predictions.sort(key=lambda x: x['score'], reverse=True)
            
            # Get all scores for confidence calculation
            all_scores = [p['score'] for p in predictions]
            
            # Calculate confidence for each prediction
            for pred in predictions:
                pred['confidence'] = self._calculate_confidence_score(pred['score'], all_scores)
                
            return predictions
            
        except Exception as e:
            logging.error(f"Error calculating prediction confidence: {str(e)}")
            # Add zero confidence if calculation fails
            for pred in predictions:
                pred['confidence'] = 0
            return predictions

    def _add_sentiment_analysis(self, prediction):
        """
        Helper method to add sentiment analysis to predictions.
        Handles both single driver predictions and predictions with alternatives.
        
        Args:
            prediction (dict): Prediction object containing at least 'driver' key
                             and optionally 'other_predictions'
        """
        try:
            # Add sentiment for main prediction
            sentiment = self.sentiment_analyzer.get_driver_sentiment(prediction['driver'])
            if sentiment:
                prediction['sentiment'] = sentiment
                prediction['sentiment']['recent_headlines'] = (
                    self.sentiment_analyzer.get_latest_headlines(prediction['driver'], limit=3)
                )
                
            # Add sentiment for other predictions if they exist
            if 'other_predictions' in prediction:
                for other_pred in prediction['other_predictions']:
                    other_sentiment = self.sentiment_analyzer.get_driver_sentiment(other_pred['driver'])
                    if other_sentiment:
                        other_pred['sentiment'] = other_sentiment
                        # Optionally add headlines for other drivers
                        # other_pred['sentiment']['recent_headlines'] = (
                        #     self.sentiment_analyzer.get_latest_headlines(other_pred['driver'], limit=1)
                        # )
        except Exception as e:
            logging.error(f"Error adding sentiment analysis: {str(e)}")

    def _format_prediction_response(self, top_prediction, other_predictions, reasons, recent_data):
        """Helper method to format the prediction response"""
        response = {
            'driver': top_prediction['driver'],
            'confidence': top_prediction['confidence'],
            'team': top_prediction['team'],
            'reasons': reasons,
            'other_predictions': [
                {
                    'driver': p['driver'],
                    'team': p['team'],
                    'confidence': p['confidence']
                } for p in other_predictions
            ],
            'prediction_metadata': {
                'using_previous_season': recent_data['using_previous_season'],
                'season_used': recent_data['season_used'],
                'confidence_adjustment': 0.7 if recent_data['using_previous_season'] else 1.0
            }
        }
        
        self._add_sentiment_analysis(response)
        return response

    def fetch_data_with_retries(self, url, retries=3, backoff_factor=0.3):
        for attempt in range(retries):
            try:
                response = requests.get(url)
                response.raise_for_status()
                return response.json()
            except HTTPError as e:
                if attempt < retries - 1:
                    sleep_time = backoff_factor * (2 ** attempt)
                    time.sleep(sleep_time)
                else:
                    logging.error(f"Failed to fetch data from {url}: {e}")
                    raise
