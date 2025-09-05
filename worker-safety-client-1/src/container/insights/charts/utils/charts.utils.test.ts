import type { TaskRiskLevelByDate } from "@/components/charts/dailyRiskHeatmap/types";
import type { WorkbookData } from "@/components/fileDownloadDropdown/providers/spreadsheet";
import type { ApplicableHazardsChartProps } from "../applicableHazardsChart/ApplicableHazardsChart";
import type { ControlsNotImplementedChartProps } from "../controlsNotImplementedChart/ControlsNotImplementedChart";
import type { PortfolioFiltersPayload } from "../../portfolioFilters/PortfolioFilters";
import type { FiltersDescriptionsReturn } from "../hooks/useFiltersDescriptions";
import type { ProjectFiltersPayload } from "../../projectFilters/ProjectFilters";
import type { TenantEntity } from "@/types/tenant/TenantEntities";
import { useTenantStore } from "@/store/tenant/useTenantStore.store";
import { mockTenantStore } from "@/utils/dev/jest";
import { insightsTenant } from "../__mocks__/tenant.mock";
import {
  formatChartDataWithFilters,
  formatDrillDownChartsDataWithFilters,
  formatRiskHeatmapChartsWithFilters,
  getProjectDescriptionFromFilters,
} from "./charts.utils";

describe("helper", () => {
  beforeAll(() => {
    mockTenantStore(insightsTenant);
  });

  describe(formatChartDataWithFilters.name, () => {
    const chartTitle = "chart title";
    const chartData = [{ pole: 1 }];

    it("should return an array with one item, with the data and the title", () => {
      const expected = formatChartDataWithFilters({
        chartTitle,
        chartData,
      });

      expect(expected).toHaveLength(1);
      expect(expected[0][0]).toBe(chartTitle);
      expect(expected[0][1]).toBe(chartData);
    });

    describe("when filters are applied", () => {
      const filtersData = [{ filter: 1 }, { filter: 2 }];
      let expected: WorkbookData;

      beforeEach(() => {
        expected = formatChartDataWithFilters({
          chartTitle,
          chartData,
          filtersData,
        });
      });

      it("should have 2 items", () => {
        expect(expected).toHaveLength(2);
      });

      it("should have the filters on the first element", () => {
        expect(expected[0][0]).toBe("Filters applied");
        expect(expected[0][1]).toBe(filtersData);
      });

      it("should have the data and chart title", () => {
        expect(expected[1][0]).toBe(chartTitle);
        expect(expected[1][1]).toBe(chartData);
      });
    });
  });

  describe(formatDrillDownChartsDataWithFilters.name, () => {
    const filters = [{ filter: 1 }, { filter: 2 }];

    describe("for `Controls not implemented` drill down", () => {
      const chartData: ControlsNotImplementedChartProps["controlsData"] = [
        { percent: 1, libraryControl: { name: "sample" } },
      ];

      const chartsData: ControlsNotImplementedChartProps["charts"] = [
        {
          title: "by title",
          label: "title",
          data: [{ name: "title", percent: 10 }],
        },
        {
          title: "by another title",
          label: "title",
          data: [
            { name: "title", percent: 10 },
            { name: "title", percent: 20 },
          ],
        },
      ];

      const params = {
        type: "control",
        selected: "sample",
        primaryData: chartData,
        drilldownData: chartsData,
      } as const;

      it("should have one item with the title and data of the main chart", () => {
        const expected = formatDrillDownChartsDataWithFilters(params);

        expect(expected[0][0]).toBe("Controls Not Implemented");
        expect(expected[0][1]).toStrictEqual([
          {
            "Control Not Implemented": "sample",
            "% of controls not implemented": 100,
          },
        ]);
      });

      it("should transform the additional charts into new items with a title and formatted data", () => {
        const expected = formatDrillDownChartsDataWithFilters(params);

        // main chart + additional charts
        expect(expected).toHaveLength(3);

        expect(expected[1]).toStrictEqual([
          "Controls by title",
          [
            {
              "% of controls not implemented by title": 1000,
              "Selected control not implemented": "sample",
              title: "title",
            },
          ],
        ]);

        expect(expected[2]).toStrictEqual([
          "Controls by another title",
          [
            {
              "% of controls not implemented by another title": 1000,
              "Selected control not implemented": "sample",
              "another title": "title",
            },
            {
              "% of controls not implemented by another title": 2000,
              "Selected control not implemented": "sample",
              "another title": "title",
            },
          ],
        ]);
      });

      describe("when filters are applied", () => {
        it("should prepend to the first item", () => {
          const expected = formatDrillDownChartsDataWithFilters({
            ...params,
            filters,
          });

          // filters in the first worksheet
          expect(expected[0][0]).toBe("Filters applied");
          expect(expected[0][1]).toBe(filters);
        });
      });
    });

    describe("for `Applicable hazards` drill down", () => {
      const chartData: ApplicableHazardsChartProps["hazardsData"] = [
        { count: 10, libraryHazard: { name: "sample" } },
      ];

      const chartsData: ApplicableHazardsChartProps["charts"] = [
        {
          title: "by task",
          label: "task",
          data: [{ name: "task", count: 5 }],
        },
        {
          title: "by project",
          label: "project",
          data: [{ name: "project", count: 10 }],
        },
        {
          title: "by location",
          label: "locations",
          data: [
            { name: "location 1", count: 15 },
            { name: "location 2", count: 20 },
          ],
        },
      ];

      const params = {
        type: "hazard",
        selected: "hazard",
        primaryData: chartData,
        drilldownData: chartsData,
      } as const;

      it("should have one item with the title and data of the main chart", () => {
        const expected = formatDrillDownChartsDataWithFilters(params);

        expect(expected[0][0]).toBe("Applicable Hazards");
        expect(expected[0][1]).toStrictEqual([
          {
            "Applicable hazard": "sample",
            "# of times hazard was applicable": 10,
          },
        ]);
      });

      it("should transform the additional charts into new items with a title and formatted data", () => {
        const expected = formatDrillDownChartsDataWithFilters(params);

        expect(expected[1]).toStrictEqual([
          "AH by task",
          [
            {
              "# of times hazard was applicable by task": 5,
              "Selected applicable hazard": "hazard",
              task: "task",
            },
          ],
        ]);

        expect(expected[2]).toStrictEqual([
          "AH by project",
          [
            {
              "# of times hazard was applicable by project": 10,
              "Selected applicable hazard": "hazard",
              project: "project",
            },
          ],
        ]);

        expect(expected[3]).toStrictEqual([
          "AH by location",
          [
            {
              "# of times hazard was applicable by location": 15,
              "Selected applicable hazard": "hazard",
              location: "location 1",
            },
            {
              "# of times hazard was applicable by location": 20,
              "Selected applicable hazard": "hazard",
              location: "location 2",
            },
          ],
        ]);
      });

      describe(" when filters are applied", () => {
        it("should prepend the filters in the first item", () => {
          const expected = formatDrillDownChartsDataWithFilters({
            ...params,
            filters,
          });

          // filters in the first worksheet
          expect(expected[0][0]).toBe("Filters applied");
          expect(expected[0][1]).toBe(filters);
        });
      });
    });
  });

  describe(formatRiskHeatmapChartsWithFilters.name, () => {
    const params = {
      title: "heatmap title",
      data: [
        {
          locationName: "Location 0",
          riskLevelByDate: [
            { date: "2022-01-29", riskLevel: "HIGH" },
            { date: "2022-01-30", riskLevel: "MEDIUM" },
            { date: "2022-02-01", riskLevel: "LOW" },
          ],
          taskName: "Task 0",
        },
        {
          locationName: "Location 1",
          taskName: "Task 1",
          riskLevelByDate: [
            { date: "2022-01-29", riskLevel: "HIGH" },
            { date: "2022-01-30", riskLevel: "MEDIUM" },
            { date: "2022-02-01", riskLevel: "LOW" },
          ],
        },
      ] as TaskRiskLevelByDate[],
    };

    it("should have one item with the title and the transformed data into the file format", () => {
      const expected = formatRiskHeatmapChartsWithFilters(params);

      expect(expected).toHaveLength(1);
      expect(expected[0][0]).toBe(params.title);
      expect(Array.isArray(expected[0][1])).toBe(true);
    });

    describe("when filters are applied", () => {
      it("should prepend the filters in the first item", () => {
        const filters = [{ filter: 1 }, { filter: 2 }];
        const expected = formatRiskHeatmapChartsWithFilters({
          ...params,
          filters,
        });

        // filters in the first worksheet
        expect(expected[0][0]).toBe("Filters applied");
        expect(expected[0][1]).toBe(filters);
      });
    });

    describe("configuring the columns for the transform data", () => {
      describe("when only has locations", () => {
        it("should output the columns | date | location name | risk level, in that order", () => {
          const expected = formatRiskHeatmapChartsWithFilters({
            ...params,
            // we want to skip this property
            // eslint-disable-next-line @typescript-eslint/no-unused-vars
            data: params.data.map(({ taskName, ...item }) => item),
          });

          expect(expected[0][1]).toEqual(
            expect.arrayContaining([
              expect.objectContaining({
                date: expect.any(String),
                "Location Name": expect.any(String),
                "Risk level (high, medium, low)":
                  expect.stringMatching(/high|medium|low/gi),
              }),
            ])
          );
        });
      });

      describe("with the tasks and locations", () => {
        it("should output the columns | date | task name | location name | risk level, in that order", () => {
          const expected = formatRiskHeatmapChartsWithFilters(params);

          expect(expected[0][1]).toEqual(
            expect.arrayContaining([
              expect.objectContaining({
                date: expect.any(String),
                "Task name": expect.any(String),
                "Location Name": expect.any(String),
                "Risk level (high, medium, low)":
                  expect.stringMatching(/high|medium|low/gi),
              }),
            ])
          );
        });
      });
      describe("with the tasks and project", () => {
        it("should output the columns | date | task name | project name | risk level, in that order", () => {
          const expected = formatRiskHeatmapChartsWithFilters({
            ...params,
            data: params.data.map(({ locationName, ...item }) => ({
              ...item,
              projectName: locationName,
            })),
          });

          expect(expected[0][1]).toEqual(
            expect.arrayContaining([
              expect.objectContaining({
                date: expect.any(String),
                "Task name": expect.any(String),
                "Project Name": expect.any(String),
                "Risk level (high, medium, low)":
                  expect.stringMatching(/high|medium|low/gi),
              }),
            ])
          );
        });
      });
    });
  });

  describe(getProjectDescriptionFromFilters.name, () => {
    let workPackageLabelPlural: string;
    let name: TenantEntity["attributes"][number];
    let externalKey: TenantEntity["attributes"][number];

    beforeAll(() => {
      const {
        workPackage: { labelPlural, attributes },
      } = useTenantStore.getState().getAllEntities();

      workPackageLabelPlural = labelPlural;
      name = attributes.name;
      externalKey = attributes.externalKey;
    });

    it("should output the name property as `All <WorkPackageEntity.labelPlural>` without a number when NOT filtering by a single project", () => {
      expect(
        getProjectDescriptionFromFilters({
          filters: {
            projectIds: [],
          } as unknown as PortfolioFiltersPayload,
          filtersDescriptions: {} as unknown as FiltersDescriptionsReturn,
        })
      ).toEqual({
        name: `All ${workPackageLabelPlural}`,
        number: undefined,
      });
    });

    it("should output the name property as `Multiple <WorkPackageEntity.labelPlural>` without a number when filtering by multiple projects", () => {
      expect(
        getProjectDescriptionFromFilters({
          filters: {
            projectIds: ["1", "2"],
          } as PortfolioFiltersPayload,
          filtersDescriptions: {
            [name.labelPlural]:
              "Davenport, Guzman and Martinez V2, Case-Berger V2",
          } as unknown as FiltersDescriptionsReturn,
        })
      ).toEqual({
        name: `Multiple ${workPackageLabelPlural}`,
        number: undefined,
      });
    });

    it("should display the workPackage name and externalKey when using a filter with possible multiple projects", () => {
      expect(
        getProjectDescriptionFromFilters({
          filters: {
            projectIds: ["1"],
          } as PortfolioFiltersPayload,
          filtersDescriptions: [
            {
              [name.label]: "Davenport, Guzman and Martinez V2",
              [externalKey.label]: "123",
            },
          ],
        })
      ).toEqual({
        name: "Davenport, Guzman and Martinez V2",
        number: "123",
      });
    });

    it("should display the workPackage name and externalKey when using a filter with only a single project id", () => {
      expect(
        getProjectDescriptionFromFilters({
          filters: {
            projectId: "12312321",
          } as unknown as ProjectFiltersPayload,
          filtersDescriptions: [
            {
              [name.label]: "Davenport, Guzman and Martinez V2",
              [externalKey.label]: "123",
            },
          ],
        })
      ).toEqual({
        name: "Davenport, Guzman and Martinez V2",
        number: "123",
      });
    });
  });
});
