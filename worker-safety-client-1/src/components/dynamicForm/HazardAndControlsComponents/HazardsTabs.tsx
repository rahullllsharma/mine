import type { Hazards } from "../../templatesComponents/customisedForm.types";
import React from "react";

type HazardsTabsProps = {
  activeTab: string;
  setActiveTab: (tab: string) => void;
  selectedHighEnergyHazards: Hazards[];
  selectedOtherHazards: Hazards[];
  subTitle: string;
};

const HazardsTabs = ({
  activeTab,
  setActiveTab,
  selectedHighEnergyHazards,
  selectedOtherHazards,
  subTitle,
}: HazardsTabsProps) => {
  return (
    <div className="flex border-b mb-4">
      <button
        className={`px-4 py-2 mr-2 ${
          activeTab === "highEnergy"
            ? "border-b-2 border-blue-500 font-medium"
            : ""
        }`}
        onClick={() => setActiveTab("highEnergy")}
      >
        {subTitle || "High Energy Hazards"}
        <span className="bg-gray-200 px-2 py-1 rounded-full text-xs">
          {selectedHighEnergyHazards.length}
        </span>
      </button>
      <button
        className={`px-4 py-2 ${
          activeTab === "otherHazards"
            ? "border-b-2 border-blue-500 font-medium"
            : ""
        }`}
        onClick={() => setActiveTab("otherHazards")}
      >
        Other Hazards
        <span className="bg-gray-200 px-2 py-1 rounded-full text-xs">
          {selectedOtherHazards.length}
        </span>
      </button>
    </div>
  );
};

export default HazardsTabs;
