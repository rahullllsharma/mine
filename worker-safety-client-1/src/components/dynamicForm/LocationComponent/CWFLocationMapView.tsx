import type { PositionCoordsType } from "@/components/map/Map";
import type {
  LocationVariables,
  LatLng,
  MapBounds,
} from "@/container/mapView/utils/mapView.types";
import type { MapRef } from "react-map-gl";
import { Marker } from "react-map-gl";
import mapboxgl from "mapbox-gl";
import { useCallback, useContext, useEffect, useRef, useState } from "react";
import { DateTime } from "luxon";
import Map, { MapProvider } from "@/components/map/Map";
import { config } from "@/config";
import { orderByName, orderByRiskLevel } from "@/graphql/utils";
import ToastContext from "@/components/shared/toast/context/ToastContext";

interface CWFLocationMapViewProps {
  selectedLocationLatitude: string | number;
  selectedLocationLongitude: string | number;
  modalMapView?: boolean;
}

export default function CWFLocationMapView({
  selectedLocationLatitude,
  selectedLocationLongitude,
  modalMapView,
}: CWFLocationMapViewProps): JSX.Element {
  const mapRef = useRef<MapRef | null>(null);
  const searchRef = useRef<HTMLInputElement>(null);
  const [currentPosition, setCurrentPosition] = useState([0, 0]);
  const [positionCoords, setPositionCoords] =
    useState<PositionCoordsType | null>(null);
  const [isMapStable, setIsMapStable] = useState<boolean>(false);
  const initialVariablesRef = useRef<LocationVariables | null>();
  const [storedMapView] = useState(sessionStorage.getItem("mapView"));

  const [isFirstRender, setIsFirstRender] = useState(true);

  const selectedLat = selectedLocationLatitude
    ? Number(selectedLocationLatitude)
    : null;
  const selectedLng = selectedLocationLongitude
    ? Number(selectedLocationLongitude)
    : null;

  const checkLocationPermission = useCallback(() => {
    if (!navigator.geolocation) {
      setCurrentPosition([
        Number(selectedLocationLongitude),
        Number(selectedLocationLatitude),
      ]);

      if (mapRef.current) {
        mapRef.current.flyTo({
          center: [
            Number(selectedLocationLongitude),
            Number(selectedLocationLatitude),
          ],
          zoom: 3.5,
          duration: 0,
          essential: true,
        });
      }
    }
  }, []);

  useEffect(() => {
    checkLocationPermission();
  }, [checkLocationPermission]);

  useEffect(() => {
    if (mapRef.current) {
      mapRef.current.flyTo({
        center: [
          Number(selectedLocationLongitude),
          Number(selectedLocationLatitude),
        ],
        zoom: 15,
        duration: 1000,
        essential: true,
      });
    }
  }, [selectedLat, selectedLng, storedMapView]);

  const getVariables = () => {
    const currentDate = DateTime.fromJSDate(new Date());
    const nextDate = currentDate.plus({ days: 1 }).toISODate();
    const previousDate = currentDate.minus({ days: 1 }).toISODate();
    const variables: LocationVariables = {
      startDate: previousDate,
      endDate: nextDate,
      search: searchRef.current?.value,
      orderBy: [orderByRiskLevel, orderByName],
    };
    return variables;
  };
  const getDatedLocVariables = (bounds: any) => {
    const variables: LocationVariables = getVariables();
    const boundaries = bounds;
    variables.minX = boundaries.getSouthWest().lng;
    variables.maxX = boundaries.getNorthEast().lng;
    variables.maxY = boundaries.getNorthEast().lat;
    variables.minY = boundaries.getSouthWest().lat;
    return variables;
  };

  const toastCtx = useContext(ToastContext);

  const createBoundsFromLatLng = (
    lat: number,
    lng: number,
    offset = 0.03
  ): MapBounds => {
    const northEast: LatLng = {
      lat: lat + offset,
      lng: lng + offset,
    };
    const southWest: LatLng = {
      lat: lat - offset,
      lng: lng - offset,
    };

    return new mapboxgl.LngLatBounds(
      [southWest.lng, southWest.lat],
      [northEast.lng, northEast.lat]
    );
  };

  const loadData = (longitude: number, latitude: number) => {
    const bounds = createBoundsFromLatLng(latitude, longitude);
    if (!searchRef.current?.value || !searchRef.current?.value.length) {
      if (bounds && bounds.getNorthEast() && bounds.getSouthWest()) {
        const variables = getDatedLocVariables(bounds);
        initialVariablesRef.current = variables;
      }
    }
  };

  useEffect(() => {
    if (positionCoords) {
      const { latitude, longitude, accuracy } = positionCoords;
      if (accuracy > 3000) {
        toastCtx?.pushToast(
          "info",
          "Your precise location could not be determined."
        );
      } else {
        setCurrentPosition([longitude, latitude]);
        if (!storedMapView) {
          callAPIonFirstLoad(longitude, latitude);
        }
      }
    }
  }, [positionCoords]);

  useEffect(() => {
    if (isMapStable && positionCoords) {
      const { latitude, longitude, accuracy } = positionCoords;
      if (accuracy < 3000) {
        getCurrentBoundsData(longitude, latitude);
      }
    }
  }, [isMapStable, positionCoords]);

  const getCurrentBoundsData = (longitude: number, latitude: number) => {
    if (storedMapView) {
      restoreMapView();
    } else {
      loadData(longitude, latitude);
    }
  };

  const restoreMapView = () => {
    if (storedMapView && mapRef.current) {
      const { center, zoom } = JSON.parse(storedMapView);

      mapRef.current.flyTo({
        center: center,
        zoom: zoom,
        duration: 0,
        essential: true,
      });

      if (isFirstRender) {
        setIsFirstRender(false);
      }
    }
  };

  useEffect(() => {
    if (storedMapView && positionCoords) {
      restoreMapView();
    }
  }, [storedMapView, positionCoords]);

  const getInitialViewState = () => {
    if (selectedLat && selectedLng) {
      return {
        longitude: selectedLng,
        latitude: selectedLat,
        zoom: 15,
      };
    }

    if (storedMapView) {
      const { center, zoom } = JSON.parse(storedMapView);
      return {
        longitude: center[0],
        latitude: center[1],
        zoom: zoom,
      };
    }

    return {
      longitude: currentPosition[0] || Number(selectedLocationLongitude),
      latitude: currentPosition[1] || Number(selectedLocationLatitude),
      zoom: currentPosition[0] ? 10 : 3.5,
    };
  };

  const callAPIonFirstLoad = (longitude: number, latitude: number) => {
    const bounds = createBoundsFromLatLng(latitude, longitude);
    if (!searchRef.current?.value || !searchRef.current?.value.length) {
      if (bounds && bounds.getNorthEast() && bounds.getSouthWest()) {
        const variables = getDatedLocVariables(bounds);
        initialVariablesRef.current = variables;
      }
    }
  };

  return (
    <div className="w-full">
      <MapProvider>
        <div className={`${modalMapView ? `h-[20vh]` : `h-[60vh]`} w-full`}>
          <Map
            id="project-map-view"
            ref={ref => {
              mapRef.current = ref;
            }}
            mapStyle={"STREETS"}
            mapboxAccessToken={config.workerSafetyMapboxAccessToken}
            hasZoom={!modalMapView}
            hasUserLocation={!modalMapView}
            className={
              modalMapView
                ? "w-full h-[20vh] pointer-events-none"
                : "w-full h-[60vh]"
            }
            setPositionCoords={setPositionCoords}
            setIsMapStable={setIsMapStable}
            initialViewState={getInitialViewState()}
            interactive={!modalMapView}
            modalMapView={modalMapView}
          >
            {selectedLat && selectedLng && (
              <Marker
                longitude={selectedLng}
                latitude={selectedLat}
                color="red"
              />
            )}
          </Map>
        </div>
      </MapProvider>
    </div>
  );
}
