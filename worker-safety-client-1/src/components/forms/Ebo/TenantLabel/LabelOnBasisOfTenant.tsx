// TODO
// As of now for temporary basis we are changing the label from Front End for XcelEnergy

import { useTenantStore } from "@/store/tenant/useTenantStore.store";

export const getUncontrolledReasons = (tenantName: string) => {
  const baseLabels = [
    { label: "Hazard not identified" },
    { label: "Direct control not properly used" },
    { label: "Direct control not available, but limited control used" },
    { label: "Direct control not available and no limited control used" },
    {
      label: "Direct control not available and Limited Control not available.",
    },
  ];

  if (
    tenantName === "xcelenergy" ||
    tenantName === "test-xcelenergy" ||
    tenantName === "test-xcelenergy1"
  ) {
    return baseLabels.map(item => ({
      label: item.label.replace("Direct", "Critical"),
    }));
  } else {
    return baseLabels;
  }
};

// labelReplacements.ts
export const replaceDirectWithCritical = (tenantName: string, text: string) => {
  if (
    tenantName === "xcelenergy" ||
    tenantName === "test-xcelenergy" ||
    tenantName === "test-xcelenergy1"
  ) {
    return text.replace(/Direct/g, "Critical").replace(/direct/g, "critical");
  }
  return text;
};

export const getLabels = (tenantName: string) => {
  const directControlsLabel = replaceDirectWithCritical(
    tenantName,
    "Direct Controls"
  );
  const directControlsImplementedLabel = replaceDirectWithCritical(
    tenantName,
    "Were direct controls implemented for the high-energy hazard?"
  );
  const chooseDirectControlsLabel = replaceDirectWithCritical(
    tenantName,
    "Choose at least one of the following direct controls:"
  );
  const directControlDescriptionLabel = replaceDirectWithCritical(
    tenantName,
    "Direct Control Description"
  );
  const noDirectControlsReasonLabel = replaceDirectWithCritical(
    tenantName,
    "Why were no direct controls implemented?"
  );
  const limitedControlsImplementedLabel = replaceDirectWithCritical(
    tenantName,
    "What limited controls were implemented for the high-energy hazard?"
  );

  const directControlTargeted = replaceDirectWithCritical(
    tenantName,
    "Direct controls must be targeted, effective, correctly installed, verified, used properly and not prone to human error"
  );

  const hazardsWithEnergy = replaceDirectWithCritical(
    tenantName,
    "Hazards with energy values below 500 foot-pounds are not considered high energy, please remove non-high energy hazards from the EBO"
  );

  return {
    directControlsLabel,
    directControlsImplementedLabel,
    chooseDirectControlsLabel,
    directControlDescriptionLabel,
    noDirectControlsReasonLabel,
    limitedControlsImplementedLabel,
    directControlTargeted,
    hazardsWithEnergy,
  };
};

export const changeLabelOnBasisOfTenant = (
  tenantName: string,
  label: string
) => {
  if (
    tenantName === "xcelenergy" ||
    tenantName === "test-xcelenergy" ||
    tenantName === "test-xcelenergy1"
  ) {
    switch (label) {
      case "Department observed":
        return "Business Unit Observed";
      case "Sub OpCo observed":
        return "Location employee(s) reports to";
      default:
        return label;
    }
  }
  return label;
};

// Utility function to get tenant name
export const getTenantName = () => {
  return useTenantStore.getState().tenant.name;
};
