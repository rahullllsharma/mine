import type { SelectPrimaryOption } from "@/components/shared/select/selectPrimary/SelectPrimary";
import type { Location } from "@/types/project/Location";
import type { WorkType } from "../../../types/task/WorkType";
import type { SummaryViewContentType } from "../ProjectSummaryView";
import { useRouter } from "next/router";
import { useCallback, useContext, useMemo, useState } from "react";
import axiosRest from "@/api/customFlowApi";
import { handleFormViewMode } from "@/components/forms/Utils";
import LocationRisk from "@/components/locationRisk/LocationRisk";
import RiskBadge from "@/components/riskBadge/RiskBadge";
import ButtonPrimary from "@/components/shared/button/primary/ButtonPrimary";
import Dropdown from "@/components/shared/dropdown/Dropdown";
import PopoverIcon from "@/components/shared/popover/popoverIcon/PopoverIcon";
import SelectPrimary from "@/components/shared/select/selectPrimary/SelectPrimary";
import ToastContext from "@/components/shared/toast/context/ToastContext";
import Tooltip from "@/components/shared/tooltip/Tooltip";
import useRestMutation from "@/hooks/useRestMutation";
import { useTenantFeatures } from "@/hooks/useTenantFeatures";
import { messages } from "@/locales/messages";
import { useAuthStore } from "@/store/auth/useAuthStore.store";
import { useTenantStore } from "@/store/tenant/useTenantStore.store";
import TemplateFormsFlyover from "./TemplateFormsFlyover";

type MenuItemProps = {
  label: string;
  visible?: boolean;
  onClick?: () => void;
};

type ProjectSummaryViewHeaderProps = {
  locations: Location[];
  projectRegionId?: string;
  projectContractorId?: string;
  selectedLocation: Location;
  onLocationSelected: (option: SelectPrimaryOption) => void;
  onAddContent: (type: SummaryViewContentType) => void;
  isCritical?: boolean;
  startDate?: string;
  projectWorkTypes?: WorkType[];
};

function ProjectSummaryViewHeader({
  locations,
  projectContractorId,
  projectRegionId,
  selectedLocation,
  onLocationSelected,
  onAddContent,
  isCritical = false,
  startDate,
  projectWorkTypes,
}: ProjectSummaryViewHeaderProps) {
  const router = useRouter();
  const { hasPermission, isViewer } = useAuthStore();
  const { tenant, getAllEntities } = useTenantStore();
  const { activity, siteCondition } = getAllEntities();
  const { displayInspections, displayJSB } = useTenantFeatures(tenant.name);
  const toastCtx = useContext(ToastContext);
  const {
    me: { permissions: userPermissions },
  } = useAuthStore();

  const locationList = useMemo<SelectPrimaryOption[]>(
    () =>
      locations.map(loc => ({
        id: loc.id,
        name: loc.name,
      })),
    [locations]
  );

  const [templateOptions, setTemplateOptions] = useState<any[]>([]);
  const [isTemplateFlyoverOpen, setIsTemplateFlyoverOpen] = useState(false);
  const [isLoadingTemplates, setIsLoadingTemplates] = useState(false);

  const defaultMenuItems = useMemo<MenuItemProps[]>(
    () => [
      {
        label: activity?.label || "Activity",
        onClick: () => onAddContent("activity"),
        visible: hasPermission("ADD_ACTIVITIES"),
      },
      {
        label: siteCondition?.label || "Site Condition",
        onClick: () => onAddContent("siteCondition"),
        visible: hasPermission("ADD_SITE_CONDITIONS"),
      },
    ],
    [
      activity,
      siteCondition,
      hasPermission,
      displayInspections,
      displayJSB,
      isViewer,
      onAddContent,
      router,
      selectedLocation.id,
    ]
  );

  const filteredDefaultMenuItems = useMemo(() => {
    return [defaultMenuItems.filter(item => item.visible !== false)];
  }, [defaultMenuItems]);

  const { mutate: fetchTemplateFormList } = useRestMutation<any>({
    endpoint: "templates/list/add-options",
    method: "post",
    axiosInstance: axiosRest,
    dtoFn: data => data,
  });

  const handleOpenTemplateFlyover = useCallback(() => {
    setIsTemplateFlyoverOpen(true);
    if (templateOptions.length === 0) {
      setIsLoadingTemplates(true);
      const workTypeIds = projectWorkTypes?.map(workType => workType.id) || [];
      fetchTemplateFormList(
        {
          work_type_ids: workTypeIds,
          status: "published",
          availability: "work-package",
        },
        {
          onSuccess: rawResponse => {
            const response = rawResponse as { data?: { data?: any[] } };
            const newTemplates =
              response?.data?.data && Array.isArray(response.data.data)
                ? response.data.data
                    .slice()
                    .sort((a, b) => a.name.localeCompare(b.name))
                : [];

            setTemplateOptions(newTemplates);
            setIsLoadingTemplates(false);
          },
          onError: error => {
            console.error(error);
            toastCtx?.pushToast("error", messages.SomethingWentWrong);
            setIsLoadingTemplates(false);
          },
        }
      );
    }
  }, [
    fetchTemplateFormList,
    templateOptions.length,
    toastCtx,
    projectWorkTypes,
  ]);

  const handleCloseTemplateFlyover = useCallback(() => {
    setIsTemplateFlyoverOpen(false);
  }, []);

  return (
    <div className="flex flex-col w-full items-start md:flex-row md:items-center">
      <TemplateFormsFlyover
        isOpen={isTemplateFlyoverOpen}
        templates={templateOptions}
        isLoading={isLoadingTemplates}
        selectedLocationId={selectedLocation.id}
        projectId={selectedLocation?.project?.id}
        projectContractorId={projectContractorId}
        projectRegionId={projectRegionId}
        startDate={startDate}
        onClose={handleCloseTemplateFlyover}
        locations={locations}
        displayJSB={displayJSB && !isViewer()}
      />
      <SelectPrimary
        className="w-full z-20 lg:w-[36rem] mr-3 mb-4 md:mb-0"
        options={locationList}
        onSelect={onLocationSelected}
        defaultOption={locationList.find(
          option => option.id === selectedLocation.id
        )}
        allowMultilineBox
      />
      <div className="flex items-center w-full md:flex-1 justify-between gap-6">
        <div className="flex items-center">
          <Tooltip
            title="The High / Medium / Low classification represents the relative likelihood of presence of high energy hazards while the task is being performed"
            position="bottom"
            className="max-w-xl"
          >
            <RiskBadge
              risk={selectedLocation.riskLevel}
              label={`${selectedLocation.riskLevel}`}
              isCritical={isCritical}
            />
          </Tooltip>
          <PopoverIcon
            className="w-60 md:w-80 -translate-x-1/2 left-1/2"
            iconName="calculator"
            iconClass="text-neutral-shade-75 ml-3"
            tooltipProps={{ title: "How is this calculated?" }}
          >
            <LocationRisk
              risk={selectedLocation.riskCalculation.totalTaskRiskLevel}
              supervisorRisk={
                selectedLocation.riskCalculation.isSupervisorAtRisk
              }
              contractorRisk={
                selectedLocation.riskCalculation.isContractorAtRisk
              }
              crewRisk={selectedLocation.riskCalculation.isCrewAtRisk}
            />
          </PopoverIcon>
        </div>
        {handleFormViewMode(userPermissions) && (
          <div className="flex items-center gap-px">
            <ButtonPrimary
              label="Add Form"
              iconStart="plus"
              onClick={handleOpenTemplateFlyover}
              iconStartClassName="font-[bold] text-xl"
              controlStateClass="py-1 px-2.5"
              className="rounded-tr-none rounded-br-none"
            />
            {filteredDefaultMenuItems[0].length > 0 && (
              <Dropdown
                menuItems={[filteredDefaultMenuItems[0]]}
                className="z-10"
                simple={true}
              >
                <ButtonPrimary
                  iconEnd="chevron_big_down"
                  iconEndClassName="font-[bold] text-xl"
                  controlStateClass="py-1 px-2.5"
                  className="rounded-tl-none rounded-bl-none"
                />
              </Dropdown>
            )}
          </div>
        )}
      </div>
    </div>
  );
}

export { ProjectSummaryViewHeader };
