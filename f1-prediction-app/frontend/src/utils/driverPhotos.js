const DRIVERS_API_URL = 'https://api.openf1.org/v1/drivers?session_key=latest';

export const getDriverPhoto = async (fullName) => {
  try {
    const response = await fetch(DRIVERS_API_URL);
    const drivers = await response.json();
    
    // Find the driver by matching their full name
    // Note: API uses format "FirstName LASTNAME" while our app might use "FirstName LastName"
    const driver = drivers.find(d => {
      const apiName = `${d.first_name} ${d.last_name}`.toLowerCase();
      const searchName = fullName.toLowerCase();
      return apiName === searchName;
    });

    return driver?.headshot_url || null;
  } catch (error) {
    console.error('Error fetching driver photo:', error);
    return null;
  }
}; 