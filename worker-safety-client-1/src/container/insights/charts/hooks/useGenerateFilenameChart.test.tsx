import { useAuthStore } from "@/store/auth/useAuthStore.store";
import { useTenantStore } from "@/store/tenant/useTenantStore.store";
import { mockTenantStore } from "@/utils/dev/jest";
import { renderHook } from "@testing-library/react-hooks";
import { InsightsTab } from "../types";
import { useGenerateFilenameChart } from "./useGenerateFilenameChart";

jest.useFakeTimers();
jest.setSystemTime(new Date("2022-05-23T10:25:00.000Z"));

describe(useGenerateFilenameChart.name, () => {
  beforeAll(() => {
    mockTenantStore();

    useAuthStore.setState(state => ({
      ...state,
      me: {
        initials: "",
        name: "",
        email: "super@email.local.urbinternal.com",
        permissions: [],
        role: "viewer",
        id: "id",
        opco: null,
        userPreferences: [],
      },
    }));

    useTenantStore.setState(state => ({
      ...state,
      tenant: {
        name: "storybook",
        displayName: "Storybook",
        entities: [],
        workos: [],
      },
    }));
  });

  it("should generate the filename for project charts", () => {
    const {
      workPackage: {
        attributes: {
          name: { label: workPackageLabel },
          externalKey: { label: workPackageNumber },
        },
      },
      location: {
        attributes: {
          name: { labelPlural: locationLabelPlural },
        },
      },
    } = useTenantStore.getState().getAllEntities();

    const filtersApplied = [
      {
        [workPackageLabel]: "project name",
        [workPackageNumber]: 123,
        [locationLabelPlural]: "New york, Albany",
      },
    ];

    const { result } = renderHook(
      () =>
        useGenerateFilenameChart(InsightsTab.PROJECT, "chart title", {
          filters: filtersApplied,
        }),
      {
        wrapper: function wrapper({ children }) {
          return <>{children}</>;
        },
      }
    );

    expect(result.current).toEqual(
      "[123]-project name-chart title-Urbint-05/23/22"
    );
  });

  it("should generate the filename for portfolio charts", () => {
    const { result } = renderHook(
      () => useGenerateFilenameChart(InsightsTab.PORTFOLIO, "chart title"),
      {
        wrapper: function wrapper({ children }) {
          return <>{children}</>;
        },
      }
    );

    expect(result.current).toEqual("storybook-chart title-Urbint-05/23/22");
  });
});
