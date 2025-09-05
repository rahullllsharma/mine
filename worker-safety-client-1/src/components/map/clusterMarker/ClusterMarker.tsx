import type { RiskLevel } from "@/components/riskBadge/RiskLevel";
import { Circle } from "./components/Circle";
import { calculateFractionsPerRisk } from "./utils/fractions";

type ClusterMarkerPropsKeys = Lowercase<
  Exclude<RiskLevel, RiskLevel.RECALCULATING>
>;

type ClusterMarkerProps = Partial<Record<ClusterMarkerPropsKeys, number>> & {
  size?: number;
};

function ClusterMarker({
  size = 50,
  ...scores
}: ClusterMarkerProps): JSX.Element {
  // total segment size based off the component size.
  const segmentSize = size * 0.5;

  const totalsAsAssoc = Object.entries(scores);
  const total = totalsAsAssoc.reduce(
    (acc, [, value]) => acc + (value > 0 ? value : 0),
    0
  );

  // calculate each arc per score
  const totalsPerFraction = calculateFractionsPerRisk(totalsAsAssoc, total);

  return (
    <div className="inline-block shadow-20 rounded-full max-w-[400px] h-auto">
      <svg
        viewBox={`0 0 ${size} ${size}`}
        width={size}
        height={size}
        xmlns="http://www.w3.org/2000/svg"
      >
        <g type="rect" className="transform rotate-[330deg] origin-center">
          {totalsPerFraction.map(({ risk, ...circleProps }) => (
            <Circle
              key={risk}
              segmentSize={segmentSize}
              segmentTotal={totalsPerFraction.length}
              {...circleProps}
            />
          ))}
        </g>
        <text
          x="50%"
          y="52%"
          dominantBaseline="middle"
          textAnchor="middle"
          className="text-base bg-neutral-shade-100 font-semibold"
        >
          {total < 999 ? total : "+999"}
        </text>
      </svg>
    </div>
  );
}

export default ClusterMarker;
