import { useTenantStore } from "@/store/tenant/useTenantStore.store";

function TaskDetailsHeader() {
  const { hazard, control } = useTenantStore(state => state.getAllEntities());
  return (
    <header className="flex flex-1 flex-wrap items-center text-left text-sm font-semibold text-neutral-shade-75 px-4 pt-4">
      <p className="flex flex-1">{`${hazard.label} / ${control.label} group`}</p>
      Applicable?
    </header>
  );
}

export { TaskDetailsHeader };
