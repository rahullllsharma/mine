/* eslint-disable @typescript-eslint/no-explicit-any */
import { useCallback, useRef } from "react";
import { useBlockLayout, useTable } from "react-table";
import { FixedSizeList } from "react-window";

export interface HeatmapTableProps {
  columns: readonly any[];
  data?: readonly any[];
  isLoading?: boolean;
  width: number;
  rowHeight?: number;
  virtualRowCount?: number;
}

export default function HeatmapTable({
  columns,
  data = [],
  width,
  rowHeight = 32,
  virtualRowCount = 10,
}: HeatmapTableProps): JSX.Element {
  const parentRef = useRef<HTMLDivElement>(null);

  const { getTableProps, getTableBodyProps, headerGroups, rows, prepareRow } =
    useTable<any>({ data, columns }, useBlockLayout);

  const RenderRow = useCallback(
    ({ index, style }) => {
      const row = rows[index];
      prepareRow(row);
      return (
        <div
          className="_tr h-8 overflow-x-hidden bg-white flex items-center"
          {...row.getRowProps({ style })}
          key={index}
        >
          {row.cells.map((cell, cellIndex) => {
            return (
              <div
                {...cell.getCellProps()}
                className="_td text-sm"
                key={cellIndex}
              >
                {cell.render("Cell")}
              </div>
            );
          })}
        </div>
      );
    },
    [prepareRow, rows]
  );

  const fixedSizeListHeight =
    Math.min(virtualRowCount, rows.length) * rowHeight;

  return (
    <div className="bg-white" style={width ? { width: width } : {}}>
      <div
        ref={parentRef}
        {...getTableProps()}
        className="flex flex-col max-h-full overflow-x-auto"
      >
        <div
          className="_thead bg-white z-10 divide-y divide-brand-gray-20"
          data-testid="table-header"
        >
          {headerGroups.map((headerGroup, index) => (
            <div
              className="_tr"
              {...headerGroup.getHeaderGroupProps()}
              key={index}
            >
              {headerGroup.headers.map(column => (
                <div
                  className="_th truncate pt-5 font-semibold"
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
        <div
          className="_tbody overflow-y-auto max-h-96"
          {...getTableBodyProps()}
          data-testid="table-body"
        >
          <div className="relative">
            <FixedSizeList
              height={fixedSizeListHeight}
              itemSize={rowHeight}
              itemCount={rows.length}
              width={width}
              className="no-scrollbar"
            >
              {RenderRow}
            </FixedSizeList>
          </div>
        </div>
      </div>
    </div>
  );
}
