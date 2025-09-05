import type { CrewGraphQLPayloadParams } from "./graphQLPayload";
import graphQLPayload from "./graphQLPayload";

describe(graphQLPayload.name, () => {
  //TODO Review test
  it.skip("convert empty all strings to nulls", () => {
    expect(
      graphQLPayload({
        crew: {
          contractor: "",
          foremanName: "",
          nWelders: "",
          nSafetyProf: "",
          nFlaggers: "",
          nLaborers: "",
          nOperators: "",
          nOtherCrew: "",
          documents: [],
        },
      })
    ).toMatchInlineSnapshot(`
      Object {
        "crew": Object {
          "contractor": null,
          "documents": Array [],
          "foremanName": null,
          "nFlaggers": null,
          "nLaborers": null,
          "nOperators": null,
          "nOtherCrew": null,
          "nSafetyProf": null,
          "nWelders": null,
        },
      }
    `);
  });

  //TODO Review test
  it.skip("convert only the empty strings to nulls", () => {
    expect(
      graphQLPayload({
        crew: {
          contractor: "John Smith",
          foremanName: "",
          nWelders: "",
          nSafetyProf: "",
          nFlaggers: "",
          nLaborers: "",
          nOperators: 2,
          nOtherCrew: 1,
          documents: [],
        },
      })
    ).toMatchInlineSnapshot(`
      Object {
        "crew": Object {
          "contractor": "John Smith",
          "documents": Array [],
          "foremanName": null,
          "nFlaggers": null,
          "nLaborers": null,
          "nOperators": 2,
          "nOtherCrew": 1,
          "nSafetyProf": null,
          "nWelders": null,
        },
      }
    `);
  });

  it("should not convert when inputs have values", () => {
    expect(
      graphQLPayload({
        crew: {
          contractor: "ACME Inc.",
          foremanName: "John Doe",
          nWelders: 1,
          nSafetyProf: 2,
          nFlaggers: 3,
          nLaborers: 4,
          nOperators: 5,
          nOtherCrew: 6,
          documents: [
            {
              id: "photo-123",
              displayName: "Hello.jpg",
              name: "Hello.jpg",
              size: "123",
              date: "2022-01-01",
              time: "10:10",
              url: "http://localhost/fake",
              signedUrl: "http://localhost/signed/fake",
            },
          ],
        },
      })
    ).toMatchInlineSnapshot(`
      Object {
        "crew": Object {
          "contractor": "ACME Inc.",
          "documents": Array [
            Object {
              "date": "2022-01-01",
              "displayName": "Hello.jpg",
              "id": "photo-123",
              "name": "Hello.jpg",
              "signedUrl": "http://localhost/signed/fake",
              "size": "123",
              "time": "10:10",
              "url": "http://localhost/fake",
            },
          ],
          "foremanName": "John Doe",
          "nFlaggers": 3,
          "nLaborers": 4,
          "nOperators": 5,
          "nOtherCrew": 6,
          "nSafetyProf": 2,
          "nWelders": 1,
        },
      }
    `);
  });

  it("should not convert the documents property", () => {
    expect(
      graphQLPayload({
        crew: {
          documents: [
            {
              id: "photo-123",
              displayName: "Hello.jpg",
              name: "Hello.jpg",
              size: "123",
              date: "2022-01-01",
              time: "10:10",
              url: "http://localhost/fake",
              signedUrl: "http://localhost/signed/fake",
            },
          ],
        },
      } as unknown as CrewGraphQLPayloadParams)
    ).toMatchInlineSnapshot(`
      Object {
        "crew": Object {
          "documents": Array [
            Object {
              "date": "2022-01-01",
              "displayName": "Hello.jpg",
              "id": "photo-123",
              "name": "Hello.jpg",
              "signedUrl": "http://localhost/signed/fake",
              "size": "123",
              "time": "10:10",
              "url": "http://localhost/fake",
            },
          ],
        },
      }
    `);
  });
});
