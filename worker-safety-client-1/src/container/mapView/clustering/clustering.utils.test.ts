import { generateDonutCss } from "./clustering.utils";

describe(generateDonutCss.name, () => {
  describe("when passing 0 properties", () => {
    it("should return an empty string", () => {
      const donutCss = generateDonutCss({
        clusterId: "1234",
        LOW: 0,
        MEDIUM: 0,
        HIGH: 0,
        UNKNOWN: 0,
        RECALCULATING: 0,
        length: 0,
      });

      expect(donutCss).toBe("");
    });
  });

  describe("when passing some properties", () => {
    it("should only add colors from existing properties", () => {
      const donutCss = generateDonutCss({
        clusterId: "1234",
        LOW: 0,
        MEDIUM: 1,
        HIGH: 0,
        UNKNOWN: 5,
        RECALCULATING: 0,
        length: 6,
      });

      expect(donutCss).toBe(
        "background: conic-gradient(#EEBF13 0deg 60deg, rgba(4, 30, 37, 0.07) 60deg 360deg)"
      );
    });
  });

  describe("when passing all properties", () => {
    it("should only add all colors", () => {
      const donutCss = generateDonutCss({
        clusterId: "1234",
        LOW: 10,
        MEDIUM: 10,
        HIGH: 10,
        UNKNOWN: 5,
        RECALCULATING: 5,
        length: 40,
      });

      expect(donutCss).toBe(
        "background: conic-gradient(#238914 0deg 90deg, #EEBF13 90deg 180deg, #D44242 180deg 270deg, rgba(4, 30, 37, 0.07) 270deg 360deg)"
      );
    });
  });
});
