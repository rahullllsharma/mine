import { useTenantStore } from "@/store/tenant/useTenantStore.store";

export const getTaskNotPerformedOptions = () => [
  { id: "Unfavorable Weather", name: "Unfavorable Weather" },
  {
    id: "Contractor Delay",
    name: `${
      useTenantStore.getState().getAllEntities().workPackage.attributes
        .primeContractor.label
    } Delay`,
  },
  { id: "Equipment Delay", name: "Equipment Delay" },
  { id: "Material Delay", name: "Material Delay" },
  {
    id: "Dependent Task Not Completed",
    name: `Dependent ${
      useTenantStore.getState().getAllEntities().task.label
    } Not Completed`,
  },
  { id: "Safety Delay", name: "Safety Delay" },
  { id: "Permitting / Design Delays", name: "Permitting / Design Delays" },
];

export const getControlNotPerformedOptions = () => [
  { id: "Planned but not implemented", name: "Planned but not implemented" },
  {
    id: "Other controls in place",
    name: `Other ${useTenantStore
      .getState()
      .getAllEntities()
      .control.labelPlural.toLowerCase()} in place`,
  },
  {
    id: "Control was not relevant",
    name: `${
      useTenantStore.getState().getAllEntities().control.label
    } was not relevant`,
  },
  {
    id: "Control was not available",
    name: `${
      useTenantStore.getState().getAllEntities().control.label
    } was not available`,
  },
];
