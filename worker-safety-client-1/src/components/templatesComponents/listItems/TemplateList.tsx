import React from "react";
import { useRouter } from "next/router";
import { DraftTemplatesList } from "../listView/DraftTemplatesList";
import { PublishedTemplatesList } from "../listView/PublishedTemplatesList";
import Loader from "../../shared/loader/Loader";
import { BodyText, SectionHeading } from "@urbint/silica";

type TemplatesListState = "loading" | "complete";
interface TemplateListProps {
  selectedTab: number;
  publishedTemplates: any[];
  draftTemplates: any[];
  disableFetchMore: boolean;
  loadMoreTemplates: () => void;
  togglePublishTemplateModal: (templateUUID?: string) => void;
  toggleVersionHistoryModal: (
    templateUUID?: string,
    templateTitle?: string
  ) => void;
  state?: TemplatesListState;
}

const TemplateList: React.FC<TemplateListProps> = ({
  selectedTab,
  state,
  publishedTemplates,
  draftTemplates,
  disableFetchMore,
  loadMoreTemplates,
  togglePublishTemplateModal,
  toggleVersionHistoryModal,
}) => {
  const router = useRouter();
  const loading = state === "loading";

  const renderContent = (hasTemplates: boolean, listComponent: JSX.Element) => {
    if (hasTemplates) {
      return listComponent;
    } else {
      if (!loading) {
        return (
          <div className="flex flex-col items-center w-full text-center px-6 pt-6">
            <SectionHeading className="mb-2">No templates added</SectionHeading>
            <BodyText>
              Click on{" "}
              <span className="font-semibold text-brand-urbint-40">
                Create Template
              </span>{" "}
              button to add a new template
            </BodyText>
          </div>
        );
      } else {
        return <Loader />;
      }
    }
  };

  if (selectedTab === 0) {
    return renderContent(
      publishedTemplates.length > 0,
      <PublishedTemplatesList
        listData={publishedTemplates}
        state={state}
        disableFetchMore={disableFetchMore}
        onLoadMore={loadMoreTemplates}
        onView={(id: string) => router.push(`/templates/view?templateId=${id}`)}
        onVersionHistory={toggleVersionHistoryModal}
      />
    );
  } else {
    return renderContent(
      draftTemplates.length > 0,
      <DraftTemplatesList
        listData={draftTemplates}
        disableFetchMore={disableFetchMore}
        onLoadMore={loadMoreTemplates}
        onEdit={(id: string) =>
          router.push(`/templates/create?templateId=${id}`)
        }
        onPublishTemplate={(id: string) => {
          togglePublishTemplateModal(id);
        }}
      />
    );
  }
};

export default TemplateList;
