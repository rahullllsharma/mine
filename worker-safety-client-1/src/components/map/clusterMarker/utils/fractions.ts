type RiskPointProperties = {
  risk: string;
  className: string;
  start: number;
  end: number;
};

function calculateFractionsPerRisk(
  totalsAsAssoc: [string, number | undefined][],
  total: number
): RiskPointProperties[] {
  let lastStartPoint = 0;

  const totalsPerFraction = totalsAsAssoc
    // exclude risks without scores
    .filter(([, value]) => !!value)
    .map(([key, value]) => {
      // determine the start and end points.
      const start = lastStartPoint;

      const segment = parseFloat(((value as number) / total).toFixed(3));
      const end = start + Math.abs(segment * 360);

      // replace the last point by the new one.
      lastStartPoint = end;

      return {
        risk: key,
        className: `text-risk-${key}`,
        start,
        end: end < 360 ? end : 359.9,
      };
    });

  return totalsPerFraction;
}

export { calculateFractionsPerRisk };
