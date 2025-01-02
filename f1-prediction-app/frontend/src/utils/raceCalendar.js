export const getRaceCalendar = async () => {
  try {
    const response = await fetch('http://127.0.0.1:5000/api/race-calendar');
    if (!response.ok) {
      throw new Error('Failed to fetch race calendar');
    }
    return await response.json();
  } catch (error) {
    console.error('Error fetching race calendar:', error);
    return []; // Fallback to an empty array or a hardcoded calendar
  }
};

export const getNextRace = async () => {
  const raceCalendar = await getRaceCalendar();
  if (!raceCalendar || raceCalendar.length === 0) {
    return null;
  }
  const now = new Date();
  return raceCalendar.find(race => new Date(race.date) > now) || raceCalendar[0];
};

export const getLastRace = async () => {
  const raceCalendar = await getRaceCalendar();
  if (!raceCalendar || raceCalendar.length === 0) {
    return null;
  }
  const now = new Date();
  return [...raceCalendar]
    .reverse()
    .find(race => new Date(race.date) < now) || raceCalendar[raceCalendar.length - 1];
};