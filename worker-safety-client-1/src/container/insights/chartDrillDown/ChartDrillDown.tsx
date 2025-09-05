import type { ReactNode } from "react";
import Input from "@/components/shared/input/Input";
import { useTenantStore } from "@/store/tenant/useTenantStore.store";
import ChartCard from "./card/ChartCard";

export type ChartItem = {
  title: string;
  content?: ReactNode;
};

type ChartDrillDownProps = {
  type: "hazard" | "control";
  inputValue?: string | number;
  charts?: ChartItem[];
};

export default function ChartDrillDown({
  type,
  inputValue,
  charts,
}: ChartDrillDownProps): JSX.Element {
  const { hazard, control } = useTenantStore(state => state.getAllEntities());

  const typeLabel =
    type === "hazard"
      ? hazard.label.toLowerCase()
      : control.label.toLowerCase();

  return (
    <div className="flex flex-col items-center gap-y-8">
      <div className="flex flex-col items-center gap-y-4">
        <p className="text-lg font-semibold text-neutral-shade-100">{`Select one (1) ${typeLabel} from the above chart to view details`}</p>
        <Input
          containerClassName="w-72"
          className="text-center"
          disabled
          value={`${inputValue}`}
        />
      </div>
      <div className="grid grid-cols-1 xl:grid-cols-2 gap-12 w-full">
        {charts?.map((chart: ChartItem, index: number) => (
          <ChartCard
            key={index}
            title={chart.title}
            type={type}
            chart={chart.content}
          />
        ))}
      </div>
    </div>
  );
}
