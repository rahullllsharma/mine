// from nivo/legends/svg/symbols/types
type LegendSymbolShape = {
  id: string | number;
  x: number;
  y: number;
  size: number;
  fill: string;
  opacity?: number;
  borderWidth?: number;
  borderColor?: string;
};

export const CustomLegendSymbolShape = ({
  x,
  y,
  size,
  fill,
  borderWidth,
  borderColor,
}: LegendSymbolShape): JSX.Element => (
  <rect
    x={x}
    y={y}
    rx={2}
    ry={2}
    fill={fill}
    strokeWidth={borderWidth}
    stroke={borderColor}
    width={size}
    height={size}
    style={{ pointerEvents: "none" }}
  />
);
