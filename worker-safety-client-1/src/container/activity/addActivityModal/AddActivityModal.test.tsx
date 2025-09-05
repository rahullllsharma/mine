import { MockedProvider } from "@apollo/client/testing";
import { render, screen, waitFor } from "@testing-library/react";
import * as apolloClient from "@apollo/client";
import { mockTenantStore } from "@/utils/dev/jest";

import AddActivityModal from "./AddActivityModal";

jest.mock("@apollo/client", () => {
  return {
    __esModule: true,
    ...jest.requireActual("@apollo/client"),
    useLazyQuery: jest.fn().mockReturnValue([
      jest.fn(),
      {
        loading: true,
      },
    ]),
  };
});

describe(AddActivityModal.name, () => {
  let restoreIntersectionObserver: typeof global.IntersectionObserver;

  beforeAll(() => {
    mockTenantStore();
    // useLazyQuery requests the IntersectionObserver class that is NOT available on the jsdom test env
    // so we temporarily mock it and restore its original value.
    restoreIntersectionObserver = global.IntersectionObserver;
    global.IntersectionObserver = jest.fn(() => ({
      observe: jest.fn(),
      disconnect: jest.fn(),
      unobserve: jest.fn(),
    })) as unknown as typeof global.IntersectionObserver;
  });

  afterAll(() => {
    global.IntersectionObserver = restoreIntersectionObserver;
  });

  describe("while the HazardsControlsLibrary are being fetched", () => {
    it("should defer adding the <TaskDetails />", () => {
      render(
        <MockedProvider mocks={[]} addTypename={false}>
          <AddActivityModal
            isOpen
            closeModal={jest.fn()}
            startDate="2022-10-05"
            projectEndDate="2022-10-10"
            projectStartDate="2022-10-01"
            locationId="project-acme"
          />
        </MockedProvider>
      );

      // wrapping inside a waitFor fn since apollo useQuery and useLazyQuery trigger async operations
      waitFor(() => {
        expect(
          screen.queryByRole("heading", { level: 5, name: /custom task/gi })
        ).not.toBeInTheDocument();
      });
    });
  });

  describe("when the HazardsControlsLibrary are fetched", () => {
    it("should render the <TaskDetails />", async () => {
      // Mock all the useLazyQuery invocation
      jest.spyOn(apolloClient, "useLazyQuery").mockReturnValue([
        jest.fn(),
        {
          data: {
            tasksLibrary: [{ id: 1, name: "custom task", hazards: [] }],
            hazardsLibrary: [{ id: 1, name: "hazard" }],
            controlsLibrary: [{ id: 1, name: "control" }],
          },
          loading: false,
        } as apolloClient.QueryResult<unknown, apolloClient.OperationVariables>,
      ]);

      render(
        <MockedProvider mocks={[]} addTypename={false}>
          <AddActivityModal
            isOpen
            closeModal={jest.fn()}
            startDate="2022-10-05"
            projectEndDate="2022-10-10"
            projectStartDate="2022-10-01"
            locationId="project-acme"
          />
        </MockedProvider>
      );

      waitFor(() => {
        expect(
          screen.queryByRole("heading", { level: 5, name: /custom task/gi })
        ).toBeInTheDocument();
      });
    });
  });
});
