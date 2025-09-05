import type { ProjectFiltersPayload } from "../../projectFilters/ProjectFilters";
import type {
  FiltersDescriptionsParams,
  FiltersDescriptionsReturn,
} from "./useFiltersDescriptions";
import { renderHook } from "@testing-library/react-hooks";
import { useTenantStore } from "@/store/tenant/useTenantStore.store";
import { mockTenantStore } from "@/utils/dev/jest";
import { InsightsTab } from "../types";
import { customInsightsTenant, insightsTenant } from "../__mocks__/tenant.mock";
import { useFiltersDescriptions } from "./useFiltersDescriptions";
import { descriptions } from "./__mocks__/mocks";

type HookArgs = Required<FiltersDescriptionsParams>;

type Filters = HookArgs["filters"];

// initial data
const tab = InsightsTab.PROJECT;

const filters = {
  startDate: "2022-01-01",
  endDate: "2022-01-03",
} as Filters;

describe(useFiltersDescriptions.name, () => {
  beforeAll(() => {
    mockTenantStore(insightsTenant);
  });

  it("should return empty array when filters are not provided", () => {
    const { result } = renderHook(() =>
      useFiltersDescriptions({
        filters: undefined,
        tab,
        descriptions,
      })
    );

    expect(result.current).toEqual([]);
  });

  describe("when deriving project filters", () => {
    describe("when extracting the result based on the selected filters", () => {
      it("should only return the mandatory filters (start and end dates) and only filters that where found", () => {
        const { result } = renderHook(useFiltersDescriptions, {
          initialProps: {
            filters: {
              ...filters,
              projectId: "1",
              locationIds: ["3"],
            },
            tab,
            descriptions: {
              ...descriptions,
              projects: [
                {
                  id: "1",
                  name: "project #1",
                  locations: [
                    {
                      id: "1",
                      name: "location #1",
                    },
                    {
                      id: "2",
                      name: "location #2",
                    },
                  ],
                },
              ],
            },
          },
        });

        expect(result.current).toEqual([
          {
            "Start date": filters.startDate,
            "End date": filters.endDate,
            "Project Name": "project #1",
          },
        ]);
      });

      it("should return the mandatory filters (start and end dates) and the project details when a location is found", () => {
        const { rerender, result } = renderHook(useFiltersDescriptions, {
          initialProps: {
            filters: {
              ...filters,
              projectId: "1",
              locationIds: ["1", "2"],
            },
            tab,
            descriptions,
          },
        });

        rerender({
          filters: {
            ...filters,
            startDate: "2022-03-03",
            projectId: "1",
            locationIds: ["1", "2"],
          },
          tab,
          descriptions,
        });

        expect(result.current).toEqual([
          {
            "Start date": "2022-03-03",
            "End date": filters.endDate,
            "Project Name": "project #1",
            "Project Number": 123,
            Locations: "location #1, location #2",
          },
        ]);
      });
    });

    describe("when the filters are updated", () => {
      const projectFilters: ProjectFiltersPayload = {
        locationIds: [],
        projectId: "1",
        ...filters,
      };

      it("should return an updated version of the filters selected", async () => {
        const { rerender, result } = renderHook(useFiltersDescriptions, {
          initialProps: { filters: projectFilters, tab, descriptions },
        });

        rerender({
          filters: {
            ...projectFilters,
            endDate: "2023-01-01",
          },
          tab,
          descriptions,
        });

        expect(result.current).toEqual([
          {
            "Project Number": 123,
            "Project Name": "project #1",
            "Start date": filters.startDate,
            "End date": "2023-01-01",
          },
        ]);
      });
    });

    describe("when using custom configuration for the tenant", () => {
      let current: FiltersDescriptionsReturn;

      beforeAll(() => {
        mockTenantStore(customInsightsTenant);

        const { result } = renderHook(useFiltersDescriptions, {
          initialProps: {
            filters: {
              ...filters,
              projectId: "1",
              locationIds: ["1", "2"],
            },
            tab,
            descriptions,
          },
        });

        current = result.current;
      });

      afterAll(() => {
        const { setTenant } = useTenantStore.getState();
        setTenant(insightsTenant);
      });

      describe("for filters with only one value", () => {
        it("should use the configuration attributes with the label property", () => {
          expect(current).toEqual([
            expect.objectContaining({
              "My Work Package Name": "project #1",
              "My Work Package Number": 123,
            }),
          ]);
        });
      });

      describe("for filters with multiple values", () => {
        it("should use the configuration attributes with the label plural property", () => {
          expect(current).toEqual([
            expect.objectContaining({
              "My Locations": "location #1, location #2",
            }),
          ]);
        });
      });
    });
  });

  describe("when deriving portfolio filters", () => {
    describe("when filters change", () => {
      beforeAll(() => {
        mockTenantStore(insightsTenant);
      });

      it("should always return the mandatory filters (start and end dates)", () => {
        const { rerender, result } = renderHook(useFiltersDescriptions, {
          initialProps: { filters, tab: InsightsTab.PORTFOLIO, descriptions },
        });

        rerender({
          filters: { ...filters, startDate: "2022-03-03" },
          tab: InsightsTab.PORTFOLIO,
          descriptions,
        });

        expect(result.current).toEqual([
          {
            "Start date": "2022-03-03",
            "End date": filters.endDate,
          },
        ]);
      });

      it("should only return the selected filters of the filters found", () => {
        const { rerender, result } = renderHook(useFiltersDescriptions, {
          initialProps: { filters, tab: InsightsTab.PORTFOLIO, descriptions },
        });

        rerender({
          filters: {
            ...filters,
            startDate: "2022-03-03",
            projectStatuses: ["1", "3"],
            // eslint-disable-next-line @typescript-eslint/ban-ts-comment
            // @ts-ignore
            projectIds: "",
            regionIds: [],
            // eslint-disable-next-line @typescript-eslint/ban-ts-comment
            // @ts-ignore
            divisionIds: undefined,
            // eslint-disable-next-line @typescript-eslint/ban-ts-comment
            // @ts-ignore
            contractorIds: null,
          },
          tab: InsightsTab.PORTFOLIO,
          descriptions,
        });

        expect(result.current).toEqual([
          {
            "Start date": "2022-03-03",
            "End date": filters.endDate,
            "Project Status": "Active, Inactive",
          },
        ]);
      });

      it("should return the all filters with their descriptions when all filters are found", () => {
        const { rerender, result } = renderHook(useFiltersDescriptions, {
          initialProps: { filters, tab: InsightsTab.PORTFOLIO, descriptions },
        });

        rerender({
          filters: {
            ...filters,
            startDate: "2022-03-03",
            projectStatuses: ["1", "3"],
            projectIds: ["1"],
            regionIds: ["1"],
            divisionIds: ["1", "2"],
            contractorIds: ["2"],
          },
          tab: InsightsTab.PORTFOLIO,
          descriptions,
        });

        expect(result.current).toEqual([
          {
            "Start date": "2022-03-03",
            "End date": filters.endDate,
            "Project Status": "Active, Inactive",
            "Project Names": "project #1",
            Regions: "region #1",
            Divisions: "division #1, division #2",
            "Prime contractors": "contractor #2",
          },
        ]);
      });
    });

    describe("when using custom configuration for the tenant", () => {
      let current: FiltersDescriptionsReturn;

      beforeAll(() => {
        mockTenantStore(customInsightsTenant);

        const { result } = renderHook(useFiltersDescriptions, {
          initialProps: {
            filters: {
              ...filters,
              startDate: "2022-03-03",
              projectStatuses: ["1", "3"],
              projectIds: ["1"],
              regionIds: ["1"],
              divisionIds: ["1", "2"],
              contractorIds: ["2"],
            },
            tab: InsightsTab.PORTFOLIO,
            descriptions,
          },
        });

        current = result.current;
      });

      describe("for filters with only one value", () => {
        it("should use the configuration attributes with the label property", () => {
          expect(current).toEqual([
            expect.objectContaining({
              "My Work Package Names": "project #1",
              "My Work Package Regions": "region #1",
              "My Work Package Prime Contractors": "contractor #2",
            }),
          ]);
        });
      });

      describe("for filters with multiple values", () => {
        it("should use the configuration attributes with the label plural property", () => {
          expect(current).toEqual([
            expect.objectContaining({
              "My Work Package Status": "Active, Inactive",
              "My Work Package Divisions": "division #1, division #2",
            }),
          ]);
        });
      });
    });
  });

  describe("when the tab and the filters change", () => {
    beforeAll(() => {
      mockTenantStore(insightsTenant);
    });

    it("should return the updated filters and their descriptions", () => {
      const { rerender, result } = renderHook(useFiltersDescriptions, {
        initialProps: {
          filters: {
            ...filters,
            startDate: "2022-03-05",
          },
          tab: InsightsTab.PORTFOLIO,
          descriptions,
        },
      });

      rerender({
        filters: {
          ...filters,
          startDate: "2022-03-03",
        },
        tab: InsightsTab.PORTFOLIO,
        descriptions,
      });

      expect(result.current).toEqual([
        {
          "Start date": "2022-03-03",
          "End date": filters.endDate,
          "Project Status": undefined,
          "Project Name": undefined,
          Region: undefined,
          Division: undefined,
          "Contractor Name": undefined,
        },
      ]);
    });
  });
});
