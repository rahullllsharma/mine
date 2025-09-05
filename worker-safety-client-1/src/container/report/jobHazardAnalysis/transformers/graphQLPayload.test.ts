import type { JobHazardAnalysisGraphQLPayloadParams } from "./graphQLPayload";
import graphQLPayloadTransforms from "./graphQLPayload";

describe(graphQLPayloadTransforms.name, () => {
  it.each([
    null,
    undefined,
    {},
    { siteConditions: null },
    { siteConditions: undefined },
    { siteConditions: {} },
    { tasks: null },
    { tasks: undefined },
    { tasks: {} },
  ])(
    "should parse the form data correctly when missing site condtions and tasks",
    jobHazardAnalysis => {
      expect(
        graphQLPayloadTransforms({
          jobHazardAnalysis,
        } as unknown as JobHazardAnalysisGraphQLPayloadParams)
      ).toEqual({
        jobHazardAnalysis: {
          siteConditions: [],
          tasks: [],
        },
      });
    }
  );

  it("should parse the form data correctly without tasks", () => {
    const formData = {
      jobHazardAnalysis: {
        siteConditions: {
          site2: {
            isApplicable: true,
            hazards: {
              hazard2: {
                isApplicable: true,
                controls: {
                  control2: {},
                },
              },
            },
          },
        },
      },
    };

    expect(graphQLPayloadTransforms(formData as any)).toMatchInlineSnapshot(`
      Object {
        "jobHazardAnalysis": Object {
          "siteConditions": Array [
            Object {
              "hazards": Array [
                Object {
                  "controls": Array [
                    Object {
                      "furtherExplanation": "",
                      "id": "control2",
                      "implemented": false,
                      "notImplementedReason": "",
                    },
                  ],
                  "id": "hazard2",
                  "isApplicable": true,
                },
              ],
              "id": "site2",
              "isApplicable": true,
            },
          ],
          "tasks": Array [],
        },
      }
    `);
  });

  it("should parse the form data correctly", () => {
    const formData = {
      jobHazardAnalysis: {
        siteConditions: {
          site2: {
            isApplicable: true,
            hazards: {
              hazard2: {
                isApplicable: true,
                controls: {
                  control2: {},
                },
              },
            },
          },
        },
        tasks: {
          task1: {
            performed: true,
            notes: "notes",
            hazards: {
              hazard1: {
                isApplicable: true,
                controls: {
                  control1: {
                    implemented: true,
                  },
                },
              },
            },
          },
        },
      },
    };

    expect(graphQLPayloadTransforms(formData as any)).toMatchInlineSnapshot(`
      Object {
        "jobHazardAnalysis": Object {
          "siteConditions": Array [
            Object {
              "hazards": Array [
                Object {
                  "controls": Array [
                    Object {
                      "furtherExplanation": "",
                      "id": "control2",
                      "implemented": false,
                      "notImplementedReason": "",
                    },
                  ],
                  "id": "hazard2",
                  "isApplicable": true,
                },
              ],
              "id": "site2",
              "isApplicable": true,
            },
          ],
          "tasks": Array [
            Object {
              "hazards": Array [
                Object {
                  "controls": Array [
                    Object {
                      "furtherExplanation": "",
                      "id": "control1",
                      "implemented": true,
                      "notImplementedReason": "",
                    },
                  ],
                  "id": "hazard1",
                  "isApplicable": true,
                },
              ],
              "id": "task1",
              "notApplicableReason": "",
              "notes": "notes",
              "performed": true,
            },
          ],
        },
      }
    `);
  });

  it("should parse the form data correctly with selections", () => {
    const formData = {
      jobHazardAnalysis: {
        siteConditions: {
          site2: {
            isApplicable: true,
            hazards: {
              hazard2: {
                isApplicable: true,
                controls: {
                  control2: {
                    isApplicable: false,
                  },
                },
              },
            },
          },
        },
        tasks: {
          task1: {
            performed: true,
            notes: "notes",
            notApplicableReason: {
              id: "Contractor Delay",
              name: "Contractor Delay",
            },
            hazards: {
              hazard1: {
                isApplicable: true,
                controls: {
                  control1: {
                    implemented: false,
                    notImplementedReason: {
                      id: "Contractor Delay",
                      name: "Contractor Delay",
                    },
                  },
                },
              },
              hazard2: {
                isApplicable: false,
                controls: {
                  control2: {
                    implemented: true,
                  },
                },
              },
            },
          },
          task2: {
            isApplicable: true,
            hazards: {
              hazard1: {
                isApplicable: true,
                controls: {
                  control1: {
                    implemented: false,
                  },
                },
              },
            },
          },
        },
      },
    };

    expect(graphQLPayloadTransforms(formData as any)).toMatchInlineSnapshot(`
      Object {
        "jobHazardAnalysis": Object {
          "siteConditions": Array [
            Object {
              "hazards": Array [
                Object {
                  "controls": Array [
                    Object {
                      "furtherExplanation": "",
                      "id": "control2",
                      "implemented": false,
                      "notImplementedReason": "",
                    },
                  ],
                  "id": "hazard2",
                  "isApplicable": true,
                },
              ],
              "id": "site2",
              "isApplicable": true,
            },
          ],
          "tasks": Array [
            Object {
              "hazards": Array [
                Object {
                  "controls": Array [
                    Object {
                      "furtherExplanation": "",
                      "id": "control1",
                      "implemented": false,
                      "notImplementedReason": "Contractor Delay",
                    },
                  ],
                  "id": "hazard1",
                  "isApplicable": true,
                },
                Object {
                  "controls": Array [
                    Object {
                      "furtherExplanation": "",
                      "id": "control2",
                      "implemented": true,
                      "notImplementedReason": "",
                    },
                  ],
                  "id": "hazard2",
                  "isApplicable": false,
                },
              ],
              "id": "task1",
              "notApplicableReason": "Contractor Delay",
              "notes": "notes",
              "performed": true,
            },
            Object {
              "hazards": Array [
                Object {
                  "controls": Array [
                    Object {
                      "furtherExplanation": "",
                      "id": "control1",
                      "implemented": false,
                      "notImplementedReason": "",
                    },
                  ],
                  "id": "hazard1",
                  "isApplicable": true,
                },
              ],
              "id": "task2",
              "notApplicableReason": "",
              "notes": "",
              "performed": true,
            },
          ],
        },
      }
    `);
  });

  describe("when doesnt have hazards", () => {
    it("should send an empty array", () => {
      const formData = {
        jobHazardAnalysis: {
          tasks: [],
          siteConditions: [
            {
              id: "d6114ed1-f01a-4532-a7b2-1cc30ee3aa1f",
              isApplicable: false,
              hazards: undefined,
            },
            {
              id: "4c76fafd-53b3-4601-b6d0-fe7fbc07a1cf",
              isApplicable: true,
              hazards: [],
            },
          ],
        },
      };
      const result = graphQLPayloadTransforms(formData as any);
      const { siteConditions } = result.jobHazardAnalysis;

      expect(siteConditions[0].hazards).toHaveLength(0);
      expect(siteConditions[1].hazards).toHaveLength(0);
    });
  });

  describe("when doesnt have controls", () => {
    it("should send an empty array", () => {
      const formData = {
        jobHazardAnalysis: {
          tasks: [],
          siteConditions: [
            {
              id: "d6114ed1-f01a-4532-a7b2-1cc30ee3aa1f",
              isApplicable: false,
              hazards: [
                {
                  id: "d6114ed1-f01a-4532-a7b2-1cc30ee3aa1f",
                  isApplicable: false,
                  controls: [],
                },
                {
                  id: "d6114ed1-f01a-4532-a7b2-1cc30ee3aa1f",
                  isApplicable: false,
                  controls: undefined,
                },
              ],
            },
          ],
        },
      };
      const result = graphQLPayloadTransforms(formData as any);
      const { siteConditions } = result.jobHazardAnalysis;
      expect(siteConditions[0].hazards[0].controls).toHaveLength(0);
      expect(siteConditions[0].hazards[1].controls).toHaveLength(0);
    });
  });

  describe("when set withControlDefaults to false", () => {
    it("must perserve the values from the form", () => {
      const formData = {
        jobHazardAnalysis: {
          siteConditions: {
            site2: {
              isApplicable: true,
              hazards: {
                hazard2: {
                  isApplicable: true,
                  controls: {
                    control1: {
                      implemented: undefined,
                    },
                    control2: {
                      implemented: false,
                      notImplementedReason: undefined,
                    },
                    control3: {
                      implemented: true,
                      notImplementedReason: "any reason",
                    },
                  },
                },
              },
            },
          },
        },
      };

      expect(
        graphQLPayloadTransforms(formData as any, {
          withDefaultControlValue: false,
        })
      ).toMatchInlineSnapshot(`
        Object {
          "jobHazardAnalysis": Object {
            "siteConditions": Array [
              Object {
                "hazards": Array [
                  Object {
                    "controls": Array [
                      Object {
                        "furtherExplanation": "",
                        "id": "control1",
                        "implemented": undefined,
                        "notImplementedReason": "",
                      },
                      Object {
                        "furtherExplanation": "",
                        "id": "control2",
                        "implemented": false,
                        "notImplementedReason": "",
                      },
                      Object {
                        "furtherExplanation": "",
                        "id": "control3",
                        "implemented": true,
                        "notImplementedReason": "",
                      },
                    ],
                    "id": "hazard2",
                    "isApplicable": true,
                  },
                ],
                "id": "site2",
                "isApplicable": true,
              },
            ],
            "tasks": Array [],
          },
        }
      `);
    });
  });
});
