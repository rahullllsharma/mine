import { render, screen } from "@testing-library/react";
import type { Column } from "react-table";
import type { TemplatesList } from "@/components/templatesComponents/customisedForm.types";
import TemplateFormTable from "./TemplateFormTable";

jest.mock("@/components/table/Table", () => {
  const MockTable = ({
    columns,
    data,
  }: {
    columns: Column<TemplatesList>[];
    data: TemplatesList[];
  }) => (
    <div data-testid="table">
      {data.map((row: TemplatesList, rowIndex: number) => (
        <div key={rowIndex} role="row">
          {columns.map((column: Column<TemplatesList>, colIndex: number) => (
            <div key={colIndex} role="cell">
              {typeof column.accessor === "function"
                ? column.accessor(row, rowIndex, {
                    subRows: [],
                    depth: 0,
                    data: data,
                  })
                : column.accessor
                ? row[column.accessor]
                : null}
            </div>
          ))}
        </div>
      ))}
    </div>
  );
  MockTable.displayName = "MockTable";
  return MockTable;
});

jest.mock("next/link", () => {
  const MockNextLink = ({ children }: { children: React.ReactNode }) => (
    <div>{children}</div>
  );
  MockNextLink.displayName = "MockNextLink";
  return MockNextLink;
});

jest.mock("@/components/shared/link/Link", () => {
  const MockLink = ({ label }: { label: string }) => <span>{label}</span>;
  MockLink.displayName = "MockLink";
  return MockLink;
});

jest.mock("@/components/statusBadge/StatusBadge", () => {
  const MockStatusBadge = ({ status }: { status: string }) => (
    <span>{status}</span>
  );
  MockStatusBadge.displayName = "MockStatusBadge";
  return MockStatusBadge;
});

jest.mock("@urbint/silica", () => {
  const MockBodyText = ({ children }: { children: React.ReactNode }) => (
    <span>{children}</span>
  );
  MockBodyText.displayName = "MockBodyText";

  const MockCaptionText = ({ children }: { children: React.ReactNode }) => (
    <span>{children}</span>
  );
  MockCaptionText.displayName = "MockCaptionText";

  const MockIcon = ({ name }: { name: string }) => <span>{name}</span>;
  MockIcon.displayName = "MockIcon";

  return {
    BodyText: MockBodyText,
    CaptionText: MockCaptionText,
    Icon: MockIcon,
  };
});

jest.mock("@/components/shared/tooltip/Tooltip", () => {
  const MockTooltip = ({ children }: { children: React.ReactNode }) => (
    <div>{children}</div>
  );
  MockTooltip.displayName = "MockTooltip";
  return MockTooltip;
});

jest.mock("@/store/tenant/useTenantStore.store", () => ({
  useTenantStore: () => ({
    getAllEntities: () => ({
      templateForm: { attributes: {} },
    }),
  }),
}));

describe("TemplateFormTable", () => {
  it("renders location column with GPS coordinates", () => {
    const mockData: TemplatesList[] = [
      {
        template_unique_id: "test-id",
        id: "test-id",
        title: "Test Form",
        status: "completed",
        location_data: {
          name: "Test Location",
          description: "Test Description",
          gps_coordinates: { latitude: "40.7128", longitude: "-74.0060" },
        },
      },
    ];

    render(<TemplateFormTable templateFormsData={mockData} />);

    const locationName = screen.getByText("Test Location");
    expect(locationName).toBeInTheDocument();
  });
});
