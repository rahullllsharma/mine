import graphQLPayload from "./graphQLPayload";

describe(graphQLPayload.name, () => {
  it("convert empty all strings to nulls", () => {
    expect(
      graphQLPayload({
        workSchedule: {
          startDatetime: "",
          endDatetime: "",
        },
      })
    ).toMatchInlineSnapshot(`
      Object {
        "workSchedule": Object {
          "endDatetime": null,
          "startDatetime": null,
        },
      }
    `);
  });

  it("convert only the empty strings to nulls", () => {
    expect(
      graphQLPayload({
        workSchedule: {
          startDatetime: "2022-03-16T00:00",
          endDatetime: "",
        },
      })
    ).toMatchInlineSnapshot(`
      Object {
        "workSchedule": Object {
          "endDatetime": null,
          "startDatetime": "2022-03-16T00:00:00.000Z",
        },
      }
    `);
  });

  it("should not convert when inputs have values", () => {
    expect(
      graphQLPayload({
        workSchedule: {
          startDatetime: "2022-03-16T10:10",
          endDatetime: "2022-03-17T20:32",
        },
      })
    ).toMatchInlineSnapshot(`
      Object {
        "workSchedule": Object {
          "endDatetime": "2022-03-17T20:32:00.000Z",
          "startDatetime": "2022-03-16T10:10:00.000Z",
        },
      }
    `);
  });
});
