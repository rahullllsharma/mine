import type { LocationFilter } from "../filters/mapFilters/MapFilters";
import type { LocationVariables } from "./mapView.types";
import mapboxgl from "mapbox-gl";

const parseFilters = (filters: LocationFilter[]) => {
  return filters
    .filter(filter => filter.values.length > 0)
    .map(filter => ({
      ...filter,
      values: filter.values.map(value => value.id),
    }));
};

export { parseFilters };

export const calculateBoundsFromInitialRef = (
  initialVariablesRefCurrentObj: LocationVariables
) => {
  if (
    typeof initialVariablesRefCurrentObj.minX === "number" &&
    typeof initialVariablesRefCurrentObj.minY === "number" &&
    typeof initialVariablesRefCurrentObj.maxX === "number" &&
    typeof initialVariablesRefCurrentObj.maxY === "number"
  ) {
    const bounds = new mapboxgl.LngLatBounds(
      [initialVariablesRefCurrentObj.minX, initialVariablesRefCurrentObj.minY],
      [initialVariablesRefCurrentObj.maxX, initialVariablesRefCurrentObj.maxY]
    );

    return bounds;
  }
};
