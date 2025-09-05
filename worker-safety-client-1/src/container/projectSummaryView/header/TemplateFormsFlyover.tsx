import type { Location } from "@/types/project/Location";
import { BodyText, CaptionText, Subheading } from "@urbint/silica";
import { useRouter } from "next/router";
import { useState } from "react";
import Link from "next/link";
import useTemplateStore from "@/pages/store/useTemplateStore";
import SelectWorkTypeModal from "@/components/templatesComponents/TemplateForms/SelectWorkTypeModal/SelectWorkTypeModal";
import Flyover from "@/components/flyover/Flyover";
import styles from "./templateFormsFlyover.module.scss";

type TemplateData = {
  id: string;
  name: string;
  work_types?: WorkType[];
};

type WorkType = {
  id: string;
  name: string;
  prepopulate?: boolean;
};

type TemplateFormsFlyoverProps = {
  isOpen: boolean;
  templates: TemplateData[];
  isLoading: boolean;
  selectedLocationId: string;
  projectId?: string;
  projectRegionId?: string;
  projectContractorId?: string;
  startDate?: string;
  onClose: () => void;
  locations: Location[];
  displayJSB?: boolean;
};

const renderWorkTypesSummary = (workTypes: WorkType[] = []) => {
  if (workTypes.length === 0) return null;

  const maxToShow = 3;
  const shown = workTypes.slice(0, maxToShow);
  const remaining = workTypes.length - maxToShow;

  return (
    <>
      {shown.map((workType, idx) => (
        <span key={workType.id}>
          {workType.name}
          {idx < shown.length - 1 ? ", " : ""}
        </span>
      ))}
      {remaining > 0 && <span>...+{remaining}</span>}
    </>
  );
};

const TemplateFormsFlyover = ({
  isOpen,
  templates,
  isLoading,
  selectedLocationId,
  projectId,
  projectRegionId,
  projectContractorId,
  startDate,
  onClose,
  locations,
  displayJSB,
}: TemplateFormsFlyoverProps): JSX.Element => {
  const router = useRouter();
  const templateStore = useTemplateStore();

  const [openSelectWorktypeModal, setOpenSelectWorktypeModal] = useState(false);
  const [selectedTemplateWorktype, setSelectedTemplateWorktype] = useState<{
    id: string;
    templateName: string;
    workTypes: WorkType[];
  } | null>(null);

  const resetTemplateWorktypeState = () => {
    setOpenSelectWorktypeModal(false);
    setSelectedTemplateWorktype(null);
  };

  const navigateToFormListPage = (
    templateId: string,
    workTypes: WorkType[] = []
  ) => {
    resetTemplateWorktypeState();
    localStorage.setItem("selectedWorkTypes", JSON.stringify(workTypes));

    // TODO: Remove projectContractorId here and fetch it from project api
    templateStore.setTemplateData({
      projectContractorId: projectContractorId,
      projectRegionId: projectRegionId,
    });

    const getLatAndLngBAsedOnLocationId = () => {
      const selectedLocation = locations.find(
        location => location.id === selectedLocationId
      );
      return {
        lat: selectedLocation?.latitude,
        lng: selectedLocation?.longitude,
      };
    };

    router.push({
      pathname: "/template-forms/add",
      query: {
        templateId: templateId,
        project: projectId,
        location: selectedLocationId,
        startDate: startDate,
        latitude: getLatAndLngBAsedOnLocationId().lat,
        longitude: getLatAndLngBAsedOnLocationId().lng,
      },
    });
  };

  const handleTemplateClick = (template: TemplateData) => {
    // Check if template has work types that require selection
    localStorage.removeItem("selectedWorkTypes");
    if (template.work_types && template.work_types.length > 1) {
      setSelectedTemplateWorktype({
        id: template.id,
        templateName: template.name,
        workTypes: template.work_types,
      });
      setOpenSelectWorktypeModal(true);
    } else {
      // Directly navigate if no work types to select
      navigateToFormListPage(template.id, template.work_types || []);
    }
  };

  return (
    <>
      <SelectWorkTypeModal
        showModal={openSelectWorktypeModal}
        selectedTemplate={selectedTemplateWorktype || null}
        closeModal={resetTemplateWorktypeState}
        cancel={resetTemplateWorktypeState}
        continueToForm={selectedWorkTypes => {
          console.log("Selected Work Types:", selectedWorkTypes);
          navigateToFormListPage(
            selectedTemplateWorktype?.id || "",
            selectedWorkTypes
          );
        }}
      />

      <Flyover
        isOpen={isOpen}
        title="Select Form Template"
        unmount
        onClose={onClose}
        footerStyle={"!relative right-0 !bottom-[1.5rem]"}
        className={styles.flyoverContainer}
      >
        {isLoading ? (
          <div className="flex justify-center items-center h-32">
            <div className="text-neutral-shade-75">Loading templates...</div>
          </div>
        ) : (
          <>
            {displayJSB && (
              <Link
                href={{
                  pathname: "/jsb",
                  query: {
                    locationId: selectedLocationId,
                    ...(router.query.source
                      ? { source: router.query.source }
                      : {}),
                  },
                }}
                passHref
                legacyBehavior
              >
                <a className="border border-gray-200 p-4 rounded-sm cursor-pointer mt-2 hover:bg-gray-50 transition-colors bg-blue-50 block">
                  <div
                    className={`font-semibold text-neutral-shade-100 ${styles.templateNameTruncate}`}
                  >
                    Job Safety Briefing
                  </div>
                  <div className="text-gray-400 text-[13px] mt-1">
                    Add Job Safety Briefing
                  </div>
                </a>
              </Link>
            )}
            {!displayJSB && templates?.length === 0 ? (
              <div className="flex justify-center items-center h-160 flex-col text-center">
                <Subheading className="mb-2">No Forms Available</Subheading>
                <CaptionText className="text-[#3C4F55]   text-[14px] mb-2">
                  Either no forms are available for work packages, or they are
                  not compatible with the Work Types associated with this work
                  package.
                </CaptionText>
                <div className="text-center text-[#3C4F55]   text-[14px]">
                  Please contact your administrator for help with form
                  availability.
                </div>
              </div>
            ) : templates?.length > 0 ? (
              templates.map(template => (
                <div
                  key={template.id}
                  className="border border-gray-200 p-4 rounded-sm cursor-pointer mt-2 hover:bg-gray-50 transition-colors"
                  onClick={() => handleTemplateClick(template)}
                >
                  <BodyText
                    className={`font-semibold text-neutral-shade-100 ${styles.templateNameTruncate}`}
                  >
                    {template.name}
                  </BodyText>
                  {template.work_types && template.work_types.length > 0 && (
                    <div className="text-gray-400 text-[13px] mt-1">
                      {renderWorkTypesSummary(template.work_types)}
                    </div>
                  )}
                </div>
              ))
            ) : null}
          </>
        )}
      </Flyover>
    </>
  );
};

export default TemplateFormsFlyover;
