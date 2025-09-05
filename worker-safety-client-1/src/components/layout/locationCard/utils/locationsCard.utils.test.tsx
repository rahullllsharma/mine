import type { Activity } from "@/types/activity/Activity";
import { render } from "@testing-library/react";
import {
  TenantMock,
  editTenantEntitiesAttributesMock,
} from "@/store/tenant/utils/tenantMock";
import { mockTenantStore } from "@/utils/dev/jest";
import {
  getCardOptionalProps,
  getActivitiesValues,
} from "./locationsCard.utils";

jest.mock("@/hooks/useTenantFeatures", () => ({
  useTenantFeatures: jest.fn(() => ({
    displayLocationCardDynamicProps: {
      identifier: "activity",
      slot3: "activity",
    },
  })),
}));

describe("Location card utils", () => {
  describe(getActivitiesValues.name, () => {
    beforeAll(() => {
      mockTenantStore(TenantMock);
    });

    describe("when passing empty arrays in the arguments", () => {
      it("should return the default initial object", () => {
        const INPUT = [
          {
            supervisors: [],
          },
        ];
        const OUTPUT = {
          activityTypes: [],
          activitySupervisors: [],
        };

        expect(getActivitiesValues(INPUT)).toEqual(OUTPUT);
      });
    });

    describe("when passing activity type", () => {
      it("should return an object with activities array populated", () => {
        const INPUT = [
          {
            libraryActivityType: {
              id: "1000",
              name: "activity type 1",
            },
            supervisors: [],
          },
        ];
        const OUTPUT = {
          activityTypes: ["activity type 1"],
          activitySupervisors: [],
        };

        expect(getActivitiesValues(INPUT)).toEqual(OUTPUT);
      });
    });

    describe("when passing supervisor", () => {
      it("should return an object with supervisors array populated", () => {
        const INPUT = [
          {
            supervisors: [
              {
                id: "1",
                name: "supervisor 1",
              },
            ],
          },
        ];
        const OUTPUT = {
          activityTypes: [],
          activitySupervisors: ["supervisor 1"],
        };

        expect(getActivitiesValues(INPUT)).toEqual(OUTPUT);
      });
    });

    describe("when passing mulitple activities with multiple activity types and supervisors", () => {
      it("should return an object with both activities and supervisors arrays populated", () => {
        const INPUT = [
          {
            libraryActivityType: {
              id: "1000",
              name: "activity type 1",
            },
            supervisors: [
              {
                id: "1",
                name: "supervisor 1",
              },
              {
                id: "2",
                name: "supervisor 2",
              },
            ],
          },
          {
            libraryActivityType: {
              id: "2000",
              name: "activity type 2",
            },
            supervisors: [
              {
                id: "3",
                name: "supervisor 3",
              },
              {
                id: "4",
                name: "supervisor 4",
              },
            ],
          },
        ];
        const OUTPUT = {
          activityTypes: ["activity type 1", "activity type 2"],
          activitySupervisors: [
            "supervisor 1",
            "supervisor 2",
            "supervisor 3",
            "supervisor 4",
          ],
        };

        expect(getActivitiesValues(INPUT)).toEqual(OUTPUT);
      });
    });
  });

  describe(getCardOptionalProps.name, () => {
    beforeAll(() => {
      mockTenantStore(TenantMock);
    });

    describe("when passing an empty props object", () => {
      it("should return the default object", () => {
        const INPUT = {
          displayLocationCardDynamicProps: {
            identifier: "activity",
            slot3: "activity",
          },
        };
        const OUTPUT = { identifier: "", slots: [] };

        expect(getCardOptionalProps(INPUT)).toEqual(OUTPUT);
      });
    });

    describe("when passing activity slots that have mixed visibility rules in the attributes configuration", () => {
      beforeEach(() => {
        const newMock = editTenantEntitiesAttributesMock([
          {
            entity: "workPackage",
            attribute: "division",
            key: "visible",
            value: false,
          },
        ]);
        mockTenantStore(newMock);
      });

      it("should display only the visible slots", () => {
        const INPUT = {
          division: "division",
          region: "region",
          activities: [
            {
              libraryActivityType: {
                id: "100",
                name: "activity type 1",
              },
              supervisors: [
                {
                  id: "10000",
                  name: "primary assigned person 1",
                },
              ],
            },
          ] as unknown as Activity[],
          displayLocationCardDynamicProps: {
            identifier: "activity",
            slot3: "activity",
          },
        };
        const OUTPUT = {
          identifier: "activity type 1",
          slots: ["region", "primary assigned person 1"],
        };

        expect(getCardOptionalProps(INPUT)).toEqual(OUTPUT);
      });
    });

    describe("when passing location slots that have mixed visibility rules in the attributes configuration", () => {
      beforeEach(() => {
        const newMock = editTenantEntitiesAttributesMock([
          {
            entity: "workPackage",
            attribute: "division",
            key: "visible",
            value: true,
          },
        ]);
        mockTenantStore(newMock);
      });

      it("should display only the visible slots", () => {
        const INPUT = {
          division: "division",
          region: "region",
          primaryAssignedPersonLocation: "primary assigned person",
          displayLocationCardDynamicProps: {
            identifier: "workPackage",
            slot3: "location",
          },
        };
        const OUTPUT = {
          identifier: "",
          slots: ["division", "region", "primary assigned person"],
        };

        expect(getCardOptionalProps(INPUT)).toEqual(OUTPUT);
      });
    });

    describe("when passing workPackage identifier with visibility", () => {
      it("should return the identifier", () => {
        const INPUT = {
          workPackageType: "work package type",
          displayLocationCardDynamicProps: {
            identifier: "workPackage",
            slot3: "location",
          },
        };
        const OUTPUT = {
          identifier: "work package type",
          slots: [],
        };

        expect(getCardOptionalProps(INPUT)).toEqual(OUTPUT);
      });
    });

    describe("when passing workPackageType identifier with no visibility", () => {
      beforeEach(() => {
        const newMock = editTenantEntitiesAttributesMock([
          {
            entity: "workPackage",
            attribute: "workPackageType",
            key: "visible",
            value: false,
          },
        ]);
        mockTenantStore(newMock);
      });

      it("should not return the identifier", () => {
        const INPUT = {
          workPackageType: "work package type",
          displayLocationCardDynamicProps: {
            identifier: "workPackage",
            slot3: "location",
          },
        };
        const OUTPUT = {
          identifier: "",
          slots: [],
        };

        expect(getCardOptionalProps(INPUT)).toEqual(OUTPUT);
      });
    });

    describe("when passing activity identifier with one value", () => {
      it("should return the identifier as a string", () => {
        const INPUT = {
          activities: [
            {
              libraryActivityType: {
                id: "100",
                name: "activity type 1",
              },
              supervisors: [],
            },
          ] as unknown as Activity[],
          displayLocationCardDynamicProps: {
            identifier: "activity",
            slot3: "activity",
          },
        };
        const OUTPUT = {
          identifier: "activity type 1",
          slots: [],
        };

        expect(getCardOptionalProps(INPUT)).toEqual(OUTPUT);
      });
    });

    describe("when passing activity identifier with multiple values", () => {
      it("should return the identifier as an element", () => {
        const { identifier } = getCardOptionalProps({
          activities: [
            {
              libraryActivityType: {
                id: "100",
                name: "activity type 1",
              },
              supervisors: [],
            },
            {
              libraryActivityType: {
                id: "200",
                name: "activity type 2",
              },
              supervisors: [],
            },
          ] as unknown as Activity[],
          displayLocationCardDynamicProps: {
            identifier: "activity",
            slot3: "activity",
          },
        });
        expect(typeof identifier).toBe("object");
        // eslint-disable-next-line @typescript-eslint/ban-ts-comment
        // @ts-ignore
        const { asFragment } = render(identifier);
        expect(asFragment()).toMatchSnapshot();
      });
    });

    describe("when passing one activity with multiple supersivor", () => {
      it("should return the supervisor in the last slot", () => {
        const INPUT = {
          activities: [
            {
              libraryActivityType: null,
              supervisors: [
                {
                  id: "10000",
                  name: "primary assigned person 1",
                },
              ],
            },
          ] as unknown as Activity[],
          displayLocationCardDynamicProps: {
            identifier: "activity",
            slot3: "activity",
          },
        };
        const OUTPUT = {
          identifier: "",
          slots: ["primary assigned person 1"],
        };

        expect(getCardOptionalProps(INPUT)).toEqual(OUTPUT);
      });
    });

    describe("when passing multiple activities with multiple supersivors", () => {
      it("should return the supervisors in the last slot", () => {
        const INPUT = {
          activities: [
            {
              libraryActivityType: null,
              supervisors: [
                {
                  id: "10000",
                  name: "primary assigned person 1",
                },
                {
                  id: "20000",
                  name: "primary assigned person 2",
                },
              ],
            },
            {
              libraryActivityType: null,
              supervisors: [
                {
                  id: "30000",
                  name: "primary assigned person 3",
                },
                {
                  id: "40000",
                  name: "primary assigned person 4",
                },
              ],
            },
          ] as unknown as Activity[],
          displayLocationCardDynamicProps: {
            identifier: "activity",
            slot3: "activity",
          },
        };
        const OUTPUT = {
          identifier: "",
          slots: [
            "primary assigned person 1, primary assigned person 2, primary assigned person 3, primary assigned person 4",
          ],
        };

        expect(getCardOptionalProps(INPUT)).toEqual(OUTPUT);
      });
    });
  });
});
