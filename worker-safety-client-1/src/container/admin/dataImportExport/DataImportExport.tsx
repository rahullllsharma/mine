import Tabs from "@/components/shared/tabs/Tabs";
import { useState } from "react";
import DataExport from "./components/dataExport/DataExport";
import DataImport from "./components/dataImport/DataImport";

export default function DataImportExport() {
  const [selectedTab, setSelectedTab] = useState(0);
  const [dataSources, setDataSources] = useState<string[]>([]);
  const [isFileImportSuccess, setIsFileImportSuccess] = useState(false);
  return (
    <div className="flex flex-col flex-1 overflow-hidden">
      <header className="text-neutral-shade-100 flex justify-between items-start mb-8">
        <div>
          <h2 className="text-xl font-semibold">Data Import & Export</h2>
          <div className="text-base text-neutral-shade-75">
            Import and export data for high-volume fields and templates.
          </div>
        </div>
      </header>
      <Tabs
        options={[
          { id: 0, name: "Data Export" },

          { id: 1, name: "Data Import" },
        ]}
        itemClasses={{
          default:
            "text-neutral-shade-75 font-semibold active:bg-neutral-shade-3 border-b-4",
          selected: "border-brand-urbint-40 border-solid z-10",
          unselected: "opacity-75 border-transparent",
        }}
        selectedIndex={selectedTab}
        defaultIndex={selectedTab}
        onSelect={setSelectedTab}
      />
      <div className="flex-1 overflow-y-hidden mt-6">
        {selectedTab === 0 && (
          <DataExport
            setDataSources={setDataSources}
            navigateToDataImport={() => setSelectedTab(1)}
            isRefreshData={isFileImportSuccess}
          />
        )}
        {selectedTab === 1 && (
          <DataImport
            dataSources={dataSources}
            onCancel={() => {
              setSelectedTab(0);
            }}
            onFileImportSuccess={setIsFileImportSuccess}
          />
        )}
      </div>
    </div>
  );
}
