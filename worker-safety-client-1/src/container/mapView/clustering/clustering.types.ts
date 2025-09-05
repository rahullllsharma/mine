import type { MapboxGeoJSONFeature } from "react-map-gl";
import type { RiskLevel } from "@/components/riskBadge/RiskLevel";
import type { FilterField } from "../filters/mapFilters/MapFilters";

export type ClusterProperties = {
  clusterId: string;
  HIGH: number;
  LOW: number;
  MEDIUM: number;
  RECALCULATING: number;
  UNKNOWN: number;
  length: number;
};

export type LocationProperties = {
  locationId: string;
  projectId: string;
  risk: RiskLevel;
};

export type ClusterProps = {
  search?: string;
  filters: { field: FilterField; values: string[] }[];
  onLocationMarkerMouseEnter: (locationId: string) => void;
};

export type DonutProps = {
  properties: ClusterProperties;
  onClickCallback: (clusterId: string, properties: ClusterProperties) => void;
};

export type LocationMarkerProps = {
  properties: LocationProperties;
  onClickCallback: (projectId: string, locationId: string) => void;
  onMouseEnterCallback: (locationId: string) => void;
};

export type MapIconCollection = { [key: string]: mapboxgl.Marker | undefined };

export enum MapFeatureType {
  "Location" = "Location",
  "Cluster" = "Cluster",
}

export type ClusterFeature = MapboxGeoJSONFeature & {
  mapFeatureType: MapFeatureType.Cluster;
  properties: ClusterProperties;
  geometry: { type: string; coordinates: [number, number] };
};

export type LocationFeature = MapboxGeoJSONFeature & {
  mapFeatureType: MapFeatureType.Location;
  properties: LocationProperties;
  geometry: { type: string; coordinates: [number, number] };
};

export type MapFeature = ClusterFeature | LocationFeature;
export type MapFeatureCollection = { [key: string]: MapFeature };
