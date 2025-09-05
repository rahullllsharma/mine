import type { BarDatum, BarItemProps } from "@nivo/bar";
import { animated, SpringValue } from "@react-spring/web";
import { BarItem } from "@nivo/bar";

type CustomBarComponentProps = {
  reversedKeys: string[];
} & BarItemProps<BarDatum>;

// A wrapper for the default `BarItem` that applies a clip path, so that the top
// of the stacked bars have rounded corners.
export const CustomBarComponent = ({
  reversedKeys,
  bar,
  style,
  ...props
}: CustomBarComponentProps): JSX.Element => {
  const stackData = bar.data.data;

  // select the first key that has data
  const idToRound = reversedKeys.reduce((acc: string, next: string) => {
    if (!acc && stackData[next] > 0) {
      return next;
    }
    return acc;
  }, "");

  // here we require a minimum height to try to avoid 'invisible' segments
  if (bar.data.id == idToRound && bar.height > 3) {
    // pull the transform off of styles so we can apply it to our own wrapper
    const { transform, ...restStyle } = style;
    const stylez = {
      ...restStyle,
      // a no-op springValue to honor the type-gods
      transform: new SpringValue({ from: "", to: "" }),
    };
    const w = bar.width;
    const h = bar.height;
    const roundInt = 3;

    const roundedTopPath = `m0,${h} v-${
      h - roundInt
    } q0,-${roundInt} ${roundInt},-${roundInt} h${
      w - roundInt * 2
    } q${roundInt},0 ${roundInt},${roundInt} v${h} h-${w} z`;
    // useful for debugging the path: <path d={roundedTopPath} fill="#989898" />
    return (
      <animated.g
        clipPath={`path('${roundedTopPath}')`}
        transform={transform}
        fill="#808080"
      >
        <BarItem {...props} bar={bar} style={stylez} />
      </animated.g>
    );
  }
  // otherwise, use the default BarItem
  return <BarItem bar={bar} style={style} {...props} />;
};
