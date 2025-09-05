import type {
  ActivePageObjType,
  ActivitiesAndTasksFormType,
  CWFLocationType,
  CWFNearestHospitalType,
  CWFSiteConditionsType,
  CWFSummaryType,
  EditComponentType,
  FormComponentPayloadType,
  FormElementsType,
  FormType,
  HazardsAndControlsFormType,
  PageType,
  PersonnelComponentType,
  ProjectDetailsType,
  UserFormMode,
  WidgetType,
} from "@/components/templatesComponents/customisedForm.types";
import { CaptionText, SectionHeading } from "@urbint/silica";
import parse from "html-react-parser";
import orderBy from "lodash/orderBy";
import router from "next/router";
import { useContext, useState } from "react";
import { isMobile, isTablet } from "react-device-detect";
import DynamicFormModal from "@/components/dynamicForm";
import CWFActivitiesAndTask from "@/components/dynamicForm/ActivitiesAndTaskComponents/CWFActivitiesAndTask";
import PhotoForm from "@/components/dynamicForm/AttachmentComponents/Photos/PhotoUploaderForm";
import { DataDisplayModal } from "@/components/dynamicForm/dataDisplay";
import CWFHazardsAndControls from "@/components/dynamicForm/HazardAndControlsComponents/CWFHazardsAndControls";
import CWFLocation from "@/components/dynamicForm/LocationComponent/CWFLocation";
import CWFNearestHospital from "@/components/dynamicForm/NearestHospitalComponents/CWFNearestHospitalComponent";
import PersonnelComponent from "@/components/dynamicForm/PersonnelComponent/PersonnelComponent";
import PersonnelSettings from "@/components/dynamicForm/PersonnelComponent/PersonnelSettings";
import CWFSiteConditions from "@/components/dynamicForm/SiteConditionsComponent/CWFSiteConditions";
import CWFSummary from "@/components/dynamicForm/SummaryComponent/CWFSummary";
import IncludeInSummaryToggle from "@/components/dynamicForm/SummaryComponent/IncludeInSummaryToggle";
import { SummaryTextedBlankField } from "@/components/dynamicForm/SummaryComponent/utils";
import ButtonDanger from "@/components/shared/button/danger/ButtonDanger";
import ButtonRegular from "@/components/shared/button/regular/ButtonRegular";
import Modal from "@/components/shared/modal/Modal";
import ToastContext from "@/components/shared/toast/context/ToastContext";
import style from "@/components/templatesComponents/CreateTemplateLayout/createTemplateStyle.module.scss";
import {
  CWFItemType,
  UserFormModeTypes,
} from "@/components/templatesComponents/customisedForm.types";
import { FormRendererProvider } from "@/components/templatesComponents/FormPreview/Components/FormRendererContext";
import FieldRenderer from "@/components/templatesComponents/PreviewComponents";
import CustomisedFromStateContext, {
  useWidgetCount,
} from "@/context/CustomisedDataContext/CustomisedFormStateContext";
import { CF_REDUCER_CONSTANTS } from "@/utils/customisedFormUtils/customisedForm.constants";
import LocationInSummary from "@/components/dynamicForm/LocationComponent/LocationInSummary";
import ImageGallery from "@/components/dynamicForm/AttachmentComponents/Photos/ImageGallery";
import { convertToPhotoUploadItem } from "@/components/dynamicForm/AttachmentComponents/Photos/utils";
import EditTitlePopUp from "../../../../dynamicForm/EditTitlePopUp/EditTitlePopUp";
import Button from "../../../../shared/button/Button";
import FormSection from "./FormComponents/Section/FormSection";

export const formGenerator = (
  item: PageType | FormElementsType | FormComponentPayloadType,
  activePageDetails: ActivePageObjType,
  activeWidgetDetails: WidgetType,
  mode: UserFormMode,
  options: {
    previousContent: any;
    nextContent: any;
  },
  projectDetails?: ProjectDetailsType,
  pageLevelIncludeInSummaryToggle?: boolean,
  setActiveWidgetDetails?: (item: WidgetType) => void,
  section?: any,
  isRepeatableSection?: boolean,
  formObject?: FormType,
  setActivePageDetails?: (item: ActivePageObjType) => void,
  inSummary = false
) => {
  const { previousContent, nextContent } = options;
  const { title, include_in_summary } = item.properties;

  const showTextedBlankFieldForSummary = (
    form: FormType | undefined
  ): boolean => {
    if (!form) return false;

    return !form.contents.some((pageContent: PageType) =>
      pageContent.contents.some((content: any) => {
        if (
          content.type !== CWFItemType.Section &&
          (!content.contents || content.contents.length === 0) &&
          content.properties?.include_in_summary === true
        ) {
          return true;
        }

        return (
          content.contents?.some(
            (subContent: any) =>
              subContent.properties?.include_in_summary === true
          ) ?? false
        );
      })
    );
  };

  switch (item.type) {
    case CWFItemType.Section:
      return (
        <>
          {(mode === UserFormModeTypes.PREVIEW ||
            mode === UserFormModeTypes.PREVIEW_PROPS) &&
            router.pathname.includes("/templates") && (
              <div className="flex justify-start pl-3">
                <IncludeInSummaryToggle
                  includeSectionInSummaryToggle={
                    include_in_summary ?? pageLevelIncludeInSummaryToggle
                  }
                  mode={mode}
                  item={item}
                />
              </div>
            )}
          <FormSection
            key={item.id}
            id={item.id}
            type={item.type}
            order={item.order}
            item={item}
            previousContent={previousContent}
            nextContent={nextContent}
            contents={orderBy(item.contents, o => o.order, "asc")}
            properties={item.properties}
            activePageDetails={activePageDetails}
            activeWidgetDetails={activeWidgetDetails}
            setActiveWidgetDetails={setActiveWidgetDetails}
            mode={mode}
            formObject={formObject}
            pageLevelIncludeInSummaryToggle={pageLevelIncludeInSummaryToggle}
            projectDetails={projectDetails}
          />
        </>
      );
    // Removing this for now
    // case "sub_page":
    //   return <FormSubPage item={item as PageType} />;

    case CWFItemType.Choice:
    case CWFItemType.Dropdown:
    case CWFItemType.Contractor:
    case CWFItemType.Region:
    case CWFItemType.InputPhoneNumber:
    case CWFItemType.YesOrNo:
    case CWFItemType.InputText:
    case CWFItemType.Slide:
    case CWFItemType.InputDateTime:
    case CWFItemType.ReportDate:
    case CWFItemType.InputNumber:
    case CWFItemType.InputLocation:
    case CWFItemType.InputEmail:
    case CWFItemType.Checkbox:
      return (
        <EditField
          key={item.id}
          item={item}
          content={item}
          section={section}
          activePageDetails={activePageDetails}
          mode={mode}
          options={options}
          isRepeatableSection={isRepeatableSection}
          formObject={formObject}
          pageLevelIncludeInSummaryToggle={pageLevelIncludeInSummaryToggle}
          inSummary={inSummary}
        >
          <FieldRenderer
            content={item}
            order={item.order}
            activePageDetails={activePageDetails}
            section={section}
            mode={mode}
            inSummary={inSummary}
          />
        </EditField>
      );
    case CWFItemType.RichTextEditor:
      return (
        <EditField
          item={item}
          content={item}
          section={section}
          activePageDetails={activePageDetails}
          mode={mode}
          options={options}
          formObject={formObject}
          pageLevelIncludeInSummaryToggle={pageLevelIncludeInSummaryToggle}
          inSummary={inSummary}
        >
          <DataField mode={mode} {...{ ...item.properties }} />
        </EditField>
      );

    case CWFItemType.Attachment:
      return (
        <EditField
          item={item as FormComponentPayloadType}
          content={item}
          section={section}
          activePageDetails={activePageDetails}
          mode={mode}
          options={options}
          formObject={formObject}
          pageLevelIncludeInSummaryToggle={pageLevelIncludeInSummaryToggle}
          inSummary={inSummary}
        >
          {inSummary && item.properties.attachment_type === "photo" ? (
            <ImageGallery
              photos={convertToPhotoUploadItem(item.properties.user_value)}
              title={item.properties.title}
              inSummary={inSummary}
            />
          ) : (
            <PhotoForm
              section={section}
              activePageDetails={activePageDetails}
              mode={mode}
              item={item as FormComponentPayloadType}
            />
          )}
        </EditField>
      );

    case CWFItemType.HazardsAndControls:
      return (
        <EditField
          item={item as HazardsAndControlsFormType}
          content={item}
          section={section}
          activePageDetails={activePageDetails}
          mode={mode}
          options={options}
          formObject={formObject}
          pageLevelIncludeInSummaryToggle={pageLevelIncludeInSummaryToggle}
          inSummary={inSummary}
        >
          <CWFHazardsAndControls
            section={section}
            activePageDetails={activePageDetails}
            mode={mode}
            item={item as HazardsAndControlsFormType}
            inSummary={inSummary}
          />
        </EditField>
      );

    case CWFItemType.ActivitiesAndTasks:
      return (
        <EditField
          item={item as ActivitiesAndTasksFormType}
          content={item}
          section={section}
          activePageDetails={activePageDetails}
          mode={mode}
          options={options}
          formObject={formObject}
          pageLevelIncludeInSummaryToggle={pageLevelIncludeInSummaryToggle}
          inSummary={inSummary}
        >
          <CWFActivitiesAndTask
            section={section}
            activePageDetails={activePageDetails}
            mode={mode}
            item={item as ActivitiesAndTasksFormType}
            inSummary={inSummary}
          />
        </EditField>
      );

    case CWFItemType.SiteConditions:
      return (
        <EditField
          item={item as CWFSiteConditionsType}
          content={item}
          section={section}
          activePageDetails={activePageDetails}
          mode={mode}
          options={options}
          formObject={formObject}
          pageLevelIncludeInSummaryToggle={pageLevelIncludeInSummaryToggle}
          inSummary={inSummary}
        >
          <CWFSiteConditions
            item={item as CWFSiteConditionsType}
            mode={mode}
            section={section}
            activePageDetails={activePageDetails}
            inSummary={inSummary}
          />
        </EditField>
      );

    case CWFItemType.Location:
      return inSummary ? (
        <LocationInSummary item={item as CWFLocationType} type={item.type} />
      ) : (
        <EditField
          item={item as CWFLocationType}
          content={item}
          section={section}
          activePageDetails={activePageDetails}
          mode={mode}
          options={options}
          formObject={formObject}
          pageLevelIncludeInSummaryToggle={pageLevelIncludeInSummaryToggle}
          inSummary={inSummary}
        >
          <CWFLocation
            item={item as CWFLocationType}
            mode={mode}
            section={section}
            activePageDetails={activePageDetails}
            projectDetails={projectDetails}
            inSummary={inSummary}
          />
        </EditField>
      );

    case CWFItemType.NearestHospital:
      return (
        <EditField
          item={item as CWFNearestHospitalType}
          content={item}
          section={section}
          activePageDetails={activePageDetails}
          mode={mode}
          options={options}
          formObject={formObject}
          pageLevelIncludeInSummaryToggle={pageLevelIncludeInSummaryToggle}
          inSummary={inSummary}
        >
          <CWFNearestHospital
            item={item as CWFNearestHospitalType}
            mode={mode}
            section={section}
            activePageDetails={activePageDetails}
            inSummary={inSummary}
          />
        </EditField>
      );

    case CWFItemType.Summary:
      return (
        <EditField
          item={item as CWFSummaryType}
          content={item}
          section={section}
          activePageDetails={activePageDetails}
          mode={mode}
          options={options}
          formObject={formObject}
          pageLevelIncludeInSummaryToggle={pageLevelIncludeInSummaryToggle}
          inSummary={inSummary}
        >
          {!formObject || !activePageDetails ? (
            <div className="flex justify-between flex-col gap-4">
              <SectionHeading className="text-xl text-neutral-shade-100 font-semibold">
                {title ?? "Summary"}
              </SectionHeading>
              <SummaryTextedBlankField />
            </div>
          ) : (
            <FormRendererProvider
              formObject={formObject}
              activePageDetails={activePageDetails}
              setActivePageDetails={
                setActivePageDetails ?? ((_: ActivePageObjType) => void 0)
              }
              mode={mode}
              hazardsData={[]}
              tasksHazardData={[]}
              isLoading={false}
              librarySiteConditionsData={undefined}
              librarySiteConditionsLoading={false}
            >
              <CWFSummary
                item={item as CWFSummaryType}
                showTextedBlankFieldForSummary={showTextedBlankFieldForSummary(
                  formObject
                )}
                activePageDetails={activePageDetails}
                mode={mode}
              />
            </FormRendererProvider>
          )}
        </EditField>
      );
    case CWFItemType.PersonnelComponent:
      return (
        <EditField
          item={item as PersonnelComponentType}
          content={item}
          section={section}
          activePageDetails={activePageDetails}
          mode={mode}
          options={options}
          formObject={formObject}
          pageLevelIncludeInSummaryToggle={pageLevelIncludeInSummaryToggle}
          inSummary={inSummary}
        >
          <PersonnelComponent
            item={item as PersonnelComponentType}
            mode={mode}
            inSummary={inSummary}
          />
        </EditField>
      );

    default:
      return null;
  }
};

const DataField = (props: any) => {
  const { data, mode } = props;
  return (
    <div
      className={`list-disc ${
        mode === UserFormModeTypes.BUILD ? "pointer-events-none" : ""
      }`}
    >
      {parse(data)}
    </div>
  );
};

type EditFieldProps = {
  children: JSX.Element;
  item: PageType | FormElementsType | FormComponentPayloadType;
  activePageDetails: ActivePageObjType;
  content: any;
  section?: any;
  mode: UserFormMode;
  options: {
    previousContent: any;
    nextContent: any;
  };
  isRepeatableSection?: boolean;
  formObject: FormType | undefined;
  pageLevelIncludeInSummaryToggle?: boolean;
  inSummary?: boolean;
};
const EditField = (props: EditFieldProps) => {
  const [isHovered, setIsHovered] = useState(false);
  const [isQuestionOpen, setIsQuestionOpen] = useState<boolean>(false);
  const [isDataOpen, setIsDataOpen] = useState<boolean>(false);
  const [isDeleteOpen, setIsDeleteOpen] = useState<boolean>(false);
  const { state, dispatch } = useContext(CustomisedFromStateContext)!;
  const { decrementWidgetCount } = useWidgetCount();
  const [previewOpen, setPreviewOpen] = useState<boolean>(false);
  const [isEditModalOpen, setIsEditModalOpen] = useState(false);
  const isMobileOrTablet = () => isMobile || isTablet;
  const toastCtx = useContext(ToastContext);
  const { include_in_summary, attachment_type, title, sub_title } =
    props.item.properties;
  const isPhoto = attachment_type;
  const attachmentTypeCheck = attachment_type;

  const initialTitle = title || "";
  const [componentTitle, setComponentTitle] = useState(initialTitle);
  const [subTitle, setSubTitle] = useState(sub_title || "High Energy Hazards");
  const [isEnergyWheelEnabled, setIsEnergyWheelEnabled] = useState<boolean>(
    state.form.metadata?.is_energy_wheel_enabled ?? true
  );
  const [isSmartAddressChecked, setIsSmartAddressChecked] = useState(true);
  const [isHistoricalIncidentEnabled, setIsHistoricalIncidentEnabled] =
    useState<boolean>(
      props.item.properties?.historical_incident?.label ? true : false
    );
  const [historicalIncidentLabel, setHistoricalIncidentLabel] =
    useState<string>(props.item.properties?.historical_incident?.label || "");

  const [includeSectionInSummaryToggle, setIncludeSectionInSummaryToggle] =
    useState(
      include_in_summary
        ? include_in_summary
        : props.pageLevelIncludeInSummaryToggle ?? false
    );

  const moveDown = () => {
    if (!props.options.nextContent) {
      return;
    }

    const thisIndex = props.item.order;
    const upperIndex = props.options.nextContent.order;
    const upperUpIndex = 999999;

    const nextContent = JSON.parse(JSON.stringify(props.options.nextContent));
    const currentContent = JSON.parse(JSON.stringify(props.item));

    // First move the upper index to upperUp index
    dispatch({
      type: CF_REDUCER_CONSTANTS.EDIT_FIELD,
      payload: {
        parentData: props.activePageDetails!,
        fieldData: {
          ...nextContent,
          order: upperIndex,
        },
        section: props.section,
        newOrder: upperUpIndex,
      },
    });
    // Then move the current index to upper index
    dispatch({
      type: CF_REDUCER_CONSTANTS.EDIT_FIELD,
      payload: {
        parentData: props.activePageDetails!,
        fieldData: {
          ...currentContent,
          order: thisIndex,
        },
        section: props.section,
        newOrder: upperIndex,
      },
    });
    // Then move the upperUp index to current index
    dispatch({
      type: CF_REDUCER_CONSTANTS.EDIT_FIELD,
      payload: {
        parentData: props.activePageDetails!,
        fieldData: {
          ...nextContent,
          order: upperUpIndex,
        },
        section: props.section,
        newOrder: thisIndex,
      },
    });
  };

  const moveUp = () => {
    if (!props.options.previousContent) {
      return;
    }

    const thisIndex = props.item.order;
    const upperIndex = props.options.previousContent.order;
    const upperUpIndex = 999999;

    const previousContent = JSON.parse(
      JSON.stringify(props.options.previousContent)
    );
    const currentContent = JSON.parse(JSON.stringify(props.item));

    // First move the upper index to upperUp index
    dispatch({
      type: CF_REDUCER_CONSTANTS.EDIT_FIELD,
      payload: {
        parentData: props.activePageDetails!,
        fieldData: {
          ...previousContent,
          order: upperIndex,
        },
        section: props.section,
        newOrder: upperUpIndex,
      },
    });
    // Then move the current index to upper index
    dispatch({
      type: CF_REDUCER_CONSTANTS.EDIT_FIELD,
      payload: {
        parentData: props.activePageDetails!,
        fieldData: {
          ...currentContent,
          order: thisIndex,
        },
        section: props.section,
        newOrder: upperIndex,
      },
    });
    // Then move the upperUp index to current index
    dispatch({
      type: CF_REDUCER_CONSTANTS.EDIT_FIELD,
      payload: {
        parentData: props.activePageDetails!,
        fieldData: {
          ...previousContent,
          order: upperUpIndex,
        },
        section: props.section,
        newOrder: thisIndex,
      },
    });
  };

  const actions =
    props.mode === UserFormModeTypes.PREVIEW_PROPS
      ? props.item.type === CWFItemType.Attachment ||
        props.item.type === CWFItemType.HazardsAndControls ||
        props.item.type === CWFItemType.ActivitiesAndTasks ||
        props.item.type === CWFItemType.Summary ||
        props.item.type === CWFItemType.SiteConditions ||
        props.item.type === CWFItemType.Location ||
        props.item.type === CWFItemType.NearestHospital ||
        props.item.type === CWFItemType.PersonnelComponent
        ? null
        : [
            {
              id: "preview",
              icon: "ci-show",
              displayName: "Preview",
            },
          ]
      : [
          {
            id: "move-up",
            icon: "ci-chevron_big_up",
            displayName: "Move up",
          },
          {
            id: "move-down",
            icon: "ci-chevron_big_down",
            displayName: "Move down",
          },
          {
            id: "edit",
            icon: "ci-edit",
            displayName: "Edit Section",
          },
          {
            id: "delete",
            icon: "ci-trash_empty",
            displayName: "Delete",
          },
        ];

  const editChangesAction = (itemType: string) => {
    switch (itemType) {
      case CWFItemType.RichTextEditor:
        setIsDataOpen(true);
        break;
      case CWFItemType.Attachment:
        setIsEditModalOpen(true);
        break;
      case CWFItemType.ActivitiesAndTasks:
        setIsEditModalOpen(true);
        break;
      case CWFItemType.HazardsAndControls:
        setIsEditModalOpen(true);
        break;
      case CWFItemType.Summary:
        setIsEditModalOpen(true);
        break;
      case CWFItemType.SiteConditions:
        setIsEditModalOpen(true);
        break;
      case CWFItemType.Location:
        setIsEditModalOpen(true);
        break;
      case CWFItemType.NearestHospital:
        setIsEditModalOpen(true);
        break;
      case CWFItemType.PersonnelComponent:
        setIsEditModalOpen(true);
        break;
      default:
        setIsQuestionOpen(true);
    }
  };

  const onSaveTitle = (componentType: string) => {
    const getTitle = () => {
      switch (componentType) {
        case CWFItemType.Attachment:
          return attachment_type && attachment_type === "photo"
            ? "Photo"
            : "Document";
        case CWFItemType.ActivitiesAndTasks:
          return "Activities and Tasks";
        case CWFItemType.HazardsAndControls:
          return "Hazards and Controls";
        case CWFItemType.Summary:
          return "Summary";
        case CWFItemType.SiteConditions:
          return "Site Conditions";
        case CWFItemType.Location:
          return "Location";
        case CWFItemType.NearestHospital:
          return "Nearest Hospital";
        default:
          return "Component";
      }
    };
    const titleText = getTitle();
    const updatedItem = {
      ...props.item,
      properties: {
        ...props.item.properties,
        title: componentTitle,
        ...(props.item?.type === "hazards_and_controls"
          ? {
              sub_title: subTitle,
            }
          : {}),
        ...(props.item?.type === "summary"
          ? {
              historical_incident: isHistoricalIncidentEnabled
                ? {
                    label: historicalIncidentLabel,
                  }
                : null,
              // Automatically set include_in_summary to true when historical incident is enabled and has a label
              include_in_summary:
                isHistoricalIncidentEnabled && historicalIncidentLabel
                  ? true
                  : props.item.properties.include_in_summary,
            }
          : {}),
      },
    };
    if (props.item?.type === "hazards_and_controls") {
      dispatch({
        type: CF_REDUCER_CONSTANTS.CHANGE_INITIAL_STATE,
        payload: {
          ...state.form,
          metadata: {
            ...state.form.metadata,
            is_energy_wheel_enabled: isEnergyWheelEnabled,
          },
        },
      });
    }
    dispatch({
      type: CF_REDUCER_CONSTANTS.EDIT_FIELD,
      payload: {
        parentData: props.activePageDetails!,
        fieldData: updatedItem,
        section: props.section,
      },
    });
    toastCtx?.pushToast(
      "success",
      `${titleText} title updated! Please click on Save/Update button to save the changes`
    );
    setIsEditModalOpen(false);
  };

  const onUpdateAdditionalField = (componentType: string) => {
    switch (componentType) {
      case CWFItemType.Location:
        const updatedItem = {
          ...props.item,
          properties: {
            ...props.item.properties,
            smart_address: isSmartAddressChecked,
          },
        };
        dispatch({
          type: CF_REDUCER_CONSTANTS.EDIT_FIELD,
          payload: {
            parentData: props.activePageDetails!,
            fieldData: updatedItem,
            section: props.section,
          },
        });
        break;
      default:
        break;
    }
  };

  const onClickOfAction = (action: string) => {
    switch (action) {
      case "edit":
        editChangesAction(props.item.type);
        break;
      case "preview":
        setPreviewOpen(true);
        break;
      case "delete":
        setIsDeleteOpen(true);
        break;
      case "move-up": {
        if (!props.options.previousContent) {
          return;
        }
        moveUp();
        break;
      }
      case "move-down": {
        if (!props.options.nextContent) {
          return;
        }
        moveDown();
        break;
      }
    }
  };
  const editContent = (content: any) => {
    dispatch({
      type: CF_REDUCER_CONSTANTS.EDIT_FIELD,
      payload: {
        parentData: props.activePageDetails!,
        fieldData: { ...content, order: props.item.order },
        section: props.section,
      },
    });
  };

  const onDeleteField = () => {
    if (props.item.properties?.include_in_widget) {
      decrementWidgetCount();
    }
    switch (props.item.type) {
      case CWFItemType.ReportDate:
        dispatch({
          type: CF_REDUCER_CONSTANTS.UPDATE_METADATA,
          payload: {
            ...state.form.metadata,
            is_report_date_included: false,
          },
        });
        break;
      case CWFItemType.Contractor:
        dispatch({
          type: CF_REDUCER_CONSTANTS.UPDATE_METADATA,
          payload: {
            ...state.form.metadata,
            is_contractor_included: false,
          },
        });
        break;
      case CWFItemType.Region:
        dispatch({
          type: CF_REDUCER_CONSTANTS.UPDATE_METADATA,
          payload: {
            ...state.form.metadata,
            is_region_included: false,
          },
        });
        break;
      case CWFItemType.ActivitiesAndTasks:
        dispatch({
          type: CF_REDUCER_CONSTANTS.CHANGE_INITIAL_STATE,
          payload: {
            ...state.form,
            metadata: {
              ...state.form.metadata,
              is_activities_and_tasks_included: false,
            },
          },
        });
        break;
      case CWFItemType.HazardsAndControls:
        dispatch({
          type: CF_REDUCER_CONSTANTS.CHANGE_INITIAL_STATE,
          payload: {
            ...state.form,
            metadata: {
              ...state.form.metadata,
              is_hazards_and_controls_included: false,
            },
          },
        });
        break;
      case CWFItemType.Summary:
        dispatch({
          type: CF_REDUCER_CONSTANTS.CHANGE_INITIAL_STATE,
          payload: {
            ...state.form,
            metadata: {
              ...state.form.metadata,
              is_summary_included: false,
            },
          },
        });
        break;
      case CWFItemType.SiteConditions:
        dispatch({
          type: CF_REDUCER_CONSTANTS.CHANGE_INITIAL_STATE,
          payload: {
            ...state.form,
            metadata: {
              ...state.form.metadata,
              is_site_conditions_included: false,
            },
          },
        });
        break;
      case CWFItemType.Location:
        dispatch({
          type: CF_REDUCER_CONSTANTS.CHANGE_INITIAL_STATE,
          payload: {
            ...state.form,
            metadata: {
              ...state.form.metadata,
              is_location_included: false,
            },
          },
        });
        break;
      case CWFItemType.NearestHospital:
        dispatch({
          type: CF_REDUCER_CONSTANTS.CHANGE_INITIAL_STATE,
          payload: {
            ...state.form,
            metadata: {
              ...state.form.metadata,
              is_nearest_hospital_included: false,
            },
          },
        });
        break;
    }
    setIsDeleteOpen(false);
    dispatch({
      type: CF_REDUCER_CONSTANTS.DELETE_FIELD,
      payload: {
        parentData: props.activePageDetails!,
        fieldData: { order: props.item.order },
        section: props.section,
      },
    });
  };

  const handleDeleteComponent = () => {
    const componentType = props?.item?.type;
    switch (componentType) {
      case CWFItemType.Attachment:
        toastCtx?.pushToast(
          "success",
          `${
            attachmentTypeCheck === "photo" ? "Photo" : "Document"
          } component deleted. Please click on Publish button to save the changes.`
        );
        break;
      case CWFItemType.ActivitiesAndTasks:
        toastCtx?.pushToast(
          "success",
          `Activities and Tasks component deleted. Please click on Publish button to save the changes.`
        );
        break;
      case CWFItemType.HazardsAndControls:
        toastCtx?.pushToast(
          "success",
          `Hazards and Controls component deleted. Please click on Publish button to save the changes.`
        );
        break;
      case CWFItemType.Summary:
        toastCtx?.pushToast(
          "success",
          `Summary component deleted. Please click on Publish button to save the changes.`
        );
        break;
      case CWFItemType.SiteConditions:
        toastCtx?.pushToast(
          "success",
          `Site Conditions component deleted. Please click on Publish button to save the changes.`
        );
        break;

      case CWFItemType.Location:
        toastCtx?.pushToast(
          "success",
          `Location component deleted. Please click on Publish button to save the changes.`
        );
        break;
      case CWFItemType.NearestHospital:
        toastCtx?.pushToast(
          "success",
          `Nearest Hospital component deleted. Please click on Publish button to save the changes.`
        );
        break;
      default:
        toastCtx?.pushToast(
          "success",
          `Component deleted. Please click on Publish button to save the changes.`
        );
        break;
    }
    onDeleteField();
  };

  const handleSummaryToggle = () => {
    const currentIncludeInSummary = !(
      include_in_summary ?? includeSectionInSummaryToggle
    );
    setIncludeSectionInSummaryToggle(currentIncludeInSummary);

    const updatedItem = {
      ...props.item,
      properties: {
        ...props.item.properties,
        include_in_summary: currentIncludeInSummary,
      },
    };

    if (props.item.type === CWFItemType.Section && props.item.contents) {
      const updatedContents = props.item.contents.map(child => ({
        ...child,
        properties: {
          ...child.properties,
          include_in_summary: currentIncludeInSummary,
        },
      }));
      updatedItem.contents = updatedContents;
    }

    dispatch({
      type: CF_REDUCER_CONSTANTS.EDIT_FIELD,
      payload: {
        parentData: props.activePageDetails,
        fieldData: updatedItem,
        section: props.section,
      },
    });

    toastCtx?.pushToast(
      "success",
      `Component ${
        include_in_summary ?? includeSectionInSummaryToggle
          ? "will not"
          : "will"
      } be included in summary. Please click on Publish button to save the changes.`
    );
  };

  const showAddToSummaryToggle = () => {
    if (props.item.type !== CWFItemType.Summary) {
      if (
        props.mode === UserFormModeTypes.PREVIEW &&
        router.pathname.includes("/templates/create")
      ) {
        return true;
      }
    }
    return false;
  };

  return (
    <>
      <section
        className={`flex flex-col relative border border-transparent border-solid ${
          props.inSummary ? "" : "p-2"
        } ${
          isHovered &&
          (props.mode === UserFormModeTypes.BUILD ||
            props.mode === UserFormModeTypes.PREVIEW_PROPS)
            ? "hover:border-brand-urbint-40"
            : ""
        }`}
        onMouseEnter={() => {
          (props.mode === UserFormModeTypes.BUILD ||
            props.mode === UserFormModeTypes.PREVIEW_PROPS) &&
            setIsHovered(true);
        }}
        onMouseLeave={() =>
          (props.mode === UserFormModeTypes.BUILD ||
            props.mode === UserFormModeTypes.PREVIEW_PROPS) &&
          setIsHovered(false)
        }
        onClick={() =>
          (props.mode === UserFormModeTypes.BUILD ||
            props.mode === UserFormModeTypes.PREVIEW_PROPS) &&
          isMobileOrTablet() &&
          setIsHovered(!isHovered)
        }
      >
        {isHovered &&
          (props.mode === UserFormModeTypes.BUILD ||
            props.mode === UserFormModeTypes.PREVIEW_PROPS) && (
            <div className="flex flex-row gap-2">
              <div
                className={`${style.sectionDetailsActionIcon} flex flex-row`}
              >
                {actions &&
                  actions.map(action => (
                    <Button
                      className="text-xl text-neutral-shade-75  hover:text-brand-urbint-40"
                      key={action.id}
                    >
                      <i
                        className={action?.icon}
                        onClick={() => onClickOfAction(action.id)}
                        aria-hidden="true"
                        title={action.displayName}
                      ></i>
                    </Button>
                  ))}
              </div>
              {props.item.type !== CWFItemType.Summary && (
                <IncludeInSummaryToggle
                  includeSectionInSummaryToggle={include_in_summary ?? false}
                  handleToggle={
                    ![
                      UserFormModeTypes.PREVIEW_PROPS,
                      UserFormModeTypes.PREVIEW,
                    ].some(formMode => props.mode.includes(formMode)) &&
                    handleSummaryToggle
                  }
                  mode={props.mode}
                  item={props.item}
                />
              )}
            </div>
          )}

        {showAddToSummaryToggle() && (
          <div className="flex justify-start">
            <IncludeInSummaryToggle
              includeSectionInSummaryToggle={
                props.pageLevelIncludeInSummaryToggle
                  ? props.pageLevelIncludeInSummaryToggle
                  : include_in_summary ?? includeSectionInSummaryToggle
              }
              mode={props.mode}
              item={props.item}
            />
          </div>
        )}

        {isEditModalOpen && (
          <>
            {props.item.type === CWFItemType.PersonnelComponent ? (
              <PersonnelSettings
                item={props.item as PersonnelComponentType}
                onClose={() => setIsEditModalOpen(false)}
                onSave={(component: PersonnelComponentType) => {
                  dispatch({
                    type: CF_REDUCER_CONSTANTS.EDIT_FIELD,
                    payload: {
                      parentData: props.activePageDetails,
                      fieldData: {
                        ...props.item,
                        properties: component.properties,
                      },
                      section: props.section,
                    },
                  });
                  setIsEditModalOpen(false);
                }}
              />
            ) : (
              <EditTitlePopUp
                isEditModalOpen={isEditModalOpen}
                setIsEditModalOpen={setIsEditModalOpen}
                titleName={componentTitle}
                setTitleName={setComponentTitle}
                onSaveTitle={onSaveTitle}
                onUpdateAdditionalField={onUpdateAdditionalField}
                isSmartAddressChecked={isSmartAddressChecked}
                setIsSmartAddressChecked={setIsSmartAddressChecked}
                item={props.item as EditComponentType}
                subTitle={subTitle}
                setSubTitle={setSubTitle}
                isEnergyWheelEnabled={isEnergyWheelEnabled}
                setIsEnergyWheelEnabled={setIsEnergyWheelEnabled}
                isHistoricalIncidentEnabled={isHistoricalIncidentEnabled}
                setIsHistoricalIncidentEnabled={setIsHistoricalIncidentEnabled}
                historicalIncidentLabel={historicalIncidentLabel}
                setHistoricalIncidentLabel={setHistoricalIncidentLabel}
              />
            )}
          </>
        )}

        {props.children}
      </section>
      <Modal
        title={isPhoto === "photo" ? "Edit Field" : "Delete component"}
        isOpen={isDeleteOpen}
        closeModal={() => setIsDeleteOpen(false)}
        size={"md"}
      >
        <div>
          <CaptionText className="text-base">
            Are you sure you want to permanently delete this component ? This
            action cannot be undone.
          </CaptionText>
          <div className="flex self-end w-full pt-4 flex-row-reverse m-t-4 border-t-2 border-solid mt-16">
            <ButtonDanger label={"Delete"} onClick={handleDeleteComponent} />
            <ButtonRegular
              className="mr-2"
              label="Cancel"
              onClick={() => setIsDeleteOpen(false)}
            />
          </div>
        </div>
      </Modal>
      <DynamicFormModal
        isOpen={isQuestionOpen}
        mode={UserFormModeTypes.EDIT}
        content={props.content}
        onClose={() => setIsQuestionOpen(false)}
        onAdd={content => {
          editContent(content);
          setIsQuestionOpen(false);
        }}
        isRepeatableSection={props.isRepeatableSection}
      />
      <DynamicFormModal
        isOpen={previewOpen}
        mode={UserFormModeTypes.PREVIEW}
        content={props.content}
        onClose={() => setPreviewOpen(false)}
        onAdd={() => {
          setIsQuestionOpen(false);
        }}
        isRepeatableSection={props.isRepeatableSection}
      />
      <DataDisplayModal
        isOpen={isDataOpen}
        onClose={() => setIsDataOpen(false)}
        content={props.content}
        onAdd={content => {
          editContent(content);
          setIsDataOpen(false);
        }}
      />
    </>
  );
};
