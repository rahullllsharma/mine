import type { LayerProps } from "react-map-gl";
import type { MapEventType } from "mapbox-gl";
import type {
  ClusterFeature,
  ClusterProperties,
  ClusterProps,
  MapFeatureCollection,
  MapIconCollection,
} from "./clustering.types";
import { forEach } from "lodash-es";
import router from "next/router";
import mapboxgl from "mapbox-gl";
import { Layer, Source, useMap } from "react-map-gl";
import { useState, useEffect } from "react";
import { createPortal } from "react-dom";
import { MapFeatureType } from "./clustering.types";
import {
  buildClusterTileUrl,
  getMapIconByFeatureType,
  groupMapFeatures,
} from "./clustering.utils";
import { ClusterCard } from "./ClusterCard";

const locationCardClickHandler = (projectId: string, locationId: string) => {
  router.push({
    pathname: "/projects/[id]",
    query: {
      id: projectId,
      location: locationId,
      source: "map",
    },
  });
};

const locationsProps: LayerProps = {
  id: "location",
  type: "circle",
  source: "location",
  "source-layer": "locations",
  filter: ["has", "risk"],
  paint: {
    "circle-color": "transparent",
    "circle-radius": 1,
  },
  layout: {},
};

const clusterProps: LayerProps = {
  id: "cluster",
  type: "circle",
  source: "cluster",
  "source-layer": "locations",
  paint: {
    "circle-color": "transparent",
    "circle-radius": 1,
  },
  layout: {},
  filter: ["has", "length"],
};

const activeMapIcons: MapIconCollection = {};

const cleanEntireMapIconCollection = (collection: MapIconCollection) => {
  Object.values(collection).forEach(item => item?.remove());
  collection = {};
};

const cleanMapIconCollection = (
  mapIconToClean: string[],
  collectionOfMapIcons: MapIconCollection
) => {
  Object.keys(collectionOfMapIcons).forEach(referenceId => {
    if (mapIconToClean.includes(referenceId)) {
      collectionOfMapIcons[referenceId]?.remove();
      delete collectionOfMapIcons[referenceId];
    }
  });
};

function Clusters({
  search,
  filters,
  onLocationMarkerMouseEnter,
}: ClusterProps) {
  // for the card add a div on click
  // use portal to send the card to that div
  const [portalDestinationId, setPortalDestinationId] = useState<
    string | undefined
  >(undefined);
  const [hasVisiblePropertiesModal, setHasVisiblePropertiesModal] =
    useState(false);
  const [visibleProperties, setVisibleProperties] =
    useState<ClusterProperties | null>(null);

  const map = useMap();

  const onClusterClick = (id: string, properties: ClusterProperties) => {
    setPortalDestinationId(id);
    setVisibleProperties(properties);
    setHasVisiblePropertiesModal(true);
  };

  const onClusterClose = () => {
    setPortalDestinationId(undefined);
    setVisibleProperties(null);
    setHasVisiblePropertiesModal(false);
  };

  const addMapIconsToMap = (
    mapFeatureCollection: MapFeatureCollection,
    mapbox: mapboxgl.Map
  ) => {
    forEach(mapFeatureCollection, (mapFeature, referenceId) => {
      const {
        mapFeatureType,
        properties,
        geometry: { coordinates },
      } = mapFeature;

      const mapIcon = activeMapIcons[referenceId];

      if (!mapIcon) {
        let mapIconMarker: HTMLElement;
        if (mapFeatureType === MapFeatureType.Location) {
          mapIconMarker = getMapIconByFeatureType(mapFeatureType)({
            properties,
            onClickCallback: locationCardClickHandler,
            onMouseEnterCallback: onLocationMarkerMouseEnter,
          });
        } else {
          mapIconMarker = getMapIconByFeatureType(mapFeatureType)({
            properties,
            onClickCallback: onClusterClick,
          });
        }

        // Store referece to printed map icon marker for removal
        activeMapIcons[referenceId] = new mapboxgl.Marker(
          mapIconMarker
        ).setLngLat(coordinates);
        activeMapIcons[referenceId]?.addTo(mapbox);
      }
    });
  };

  const updateClusters = (mapbox: MapEventType["render"]["target"]) => {
    const allFeatures = mapbox?.queryRenderedFeatures(undefined, {
      layers: ["cluster", "location"],
    }) as ClusterFeature[];

    const { mapFeatures, referenceIds } = groupMapFeatures(allFeatures);

    if (referenceIds.length === 0) {
      cleanEntireMapIconCollection(activeMapIcons);
      return;
    }

    addMapIconsToMap(mapFeatures, mapbox);

    // active map icon cleanup, removes old printed map icons
    const mapIconsIdsNoLongerInUse = Object.keys(activeMapIcons).filter(
      oldReferenceId => !referenceIds.includes(oldReferenceId)
    );
    cleanMapIconCollection(mapIconsIdsNoLongerInUse, activeMapIcons);
  };

  useEffect(() => {
    if (!map.current) {
      return;
    }

    const mapbox = map.current;

    const listener = (e: MapEventType["render"]) => updateClusters(e.target);

    mapbox.on("render", listener);

    return () => {
      // Reset our cluster variables
      // when we take this layer off the screen
      cleanEntireMapIconCollection(activeMapIcons);
      mapbox.off("render", listener);
    };
    // We only want this to run once on render
  }, []);

  return (
    <>
      <Source
        id="locations"
        key="locations-source"
        type="vector"
        tiles={[buildClusterTileUrl(search, filters)]}
      >
        <Layer key="locations" {...locationsProps} />
        <Layer key="clusters" {...clusterProps} />
      </Source>
      {hasVisiblePropertiesModal &&
        visibleProperties &&
        createPortal(
          <ClusterCard
            properties={visibleProperties}
            onCloseClusterCard={onClusterClose}
          />,
          document.querySelector(
            `[data-cluster-id='${portalDestinationId}']`
          ) ?? document.body
        )}
    </>
  );
}

export { Clusters };
