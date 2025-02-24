// Map team names to their colors, including variations and normalized names
const teamColorMap = {
  // Current teams (2024)
  'Red Bull Racing': 'red-bull',
  'Mercedes': 'mercedes',
  'Ferrari': 'ferrari',
  'McLaren': 'mclaren',
  'Aston Martin': 'aston-martin',
  'Alpine': 'alpine',
  'Williams': 'williams',
  'RB': 'rb',  // Formerly AlphaTauri
  'Kick Sauber': 'sauber',  // Formerly Alfa Romeo
  'Haas F1 Team': 'haas',
  
  // Variations for compatibility
  'Mercedes-AMG': 'mercedes',
  'Haas': 'haas',
  'Haas F1': 'haas',
  
  // Default fallback
  'default': 'f1-gray'
};

export const getTeamColorClass = (teamName) => {
  const normalizedName = teamName?.trim();
  const colorClass = teamColorMap[normalizedName] || 'f1-gray';
  return `text-${colorClass}`;
};

export const getTeamBgColorClass = (teamName) => {
  const normalizedName = teamName?.trim();
  const colorClass = teamColorMap[normalizedName] || 'f1-gray';
  return `bg-${colorClass}/10`; // Using 10% opacity for background
};

export const getTeamBorderColorClass = (teamName) => {
  const normalizedName = teamName?.trim();
  const colorClass = teamColorMap[normalizedName] || 'f1-gray';
  return `border-${colorClass}`;
}; 