import requests
from datetime import datetime
import logging

class ChampionshipCalculator:
    def __init__(self):
        self.BASE_URL = "https://api.jolpi.ca/ergast/f1"

    def get_current_standings(self):
        try:
            # Get driver standings
            driver_response = requests.get(f"{self.BASE_URL}/current/driverStandings")
            driver_data = driver_response.json()['MRData']['StandingsTable']['StandingsLists'][0]['DriverStandings']

            # Get constructor standings
            constructor_response = requests.get(f"{self.BASE_URL}/current/constructorStandings")
            constructor_data = constructor_response.json()['MRData']['StandingsTable']['StandingsLists'][0]['ConstructorStandings']

            return driver_data, constructor_data
        except Exception as e:
            logging.error(f"Error fetching standings: {e}")
            return None, None

    def calculate_championship_status(self):
        driver_data, constructor_data = self.get_current_standings()
        if not driver_data or not constructor_data:
            return {
                'status': 'error',
                'message': 'Unable to fetch championship data'
            }

        try:
            # Get current round from the season schedule
            schedule_response = requests.get(f"{self.BASE_URL}/current/last")
            schedule_data = schedule_response.json()
            current_round = int(schedule_data['MRData']['RaceTable']['round'])

            # Get total rounds in the season
            season_response = requests.get(f"{self.BASE_URL}/current")
            total_rounds = int(season_response.json()['MRData']['total'])
            remaining_races = total_rounds - current_round

            # Calculate maximum points available per race
            max_points_per_race = 26  # 25 for win + 1 for fastest lap
            max_remaining_points = remaining_races * max_points_per_race

            # Process driver standings
            driver_standings = [{
                'driver': d['Driver']['givenName'] + ' ' + d['Driver']['familyName'],
                'points': float(d['points']),
                'team': d['Constructors'][0]['name']
            } for d in driver_data]

            # Process constructor standings
            constructor_standings = [{
                'team': c['Constructor']['name'],
                'points': float(c['points'])
            } for c in constructor_data]

            # Calculate championship contenders
            driver_contenders = []
            constructor_contenders = []

            if remaining_races > 0:
                leader_points = driver_standings[0]['points']
                constructor_leader_points = constructor_standings[0]['points']

                # Calculate driver contenders
                for driver in driver_standings:
                    points_behind = leader_points - driver['points']
                    if points_behind <= max_remaining_points:
                        driver_contenders.append({
                            'driver': driver['driver'],
                            'team': driver['team'],
                            'points': driver['points'],
                            'points_needed': points_behind if points_behind > 0 else 0
                        })

                # Calculate constructor contenders
                max_constructor_remaining = max_remaining_points * 2  # Two cars per team
                for constructor in constructor_standings:
                    points_behind = constructor_leader_points - constructor['points']
                    if points_behind <= max_constructor_remaining:
                        constructor_contenders.append({
                            'team': constructor['team'],
                            'points': constructor['points'],
                            'points_needed': points_behind if points_behind > 0 else 0
                        })

            if remaining_races == 0:
                return {
                    'status': 'completed',
                    'driver_champion': driver_standings[0]['driver'],
                    'constructor_champion': constructor_standings[0]['team'],
                    'driver_standings': driver_standings[:3],
                    'constructor_standings': constructor_standings[:3]
                }
            else:
                return {
                    'status': 'in_progress',
                    'remaining_races': remaining_races,
                    'driver_standings': driver_standings[:3],
                    'constructor_standings': constructor_standings[:3],
                    'championship_contenders': {
                        'drivers': driver_contenders,
                        'constructors': constructor_contenders
                    }
                }
        except Exception as e:
            logging.error(f"Error calculating championship status: {e}")
            return {
                'status': 'error',
                'message': 'Error calculating championship status'
            } 