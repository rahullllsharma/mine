import type { FilterField } from "../filters/mapFilters/MapFilters";
import type {
  ClusterProperties,
  DonutProps,
  LocationMarkerProps,
  MapFeature,
  MapFeatureCollection,
} from "./clustering.types";
import resolveConfig from "tailwindcss/resolveConfig";
import { RiskLevel } from "@/components/riskBadge/RiskLevel";
import {
  getDefaultTextColorByRiskLevel,
  getLocationRiskIconBackgroundColorByRiskLevel,
  getRiskIcon,
} from "@/utils/risk";
import { config } from "@/config";
import customConfig from "../../../../tailwind.config.js";
import { MapFeatureType } from "./clustering.types";
import styles from "./Clustering.module.css";

// eslint-disable-next-line @typescript-eslint/ban-ts-comment
// @ts-ignore
const fullConfig = resolveConfig(customConfig);

// eslint-disable-next-line @typescript-eslint/ban-ts-comment
// @ts-ignore
const RISK_COLORS = fullConfig?.theme?.colors?.risk;
const PROP_MAP = {
  LOW: RISK_COLORS.low ?? "black",
  MEDIUM: RISK_COLORS.medium ?? "black",
  HIGH: RISK_COLORS.high ?? "black",
  UNKNOWN: RISK_COLORS.unknown ?? "black",
  RECALCULATING: RISK_COLORS.recalculating ?? "black",
};

const generateDonutSlice = (
  degrees: number,
  newDegrees: number,
  color: string,
  currentSlicesCss: string
) => {
  let newSlicesCss = currentSlicesCss;

  newSlicesCss = degrees > 0 ? `${currentSlicesCss}, ` : currentSlicesCss;
  newSlicesCss =
    newSlicesCss + `${color} ${degrees}deg ${degrees + newDegrees}deg`;

  return newSlicesCss;
};

const generateDonutCss = (properties: ClusterProperties) => {
  const { length, LOW, MEDIUM, HIGH, UNKNOWN, RECALCULATING } = properties;

  const lowDegrees = LOW ? (LOW / length) * 360 : 0;
  const mediumDegrees = MEDIUM ? (MEDIUM / length) * 360 : 0;
  const highDegrees = HIGH ? (HIGH / length) * 360 : 0;
  const unknownSum = (UNKNOWN ?? 0) + (RECALCULATING ?? 0);
  const unknownDegrees = unknownSum ? (unknownSum / length) * 360 : 0;

  let donutCss = "";
  let degrees = 0;

  if (LOW) {
    donutCss = generateDonutSlice(degrees, lowDegrees, PROP_MAP.LOW, donutCss);
    degrees = degrees + lowDegrees;
  }

  if (MEDIUM) {
    donutCss = generateDonutSlice(
      degrees,
      mediumDegrees,
      PROP_MAP.MEDIUM,
      donutCss
    );
    degrees = degrees + mediumDegrees;
  }

  if (HIGH) {
    donutCss = generateDonutSlice(
      degrees,
      highDegrees,
      PROP_MAP.HIGH,
      donutCss
    );
    degrees = degrees + highDegrees;
  }

  if (UNKNOWN || RECALCULATING) {
    donutCss = generateDonutSlice(
      degrees,
      unknownDegrees,
      PROP_MAP.UNKNOWN,
      donutCss
    );
    degrees = degrees + unknownDegrees;
  }

  return donutCss ? `background: conic-gradient(${donutCss})` : donutCss;
};

const filterToParamMap: { [K in FilterField]: string } = {
  CONTRACTOR: "contractor_ids",
  DIVISIONS: "library_division_ids",
  PROJECT_STATUS: "project_status",
  PROJECT: "project_ids",
  REGIONS: "library_region_ids",
  RISK: "risk_levels",
  SUPERVISOR: "supervisor_ids",
  TYPES: "library_project_type_ids",
};

const buildClusterTileUrl = (
  search?: string,
  filters?: { field: FilterField; values: string[] }[]
) => {
  const baseClusterTileEndpoint = `${config.workerSafetyServiceUrlGraphQL}/locations/tile/{z}/{x}/{y}`;
  const queryParams = new URLSearchParams("?");

  if (search) {
    queryParams.append("search", search);
  }
  if (filters && filters.length > 0) {
    filters.forEach(filter => {
      filter.values.forEach(filterValue =>
        queryParams.append(
          filterToParamMap[filter.field],
          filter.field === "RISK" ? filterValue.toLowerCase() : filterValue
        )
      );
    });
  }

  return baseClusterTileEndpoint + "?" + queryParams.toString();
};

const groupMapFeatures = (
  allFeatures: MapFeature[]
): {
  mapFeatures: MapFeatureCollection;
  referenceIds: string[];
} => {
  return allFeatures.reduce(
    (acc, feature) => {
      const { properties } = feature;
      const isLocation = feature.layer.id === "location";
      const referenceId = isLocation
        ? properties.locationId
        : properties.clusterId;
      const mapFeatureType = isLocation
        ? MapFeatureType.Location
        : MapFeatureType.Cluster;
      feature.mapFeatureType = mapFeatureType;

      return {
        ...acc,
        mapFeatures: { ...acc.mapFeatures, [referenceId]: feature },
        referenceIds: [...acc.referenceIds, referenceId],
      };
    },
    {
      mapFeatures: {},
      referenceIds: [],
    } as {
      mapFeatures: MapFeatureCollection;
      referenceIds: string[];
    }
  );
};

function createDonutChart({ properties, onClickCallback }: DonutProps) {
  const div = document.createElement("div");
  const formattedId = `cluster${properties.clusterId}`;
  div.setAttribute("class", "rounded-full w-10 h-10 bg-white cursor-pointer");

  const wrapperDiv = div.appendChild(document.createElement("div"));
  wrapperDiv.className = "rounded-full w-full h-full relative";
  wrapperDiv.setAttribute("data-cluster-id", formattedId);
  wrapperDiv.addEventListener("click", () => {
    onClickCallback(formattedId, properties);
  });

  const donutCss = generateDonutCss(properties);

  const donutDiv = wrapperDiv.appendChild(document.createElement("div"));
  donutDiv.className = styles["donut"];
  donutDiv.style.cssText = donutCss;

  const lengthDiv = wrapperDiv.appendChild(document.createElement("div"));
  lengthDiv.className =
    "bg-white rounded-full m-auto w-6 h-6 absolute top-0 bottom-0 left-0 right-0 flex flex-wrap justify-center content-center";
  lengthDiv.textContent = properties.length.toString();

  return div;
}

function createLocationMarker({
  properties,
  onClickCallback,
  onMouseEnterCallback,
}: LocationMarkerProps) {
  const iconName = getRiskIcon(properties.risk) ?? "help_questionmark";
  const locationMarker = document.createElement("div");
  const formattedId = `location-${properties.locationId}`;
  locationMarker.setAttribute("data-location-id", formattedId);
  locationMarker.setAttribute(
    "class",
    `flex justify-center items-center w-auto min-w-[1.25rem] h-5 text-base rounded-full shadow-10 hover:ring hover:ring-white cursor-pointer ${getLocationRiskIconBackgroundColorByRiskLevel(
      properties.risk
    )}
        ${getDefaultTextColorByRiskLevel(properties.risk)}`
  );

  locationMarker.addEventListener("click", () =>
    onClickCallback(properties.projectId, properties.locationId)
  );

  locationMarker.addEventListener("mouseenter", () =>
    onMouseEnterCallback(properties.locationId)
  );

  let riskIconElement: HTMLElement;
  // The Medium risk icon required an svg from our React Icon
  // Library that wasn't available in raw HTML. Used <span> instead
  if (properties.risk === RiskLevel.MEDIUM) {
    riskIconElement = document.createElement("span");
    riskIconElement.innerHTML = "~";
  } else {
    riskIconElement = document.createElement("i");
    riskIconElement.setAttribute("class", `ci-${iconName}`);
  }

  locationMarker.appendChild(riskIconElement);

  return locationMarker;
}

const mapIconFunctionMap = {
  [MapFeatureType.Cluster]: createDonutChart,
  [MapFeatureType.Location]: createLocationMarker,
};
type MapIconFunctionMap = typeof mapIconFunctionMap;

function getMapIconByFeatureType<T extends MapFeatureType>(
  mapFeatureType: T
): MapIconFunctionMap[T] {
  return mapIconFunctionMap[mapFeatureType];
}

export {
  generateDonutCss,
  buildClusterTileUrl,
  groupMapFeatures,
  getMapIconByFeatureType,
};
