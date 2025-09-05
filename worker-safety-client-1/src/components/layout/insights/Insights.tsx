import type { ReactNode } from "react";
import cx from "classnames";
import EmptyContent from "@/components/emptyContent/EmptyContent";
import TabsLight from "@/components/shared/tabs/light/TabsLight";
import { useTenantStore } from "@/store/tenant/useTenantStore.store";
import PageLayout from "../pageLayout/PageLayout";

type InsightsProps = {
  filters?: ReactNode;
  charts?: ReactNode[];
  emptyChartsTitle: string;
  emptyChartsDescription?: string;
  onTabChange: (index: number) => void;
  hasData?: boolean;
};

const EmptyChartContent = ({
  title,
  description = "Try adjusting your filters, to return more data",
}: {
  title: string;
  description?: string;
}): JSX.Element => (
  <div className="bg-white rounded-xl flex flex-1 items-center justify-center min-h-[130px] max-h-48">
    <EmptyContent title={title} description={description} />
  </div>
);

export default function Insights({
  filters,
  charts = [],
  emptyChartsTitle,
  emptyChartsDescription,
  onTabChange,
  hasData = true,
}: InsightsProps): JSX.Element {
  const { workPackage } = useTenantStore(state => state.getAllEntities());
  const tabOptions = ["Portfolio", workPackage.label];

  return (
    <PageLayout className="responsive-padding-x bg-white" showExpand={true}>
      <div className="h-full hidden lg:block">
        <TabsLight options={tabOptions} onSelect={onTabChange} />

        <div className="flex flex-wrap  bg-white rounded-xl p-6 mt-5 ">
          <div className="lg:w-full pr-4 pl-4">
            <div className="sticky top-0">{filters}</div>
          </div>
        </div>

        <div className="flex mt-6 pb-6 gap-x-8 ">
          {charts.length > 0 && (
            <div
              className={cx("flex flex-col gap-y-8 flex-1 my-14", {
                // we need to 'render' the chart comps even when they don't have
                // data, so they can make more requests when the filters change
                ["relative"]: hasData,
                ["hidden"]: !hasData,
              })}
            >
              {charts.map((chart, index) => (
                <section
                  key={index}
                  className="bg-white p-6 rounded-xl overflow-hidden"
                >
                  {chart}
                </section>
              ))}
            </div>
          )}
          {(charts.length === 0 || !hasData) && (
            <EmptyChartContent
              title={emptyChartsTitle}
              description={emptyChartsDescription}
            />
          )}
        </div>
      </div>
      <div className="h-2/3 w-full flex items-center lg:hidden">
        <EmptyContent
          title="Your screen size is not large enough to support this feature"
          description="Please increase your screen size to access the content"
        />
      </div>
    </PageLayout>
  );
}
