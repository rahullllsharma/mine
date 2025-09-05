import type { PropsWithClassName } from "@/types/Generic";
import { describeArc } from "../utils/math";

type CircleProps = PropsWithClassName<{
  segmentSize: number;
  segmentTotal: number;
  start: number;
  end: number;
}>;

const Circle = ({
  className,
  segmentSize = 40,
  segmentTotal = 4,
  start = 0,
  end = 360,
}: CircleProps): JSX.Element => {
  // to create an effect of a padding, we need to subtract some inner padding to the circle.
  const radius = segmentSize - 8;
  const offset = segmentTotal > 1 ? 4 : 0;

  // segments are used to created the white effect
  const startPoint = start + offset;
  const endPoint = end - offset;

  return (
    <path
      className={className}
      fill="none"
      stroke="currentColor"
      strokeWidth="5"
      d={describeArc(segmentSize, segmentSize, radius, startPoint, endPoint)}
    />
  );
};

export { Circle };
