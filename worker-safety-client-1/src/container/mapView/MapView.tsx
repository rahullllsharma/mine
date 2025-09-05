import type { MapStyleType } from "@/components/map/configs/mapStyles";
import type { LocationMarkerEvent } from "@/components/map/locationMarker/LocationMarker";
import type { MapLocation } from "@/types/project/Location";
import type { ChangeEvent } from "react";
import type { MapRef } from "react-map-gl";
import type {
  FilterField,
  LocationFilter,
} from "./filters/mapFilters/MapFilters";
import type { MultiOption } from "./filters/multiOptionWrapper/MultiOptionWrapper";
import type { PositionCoordsType } from "@/components/map/Map";
import type {
  LocationVariables,
  MapViewMobileViews,
  MapProjectLibraries,
  QuickFilter,
  LatLng,
  MapBounds,
} from "./utils/mapView.types";
import {
  ApolloError,
  useLazyQuery,
  useMutation,
  useQuery,
} from "@apollo/client";
import cx from "classnames";
import mapboxgl from "mapbox-gl";
import router from "next/router";
import { useCallback, useContext, useEffect, useRef, useState } from "react";
import { DateTime } from "luxon";
import { Icon } from "@urbint/silica";
import { isMobile, isTablet } from "react-device-detect";
import { RiskLevel } from "@/components/riskBadge/RiskLevel";
import PageLayout from "@/components/layout/pageLayout/PageLayout";
import Map, { MapProvider } from "@/components/map/Map";
import LocationMarker from "@/components/map/locationMarker/LocationMarker";
import MapPopup from "@/components/map/popup/MapPopup";
import RiskLegend from "@/components/map/riskLegend/RiskLegend";
import ButtonSecondary from "@/components/shared/button/secondary/ButtonSecondary";
import Input from "@/components/shared/input/Input";
import PopoverIcon from "@/components/shared/popover/popoverIcon/PopoverIcon";
import { config } from "@/config";
import MapFiltersQuery from "@/graphql/queries/MapProjectLibraries.query.gql";
import { orderByName, orderByRiskLevel } from "@/graphql/utils";
import { useTenantFeatures } from "@/hooks/useTenantFeatures";
import { useTenantStore } from "@/store/tenant/useTenantStore.store";
import { isFeatureEnabled } from "@/utils/env";
import { useAuthStore } from "@/store/auth/useAuthStore.store";
import ToastContext from "@/components/shared/toast/context/ToastContext";
import { sentenceCap } from "@/utils/risk";
import LocationRiskIcon from "@/components/map/locationRiskIcon/LocationRiskIcon";
import { sessionExpiryHandlerForApolloClient } from "@/utils/auth";
import LocationsCount from "../../../src/graphql/queries/locationCount.gql";
import DatedLocationsInfo from "../../../src/graphql/queries/datedLocationsInfo.gql";
import SearchedLocationsCount from "../../../src/graphql/queries/searchedLocationsCount.gql";
import LocationsSearch from "../../../src/graphql/queries/locationsSearch.gql";
import SaveMapFiltersMutation from "../../pages/map/SaveMapFilters.mutation.gql";
import MapFilters, {
  getRiskLevelOptions,
} from "./filters/mapFilters/MapFilters";
import { Clusters } from "./clustering/Clusters";
import { FloatingActionButton } from "./components/floatingActionButton/FloatingActionButton";
import { MapPopupContent } from "./components/mapPopupContent/MapPopupContent";
import { useMapContext } from "./context/MapProvider";
import { LocationCards } from "./hoc/locationCards";
import MapLayersMenu from "./mapLayersMenu/MapLayersMenu";
import { calculateBoundsFromInitialRef, parseFilters } from "./utils";

const SET_LOCATIONS_LIMIT = 200;

const zoomPaddingObj = { padding: 20, maxZoom: 17 };

export default function MapView(): JSX.Element {
  const abortControllerRef = useRef<AbortController | null>(null);
  const {
    tenant: { name: tenantName },
    getAllEntities,
  } = useTenantStore();
  const { me } = useAuthStore();
  const entitiesAttributes = getAllEntities();
  const { location: locationEntity } = entitiesAttributes;
  const { displayLocationCardDynamicProps } = useTenantFeatures(tenantName);
  const mapRef = useRef<MapRef | null>(null);
  const { riskLegend, satelliteView, filters, setFilters } = useMapContext();
  const [filteredLocations, setFilteredLocations] = useState<MapLocation[]>(
    () => {
      const storedLocations = sessionStorage.getItem("filteredLocationsStore");
      return storedLocations ? JSON.parse(storedLocations) : [];
    }
  );
  const [locationCardsDataRaw, setLocationCardsDataRaw] = useState<
    MapLocation[]
  >([]);
  const [isSearchThisAreaVisible, setIsSearchThisAreaVisible] = useState(false);
  const [activeViewOnMobile, setActiveViewOnMobile] =
    useState<MapViewMobileViews>("map");
  const [showFilters, setShowFilters] = useState(false);
  const searchRef = useRef<HTMLInputElement>(null);
  const isClusteringEnabled = isFeatureEnabled("map_clustering");
  const [searchInputValue, setSearchInputValue] = useState("");
  const quickFilterOptions = useRef<MultiOption[]>([]);
  const [quickFilterButtons, setQuickFilterButtons] = useState<QuickFilter[]>(
    []
  );
  const [currentPosition, setCurrentPosition] = useState([0, 0]);
  const [showLoading, setShowLoading] = useState(true);
  const [locationByIdData, setLocationByIdData] = useState<MapLocation | null>(
    null
  );
  const [positionCoords, setPositionCoords] =
    useState<PositionCoordsType | null>(null);
  const [isMapStable, setIsMapStable] = useState<boolean>(false);
  const initialVariablesRef = useRef<LocationVariables | null>();
  const [storedMapView] = useState(sessionStorage.getItem("mapView"));

  const [isFirstRender, setIsFirstRender] = useState(true);
  const [hasInitialized, setHasInitialized] = useState(false);
  const globalFilters = ["DIVISIONS", "REGIONS", "CONTRACTOR", "SUPERVISOR"];
  const [isSearchAreaActive, setIsSearchAreaActive] = useState(true);
  const getGlobalBounds = () => {
    return {
      getNorthEast: () => ({ lat: 90, lng: 180 }),
      getSouthWest: () => ({ lat: -90, lng: -180 }),
    };
  };
  const DEFAULT_US_CENTER = {
    longitude: -98.5795,
    latitude: 39.8283,
    zoom: 3.5,
  };

  const checkLocationPermission = useCallback(() => {
    if (!navigator.geolocation) {
      setShowLoading(false);
      setCurrentPosition([
        DEFAULT_US_CENTER.longitude,
        DEFAULT_US_CENTER.latitude,
      ]);

      if (storedMapView) {
        restoreMapAndSidebarData();
      } else {
        if (mapRef.current) {
          mapRef.current.flyTo({
            center: [DEFAULT_US_CENTER.longitude, DEFAULT_US_CENTER.latitude],
            zoom: DEFAULT_US_CENTER.zoom,
            duration: 0,
            essential: true,
          });
        }
      }
      setHasInitialized(true);
      return;
    }

    navigator.permissions
      .query({ name: "geolocation" })
      .then(result => {
        if (result.state === "denied" || result.state === "prompt") {
          setShowLoading(false);
          setCurrentPosition([
            DEFAULT_US_CENTER.longitude,
            DEFAULT_US_CENTER.latitude,
          ]);

          if (storedMapView) {
            restoreMapAndSidebarData();
          } else {
            if (mapRef.current) {
              mapRef.current.flyTo({
                center: [
                  DEFAULT_US_CENTER.longitude,
                  DEFAULT_US_CENTER.latitude,
                ],
                zoom: DEFAULT_US_CENTER.zoom,
                duration: 0,
                essential: true,
              });
            }
          }
          setHasInitialized(true);
        }
      })
      .catch(() => {
        setShowLoading(false);
        setCurrentPosition([
          DEFAULT_US_CENTER.longitude,
          DEFAULT_US_CENTER.latitude,
        ]);

        if (storedMapView) {
          restoreMapAndSidebarData();
        } else {
          if (mapRef.current) {
            mapRef.current.flyTo({
              center: [DEFAULT_US_CENTER.longitude, DEFAULT_US_CENTER.latitude],
              zoom: DEFAULT_US_CENTER.zoom,
              duration: 0,
              essential: true,
            });
          }
        }
        setHasInitialized(true);
      });
  }, []);

  const restoreMapAndSidebarData = useCallback(() => {
    if (storedMapView && mapRef.current) {
      const { center, zoom } = JSON.parse(storedMapView);

      mapRef.current.flyTo({
        center: center,
        zoom: zoom,
        duration: 0,
        essential: true,
      });

      const storedLocations = sessionStorage.getItem("filteredLocationsStore");
      if (storedLocations) {
        try {
          const parsedLocations = JSON.parse(storedLocations);
          if (Array.isArray(parsedLocations)) {
            setFilteredLocations(parsedLocations);
            setLocationCardsDataRaw(parsedLocations);
            setIsSearchAreaActive(true);
          }
        } catch (error) {
          console.error("Error parsing stored locations:", error);
          setFilteredLocations([]);
          setLocationCardsDataRaw([]);
        }
      }
      setHasInitialized(true);
    }
  }, [storedMapView, setHasInitialized]);

  useEffect(() => {
    checkLocationPermission();
  }, [checkLocationPermission]);

  const getVariables = () => {
    const currentDate = DateTime.fromJSDate(new Date());
    const nextDate = currentDate.plus({ days: 1 }).toISODate();
    const previousDate = currentDate.minus({ days: 1 }).toISODate();
    const variables: LocationVariables = {
      startDate: previousDate,
      endDate: nextDate,
      filterBy: parseFilters(filters),
      search: searchRef.current?.value,
      orderBy: [orderByRiskLevel, orderByName],
    };
    return variables;
  };
  const getDatedLocVariables = (bounds: any) => {
    const variables: LocationVariables = getVariables();
    const filterSelected = variables.filterBy || [];
    const hasGlobalFilters = filterSelected.some(filter =>
      globalFilters.includes(filter.field)
    );
    const boundaries = hasGlobalFilters ? getGlobalBounds() : bounds;
    variables.minX = boundaries.getSouthWest().lng;
    variables.maxX = boundaries.getNorthEast().lng;
    variables.maxY = boundaries.getNorthEast().lat;
    variables.minY = boundaries.getSouthWest().lat;
    return variables;
  };

  const getVariablesWithLimit = (datedLoc = false) => {
    const variables: LocationVariables = getVariables();
    if (datedLoc) {
      variables["minX"] = 0;
      variables["maxX"] = 0;
      variables["maxY"] = 0;
      variables["minY"] = 0;
    }
    variables["limit"] = 0;
    variables["offset"] = 0;
    return variables;
  };

  const stateReset = () => {
    setFilteredLocations([]);
    setLocationCardsDataRaw([]);
    setShowLoading(true);
    setIsSearchThisAreaVisible(false);
    setIsSearchAreaActive(false);
  };

  const [getLocationCount, { loading: loadingLocCount }] = useLazyQuery(
    LocationsCount,
    {
      fetchPolicy: "cache-and-network",
      onError: _err => {
        sessionExpiryHandlerForApolloClient(_err);
        toastCtx?.pushToast(
          "error",
          "Error while getting dated project locations"
        );
      },
      onCompleted: async data => {
        if (data?.filterLocationDateRange?.length > 0) {
          const locCount = data.filterLocationDateRange[0].locationsCount;
          const bounds = initialVariablesRef.current
            ? calculateBoundsFromInitialRef(initialVariablesRef.current)
            : mapRef.current?.getBounds();
          if (
            locCount > 0 &&
            (!searchRef.current?.value || !searchRef.current?.value.length) &&
            bounds &&
            bounds.getNorthEast() &&
            bounds.getSouthWest()
          ) {
            const variables = getDatedLocVariables(bounds);
            if (initialVariablesRef.current) {
              initialVariablesRef.current = null;
            }
            stateReset();
            for (let i = 0; i < locCount; i += SET_LOCATIONS_LIMIT) {
              try {
                const locationData = await fetchMoreDatedLoc({
                  variables: {
                    ...variables,
                    offset: i,
                    limit: SET_LOCATIONS_LIMIT,
                  },
                  context: {
                    fetchOptions: {
                      signal: abortControllerRef.current?.signal,
                    },
                  },
                });
                if (i === 0) {
                  setShowLoading(false);
                }
                setIsSearchThisAreaVisible(true);
                if (locationData?.data?.filterLocationDateRange?.length > 0) {
                  setFilteredLocations(prev =>
                    prev.concat(
                      locationData?.data?.filterLocationDateRange[0]
                        .filterLocationsDateRange
                    )
                  );
                  setLocationCardsDataRaw(prev =>
                    prev.concat(
                      locationData?.data?.filterLocationDateRange[0]
                        .filterLocationsDateRange
                    )
                  );
                }
              } catch (error: unknown) {
                if (
                  error instanceof Error &&
                  (error.name === "AbortError" || error.message === "Aborted")
                ) {
                  return;
                } else {
                  throw new ApolloError({
                    networkError:
                      error instanceof Error
                        ? error
                        : new Error("Unknown error"),
                  });
                }
              } finally {
                setShowLoading(false);
                if (i + SET_LOCATIONS_LIMIT >= locCount) {
                  setIsSearchAreaActive(true);
                }
              }
            }
          } else {
            setShowLoading(false);
            setFilteredLocations([]);
            setLocationCardsDataRaw([]);
          }
        }
        saveMapFilters({
          variables: {
            userId: me.id,
            data: JSON.stringify(filters),
          },
        });
        setShowFilters(false);
      },
    }
  );

  const [getSearchedLocationCount, { loading: loadingSearchLocCount }] =
    useLazyQuery(SearchedLocationsCount, {
      fetchPolicy: "cache-and-network",
      onError: _err => {
        sessionExpiryHandlerForApolloClient(_err);
        toastCtx?.pushToast(
          "error",
          "Error while getting searched project locations"
        );
      },
      onCompleted: async data => {
        if (data?.filterLocationDateRange?.length > 0) {
          const locCount = data.filterLocationDateRange[0].locationsCount;
          if (locCount > 0) {
            const variables = getVariables();
            initialVariablesRef.current = null;
            stateReset();
            for (let i = 0; i < locCount; i = i + SET_LOCATIONS_LIMIT) {
              const locationData = await fetchMoreSearchLoc({
                variables: {
                  ...variables,
                  offset: i,
                  limit: SET_LOCATIONS_LIMIT,
                },
              });
              if (i === 0) {
                setShowLoading(false);
              }
              setIsSearchThisAreaVisible(true);

              if (locationData?.data?.filterLocationDateRange?.length > 0) {
                setFilteredLocations(prev =>
                  prev.concat(
                    locationData?.data?.filterLocationDateRange[0]
                      .filterLocationsDateRange
                  )
                );
                setLocationCardsDataRaw(prev =>
                  prev.concat(
                    locationData?.data?.filterLocationDateRange[0]
                      .filterLocationsDateRange
                  )
                );
              }
            }
            setShowLoading(false);
            setIsSearchAreaActive(true);
          } else {
            setShowLoading(false);
            setFilteredLocations([]);
            setLocationCardsDataRaw([]);
          }
        }
        saveMapFilters({
          variables: {
            userId: me.id,
            data: JSON.stringify(filters),
          },
        });
        setShowFilters(false);
      },
    });

  const toastCtx = useContext(ToastContext);
  const { fetchMore: fetchMoreSearchLoc, loading: loadingSearchLocations } =
    useQuery(LocationsSearch, {
      fetchPolicy: "cache-and-network",
      skip: true,
      variables: getVariablesWithLimit(),
      onError: _err => {
        sessionExpiryHandlerForApolloClient(_err);
        toastCtx?.pushToast(
          "error",
          "Error while getting searched project locations"
        );
      },
    });

  const { fetchMore: fetchMoreDatedLoc, loading: loadingLocations } = useQuery(
    DatedLocationsInfo,
    {
      fetchPolicy: "cache-and-network",
      skip: true,
      variables: getVariablesWithLimit(true),
      onError: _err => {
        sessionExpiryHandlerForApolloClient(_err);
        toastCtx?.pushToast(
          "error",
          "Error while getting dated project locations"
        );
      },
    }
  );

  const [getProjectLibraries, { data: projectLibrariesRaw }] = useLazyQuery(
    MapFiltersQuery,
    {
      fetchPolicy: "cache-and-network",
      notifyOnNetworkStatusChange: true,
      onError: _err => {
        sessionExpiryHandlerForApolloClient(_err);
        toastCtx?.pushToast("error", "Error while getting project libraries");
      },
    }
  );

  const [saveMapFilters] = useMutation(SaveMapFiltersMutation);

  const projectLibraries: MapProjectLibraries = projectLibrariesRaw ?? {
    projectTypesLibrary: [],
    divisionsLibrary: [],
    regionsLibrary: [],
    contractors: [],
    supervisors: [],
  };
  const locationCards = locationCardsDataRaw ?? [];

  useEffect(() => {
    setLocationByIdData(locationCardsDataRaw[0]);
  }, [locationCardsDataRaw]);

  const getBounds = useCallback(() => {
    const bounds = new mapboxgl.LngLatBounds();
    filteredLocations.forEach(location => {
      bounds.extend([+location.longitude, +location.latitude]);
    });
    return bounds;
  }, [filteredLocations]);

  const fitBounds = useCallback(() => {
    if (!mapRef.current || filteredLocations.length === 0) {
      return;
    }

    const mapBound = getBounds();
    const fitBoundsOptions = storedMapView
      ? {
          padding: 20,
          maxZoom: JSON.parse(storedMapView).zoom,
        }
      : zoomPaddingObj;
    mapRef.current.fitBounds(mapBound, fitBoundsOptions);
  }, [currentPosition, getBounds, filteredLocations.length]);

  useEffect(() => {
    if (filteredLocations.length <= SET_LOCATIONS_LIMIT) {
      fitBounds();
    }
  }, [filteredLocations, fitBounds]);

  useEffect(() => {
    getRiskLevelOptions.forEach(item => {
      const obj: QuickFilter = {
        id: item.id,
        name: item.name,
        icon: "chevron_up",
        state: false,
      };

      switch (item.id) {
        case RiskLevel.LOW:
          obj["icon"] = "chevron_down";
        case RiskLevel.MEDIUM:
          obj["icon"] = "tilde";
        case RiskLevel.UNKNOWN:
          obj["icon"] = "help_questionmark";
        case RiskLevel.HIGH:
        default:
          obj["icon"] = "chevron_up";
      }
      setQuickFilterButtons(prevState => [...prevState, obj]);
    });
  }, []);

  const {
    projectTypesLibrary,
    divisionsLibrary,
    regionsLibrary,
    contractors,
    supervisors,
  } = projectLibraries;

  useEffect(() => {
    getProjectLibraries({
      variables: {
        orderBy: [orderByName],
      },
    });
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  useEffect(() => {
    updateQuickFilterStates();
    const bounds = mapRef.current?.getBounds();
    if (!searchRef.current?.value || !searchRef.current?.value.length) {
      if (bounds && bounds.getNorthEast() && bounds.getSouthWest()) {
        const variables = getDatedLocVariables(bounds);
        getLocationCount({ variables });
      }
    } else {
      const variables = getVariables();
      getSearchedLocationCount({ variables });
    }
  }, [filters, quickFilterButtons]);

  const isMapViewActiveOnMobile = activeViewOnMobile === "map";
  const mapStyle: MapStyleType = satelliteView.isActive
    ? "SATELLITE_STREETS"
    : "STREETS";

  const locationMarkerClick = (
    mapboxEvent: LocationMarkerEvent,
    mapLocation: MapLocation
  ) => {
    mapboxEvent.originalEvent.stopPropagation(); // https://github.com/visgl/react-map-gl/blob/7.0-release/examples/controls/src/app.tsx#L32
    filteredLocations.forEach(location => {
      if (location.id === mapLocation.id) {
        setLocationByIdData(location);
      }
    });
  };

  const onMouseEnter = (locationId: string) => {
    filteredLocations.forEach(location => {
      if (location.id === locationId) {
        setLocationByIdData(location);
      }
    });
  };

  const locationCardClickHandler = (location: MapLocation) => {
    router.push({
      pathname: "/projects/[id]",
      query: {
        id: location.project.id,
        location: location.id,
        source: "map",
      },
    });
  };

  const isMarkerActive = (location: MapLocation) =>
    location.id === locationByIdData?.id;

  const toggleFilters = () => setShowFilters(prevState => !prevState);

  const totalFiltersSelected = filters.reduce(
    (acc, filter) => acc + filter.values.length,
    0
  );

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
        getLocationCount({ variables });
      }
    } else {
      const variables = getVariables();
      getSearchedLocationCount({ variables });
    }
  };
  const triggerMapRef = (ref: MapRef | null) => {
    if (ref) {
      if (mapRef.current != null) {
        mapRef.current.on("zoom", () => {
          setIsSearchThisAreaVisible(true);
        });
        mapRef.current.on("dragend", () => {
          setIsSearchThisAreaVisible(true);
        });
      }
    }
  };

  useEffect(() => {
    if (positionCoords && !hasInitialized) {
      const { latitude, longitude, accuracy } = positionCoords;
      setShowLoading(false);
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
      setHasInitialized(true);
    }
  }, [positionCoords, hasInitialized]);

  useEffect(() => {
    if (isMapStable && positionCoords && !hasInitialized) {
      const { latitude, longitude, accuracy } = positionCoords;
      if (accuracy < 3000) {
        getCurrentBoundsData(longitude, latitude);
      }
    }
  }, [isMapStable, positionCoords, hasInitialized]);

  const getCurrentBoundsData = (longitude: number, latitude: number) => {
    if (storedMapView) {
      restoreMapView();
    } else {
      loadData(longitude, latitude);
    }
  };

  const handleButtonClick = () => {
    if (abortControllerRef.current) {
      abortControllerRef.current.abort();
    }

    const newAbortController = new AbortController();
    abortControllerRef.current = newAbortController;

    if (mapRef.current?.getBounds()) {
      const bounds = mapRef.current?.getBounds();
      if (!searchRef.current?.value || !searchRef.current?.value.length) {
        if (bounds && bounds.getNorthEast() && bounds.getSouthWest()) {
          const variables = getDatedLocVariables(bounds);
          initialVariablesRef.current = variables;
          getLocationCount({
            variables,
            context: { fetchOptions: { signal: newAbortController.signal } },
          });
        }
      } else {
        const variables = getVariables();
        getSearchedLocationCount({
          variables,
          context: { fetchOptions: { signal: newAbortController.signal } },
        });
      }
    }
  };

  const searchBtnOnClick = (event: React.KeyboardEvent<HTMLInputElement>) => {
    if (event.key === "Enter") {
      setIsSearchThisAreaVisible(false);
      const bounds = mapRef.current?.getBounds();
      if (!searchRef.current?.value || !searchRef.current?.value.length) {
        if (bounds && bounds.getNorthEast() && bounds.getSouthWest()) {
          const variables = getDatedLocVariables(bounds);
          getLocationCount({ variables });
        }
      } else {
        setSearchInputValue(searchRef.current?.value);
        const variables = getVariables();
        getSearchedLocationCount({ variables });
      }
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
        const storedLocations = JSON.parse(
          sessionStorage.getItem("filteredLocationsStore") || "[]"
        );
        if (Array.isArray(storedLocations)) {
          setFilteredLocations([...storedLocations]);
          setLocationCardsDataRaw([...storedLocations]);
        } else {
          setFilteredLocations([]);
          setLocationCardsDataRaw([]);
        }
        setIsFirstRender(false);
      }
      setHasInitialized(true);
    }
  };

  useEffect(() => {
    if (filteredLocations.length > 0) {
      const limitedLocations =
        filteredLocations.length > 500
          ? filteredLocations.slice(0, 500)
          : filteredLocations;
      sessionStorage.setItem(
        "filteredLocationsStore",
        JSON.stringify(limitedLocations)
      );
    } else {
      const storedLocations = sessionStorage.getItem("filteredLocationsStore");
      if (storedLocations) {
        sessionStorage.removeItem("filteredLocationsStore");
      }
    }
  }, [filteredLocations]);

  useEffect(() => {
    if (storedMapView && positionCoords && !hasInitialized) {
      restoreMapView();
    }
  }, [storedMapView, positionCoords, hasInitialized]);

  const filterUpdateHandler = (values: MultiOption[], field: FilterField) => {
    const updatedFilters = filters.map((filter: LocationFilter) =>
      filter.field === field ? { field, values } : filter
    );
    setFilters(updatedFilters);
  };

  const toggleQuickFilters = (risk: string) => {
    for (const element of filters) {
      if (element.field === "RISK") {
        const riskIndex = element.values.findIndex(
          (item: MultiOption) => item.name === risk
        );
        return Math.max(riskIndex, -1);
      } else {
        continue;
      }
    }
  };

  const updateQuickFilterStates = () => {
    for (const element of filters) {
      if (element.field === "RISK") {
        if (element.values.length) {
          quickFilterOptions.current = [];
          quickFilterButtons.forEach(quickFilterObj => {
            quickFilterObj.state = false;
          });
          for (const elementValue of element.values) {
            quickFilterOptions.current.push(elementValue);
            quickFilterButtons.forEach(quickFilterObj => {
              if (elementValue.name === quickFilterObj.name) {
                quickFilterObj.state = true;
              }
            });
          }
        } else {
          quickFilterOptions.current.splice(
            0,
            quickFilterOptions.current.length
          );
          quickFilterButtons.forEach(quickFilterObj => {
            quickFilterObj.state = false;
          });
        }
      } else continue;
    }
  };

  const quickFilterButtonOnClick = (
    event: React.MouseEvent<HTMLButtonElement, MouseEvent>
  ) => {
    const id = event?.currentTarget?.id;

    quickFilterButtons.forEach((filterBtn: QuickFilter, index) => {
      if (id == "riskBtn" + index) {
        const riskFilterIndex = toggleQuickFilters(filterBtn.name);
        if (riskFilterIndex == -1) {
          filterBtn.state = true;
          quickFilterOptions.current.push({
            id: filterBtn.id,
            name: filterBtn.name,
          });
        } else {
          filterBtn.state = false;
          quickFilterOptions.current.splice(riskFilterIndex as number, 1);
        }
      }
    });
    filterUpdateHandler(quickFilterOptions.current, "RISK");
  };

  const locationMarkers = filteredLocations.map(location => {
    const { id, latitude, longitude, riskLevel, datedActivities } = location;
    const isCritical =
      datedActivities?.some(data => data.isCritical === true) || false;

    return (
      <LocationMarker
        key={id}
        latitude={latitude}
        longitude={longitude}
        riskLevel={riskLevel}
        onMouseEnter={() => onMouseEnter(location.id)}
        onClick={event => locationMarkerClick(event, location)}
        isActive={isMarkerActive(location)}
        isCritical={isCritical}
      />
    );
  });

  const getInitialViewState = () => {
    if (storedMapView) {
      const { center, zoom } = JSON.parse(storedMapView);
      return {
        longitude: center[0],
        latitude: center[1],
        zoom: zoom,
      };
    }

    return {
      longitude: currentPosition[0],
      latitude: currentPosition[1],
      zoom: 15,
    };
  };

  const callAPIonFirstLoad = (longitude: number, latitude: number) => {
    const bounds = createBoundsFromLatLng(latitude, longitude);
    if (!searchRef.current?.value || !searchRef.current?.value.length) {
      if (bounds && bounds.getNorthEast() && bounds.getSouthWest()) {
        const variables = getDatedLocVariables(bounds);
        initialVariablesRef.current = variables;
        getLocationCount({ variables });
      }
    } else {
      const variables = getVariables();
      getSearchedLocationCount({ variables });
    }
  };

  return (
    <PageLayout sectionPadding="none" className="h-full">
      <div className="flex gap-4 py-2 px-3">
        <Input
          containerClassName="w-full md:w-78 lg:flex lg:w-78"
          placeholder={`Search ${locationEntity.labelPlural.toLowerCase()}`}
          onChange={(e: ChangeEvent<HTMLInputElement>) => {
            setSearchInputValue(e.target.value);
          }}
          onKeyDown={searchBtnOnClick}
          icon="search"
          allowClear={true}
          clearInputText={() => {
            setSearchInputValue("");
            const bounds = mapRef.current?.getBounds();
            if (bounds && bounds.getNorthEast() && bounds.getSouthWest()) {
              const variables = getDatedLocVariables(bounds);
              getLocationCount({ variables });
            }
          }}
          ref={searchRef}
          value={searchInputValue}
        />
        {!isMobile && !isTablet && (
          <div className="flex items-center gap-2 md:ml-auto">
            {quickFilterButtons.map((object: QuickFilter, index) => (
              <ButtonSecondary
                key={index}
                id={"riskBtn" + index}
                label={
                  <div className="flex items-center gap-2">
                    {object.state && <Icon name="check_big" />}
                    {sentenceCap(object.id)}
                    <LocationRiskIcon
                      riskLevel={object.id as RiskLevel}
                      label="badge"
                    ></LocationRiskIcon>
                  </div>
                }
                controlStateClass="text-base p-1.5"
                className="border border-neutral-shade-26 shadow-5 hover:shadow-10 text-neutral-shade-100 flex-shrink-0"
                onClick={quickFilterButtonOnClick}
                disabled={!isSearchAreaActive}
              />
            ))}
          </div>
        )}

        <div className="flex items-center gap-2 md:ml-auto">
          <span className="hidden md:block text-tiny text-neutral-shade-75 flex-shrink-0">
            {filteredLocations.length} results
          </span>
          <ButtonSecondary
            iconStart="filter"
            label={
              totalFiltersSelected > 0
                ? `(${totalFiltersSelected.toString()})`
                : ""
            }
            controlStateClass="text-base p-1.5"
            className="text-neutral-shade-100 flex-shrink-0"
            onClick={toggleFilters}
            disabled={!isSearchAreaActive}
          />
        </div>
      </div>
      <MapProvider>
        <div className="relative overflow-hidden h-full sm:flex sm:grow">
          <aside
            className={cx(
              "absolute inset-0 bg-white w-full sm:relative sm:block sm:max-w-[300px] bottom-0",
              {
                "z-10": !isMapViewActiveOnMobile,
              }
            )}
          >
            <LocationCards
              elements={locationCards}
              onElementClick={locationCardClickHandler}
              isLoading={
                loadingLocCount ||
                loadingSearchLocCount ||
                loadingLocations ||
                loadingSearchLocations ||
                showLoading
              }
            />
          </aside>
          <Map
            id="project-map-view"
            ref={ref => {
              mapRef.current = ref;
              triggerMapRef(ref);
            }}
            mapStyle={mapStyle}
            mapboxAccessToken={config.workerSafetyMapboxAccessToken}
            hasZoom
            hasUserLocation
            className={"w-full h-full"}
            setPositionCoords={setPositionCoords}
            setIsMapStable={setIsMapStable}
            initialViewState={getInitialViewState()}
          >
            {isMobile && (
              <div className="flex gap-4 py-2 ">
                <div className="flex px-4 mt-1 w-full sm:justify-center  top-0 absolute bg-transparent items-center gap-2 md:ml-auto overflow-x-auto no-scrollbar  ">
                  {quickFilterButtons.map((object: QuickFilter, index) => (
                    <ButtonSecondary
                      key={index}
                      id={"riskBtn" + index}
                      label={
                        <div className="flex items-center gap-2 text-[13px] font-normal ">
                          {object.state && <Icon name="check_big" />}
                          {sentenceCap(object.id)}
                          <LocationRiskIcon
                            riskLevel={object.id as RiskLevel}
                            label="badge"
                          ></LocationRiskIcon>
                        </div>
                      }
                      controlStateClass="text-base p-1.5"
                      className="border border-neutral-shade-26 rounded-[10px] shadow-5 hover:shadow-10 text-neutral-shade-100 flex-shrink-0"
                      onClick={quickFilterButtonOnClick}
                      disabled={!isSearchAreaActive}
                    />
                  ))}
                </div>
              </div>
            )}
            {isSearchThisAreaVisible && (
              <div className="absolute top-10 left-0 right-0 flex justify-center">
                <div className="bg-neutral-light-100 px-2 py-3 h-8 flex justify-center items-center border border-neutral-shade-26 shadow-5 border-solid border-borders rounded-xl appearance-none">
                  <Icon name="search" className="text-lg" />
                  <button
                    className="bg-neutral-light-100 px-1 flex justify-center items-center appearance-none font-normal font-inter text-sm"
                    onClick={handleButtonClick}
                  >
                    Search this area
                  </button>
                </div>
              </div>
            )}
            <aside className="absolute bg-white right-2.5 top-24 mt-14 rounded shadow-20 sm:top-18 lg:top-20 xl:top-18 2xl:top-8">
              <PopoverIcon
                className="w-72 right-10"
                iconName="layers_outline"
                iconClass="text-neutral-shade-75 text-2xl p-0.5"
                tooltipProps={{
                  title: "Manage map layers",
                  position: "left",
                  closeOnClick: true,
                }}
              >
                <MapLayersMenu />
              </PopoverIcon>
            </aside>

            {isClusteringEnabled ? (
              <Clusters
                search={searchRef.current?.value}
                filters={parseFilters(filters)}
                onLocationMarkerMouseEnter={onMouseEnter}
              />
            ) : (
              locationMarkers
            )}

            {riskLegend.isActive && (
              <RiskLegend
                position="none"
                label={`${locationEntity.label} Risk`}
                className={cx(
                  "transition-all md:mb-16 mb-3 motion-reduce:transition-none bottom-16 right-4 md:bottom-4"
                )}
              />
            )}

            {locationByIdData && (
              <MapPopup
                longitude={locationByIdData.longitude}
                latitude={locationByIdData.latitude}
                onClose={() => setLocationByIdData(null)}
                className="w-78"
              >
                <MapPopupContent
                  onClick={() => locationCardClickHandler(locationByIdData)}
                  location={locationByIdData}
                  displayLocationCardDynamicProps={
                    displayLocationCardDynamicProps
                  }
                />
              </MapPopup>
            )}
          </Map>
          <MapFilters
            projectTypesLibrary={projectTypesLibrary}
            divisionsLibrary={divisionsLibrary}
            regionsLibrary={regionsLibrary}
            supervisors={supervisors}
            contractors={contractors}
            isOpen={showFilters}
            onClose={toggleFilters}
          />
        </div>
      </MapProvider>
      <FloatingActionButton
        className="left-4 motion-reduce:transition-none transition-transform scale-100 sm:scale-0 sm:invisible mb-16 max-w-max"
        onClick={() =>
          setActiveViewOnMobile(prev => (prev === "map" ? "list" : "map"))
        }
        label={`Show ${isMapViewActiveOnMobile ? "list" : "map"}`}
        icon={isMapViewActiveOnMobile ? "list_ul" : "map"}
      />
    </PageLayout>
  );
}
