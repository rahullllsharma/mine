import { calculateFractionsPerRisk } from "./fractions";

describe(calculateFractionsPerRisk.name, () => {
  it.each`
    high  | medium       | low          | unknown
    ${25} | ${25}        | ${25}        | ${25}
    ${25} | ${25}        | ${25}        | ${undefined}
    ${25} | ${25}        | ${undefined} | ${undefined}
    ${25} | ${undefined} | ${undefined} | ${undefined}
    ${25} | ${25}        | ${25}        | ${25}
    ${25} | ${25}        | ${25}        | ${0}
    ${25} | ${25}        | ${0}         | ${0}
    ${25} | ${0}         | ${0}         | ${0}
  `(
    "should calculate the proper paths and remove risks without scores",
    scores => {
      const params = Object.entries(scores) as [string, number | undefined][];
      const total = params.reduce((acc, [, val]) => acc + (val ?? 0), 0);

      const result = calculateFractionsPerRisk(params, total);
      expect(result).toMatchSnapshot();

      expect(result.length).toEqual(
        params.filter(([, value]) => !!value).length
      );

      // Remove all the undefined elements
      params.forEach(([key, value]) => {
        if (!value) {
          expect(
            result.some(fraction => fraction.className.includes(key))
          ).toBe(false);
        }
      });
    }
  );
});
