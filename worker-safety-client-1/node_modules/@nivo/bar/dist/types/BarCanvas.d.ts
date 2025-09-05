/// <reference types="react" />
import { BarCanvasLayer, BarDatum } from './types';
export declare const BarCanvas: import("react").ForwardRefExoticComponent<Partial<import("./types").BarCommonProps<BarDatum>> & import("./types").DataProps<BarDatum> & import("./types").BarHandlers<BarDatum, HTMLCanvasElement> & import("@nivo/core").Dimensions & Partial<{
    axisBottom: import("@nivo/axes").CanvasAxisProps<any>;
    axisLeft: import("@nivo/axes").CanvasAxisProps<any>;
    axisRight: import("@nivo/axes").CanvasAxisProps<any>;
    axisTop: import("@nivo/axes").CanvasAxisProps<any>;
    renderBar: (context: CanvasRenderingContext2D, props: import("./types").RenderBarProps<BarDatum>) => void;
    layers: BarCanvasLayer<BarDatum>[];
    pixelRatio: number;
}> & import("react").RefAttributes<HTMLCanvasElement>>;
//# sourceMappingURL=BarCanvas.d.ts.map