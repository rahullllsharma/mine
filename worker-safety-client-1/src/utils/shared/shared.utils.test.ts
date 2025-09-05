import { appendToFilename, stripTypename } from "./shared.utils";

describe("shared/helpers", () => {
  describe(stripTypename.name, () => {
    const objectsWithTypename = [
      [],
      { __typename: "__typename", t: "__typename" },
      [{ __typename: "__typename", t: "__typename" }],
      {
        __typename: "__typename",
        id: "3c3af0ec-3cf5-4566-bf20-2a3953af7a7e",
        completedBy: null,
        completedAt: [
          {
            __typename: "__typename",
          },
          [
            {
              __typename: "__typename",
            },
            {
              t: "__typename",
            },
          ],
          "prop",
        ],
        sections: {
          taskSelection: {
            selectedTasks: [
              {
                id: "86873ccd-6109-4633-9d2d-426fd91760db",
              },
            ],
          },
        },
        status: "IN_PROGRESS",
      },
      {
        id: "3c3af0ec-3cf5-4566-bf20-2a3953af7a7e",
        completedBy: null,
        completedAt: {
          __typename: "query",
          id: "86873ccd-6109-4633-9d2d-426fd91760db",
        },
        sections: {
          taskSelection: {
            __typename: "xxxx",
            id: "86873ccd-6109-4633-9d2d-426fd91760db",
            selectedTasks: [
              {
                __typename: "qqqq",
                id: "86873ccd-6109-4633-9d2d-426fd91760db",
              },
            ],
          },
        },
        status: "IN_PROGRESS",
      },
      {
        operationName: "SaveDailyReport",
        variables: {
          dailyReportInput: {
            id: "e28ab28d-63cc-4b62-8af5-3a3cc829c61f",
            projectLocationId: "11f0bfce-44aa-4ee0-86d2-fb35775b6798",
            date: "2022-02-01",
            __typename: "Sections",
            additionalInformation: null,
            crew: null,
            jobHazardAnalysis: null,
            safetyAndCompliance: null,
            taskSelection: {
              __typename: "TaskSelectionSection",
              selectedTasks: [
                {
                  __typename: "TaskSelection",
                  id: "86873ccd-6109-4633-9d2d-426fd91760db",
                  name: "Above-ground welding - Above ground weld",
                  riskLevel: "HIGH",
                },
              ],
            },
            workSchedule: {
              __typename: "WorkSchedule",
              endDatetime: "2022-02-04T20:20:00.000Z",
              startDate: "2022-02-01T10:10:00.000Z",
            },
            "job-hazard-analysis": {
              "0c7d5b09-bb4e-4b91-8e15-89a59c76190d-isApplicable": true,
              "507a609b-0516-4484-8d02-a99041d5e829-isApplicable": true,
              "cd27615d-c2f5-46ee-82f3-a62bd2e5b7eb-isImplemented": true,
              "55c973e6-1d9c-4885-94f8-a5c2f3c554e9-isImplemented": true,
              "a33f85e4-c9d3-4bd4-bc9e-dfb28e9269cb-isImplemented": true,
            },
          },
        },
      },
    ];

    it.each(objectsWithTypename)(
      "should remove the __typename property",
      param => {
        expect(JSON.stringify(stripTypename(param))).toEqual(
          expect.not.stringMatching(/\"__typename\":/gi)
        );
      }
    );

    it("should NOT change the original param when __typename does not exist in the object", () => {
      const param = {
        id: "3c3af0ec-3cf5-4566-bf20-2a3953af7a7e",
        completedBy: null,
        completedAt: {},
        sections: {
          taskSelection: {
            selectedTasks: [
              {
                id: "86873ccd-6109-4633-9d2d-426fd91760db",
              },
            ],
          },
        },
        status: "IN_PROGRESS",
      };
      expect(stripTypename(param)).toStrictEqual(param);
    });
  });

  describe(appendToFilename.name, () => {
    describe("when the filename doesn't contain any a file extension", () => {
      it("should return the filename and the value", () => {
        const result = appendToFilename("file", "name");
        expect(result).toBe("filename");
      });
    });

    describe("when the filename contains a file extension", () => {
      it("should return the value before the file extension", () => {
        const result = appendToFilename("filename.pdf", "_suffix");
        expect(result).toBe("filename_suffix.pdf");
      });
    });

    describe('when the filename contains more than one "." besides the file extension', () => {
      it("should return the value before the file extension", () => {
        const result = appendToFilename(
          "filename.something.another.type.pdf",
          "_suffix"
        );
        expect(result).toBe("filename.something.another.type_suffix.pdf");
      });
    });
  });
});
