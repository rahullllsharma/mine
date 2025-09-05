import type { Column } from "react-table";
import type { OnDragEndResponder } from "react-beautiful-dnd";

export type AttributeKey =
  | "formName"
  | "status"
  | "createdBy"
  | "createdOn"
  | "completedOn"
  | "Project"
  | "location"
  | "region"
  | "updatedBy"
  | "updatedOn"
  | "reportDate"
  | "supervisor";

export interface HasTypename {
  __typename: string;
}

export type TableProps<T extends object> = {
  columns: readonly Column<T>[];
  data?: readonly T[];
  isLoading?: boolean;
  lastVisitedRowItemId?: string;
  emptyStateMessage?: string;
} & (
  | {
      reOrderable: true;
      onDragEnd: OnDragEndResponder;
    }
  | { reOrderable?: false; onDragEnd?: never }
);
