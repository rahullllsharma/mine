import { countTotalControls, groupBy, groupByAliasesOrName } from "./Utils";

describe("Utils", () => {
  describe("when countTotalControls is called", () => {
    describe("when hazard is empty", () => {
      it("should return a count of 0 controls", () => {
        const total = countTotalControls([]);
        expect(total).toBe(0);
      });
    });

    describe("when hazard is not empty", () => {
      const controls = [
        {
          id: "1",
          name: "control name",
          isApplicable: true,
        },
        {
          id: "2",
          name: "control name 2",
          isApplicable: true,
        },
      ];

      it(`should return a count of ${controls.length * 2} controls`, () => {
        const hazards = [
          {
            id: "1",
            name: "hazard 1",
            isApplicable: true,
            controls,
          },
          {
            id: "1",
            name: "hazard 1",
            isApplicable: true,
            controls,
          },
        ];
        const total = countTotalControls(hazards);
        expect(total).toBe(controls.length * 2);
      });
    });
  });

  describe("when groupBy is called", () => {
    describe("when elements is empty", () => {
      it("should return a empty collection", () => {
        expect(groupBy([], "")).toStrictEqual({});
      });
    });

    describe("when identity does not exist", () => {
      it("should return an 'undefined' key", () => {
        const groupedBy = groupBy(
          [{ a: "aaaa", b: "bbbb", c: { d: "dddd" } }],
          "someIdentity"
        );

        const keys = Object.keys(groupedBy);
        expect(keys).toHaveLength(1);
        expect(keys[0]).toBe("undefined");
      });
    });

    describe("when identity exist", () => {
      it("should return a collection with identity as key", () => {
        const groupedBy = groupBy(
          [{ a: "aaaa", b: "bbbb", c: { d: "identityKey" } }],
          "c.d"
        );

        const keys = Object.keys(groupedBy);
        expect(keys).toHaveLength(1);
        expect(keys[0]).toBe("identityKey");
      });

      describe("when we have multiple values for the same identity", () => {
        it("should return a collection indexed by each identity", () => {
          const groupedBy = groupBy(
            [
              { a: "aaaa", b: "bbbb", c: { d: "identityKey" } },
              { a: "aaaa", b: "bbbb", c: { d: "identityKey" } },
              { a: "aaaa", b: "bbbb", c: { d: "identityKeyOther" } },
            ],
            "c.d"
          );

          const keys = Object.keys(groupedBy);
          expect(keys).toHaveLength(2);
        });
      });
    });
  });
});

describe("groupByAliasesOrName", () => {
  it("should deduplicate tasks within the same alias group", () => {
    const tasks = [
      {
        id: "task1",
        name: "Clearing & grading",
        category: "Civil work",
        activitiesGroups: [
          {
            id: "group1",
            name: "Site Setup/Mobilization",
            aliases: ["activity-group 123"],
          },
        ],
      },
      {
        id: "task1__group2",
        name: "Clearing & grading",
        category: "Civil work",
        activitiesGroups: [
          {
            id: "group2",
            name: "activity-group 123",
            aliases: ["activity-group 123", "activity-group 456"],
          },
        ],
      },
    ];

    const result = groupByAliasesOrName(tasks);

    // Should have only one group for "activity-group 123"
    expect(result["activity-group 123"]).toHaveLength(1);

    // The task should have both activity groups merged
    const mergedTask = result["activity-group 123"][0];
    expect(mergedTask.activitiesGroups).toHaveLength(2);
    expect(mergedTask.activitiesGroups?.map((g: any) => g.id)).toContain(
      "group1"
    );
    expect(mergedTask.activitiesGroups?.map((g: any) => g.id)).toContain(
      "group2"
    );

    // Should have a separate group for "activity-group 456"
    expect(result["activity-group 456"]).toHaveLength(1);
  });

  it("should handle tasks with no aliases by falling back to group names", () => {
    const tasks = [
      {
        id: "task1",
        name: "Task 1",
        activitiesGroups: [
          {
            id: "group1",
            name: "Group A",
            aliases: [],
          },
        ],
      },
    ];

    const result = groupByAliasesOrName(tasks);
    expect(result["Group A"]).toHaveLength(1);
    expect(result["Group A"][0].id).toBe("task1");
  });

  it("should handle null aliases by falling back to group names", () => {
    const tasks = [
      {
        id: "223b04e9-62fa-4cf9-97f7-42d7e63994f0",
        name: "Clearing & grading",
        category: "Civil work",
        activitiesGroups: [
          {
            id: "263b01e7-f705-44a2-a8c1-82290b713ec8",
            name: "Site Setup/Mobilization",
            aliases: [null, "activity-group 123 "],
          },
        ],
        isCritical: false,
      },
    ];

    const result = groupByAliasesOrName(tasks as any);

    // Should create group for "Site Setup/Mobilization" (fallback to name)
    expect(result["Site Setup/Mobilization"]).toHaveLength(1);
    expect((result["Site Setup/Mobilization"][0] as any).name).toBe(
      "Clearing & grading"
    );

    // Should also create group for "activity-group 123"
    expect(result["activity-group 123"]).toHaveLength(1);
    expect((result["activity-group 123"][0] as any).name).toBe(
      "Clearing & grading"
    );
  });

  it("should handle undefined aliases by falling back to group names", () => {
    const tasks = [
      {
        id: "task1",
        name: "Task 1",
        activitiesGroups: [
          {
            id: "group1",
            name: "Group B",
            aliases: [undefined, "alias1"],
          },
        ],
      },
    ];

    const result = groupByAliasesOrName(tasks as any);

    // Should create group for "Group B" (fallback to name)
    expect(result["Group B"]).toHaveLength(1);
    expect(result["Group B"][0].id).toBe("task1");

    // Should also create group for "alias1"
    expect(result["alias1"]).toHaveLength(1);
    expect(result["alias1"][0].id).toBe("task1");
  });

  it("should handle empty string aliases by falling back to group names", () => {
    const tasks = [
      {
        id: "task1",
        name: "Task 1",
        activitiesGroups: [
          {
            id: "group1",
            name: "Group C",
            aliases: ["", "   ", "valid-alias"],
          },
        ],
      },
    ];

    const result = groupByAliasesOrName(tasks as any);

    // Should create group for "Group C" (fallback to name due to empty strings)
    expect(result["Group C"]).toHaveLength(1);
    expect(result["Group C"][0].id).toBe("task1");

    // Should also create group for "valid-alias"
    expect(result["valid-alias"]).toHaveLength(1);
    expect(result["valid-alias"][0].id).toBe("task1");
  });

  it("should create multiple activity groups when alias has multiple strings", () => {
    const tasks = [
      {
        id: "223b04e9-62fa-4cf9-97f7-42d7e63994f0",
        name: "Clearing & grading",
        category: "Civil work",
        activitiesGroups: [
          {
            id: "263b01e7-f705-44a2-a8c1-82290b713ed8",
            name: "activity-group 123",
            aliases: ["activity-group 123 ", "activity-group 456 "],
          },
        ],
        isCritical: false,
      },
    ];

    const result = groupByAliasesOrName(tasks as any);

    // Should create two separate groups for the same task
    expect(result["activity-group 123"]).toHaveLength(1);
    expect(result["activity-group 456"]).toHaveLength(1);

    // Both groups should contain the same task
    expect((result["activity-group 123"][0] as any).name).toBe(
      "Clearing & grading"
    );
    expect((result["activity-group 456"][0] as any).name).toBe(
      "Clearing & grading"
    );

    // Both should have the same task ID
    expect(result["activity-group 123"][0].id).toBe(
      "223b04e9-62fa-4cf9-97f7-42d7e63994f0"
    );
    expect(result["activity-group 456"][0].id).toBe(
      "223b04e9-62fa-4cf9-97f7-42d7e63994f0"
    );
  });

  it("should handle mixed null/undefined/empty aliases with valid aliases", () => {
    const tasks = [
      {
        id: "task1",
        name: "Task 1",
        activitiesGroups: [
          {
            id: "group1",
            name: "Group D",
            aliases: [
              null,
              undefined,
              "",
              "   ",
              "valid-alias-1",
              "valid-alias-2",
            ],
          },
        ],
      },
    ];

    const result = groupByAliasesOrName(tasks as any);

    // Should create group for "Group D" (fallback to name due to invalid aliases)
    expect(result["Group D"]).toHaveLength(1);
    expect(result["Group D"][0].id).toBe("task1");

    // Should create groups for valid aliases
    expect(result["valid-alias-1"]).toHaveLength(1);
    expect(result["valid-alias-1"][0].id).toBe("task1");

    expect(result["valid-alias-2"]).toHaveLength(1);
    expect(result["valid-alias-2"][0].id).toBe("task1");
  });

  it("should handle tasks with no activitiesGroups", () => {
    const tasks = [
      {
        id: "task1",
        name: "Task 1",
        activitiesGroups: [],
      },
    ];

    const result = groupByAliasesOrName(tasks);
    expect(result).toEqual({});
  });

  it("should handle tasks with activitiesGroups but no aliases or names", () => {
    const tasks = [
      {
        id: "task1",
        name: "Task 1",
        activitiesGroups: [
          {
            id: "group1",
            aliases: [],
          },
        ],
      },
    ];

    const result = groupByAliasesOrName(tasks);
    expect(result).toEqual({});
  });

  it("should handle real-world scenario with mixed aliases and names", () => {
    const tasks = [
      {
        id: "223b04e9-62fa-4cf9-97f7-42d7e63994f0",
        name: "Clearing & grading",
        category: "Civil work",
        activitiesGroups: [
          {
            id: "263b01e7-f705-44a2-a8c1-82290b713ec8",
            name: "Site Setup/Mobilization",
            aliases: [null, "activity-group 123 "],
          },
          {
            id: "263b01e7-f705-44a2-a8c1-82290b713ed8",
            name: "activity-group 123",
            aliases: ["activity-group 123 ", "activity-group 456 "],
          },
        ],
        isCritical: false,
      },
      {
        id: "ed717165-b18b-4f07-ba6a-f4a4e046123b",
        name: "Surveying & staking",
        category: "Civil work",
        activitiesGroups: [
          {
            id: "263b01e7-f705-44a2-a8c1-82290b713ec8",
            name: "Site Setup/Mobilization",
            aliases: [null, "activity-group 123 "],
          },
        ],
        isCritical: false,
      },
      {
        id: "37a72bab-91b2-41b4-bd83-107a5a4b4951",
        name: "Locates / Mark-outs",
        category: "Civil work",
        activitiesGroups: [
          {
            id: "263b01e7-f705-44a2-a8c1-82290b713ec8",
            name: "Site Setup/Mobilization",
            aliases: [null, "activity-group 123 "],
          },
        ],
        isCritical: false,
      },
      {
        id: "3fc9c105-f594-41be-9f24-c5c74cb495ad",
        name: "Gassing-in",
        category: "Commissioning of facility",
        activitiesGroups: [
          {
            id: "22172a0d-dfcb-46b6-b543-3593d5084873",
            name: "Purging/Gas-in",
            aliases: ["Purging/Gas-in"],
          },
        ],
        isCritical: false,
      },
    ];

    const result = groupByAliasesOrName(tasks as any);

    // Test "Site Setup/Mobilization" group (fallback to name due to null aliases)
    expect(result["Site Setup/Mobilization"]).toHaveLength(3);
    expect(result["Site Setup/Mobilization"].map((t: any) => t.name)).toContain(
      "Clearing & grading"
    );
    expect(result["Site Setup/Mobilization"].map((t: any) => t.name)).toContain(
      "Surveying & staking"
    );
    expect(result["Site Setup/Mobilization"].map((t: any) => t.name)).toContain(
      "Locates / Mark-outs"
    );

    // Test "activity-group 123" group
    expect(result["activity-group 123"]).toHaveLength(3);
    expect(result["activity-group 123"].map((t: any) => t.name)).toContain(
      "Clearing & grading"
    );
    expect(result["activity-group 123"].map((t: any) => t.name)).toContain(
      "Surveying & staking"
    );
    expect(result["activity-group 123"].map((t: any) => t.name)).toContain(
      "Locates / Mark-outs"
    );

    // Test "activity-group 456" group
    expect(result["activity-group 456"]).toHaveLength(1);
    expect((result["activity-group 456"][0] as any).name).toBe(
      "Clearing & grading"
    );

    // Test "Purging/Gas-in" group
    expect(result["Purging/Gas-in"]).toHaveLength(1);
    expect((result["Purging/Gas-in"][0] as any).name).toBe("Gassing-in");
  });

  it("should handle complex scenario with multiple tasks and mixed alias patterns", () => {
    const tasks = [
      {
        id: "task1",
        name: "Task 1",
        activitiesGroups: [
          {
            id: "group1",
            name: "Group A",
            aliases: [null, "alias1", ""],
          },
          {
            id: "group2",
            name: "Group B",
            aliases: ["alias2", "alias3"],
          },
        ],
      },
      {
        id: "task2",
        name: "Task 2",
        activitiesGroups: [
          {
            id: "group3",
            name: "Group C",
            aliases: [undefined, "alias1"],
          },
        ],
      },
    ];

    const result = groupByAliasesOrName(tasks as any);

    // Test fallback to names
    expect(result["Group A"]).toHaveLength(1);
    expect(result["Group A"][0].id).toBe("task1");

    expect(result["Group C"]).toHaveLength(1);
    expect(result["Group C"][0].id).toBe("task2");

    // Test valid aliases
    expect(result["alias1"]).toHaveLength(2);
    expect(result["alias1"].map((t: any) => t.id)).toContain("task1");
    expect(result["alias1"].map((t: any) => t.id)).toContain("task2");

    expect(result["alias2"]).toHaveLength(1);
    expect(result["alias2"][0].id).toBe("task1");

    expect(result["alias3"]).toHaveLength(1);
    expect(result["alias3"][0].id).toBe("task1");
  });
});
