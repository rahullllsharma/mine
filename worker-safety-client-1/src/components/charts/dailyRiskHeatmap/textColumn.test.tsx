import { buildTextColumn } from "./textColumn";

describe("buildTextColumn", () => {
  it("supports a default width", () => {
    const colDef = { id: "some-id", Header: "some header" };
    const res = buildTextColumn(6, colDef);
    expect(res.width).toBe(140);
  });

  it("supports overwriting the width", () => {
    const colDef = { id: "some-id", width: 100, Header: "some header" };
    const res = buildTextColumn(6, colDef);
    expect(res.width).toBe(100);
  });
});
