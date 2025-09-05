export const MAP_STYLES = {
  STREETS: "mapbox://styles/mapbox/streets-v11",
  OUTDOORS: "mapbox://styles/mapbox/outdoors-v11",
  LIGHT: "mapbox://styles/mapbox/light-v10",
  DARK: "mapbox://styles/mapbox/dark-v10",
  SATELLITE: "mapbox://styles/mapbox/satellite-v9",
  SATELLITE_STREETS: "mapbox://styles/mapbox/satellite-streets-v11",
  NAVIGATION_DAY: "mapbox://styles/mapbox/navigation-day-v1",
  NAVIGATION_NIGHT: "mapbox://styles/mapbox/navigation-night-v1",
};

export type MapStyleType = keyof typeof MAP_STYLES;
