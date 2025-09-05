import type { PropsWithClassName } from "@/types/Generic";
import type { AccordionProps } from "@/components/shared/accordion/Accordion";
import cx from "classnames";
import Accordion from "@/components/shared/accordion/Accordion";

const positions = {
  "bottom-right": "right-4 bottom-4",
} as const;

type PositionKeys = keyof typeof positions;

export type MapLegendProps = PropsWithClassName<
  Pick<AccordionProps, "header" | "isDefaultOpen"> & {
    position: "none" | PositionKeys;
  }
>;

export default function MapLegend({
  header,
  className,
  children,
  position = "none",
  isDefaultOpen = true,
}: MapLegendProps): JSX.Element {
  return (
    <aside
      className={cx("absolute inline-block bg-white w-44", className, {
        [`${positions[position as PositionKeys]}`]: position !== "none",
      })}
    >
      <Accordion
        isDefaultOpen={isDefaultOpen}
        headerClassName="p-3"
        animation="pop"
        header={
          <span role="heading" aria-level={6} className="text-sm font-semibold">
            {header}
          </span>
        }
      >
        <div className="p-3 border-t border-solid border-brand-gray-20">
          {children}
        </div>
      </Accordion>
    </aside>
  );
}
