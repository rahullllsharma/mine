import { OrderByDirection } from "@/types/graphql/OrderByDirection";

type OrderByField =
  | "NAME"
  | "CATEGORY"
  | "RISK_LEVEL"
  | "PROJECT_NAME"
  | "PROJECT_LOCATION_NAME"
  | "START_DATE"
  | "ID"
  | "CREATED_AT"
  | "UPDATED_AT";

const orderBy = (field: OrderByField, direction: OrderByDirection) => {
  return {
    field,
    direction,
  };
};

export const orderByName = orderBy("NAME", OrderByDirection.ASC);
export const orderByCategory = orderBy("CATEGORY", OrderByDirection.ASC);
export const orderByRiskLevel = orderBy("RISK_LEVEL", OrderByDirection.DESC);
export const orderByProjectName = orderBy("PROJECT_NAME", OrderByDirection.ASC);
export const orderByLocationName = orderBy(
  "PROJECT_LOCATION_NAME",
  OrderByDirection.ASC
);
export const orderByNewestStartDate = orderBy(
  "START_DATE",
  OrderByDirection.DESC
);
export const orderById = orderBy("ID", OrderByDirection.ASC);
export const orderByCreatedAt = orderBy("CREATED_AT", OrderByDirection.DESC);
export const orderByUpdatedAt = orderBy("UPDATED_AT", OrderByDirection.DESC);
