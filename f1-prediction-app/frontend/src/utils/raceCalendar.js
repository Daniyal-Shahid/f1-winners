const raceCalendar2024 = [
    { name: 'Bahrain Grand Prix', date: '2024-03-02', time: '15:00', sprint: false },
    { name: 'Saudi Arabian Grand Prix', date: '2024-03-09', time: '17:00', sprint: false },
    { name: 'Australian Grand Prix', date: '2024-03-24', time: '04:00', sprint: false },
    { name: 'Japanese Grand Prix', date: '2024-04-07', time: '06:00', sprint: false },
    { name: 'Chinese Grand Prix', date: '2024-04-21', time: '08:00', sprint: true },
    { name: 'Miami Grand Prix', date: '2024-05-05', time: '21:00', sprint: true },
    { name: 'Emilia Romagna Grand Prix', date: '2024-05-19', time: '14:00', sprint: false },
    { name: 'Monaco Grand Prix', date: '2024-05-26', time: '14:00', sprint: false },
    { name: 'Canadian Grand Prix', date: '2024-06-09', time: '19:00', sprint: false },
    { name: 'Spanish Grand Prix', date: '2024-06-23', time: '14:00', sprint: false },
    { name: 'Austrian Grand Prix', date: '2024-06-30', time: '14:00', sprint: true },
    { name: 'British Grand Prix', date: '2024-07-07', time: '15:00', sprint: false },
    { name: 'Hungarian Grand Prix', date: '2024-07-21', time: '14:00', sprint: false },
    { name: 'Belgian Grand Prix', date: '2024-07-28', time: '14:00', sprint: false },
    { name: 'Dutch Grand Prix', date: '2024-08-25', time: '14:00', sprint: false },
    { name: 'Italian Grand Prix', date: '2024-09-01', time: '14:00', sprint: false },
    { name: 'Azerbaijan Grand Prix', date: '2024-09-15', time: '12:00', sprint: false },
    { name: 'Singapore Grand Prix', date: '2024-09-22', time: '13:00', sprint: false },
    { name: 'United States Grand Prix', date: '2024-10-21', time: '20:00', sprint: true },
    { name: 'Mexican Grand Prix', date: '2024-10-27', time: '20:00', sprint: false },
    { name: 'Brazilian Grand Prix', date: '2024-11-03', time: '17:00', sprint: true },
    { name: 'Las Vegas Grand Prix', date: '2024-11-23', time: '06:00', sprint: false },
    { name: 'Qatar Grand Prix', date: '2024-12-01', time: '17:00', sprint: true },
    { name: 'Abu Dhabi Grand Prix', date: '2024-12-08', time: '13:00', sprint: false },
  ];
  
  export const getNextRace = () => {
    const now = new Date();
    return raceCalendar2024.find(race => new Date(race.date) > now) || raceCalendar2024[0];
  };

  export const getLastRace = () => {
    const now = new Date();
    return [...raceCalendar2024]
      .reverse()
      .find(race => new Date(race.date) < now) || raceCalendar2024[raceCalendar2024.length - 1];
  };