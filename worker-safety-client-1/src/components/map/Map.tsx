import type { PropsWithClassName } from "@/types/Generic";
import type { TransformRequestFunction } from "mapbox-gl";
import type {
  GeolocateControlRef,
  GeolocateErrorEvent,
  MapRef,
} from "react-map-gl";
import type { ComponentProps, ForwardedRef } from "react";
import type { MapStyleType } from "./configs/mapStyles";
import cx from "classnames";
import { forwardRef, useContext, useEffect, useRef } from "react";
import ReactMapbox, {
  GeolocateControl,
  MapProvider,
  NavigationControl,
} from "react-map-gl";

import { signIn, useSession } from "next-auth/react";
import { COUNTRIES_COORDINATES } from "@/components/map/configs/countriesCoordinates";
import ToastContext from "@/components/shared/toast/context/ToastContext";
import { config } from "@/config";
import { messages } from "@/locales/messages";
import "mapbox-gl/dist/mapbox-gl.css";
import { MAP_STYLES } from "./configs/mapStyles";

type ReactMapboxProps = ComponentProps<typeof ReactMapbox>;

type MapPropsRequiredProps = Required<
  Pick<ReactMapboxProps, "mapboxAccessToken">
>;

type MapOptionalProps = Partial<Pick<ReactMapboxProps, "id" | "children">>;

type MapCustomProps = {
  hasZoom?: boolean;
  hasUserLocation?: boolean;
  mapStyle?: MapStyleType;
  setPositionCoords?: (coords: PositionCoordsType) => void;
  setIsMapStable?: (isStable: boolean) => void;
  initialViewState?: {
    longitude: number;
    latitude: number;
    zoom: number;
  };
  interactive?: boolean;
  modalMapView?: boolean;
};

export type PositionCoordsType = {
  latitude: number;
  longitude: number;
  accuracy: number;
};

export type MapProps = PropsWithClassName<
  MapPropsRequiredProps & MapOptionalProps & MapCustomProps
>;
const navigationControlStyle = {
  marginTop: "clamp(0px, calc(60px - 2vw), 60px)",
};

const geolocateControlStyle = { marginTop: "clamp(4px, calc(9px - 0vw), 8px)" };

/**
 * The <Map /> powered by `mapbox-gl` and `react-map-gl`
 * This only adds nice defaults for the Maps component and styles.
 */
function Map(
  {
    id,
    children,
    mapboxAccessToken,
    mapStyle = "STREETS",
    className = "w-auto h-screen",
    hasZoom = false,
    hasUserLocation = false,
    setPositionCoords,
    setIsMapStable,
    initialViewState,
    interactive = true,
    modalMapView,
  }: MapProps,
  ref: ForwardedRef<MapRef>
): JSX.Element {
  const geolocateControlRef = useRef<GeolocateControlRef>(null);
  const toastCtx = useContext(ToastContext);
  const locationCapturedRef = useRef<boolean>(false);
  const isMapLoadedRef = useRef<boolean>(false); // Track if the map has completed its initial load
  const mapRef = useRef<mapboxgl.Map | null>(null);
  const { data: session } = useSession({ required: true });

  if (typeof mapboxAccessToken !== "string") {
    throw new Error(messages.mapApiError);
  }

  const onGeoloateError = (error: GeolocateErrorEvent) => {
    if (error.code === 1) {
      toastCtx?.pushToast("error", messages.mapErrorNoPermissions);
    }
  };

  const transformRequest: TransformRequestFunction = (url: string) => {
    if (url.startsWith(config.workerSafetyServiceUrlGraphQL)) {
      return {
        url: url,
        headers: { Authorization: `Bearer ${session?.accessToken}` },
      };
    }
    return { url: url };
  };

  useEffect(() => {
    if (hasUserLocation && geolocateControlRef.current) {
      geolocateControlRef.current.trigger();
    }
    if (session?.error) void signIn("keycloak", { redirect: true });
  }, [geolocateControlRef.current, hasUserLocation]);

  const onGeolocateSuccess = (position: {
    coords: { latitude: number; longitude: number; accuracy: number };
  }) => {
    if (!locationCapturedRef.current) {
      const { latitude, longitude, accuracy } = position.coords;
      if (setPositionCoords) {
        setPositionCoords({ latitude, longitude, accuracy });
      }
      locationCapturedRef.current = true;
    }
  };

  const handleMapMoveEnd = () => {
    if (isMapLoadedRef.current && setIsMapStable) {
      if (mapRef.current) {
        const center = mapRef.current.getCenter();
        const zoom = mapRef.current.getZoom();
        const mapView = JSON.stringify({
          center: [center.lng, center.lat],
          zoom: zoom,
        });
        sessionStorage.setItem("mapView", mapView);
      }
      setIsMapStable(true);
    }
  };

  const handleMapLoad = (event: mapboxgl.EventData) => {
    const map = event.target as mapboxgl.Map;
    mapRef.current = map;

    isMapLoadedRef.current = true;

    map.on("idle", () => {
      if (isMapLoadedRef.current && setIsMapStable) {
        setIsMapStable(true);
      }
    });
  };

  return (
    <div className={cx("relative", className)} data-testid="map">
      <ReactMapbox
        id={id}
        ref={ref}
        mapboxAccessToken={mapboxAccessToken}
        initialViewState={
          initialViewState || {
            ...COUNTRIES_COORDINATES.US,
            zoom: 12,
          }
        }
        mapStyle={MAP_STYLES[mapStyle]}
        // WSAPP-486 - comenting this prop for now, as when reuseMaps is set to true, when a map component is unmounted, the underlying Map instance is retained in memory.
        // and this is causing some inconsistency in the risk legend's behaviour

        //reuseMaps
        touchPitch={hasZoom}
        attributionControl={false}
        transformRequest={transformRequest}
        onLoad={handleMapLoad}
        onMoveEnd={handleMapMoveEnd}
        interactive={interactive}
      >
        {hasZoom && (
          <NavigationControl
            style={navigationControlStyle}
            showZoom
            showCompass={false}
          />
        )}

        {hasUserLocation && (
          <GeolocateControl
            ref={
              modalMapView || modalMapView === undefined
                ? geolocateControlRef
                : null
            }
            style={geolocateControlStyle}
            showUserLocation
            showUserHeading
            trackUserLocation
            onGeolocate={onGeolocateSuccess}
            onError={onGeoloateError}
          />
        )}

        {children}
      </ReactMapbox>
    </div>
  );
}

export { MapProvider };

export default forwardRef(Map);