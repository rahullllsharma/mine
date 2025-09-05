import type { Meta, Story } from "@storybook/react";
import type { TableProps } from "./table.types";
import type { Column } from "react-table";
import NextLink from "next/link";

import RiskBadge from "../riskBadge/RiskBadge";
import { RiskLevel } from "../riskBadge/RiskLevel";
import Link from "../shared/link/Link";
import Table from "./Table";

export default {
  title: "Components/Table",
  component: Table,
  argTypes: {
    columns: { table: { disable: true } },
    data: { table: { disable: true } },
  },
} as Meta<TableProps<TableData>>;

interface TableData {
  id: number;
  type: string;
  impact: RiskLevel;
}

const tableData: TableData[] = [
  {
    id: 123,
    type: "Standard",
    impact: RiskLevel.HIGH,
  },
  {
    id: 1341,
    type: "Standard",
    impact: RiskLevel.HIGH,
  },
  {
    id: 123321,
    type: "Standard",
    impact: RiskLevel.LOW,
  },
  {
    id: 1233213,
    type: "Standard",
    impact: RiskLevel.LOW,
  },
];

const columns: Column<TableData>[] = [
  {
    id: "ticket_number",
    Header: "TICKET #",
    accessor: (data: TableData) => data.id,
  },
  {
    id: "type",
    Header: "Ticket type",
    accessor: "type",
  },
];

export const Standard = (): JSX.Element => (
  <Table columns={columns} data={tableData} />
);

const columnsWithTicketLink: Column<TableData>[] = [
  {
    id: "ticket_number",
    Header: "TICKET #",
    // eslint-disable-next-line react/display-name
    accessor: (data: TableData) => (
      <NextLink href="">
        <Link label={data.id} />
      </NextLink>
    ),
  },
  {
    id: "type",
    Header: "Ticket type",
    accessor: "type",
  },
];
export const withLink = (): JSX.Element => (
  <Table columns={columnsWithTicketLink} data={tableData} />
);

export const empty = (): JSX.Element => (
  <Table columns={columns} data={[]} emptyStateMessage="No data to display" />
);

const singleColumnDefinition: Column<TableData>[] = [
  {
    id: "col_id_1",
    Header: "TICKET #",
    accessor: (data: TableData) => data.id,
  },
];

export const singleColumn = (): JSX.Element => (
  <Table columns={singleColumnDefinition} data={tableData} />
);

const columnWithRiskBadge: Column<TableData>[] = [
  {
    id: "ticket_number",
    Header: "TICKET #",
    accessor: (obj: TableData) => obj.id,
  },
  {
    id: "type",
    Header: "Ticket type",
    accessor: "type",
  },
  {
    id: "impact_threat",
    Header: "Impact",
    // eslint-disable-next-line react/display-name
    accessor: (data: TableData) => (
      <RiskBadge risk={data.impact} label={data.impact} />
    ),
  },
];
export const withRiskBadge = (): JSX.Element => (
  <Table columns={columnWithRiskBadge} data={tableData} />
);

export const loadingSingleColumn = (): JSX.Element => (
  <Table columns={singleColumnDefinition} isLoading={true} />
);
export const loadingMultipleColumns = (): JSX.Element => (
  <Table columns={columnWithRiskBadge} isLoading={true} />
);

const Template: Story<TableProps<TableData>> = args => <Table {...args} />;

export const Playground = Template.bind({});

Playground.args = {
  columns: columnWithRiskBadge,
  data: tableData,
  isLoading: false,
  emptyStateMessage: "No data to display",
};
