import fastf1
import pandas as pd
from datetime import datetime
import logging

class RaceCalendarService:
    def __init__(self):
        self.current_year = datetime.now().year

    def get_race_calendar(self):
        """Fetch the current season's race calendar."""
        try:
            schedule = fastf1.get_event_schedule(self.current_year)
            race_calendar = []
            for _, event in schedule.iterrows():
                race_calendar.append({
                    'name': event['EventName'],
                    'date': event['EventDate'].strftime('%Y-%m-%d'),
                    'time': event['Session5Date'].strftime('%H:%M') if pd.notna(event['Session5Date']) else 'TBD',
                    'sprint': 'Sprint' in event['EventFormat']
                })
            return race_calendar
        except Exception as e:
            logging.error(f"Error fetching race calendar: {str(e)}")
            return None