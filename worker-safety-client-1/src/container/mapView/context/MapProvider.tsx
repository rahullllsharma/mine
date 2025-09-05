import type { ReactNode } from "react";
import type { LocationFilter } from "../filters/mapFilters/MapFilters";
import { noop } from "lodash-es";
import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useMemo,
  useState,
} from "react";
import { useAuthStore } from "@/store/auth/useAuthStore.store";

type MapProviderProps = {
  children: ReactNode;
  defaultFilters?: LocationFilter[];
};

type MapContextItemProps = {
  isActive: boolean;
  toggle: () => void;
};

type MapContextProps = {
  riskLegend: MapContextItemProps;
  satelliteView: MapContextItemProps;
  filters: LocationFilter[];
  setFilters: (filters: LocationFilter[]) => void;
};

const defaultFilters: LocationFilter[] = [
  { field: "RISK", values: [] },
  { field: "TYPES", values: [] },
  { field: "DIVISIONS", values: [] },
  { field: "REGIONS", values: [] },
  { field: "PROJECT", values: [] },
  { field: "CONTRACTOR", values: [] },
  { field: "SUPERVISOR", values: [] },
  { field: "PROJECT_STATUS", values: [] },
];

const defaultState: MapContextProps = {
  riskLegend: { isActive: true, toggle: noop },
  satelliteView: { isActive: false, toggle: noop },
  filters: defaultFilters,
  setFilters: noop,
};

const MapContext = createContext<MapContextProps>(defaultState);

export const useMapContext = (): MapContextProps => useContext(MapContext);

export default function MapProvider({
  children,
  defaultFilters: fallbackFilters = defaultFilters,
}: MapProviderProps): JSX.Element {
  const [isRiskLevelVisible, setIsRiskLevelVisible] = useState(true);
  const [isSatelliteViewEnabled, setIsSatelliteViewEnabled] = useState(false);

  const [mapFilters, setMapFilters] = useState<LocationFilter[]>([]);
  const { getLocationMapFilters, setLocationMapFilters } = useAuthStore();

  useEffect(() => {
    const stored = getLocationMapFilters();
    setMapFilters(stored?.length ? stored : fallbackFilters);
  }, [fallbackFilters, getLocationMapFilters]);

  const toggleRiskLevel = useCallback(() => {
    setIsRiskLevelVisible(prevState => !prevState);
  }, []);

  const toggleSatelliteView = useCallback(() => {
    setIsSatelliteViewEnabled(prevState => !prevState);
  }, []);

  const setFilters = useCallback(
    (filters: LocationFilter[]) => {
      setMapFilters(filters);
      setLocationMapFilters(filters);
    },
    [setLocationMapFilters]
  );

  const mapContext = useMemo<MapContextProps>(
    () => ({
      riskLegend: { isActive: isRiskLevelVisible, toggle: toggleRiskLevel },
      satelliteView: {
        isActive: isSatelliteViewEnabled,
        toggle: toggleSatelliteView,
      },
      filters: mapFilters,
      setFilters,
    }),
    [
      isRiskLevelVisible,
      toggleRiskLevel,
      isSatelliteViewEnabled,
      toggleSatelliteView,
      mapFilters,
      setFilters,
    ]
  );

  return (
    <MapContext.Provider value={mapContext}>{children}</MapContext.Provider>
  );
}
