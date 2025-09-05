/* eslint-disable @typescript-eslint/no-explicit-any */

import type { Column } from "react-table";
import type { AttributeKey, HasTypename, TableProps } from "./table.types";
import cx from "classnames";
import { useCallback, useMemo } from "react";
import { useFlexLayout, useTable } from "react-table";
import { useRouter } from "next/router";
import { useTenantStore } from "@/store/tenant/useTenantStore.store";
import DragDropContextComponent from "./dnd/DragDropContextComponent";
import DraggableTableRow from "./dnd/DraggableTableRow";
import DroppableTableBody from "./dnd/DroppableTableBody";
import { TableLoader } from "./loader/TableLoader";

function isWithTypename(obj: unknown): obj is HasTypename {
  return (
    typeof obj === "object" &&
    obj !== null &&
    "__typename" in obj &&
    typeof (obj as any).__typename === "string"
  );
}

function dragHandleColumn<T extends object>(): Column<T> {
  return {
    id: "drag-handle",
    width: 25,
    accessor: () => <></>,
  };
}

export default function Table<T extends object>({
  columns,
  data = [],
  isLoading = false,
  lastVisitedRowItemId = "",
  emptyStateMessage = "",
  reOrderable = false,
  // eslint-disable-next-line @typescript-eslint/no-empty-function
  onDragEnd = () => {},
}: TableProps<T>): JSX.Element {
  const { pathname } = useRouter();
  const variant = pathname.includes("template-forms") ? "template" : "form";
  const { templateForm } = useTenantStore(state => state.getAllEntities());
  const processedData = useMemo(() => {
    return data.map(item => {
      if (
        isWithTypename(item) &&
        item.__typename === "NatGridJobSafetyBriefing"
      ) {
        return {
          ...item,
          __typename: "Distribution Job Safety Briefing",
        };
      }
      return item;
    });
  }, [data]);

  const labelAndVisibility = (key: AttributeKey) => ({
    label: templateForm.attributes[key]?.label,
    visible: templateForm.attributes[key]?.visible,
  });

  const finalColumns = useMemo<Column<T>[]>(() => {
    const base = reOrderable ? [dragHandleColumn<T>(), ...columns] : columns;
    const withMeta = base.map(col => {
      switch (col.id) {
        case "formName": {
          const { label, visible } = labelAndVisibility("formName");
          return { ...col, Header: label, isVisible: visible };
        }
        case "status": {
          const { label, visible } = labelAndVisibility("status");
          return { ...col, Header: label, isVisible: visible, width: 200 };
        }
        case "created_by": {
          const { label, visible } = labelAndVisibility("createdBy");
          return { ...col, Header: label, isVisible: visible };
        }
        case "created_at": {
          const { label, visible } = labelAndVisibility("createdOn");
          return { ...col, Header: label, isVisible: visible };
        }
        case "completed_at": {
          const { label, visible } = labelAndVisibility("completedOn");
          return { ...col, Header: label, isVisible: visible };
        }
        case "WorkPackageName": {
          const { label, visible } = labelAndVisibility("Project");
          return { ...col, Header: label, isVisible: visible };
        }
        case "WorkPackage": {
          const { label, visible } = labelAndVisibility("location");
          return { ...col, Header: label, isVisible: visible };
        }
        case "region": {
          const { label, visible } = labelAndVisibility("region");
          return { ...col, Header: label, isVisible: visible };
        }
        case "updated_by": {
          const { label, visible } = labelAndVisibility("updatedBy");
          return { ...col, Header: label, isVisible: visible };
        }
        case "updated_at": {
          const { label, visible } = labelAndVisibility("updatedOn");
          return { ...col, Header: label, isVisible: visible };
        }
        case "report_date": {
          const { label, visible } = labelAndVisibility("reportDate");
          return { ...col, Header: label, isVisible: visible };
        }
        case "supervisor": {
          const { label, visible } = labelAndVisibility("supervisor");
          return { ...col, Header: label, isVisible: visible };
        }
        default:
          return { ...col, isVisible: true };
      }
    });
    return withMeta.filter(c => c.isVisible);
  }, [columns, reOrderable, templateForm]);

  const { getTableProps, getTableBodyProps, headerGroups, rows, prepareRow } =
    useTable<T>(
      {
        data: processedData,
        columns: (variant === "template"
          ? finalColumns
          : columns) as Column<T>[],
      },
      useFlexLayout
    );
  const tableComponents = useMemo(
    () => ({
      TableWrapperComponent: reOrderable ? DragDropContextComponent : "div",
      TableBodyComponent: reOrderable ? DroppableTableBody : "div",
      TableRowComponent: reOrderable ? DraggableTableRow : "div",
    }),
    [reOrderable]
  );

  const renderRow = useCallback(() => {
    return rows.length === 0 && !!emptyStateMessage ? (
      <p className="mt-8 text-base text-gray-500">{emptyStateMessage}</p>
    ) : (
      rows.map((row, index) => {
        prepareRow(row);
        return (
          <tableComponents.TableRowComponent
            className={cx(
              "_tr px-4 py-1 min-h-[3.5rem] bg-white  flex items-center",
              {
                "shadow-10": reOrderable,
                "bg-blue-50":
                  // eslint-disable-next-line @typescript-eslint/ban-ts-comment
                  // @ts-ignore
                  lastVisitedRowItemId === row.original.id,
              },
              row.getRowProps().className
            )}
            {...row.getRowProps()}
            key={row.id || index}
            index={index}
            id={index.toString()}
          >
            {row.cells.map((cell, cellIndex) => {
              return (
                <div
                  {...cell.getCellProps()}
                  className={cx(
                    "_td text-sm pr-4 last:pr-0",
                    cell.getCellProps().className
                  )}
                  key={cellIndex}
                >
                  {cell.render("Cell")}
                </div>
              );
            })}
          </tableComponents.TableRowComponent>
        );
      })
    );
  }, [
    prepareRow,
    rows,
    lastVisitedRowItemId,
    emptyStateMessage,
    tableComponents,
    reOrderable,
  ]);

  return (
    <tableComponents.TableWrapperComponent
      onDragEnd={onDragEnd}
      className="w-full flex bg-white"
    >
      <div
        {...getTableProps()}
        className={cx(
          "flex-1 flex flex-col overflow-y-auto",
          getTableProps().className
        )}
      >
        <div
          className={cx(
            "_thead bg-white z-10 border-b border-gray-200 divide-y divide-brand-gray-20 sticky top-0",
            {
              "px-7": reOrderable,
              "px-4": !reOrderable,
            }
          )}
          data-testid="table-header"
        >
          {headerGroups.map((headerGroup, index) => (
            <div
              className={cx(
                "_tr justify-between",
                headerGroup.getHeaderGroupProps().className
              )}
              {...headerGroup.getHeaderGroupProps()}
              key={index}
            >
              {headerGroup.headers.map(column => (
                <div
                  className={cx(
                    "_th pt-5 pb-3 font-bold uppercase text-neutral-shade-75 truncate",
                    column.getHeaderProps().className
                  )}
                  {...column.getHeaderProps()}
                  key={column.id}
                  data-testid={`table-header-${column.id}`}
                >
                  {column.render("Header")}
                </div>
              ))}
            </div>
          ))}
        </div>
        <tableComponents.TableBodyComponent
          className={cx(
            "_tbody flex flex-col gap-2.5",
            {
              "mt-6 p-3 bg-gray-50": reOrderable && processedData.length,
            },
            getTableBodyProps().className
          )}
          {...getTableBodyProps()}
          data-testid="table-body"
        >
          {isLoading ? (
            <TableLoader columnsSize={columns.length} />
          ) : (
            renderRow()
          )}
        </tableComponents.TableBodyComponent>
      </div>
    </tableComponents.TableWrapperComponent>
  );
}
