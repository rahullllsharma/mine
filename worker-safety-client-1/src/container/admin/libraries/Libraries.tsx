import { useState } from "react";
import TabsLight from "@/components/shared/tabs/light/TabsLight";
import { useTenantStore } from "@/store/tenant/useTenantStore.store";
import { TaskLibrary } from "./TaskLibrary";
import { ActivityGroups } from "./ActivityGroups";
import { HazardsLibrary } from "./HazardLibrary";

const Libraries = () => {
  const [selectedTab, setSelectedTab] = useState<number>(0);

  const { task, hazard } = useTenantStore(state => state.getAllEntities());
  const tabOptions = [task.labelPlural, "Activity Groups", hazard.labelPlural];

  const onSelect = (index: number) => {
    setSelectedTab(index);
  };

  return (
    <section className="flex flex-col overflow-hidden">
      <TabsLight options={tabOptions} onSelect={onSelect} />
      <div className="flex flex-1 overflow-hidden ">
        {selectedTab === 0 ? <TaskLibrary /> : null}
        {selectedTab === 1 ? <ActivityGroups /> : null}
        {selectedTab === 2 ? <HazardsLibrary /> : null}
      </div>
    </section>
  );
};

export { Libraries };
