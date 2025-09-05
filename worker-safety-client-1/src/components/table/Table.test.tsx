import type { Column } from "react-table";
import { render, screen } from "@testing-library/react";
import { within } from "@testing-library/dom";

import React from "react";

import Table from "./Table";

interface TableData {
  id: number;
  type: string;
}

const columns: Column<TableData>[] = [
  {
    id: "ticket_number",
    Header: "TICKET #",
    accessor: "id",
  },
  {
    id: "type",
    Header: "Ticket type",
    // eslint-disable-next-line react/display-name
    accessor: (data: TableData) => (
      <span data-testid="table-html-cell">{data.type}</span>
    ),
  },
];

const data: TableData[] = [
  {
    id: 123,
    type: "Standard",
  },
];

describe("Table", () => {
  describe("when table renders", () => {
    it("should render header and body", () => {
      render(<Table columns={columns} data={data} />);
      const tableHeader = screen.getByTestId("table-header");
      const tableBody = screen.getByTestId("table-body");

      expect(tableHeader).toBeInTheDocument();
      expect(tableBody).toBeInTheDocument();
    });
  });

  describe(`when table contain ${columns.length} columns`, () => {
    it(`should render a header with ${columns.length} columns`, () => {
      render(<Table columns={columns} data={data} />);

      const columnHeaders = screen.getAllByRole("columnheader");

      expect(columnHeaders?.length).toEqual(columns.length);
    });
  });

  describe("when table data does not exist", () => {
    it("should not have rows", () => {
      render(<Table columns={columns} />);

      const tableBody = screen.getByTestId("table-body");
      const rows = within(tableBody).queryByRole("row");

      expect(rows).toBe(null);
    });
  });

  describe("when table data is empty", () => {
    it("should not have rows", () => {
      render(<Table columns={columns} data={[]} />);

      const tableBody = screen.getByTestId("table-body");
      const rows = within(tableBody).queryByRole("row");

      expect(rows).toBe(null);
    });
  });

  describe(`when table data contain ${data.length} entries`, () => {
    it(`should render ${data.length} rows`, () => {
      render(<Table columns={columns} data={data} />);

      const tableBody = screen.getByTestId("table-body");
      const rows = within(tableBody).getAllByRole("row");

      expect(rows.length).toEqual(data.length);
    });
  });

  describe(`when table cell contain custom HTML element`, () => {
    it(`should render the HTML`, () => {
      render(<Table columns={columns} data={data} />);

      const tableBody = screen.getByTestId("table-body");
      const row = within(tableBody).getByRole("row");
      const cell = within(row).getByTestId("table-html-cell");

      expect(cell.tagName).toEqual("SPAN");
    });
  });

  describe("when table is in loading state", () => {
    it("should render placeholders", () => {
      render(<Table columns={columns} isLoading={true} />);

      const tableBody = screen.getByTestId("table-body");
      const rows = within(tableBody).getAllByRole("row");

      expect(rows?.length).toBeGreaterThan(0);
    });
  });
});
