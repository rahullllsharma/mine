import { breakIntoTspans } from "./chartAxesHelpers";

describe("breakIntoTspans", () => {
  it.each([
    {
      value: "Some short label",
      result: [
        <tspan dy={0} x={0} key={0}>
          Some short label
        </tspan>,
      ],
    },
    {
      value: "Some label longer than the maxLineLength that should be split",
      result: [
        <tspan dy={0} x={0} key={0}>
          Some label longer than the
        </tspan>,
        <tspan dy={21} x={0} key={1}>
          maxLineLength that should be split
        </tspan>,
      ],
    },
    {
      value:
        "Some even longer label that goes on and on and on and on and should end with an ellispes",
      result: [
        <tspan dy={0} x={0} key={0}>
          Some even longer label that goes on
        </tspan>,
        <tspan dy={21} x={0} key={1}>
          and on and on and on and should e...
        </tspan>,
      ],
    },
    {
      value:
        "% that 'Erection of proper barricades and warning signs' was not implemented",
      result: [
        <tspan dy={0} x={0} key={0}>
          % that &apos;Erection of proper
        </tspan>,
        <tspan dy={21} x={0} key={1}>
          barricades and warning signs&apos; was...
        </tspan>,
      ],
    },
  ])("splits $value as expected", ({ value, result }) => {
    expect(breakIntoTspans(value)).toEqual(result);
  });
});
