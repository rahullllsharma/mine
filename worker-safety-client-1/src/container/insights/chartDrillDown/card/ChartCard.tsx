import type { ReactNode } from "react";
import { Icon } from "@urbint/silica";
import { useTenantStore } from "@/store/tenant/useTenantStore.store";

type ChartCardProps = {
  title: string;
  type: "hazard" | "control";
  chart?: ReactNode;
};

const EmptyCardContent = ({ type }: { type: string }): JSX.Element => {
  const { hazard, control } = useTenantStore(state => state.getAllEntities());

  const typeLabel =
    type === "hazard"
      ? hazard.label.toLowerCase()
      : control.label.toLowerCase();
  return (
    <>
      <p className="text-neutral-shade-75 text-sm px-4 text-center">
        {`A chart will appear here when one (1) ${typeLabel} is selected`}
      </p>
      <Icon
        name="bar_chart_square"
        className="text-neutral-shade-58 text-4xl"
      />
    </>
  );
};

export default function ChartCard({
  title,
  type,
  chart = <EmptyCardContent type={type} />,
}: ChartCardProps): JSX.Element {
  return (
    <div className="flex flex-col items-center">
      <p className="text-neutral-shade-100 text-base font-semibold mb-2">
        {title}
      </p>
      <div className="flex flex-col items-center justify-center border border-dashed border-neutral-shade-58 rounded-lg w-full h-96">
        {chart}
      </div>
    </div>
  );
}
