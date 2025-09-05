import PageLayout from "@/components/layout/pageLayout/PageLayout";
import type { NavigationOption } from "@/components/navigation/Navigation";
import Navigation from "@/components/navigation/Navigation";
import type { IconName } from "@urbint/silica";
import { useState } from "react";
// import DataImportExport from "@/container/admin/dataImportExport/DataImportExport";
import DataImportExport from "@/container/admin/dataImportExport/DataImportExport";
import { IngestData } from "@/container/admin/ingestData/IngestData";
import Insights from "@/container/admin/insights/Insights";
import { Libraries } from "@/container/admin/libraries/Libraries";
import { TenantAttributes } from "@/container/admin/tenantAttributes/TenantAttributes";
import { useTenantFeatures } from "@/hooks/useTenantFeatures";
import { useAuthStore } from "@/store/auth/useAuthStore.store";
import { useTenantStore } from "@/store/tenant/useTenantStore.store";

const getTabOptions = ({
  displayInsights,
}: { displayInsights?: boolean } = {}): NavigationOption[] => {
  return [
    {
      id: 0,
      name: "Tenant Attributes",
      icon: "label",
    },
    {
      id: 1,
      name: "Library Ingest",
      icon: "label",
    },
    {
      id: 2,
      name: "Libraries",
      icon: "label",
    },
    ...(displayInsights
      ? [
          {
            id: 3,
            name: "Insights",
            icon: "label" as IconName,
          },
        ]
      : []),
    {
      id: 4,
      name: "Data Import & Export",
      icon: "label" as IconName,
    },
  ];
};

export default function AdminConfigurations(): JSX.Element {
  const [selectedTab, setSelectedTab] = useState(0);
  const {
    tenant: { name, displayName },
  } = useTenantStore();
  const { displayInsights } = useTenantFeatures(name);
  const isAdmin = useAuthStore(state => state.isAdmin);

  const tabsOptions = getTabOptions({ displayInsights });

  return (
    <PageLayout>
      <section className="mb-6 responsive-padding-x">
        <h1 className="text-2xl text-neutral-shade-100">{displayName}</h1>
      </section>
      <section className="responsive-padding-x grid gap-x-6 grid-rows-2-auto-expand md:grid-cols-2-auto-expand md:grid-rows-none h-screen overflow-hidden">
        <Navigation
          options={tabsOptions}
          onChange={setSelectedTab}
          selectedIndex={selectedTab}
          sidebarClassNames="bg-white p-3"
          selectClassNames="ml-3 w-60 mb-4"
        />
        <div className="p-8 bg-white flex flex-col h-full overflow-hidden">
          {selectedTab === 0 ? <TenantAttributes /> : null}
          {selectedTab === 1 ? <IngestData /> : null}
          {selectedTab === 2 ? <Libraries /> : null}
          {selectedTab === 3 ? <Insights /> : null}
          {selectedTab === 4 && isAdmin() ? <DataImportExport /> : null}
        </div>
      </section>
    </PageLayout>
  );
}
