import type { ComputedDatum, BarDatum } from "@nivo/bar";

export type StackedBarChartDataDescription = {
  key: string;
  color?: string | ((datum: ComputedDatum<BarDatum>) => string);
  hoverColor?: string | ((datum: ComputedDatum<BarDatum>) => string);
  selectedColor?: string | ((datum: ComputedDatum<BarDatum>) => string);
  labelColor?: string | ((datum: ComputedDatum<BarDatum>) => string);
};
