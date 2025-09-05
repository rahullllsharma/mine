import type { DailyReport } from "@/types/report/DailyReport";

import { act, render, screen } from "@testing-library/react";

import { MockedProvider } from "@apollo/client/testing";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { useProjects } from "@/hooks/useProjects";
import { useAuthStore } from "@/store/auth/useAuthStore.store";
import { getFormattedLocaleDateTime } from "@/utils/date/helper";
import { formRender, mockTenantStore } from "@/utils/dev/jest";
import DailyInspectionPageHeader from "./components/dailyInspectionPageHeader/DailyInspectionPageHeader";
import DailyInspectionReport from "./DailyInspection";

jest.mock("@/hooks/useLeavePageConfirm");

jest.mock("next/router", () => ({
  __esModule: true,
  default: jest.fn(),
  useRouter: jest.fn(() => ({
    pathname: "pathname",
    asPath: "pathname",
    push: jest.fn(),
    query: {
      activeTab: "plan",
    },
  })),
}));

jest.mock("next-auth/react", () => {
  const originalModule = jest.requireActual("next-auth/react");
  const mockSession = {
    expires: new Date(Date.parse("2022-01-24") + 2 * 86400).toISOString(),
    user: { username: "admin" },
  };
  return {
    __esModule: true,
    ...originalModule,
    useSession: jest.fn(() => {
      return { data: mockSession, status: "authenticated" }; // return type is [] in v3 but changed to {} in v4
    }),
  };
});

const today = "2022-01-24";
jest.useFakeTimers();
jest.setSystemTime(new Date(today).valueOf());

// eslint-disable-next-line react-hooks/rules-of-hooks
const projects = useProjects();
const [project] = projects;
const [location] = project.locations;

const workSchedule = {
  startDatetime: "2022-01-04T00:00:00.000Z",
  endDatetime: "2022-01-04T01:00:00.000Z",
};

const dailyReport = {
  id: "f779cb91-c767-4a8a-a37a-401c1ee60830",
  status: "IN_PROGRESS",
  sections: {
    workSchedule,
  },
  sectionsJSON: JSON.stringify({
    workSchedule,
  }),
  createdBy: {
    id: "id",
  },
} as unknown as DailyReport;

const queryClient = new QueryClient();

describe(DailyInspectionReport.name, () => {
  mockTenantStore();
  let cacheHistoryState: History;

  beforeEach(() => {
    cacheHistoryState = window.history;

    Object.defineProperty(window, "history", {
      value: {
        replaceState: jest.fn(),
        state: {
          as: "pathname",
        },
      },
      writable: true,
    });

    window.HTMLElement.prototype.scrollTo = jest.fn();
  });

  afterEach(() => {
    Object.defineProperties(
      window.history,
      cacheHistoryState as unknown as PropertyDescriptorMap
    );
  });

  it("should render an empty daily report correctly", async () => {
    await act(async () => {
      const { asFragment } = formRender(
        <MockedProvider mocks={[]}>
          <QueryClientProvider client={queryClient}>
            <DailyInspectionReport
              project={project}
              location={location}
              projectSummaryViewDate={today}
              recommendations={null}
            />
          </QueryClientProvider>
        </MockedProvider>
      );
      expect(asFragment()).toMatchSnapshot();
    });

    screen.getByRole("heading", {
      level: 2,
      name: /Daily Inspection Report/i,
    });

    screen.getByRole("heading", {
      level: 3,
      name: text => text.includes(project.name) && text.includes(location.name),
    });

    // Since we're creating a new daily inspection report, the work schedule should be empty
    const formattedToday = getFormattedLocaleDateTime(today);
    expect(
      screen.getByLabelText(/contractor work start day and time/i)
    ).toHaveValue(formattedToday);
    expect(
      screen.getByLabelText(/contractor work end day and time/i)
    ).toHaveValue(formattedToday);
  });

  it("should render a active daily report correctly", async () => {
    await act(async () => {
      const { asFragment } = formRender(
        <MockedProvider mocks={[]}>
          <QueryClientProvider client={queryClient}>
            <DailyInspectionReport
              project={project}
              location={location}
              dailyReport={dailyReport}
              recommendations={null}
            />
          </QueryClientProvider>
        </MockedProvider>
      );

      expect(asFragment()).toMatchSnapshot();
    });

    screen.getByRole("heading", {
      level: 2,
      name: /Daily Inspection Report/i,
    });

    screen.getByRole("heading", {
      level: 3,
      name: text => text.includes(project.name) && text.includes(location.name),
    });

    // Since we're creating a new daily inspection report, the work schedule should be empty
    const formattedStartDateTime = getFormattedLocaleDateTime(
      dailyReport.sections?.workSchedule?.startDatetime as string
    );
    const formattedEndDateTime = getFormattedLocaleDateTime(
      dailyReport.sections?.workSchedule?.endDatetime as string
    );

    expect(
      screen.getByLabelText(/contractor work start day and time/i)
    ).toHaveValue(formattedStartDateTime);
    expect(
      screen.getByLabelText(/contractor work end day and time/i)
    ).toHaveValue(formattedEndDateTime);
  });

  describe("Section workflow", () => {
    describe("Work Schedule", () => {
      xit.each([
        {
          ...workSchedule,
        },
      ])(
        "should transform and display all dates, respecting the user local settings",
        async () => {
          await act(async () => {
            const { asFragment } = formRender(
              <MockedProvider mocks={[]}>
                <QueryClientProvider client={queryClient}>
                  <DailyInspectionReport
                    project={project}
                    location={location}
                    projectSummaryViewDate={today}
                    recommendations={null}
                  />
                </QueryClientProvider>
              </MockedProvider>
            );
            expect(asFragment()).toMatchSnapshot();
          });
        }
      );
      it.todo(
        "should successfully request the endpoint with input fields and move to the next step"
      );
      it.todo(
        "should fill in the input fields when daily report has the work schedule stored"
      );
      it.todo(
        "should display a toast when handling the validation issues from the request"
      );
      it.todo(
        "should display a toast when there is a network issue from the request"
      );
    });
    describe("Tasks", () => {
      it.todo(
        "should successfully request the endpoint with input fields and move to the next step"
      );
      it.todo(
        "should fill in the input fields when daily report has the work schedule stored"
      );
      it.todo(
        "should display a toast when handling the validation issues from the request"
      );
      it.todo(
        "should display a toast when there is a network issue from the request"
      );
      it.todo("should reset the tasks when the work schedule has changed");
    });
  });
});

describe("DailyInspectionPageHeader", () => {
  const props = {
    id: "id",
    locationId: "new york",
    reportId: "reportId",
    reportCreatedUserId: "id",
    projectName: "projectName",
    projectNumber: "123456",
    locationName: "locationName",
    isReportSaved: false,
    isReportComplete: false,
    onReopen: jest.fn(),
  };

  it("should render correctly", () => {
    render(
      <MockedProvider mocks={[]}>
        <DailyInspectionPageHeader {...props} />
      </MockedProvider>
    );

    screen.getByRole("heading", {
      level: 2,
      name: /daily inspection report/i,
    });
  });

  describe("when a report is saved", () => {
    describe("and the report is NOT completed", () => {
      describe("and the report can be removed", () => {
        describe.each`
          userId | permissions               | reportId | createdById
          ${1}   | ${["DELETE_REPORTS"]}     | ${"a"}   | ${1}
          ${1}   | ${["DELETE_REPORTS"]}     | ${"a"}   | ${2}
          ${2}   | ${["DELETE_OWN_REPORTS"]} | ${"b"}   | ${2}
        `(
          "when the user with id $userId and has $permissions, for the report created by user $createdById",
          ({ userId, permissions, reportId, createdById }) => {
            beforeEach(() => {
              useAuthStore.setState(state => ({
                ...state,
                me: {
                  initials: "",
                  name: "",
                  email: "super@email.local.urbinternal.com",

                  permissions,
                  role: "viewer",
                  id: userId,

                  opco: null,
                  userPreferences: [],
                },
              }));
            });
            it("should display the TRASH button ", () => {
              render(
                <MockedProvider mocks={[]}>
                  <QueryClientProvider client={queryClient}>
                    <DailyInspectionPageHeader
                      {...props}
                      reportId={reportId}
                      reportCreatedUserId={createdById}
                      isReportSaved
                    />
                  </QueryClientProvider>
                </MockedProvider>
              );

              screen.getAllByRole("button");
            });
          }
        );

        describe.each`
          userId | permissions                                      | reportId | createdById
          ${1}   | ${["CAN_VIEW_PROJECTS", ["DELETE_OWN_REPORTS"]]} | ${"a"}   | ${2}
          ${1}   | ${["CAN_VIEW_PROJECTS"]}                         | ${"a"}   | ${1}
          ${1}   | ${["CAN_EDIT_PROJECTS", "CAN_ADD_ADHOC_TASKS"]}  | ${"b"}   | ${1}
          ${1}   | ${["CAN_EDIT"]}                                  | ${"b"}   | ${1}
        `(
          "when the user with id $userId and has $permissions, for the report created by user $createdById",
          ({ userId, permissions, reportId, createdById }) => {
            beforeEach(() => {
              useAuthStore.setState(state => ({
                ...state,
                me: {
                  initials: "",
                  name: "",
                  email: "super@email.local.urbinternal.com",

                  permissions,
                  role: "viewer",
                  id: userId,
                  opco: null,
                  userPreferences: [],
                },
              }));
            });
            it("should NOT display the TRASH button", () => {
              render(
                <MockedProvider mocks={[]}>
                  <QueryClientProvider client={queryClient}>
                    <DailyInspectionPageHeader
                      {...props}
                      reportId={reportId}
                      reportCreatedUserId={createdById}
                      isReportSaved
                    />
                  </QueryClientProvider>
                </MockedProvider>
              );

              expect(screen.queryByText("Delete")).not.toBeInTheDocument();
            });
          }
        );
      });
    });
  });
});
