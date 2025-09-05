import type {
  ActivePageObjType,
  FormElementsType,
  FormType,
  PageType,
  ProjectDetailsType,
  UserFormMode,
  WidgetType,
} from "@/components/templatesComponents/customisedForm.types";
import { Icon, SectionHeading } from "@urbint/silica";
import { useContext, useEffect, useState, useRef } from "react";
import { isMobile, isTablet } from "react-device-detect";
import { v4 as uuidv4 } from "uuid";
import {
  CWFItemType,
  UserFormModeTypes,
} from "@/components/templatesComponents/customisedForm.types";
import DynamicFormModal from "@/components/dynamicForm";
import ButtonDanger from "@/components/shared/button/danger/ButtonDanger";
import ButtonRegular from "@/components/shared/button/regular/ButtonRegular";
import ButtonSecondary from "@/components/shared/button/secondary/ButtonSecondary";
import Modal from "@/components/shared/modal/Modal";
import ToastContext from "@/components/shared/toast/context/ToastContext";
import { formGenerator } from "@/components/templatesComponents/CreateTemplateLayout/PreviewComponent/FormRenderer/formGenerator";
import CustomisedFromStateContext from "@/context/CustomisedDataContext/CustomisedFormStateContext";
import { DataDisplayModal } from "@/components/dynamicForm/dataDisplay";
import {
  CF_REDUCER_CONSTANTS,
  HIDDEN_COMPONENTS_FOR_REPEATABLE,
} from "@/utils/customisedFormUtils/customisedForm.constants";
import FormComponentsPopUp from "@/components/templatesComponents/FormComponents/FormComponentsPopUp";
import IncludeInSummaryToggle from "@/components/dynamicForm/SummaryComponent/IncludeInSummaryToggle";
import style from "../../../../createTemplateStyle.module.scss";
import PreviewCTASectionComponent from "../../../PreviewCTASectionComponent";
import AddSectionComponent from "../../../AddSection";

type FormSectionProps = {
  id: string;
  type: string;
  order: number;
  item: PageType | FormElementsType;
  previousContent: any;
  nextContent: any;
  properties: any;
  contents: any[];
  activePageDetails: ActivePageObjType;
  activeWidgetDetails: WidgetType;
  setActiveWidgetDetails?: (item: WidgetType) => void;
  mode: UserFormMode;
  formObject?: FormType;
  pageLevelIncludeInSummaryToggle?: boolean;
  inSummary?: boolean;
  projectDetails?: ProjectDetailsType;
};

type ActionType = {
  id: string;
  icon: string;
  displayName: string;
};

const FormSection = ({
  id,
  type,
  order,
  item,
  previousContent,
  nextContent,
  contents,
  properties,
  activePageDetails,
  activeWidgetDetails,
  setActiveWidgetDetails,
  mode,
  formObject,
  pageLevelIncludeInSummaryToggle,
  projectDetails,
  inSummary = false,
}: FormSectionProps) => {
  const [isHovered, setIsHovered] = useState(false);
  const [isOpen, setIsOpen] = useState(false);
  const [isQuestionOpen, setIsQuestionOpen] = useState<boolean>(false);
  const [isDataOpen, setIsDataOpen] = useState<boolean>(false);
  const [isEditModalOpen, setIsEditModalOpen] = useState(false);
  const [sectionName, setSectionName] = useState("");
  const { state, dispatch } = useContext(CustomisedFromStateContext)!;
  const [isDeleteSectionOpen, setDeleteSectionOpen] = useState<boolean>(false);
  const toastCtx = useContext(ToastContext);
  const [isComponentsOpen, setIsComponentsOpen] = useState<boolean>(false);
  const { include_in_summary } = item.properties;
  const [includeSectionInSummaryToggle, setIncludeSectionInSummaryToggle] =
    useState(
      include_in_summary
        ? include_in_summary
        : pageLevelIncludeInSummaryToggle ?? false
    );
  const [deleteSection, setDeleteSection] = useState<boolean>(false);
  const [newlyAddedSectionId, setNewlyAddedSectionId] = useState<string | null>(
    null
  );
  const sectionRef = useRef<HTMLElement>(null);
  const isMobileOrTablet = () => isMobile || isTablet;

  const actions: ActionType[] = [
    {
      id: "move_up",
      icon: "ci-chevron_up",
      displayName: "Move Section Up",
    },
    {
      id: "move_down",
      icon: "ci-chevron_down",
      displayName: "Move Section Down",
    },
    {
      id: "add_component",
      icon: "ci-plus_square",
      displayName: "Add Component",
    },
    {
      id: "edit",
      icon: "ci-edit",
      displayName: "Edit Section",
    },
    {
      id: "delete_section",
      icon: "ci-trash_empty",
      displayName: "Delete Section",
    },
  ];

  useEffect(() => {
    if (
      activeWidgetDetails != null &&
      !isOpen &&
      !isQuestionOpen &&
      !isDataOpen &&
      setActiveWidgetDetails
    ) {
      setActiveWidgetDetails(null);
    }
  }, [isOpen, isQuestionOpen, isDataOpen]);

  const setQuestionModalOpen = () => {
    setIsOpen(false);
    setIsQuestionOpen(true);
  };

  const setDataModalOpen = () => {
    setIsOpen(false);
    setIsDataOpen(true);
  };

  const setComponentsModalOpen = () => {
    setIsOpen(false);
    setIsComponentsOpen(true);
  };

  const moveSectionUp = () => {
    // Section can only be a child of ActivePageType so null values should not even be coming this part of the code

    // TODO: Fix usage of ActivePageObjType in FormGenerator.tsx file...
    if (!previousContent || !activePageDetails) return;

    dispatch({
      type: CF_REDUCER_CONSTANTS.SWITCH_CONTENT_ORDERS,
      payload: {
        parent: activePageDetails,
        updatedContents: [
          { ...item, order: previousContent.order },
          { ...previousContent, order: item.order },
        ],
      },
    });
  };

  const moveSectionDown = () => {
    // Section can only be a child of ActivePageType so null values should not even be coming this part of the code

    // TODO: Fix usage of ActivePageObjType in FormGenerator.tsx file...
    if (!nextContent || !activePageDetails) return;

    dispatch({
      type: CF_REDUCER_CONSTANTS.SWITCH_CONTENT_ORDERS,
      payload: {
        parent: activePageDetails,
        updatedContents: [
          { ...item, order: nextContent.order },
          { ...nextContent, order: item.order },
        ],
      },
    });
  };

  const onClickOfAction = (action: string) => {
    switch (action) {
      case "edit":
        setSectionName(properties.title);
        setIsEditModalOpen(true);
        break;
      case "move_up":
        moveSectionUp();
        break;
      case "move_down":
        moveSectionDown();
        break;
      case "add_component":
        setIsOpen(true);
        if (setActiveWidgetDetails) {
          setActiveWidgetDetails({
            id: id,
            parentDetails: activePageDetails!,
          });
        }
        break;
      case "delete_section":
        setDeleteSectionOpen(true);
        break;
    }
  };

  const addContent = (value: any) => {
    // New components inside a section should inherit the section's include_in_summary state
    const shouldIncludeInSummary = properties.include_in_summary ?? false;

    const field = {
      order: contents.length + 1,
      ...value,
      properties: {
        ...value.properties,
        include_in_summary: shouldIncludeInSummary,
      },
    };
    dispatch({
      type: CF_REDUCER_CONSTANTS.ADD_SECTION_FIELD,
      payload: {
        parentData: activePageDetails,
        fieldData: field,
        section: {
          id: id,
          type,
          order,
          properties,
          contents,
        },
      },
    });
  };

  const checkAndUpdateMeta = (sectionDetails: any) => {
    if (!sectionDetails) return;

    let isHazardsAndControlsIncluded = false;
    let isActivitiesAndTasksIncluded = false;
    let isSummaryIncluded = false;
    let isSiteConditionsIncluded = false;
    let isLocationIncluded = false;
    let isNearestHospitalIncluded = false;
    let isRegionIncluded = false;
    let isContractorIncluded = false;
    let isReportDateIncluded = false;

    sectionDetails.forEach((content: any) => {
      if (content.type === CWFItemType.HazardsAndControls) {
        isHazardsAndControlsIncluded = true;
      }
      if (content.type === CWFItemType.ActivitiesAndTasks) {
        isActivitiesAndTasksIncluded = true;
      }
      if (content.type === CWFItemType.Summary) {
        isSummaryIncluded = true;
      }
      if (content.type === CWFItemType.SiteConditions) {
        isSiteConditionsIncluded = true;
      }
      if (content.type === CWFItemType.Location) {
        isLocationIncluded = true;
      }
      if (content.type === CWFItemType.NearestHospital) {
        isNearestHospitalIncluded = true;
      }
      if (content.type === CWFItemType.Region) {
        isRegionIncluded = true;
      }
      if (content.type === CWFItemType.Contractor) {
        isContractorIncluded = true;
      }
      if (content.type === CWFItemType.ReportDate) {
        isReportDateIncluded = true;
      }
    });

    const updatedMetadata = {
      ...state.form.metadata,
    };

    if (isHazardsAndControlsIncluded) {
      updatedMetadata.is_hazards_and_controls_included = false;
    }

    if (isActivitiesAndTasksIncluded) {
      updatedMetadata.is_activities_and_tasks_included = false;
    }

    if (isSummaryIncluded) {
      updatedMetadata.is_summary_included = false;
    }

    if (isSiteConditionsIncluded) {
      updatedMetadata.is_site_conditions_included = false;
    }

    if (isLocationIncluded) {
      updatedMetadata.is_location_included = false;
    }

    if (isNearestHospitalIncluded) {
      updatedMetadata.is_nearest_hospital_included = false;
    }
    if (isRegionIncluded) {
      updatedMetadata.is_region_included = false;
    }
    if (isContractorIncluded) {
      updatedMetadata.is_contractor_included = false;
    }
    if (isReportDateIncluded) {
      updatedMetadata.is_report_date_included = false;
    }

    dispatch({
      type: CF_REDUCER_CONSTANTS.CHANGE_INITIAL_STATE,
      payload: {
        ...state.form,
        metadata: updatedMetadata,
      },
    });
  };

  const onDeleteSection = () => {
    // Count all items in the section that have include_in_widget set to true
    const countWidgetItems = (sectionContents: any[]): number => {
      let count = 0;
      for (const content of sectionContents) {
        if (content.properties?.include_in_widget) {
          count++;
        }
        // Recursively check nested contents (for sections within sections)
        if (content.contents && Array.isArray(content.contents)) {
          count += countWidgetItems(content.contents);
        }
      }
      return count;
    };

    // Count widget items in this section before deletion
    const widgetItemsCount = countWidgetItems(contents);

    // Get current widget count
    const currentWidgetCount = state.form.settings?.widgets_added || 0;

    // Calculate new widget count after decrementing
    const newWidgetCount = Math.max(currentWidgetCount - widgetItemsCount, 0);

    const formContent = [...state.form.contents];
    let parentId = "";
    let subPageId = "";
    let pageContents = [];
    //Deleting Section from Parent Page
    if (activePageDetails?.type === CWFItemType.Page) {
      const activePage = formContent.find(
        (page: any) => page.id === activePageDetails?.id
      );
      if (activePage) {
        activePage.contents = activePage.contents.filter(
          (content: any) => content.id !== id
        );
        parentId = activePageDetails.id;
        pageContents = activePage.contents;
      }
      //Deleting Section from Sub Page
    } else if (activePageDetails?.type === CWFItemType.SubPage) {
      const activeParentPage = formContent.find(
        (page: any) => page.id === activePageDetails?.parentId
      );
      if (activeParentPage) {
        const subPageRecord = activeParentPage.contents.find(
          (subPage: any) => subPage.id === activePageDetails?.id
        );
        if (subPageRecord) {
          subPageRecord.contents = subPageRecord.contents.filter(
            (content: any) => content.id !== id
          );
          parentId = activePageDetails.parentId;
          subPageId = activePageDetails.id;
          pageContents = subPageRecord.contents;
        }
      }
    }
    checkAndUpdateMeta(contents);

    dispatch({
      type: CF_REDUCER_CONSTANTS.DELETE_SECTION,
      payload: { parentId, subPageId, pageContents },
    });

    // Then update widget count immediately after
    if (widgetItemsCount > 0) {
      console.log("UPDATE_WIDGET_SETTINGS dispatch");
      dispatch({
        type: CF_REDUCER_CONSTANTS.UPDATE_WIDGET_SETTINGS,
        payload: {
          widgets_added: newWidgetCount,
        },
      });
    }

    toastCtx?.pushToast("success", "Section deleted");
    setDeleteSectionOpen(false);
  };

  const makeSectionRepeatable = () => {
    const prePopulationRuleNames = contents.map(
      content => content.properties.pre_population_rule_name
    );
    const contentTypes = contents.map(content => content.type);

    // Check if pre population rule is applied exists in pre_population_rule_names
    const hasPrePopulationRule = prePopulationRuleNames.includes(
      "user_last_completed_form"
    );

    // Check if any content type exists in componentType array
    const hasMatchingComponentType = contentTypes.some(contentType =>
      HIDDEN_COMPONENTS_FOR_REPEATABLE.includes(contentType)
    );

    return hasPrePopulationRule || hasMatchingComponentType;
  };

  const handleSummaryToggle = () => {
    const currentIncludeInSummary = !(
      include_in_summary ?? includeSectionInSummaryToggle
    );
    setIncludeSectionInSummaryToggle(currentIncludeInSummary);

    const updatedItem = {
      ...item,
      properties: {
        ...item.properties,
        include_in_summary: currentIncludeInSummary,
      },
    };

    dispatch({
      type: CF_REDUCER_CONSTANTS.EDIT_FIELD,
      payload: {
        parentData: activePageDetails,
        fieldData: updatedItem,
      },
    });

    const updateAllNestedComponents = (
      component: FormElementsType,
      currentSection: FormElementsType | null = null
    ) => {
      const updatedComponent = {
        ...component,
        properties: {
          ...component.properties,
          include_in_summary: currentIncludeInSummary,
        },
      };
      dispatch({
        type: CF_REDUCER_CONSTANTS.EDIT_FIELD,
        payload: {
          parentData: activePageDetails,
          section: currentSection,
          fieldData: updatedComponent,
          newOrder: updatedComponent.order,
        },
      });
    };
    if (item.contents) {
      item.contents.forEach((content: FormElementsType) => {
        updateAllNestedComponents(content, item);
      });
    }
    toastCtx?.pushToast(
      "success",
      `Section ${
        include_in_summary ?? includeSectionInSummaryToggle
          ? "will not"
          : "will"
      } be included in summary. Please click on Publish button to save the changes.`
    );
  };

  const handleAddRepeatableSection = () => {
    const content = [...contents];
    content.map((contentItem: any) => {
      contentItem.properties.user_value = null;
      contentItem.properties.user_comments = null;
      contentItem.properties.user_attachments = null;
    });

    const newSectionId = uuidv4();
    setNewlyAddedSectionId(newSectionId);

    dispatch({
      type: CF_REDUCER_CONSTANTS.ADD_SECTION,
      payload: {
        parentData: activePageDetails,
        sectionData: {
          id: newSectionId,
          type: CWFItemType.Section,
          order: order,
          properties: {
            title: properties.title,
            is_repeatable: false,
            child_instance: true,
          },
          contents: content,
        },
      },
    });
  };

  const disableDeleteSection =
    mode === UserFormModeTypes.PREVIEW ||
    mode === UserFormModeTypes.PREVIEW_PROPS;
  useEffect(() => {
    // If all direct children in contents have include_in_summary true, set section toggle to true, else false
    if (
      Array.isArray(contents) &&
      contents.length > 0 &&
      mode === UserFormModeTypes.BUILD
    ) {
      const allIncluded = contents.every(
        (c: FormElementsType) => c.properties?.include_in_summary === true
      );
      if (includeSectionInSummaryToggle !== allIncluded) {
        setIncludeSectionInSummaryToggle(allIncluded);
        const updatedItem = {
          ...item,
          properties: {
            ...item.properties,
            include_in_summary: allIncluded,
          },
        };

        dispatch({
          type: CF_REDUCER_CONSTANTS.EDIT_FIELD,
          payload: {
            parentData: activePageDetails,
            fieldData: updatedItem,
          },
        });
      }
    }
  }, [contents]);

  useEffect(() => {
    if (newlyAddedSectionId) {
      setTimeout(() => {
        const newlyAddedSection = document.querySelector(
          `[data-section-id="${newlyAddedSectionId}"]`
        ) as HTMLElement;

        if (newlyAddedSection) {
          const scrollContainer = newlyAddedSection.closest(
            ".overflow-y-auto"
          ) as HTMLElement;

          if (scrollContainer) {
            // Calculate the position of the section relative to the scroll container
            const containerRect = scrollContainer.getBoundingClientRect();
            const sectionRect = newlyAddedSection.getBoundingClientRect();
            const relativeTop = sectionRect.top - containerRect.top;

            scrollContainer.scrollTo({
              top: scrollContainer.scrollTop + relativeTop,
              behavior: "smooth",
            });
          }
        }
        setNewlyAddedSectionId(null);
      }, 0);
    }
  }, [newlyAddedSectionId]);

  return (
    <>
      {isEditModalOpen && (
        <AddSectionComponent
          initialName={sectionName}
          initialRepeatable={properties.is_repeatable}
          setSectionName={(newName, is_repeatable) => {
            dispatch({
              type: CF_REDUCER_CONSTANTS.EDIT_SECTION_FIELD,
              payload: {
                sectionId: id,
                updatedProperties: {
                  title: newName,
                  is_repeatable: is_repeatable,
                },
              },
            });
            setIsEditModalOpen(false);
          }}
          onCancel={() => setIsEditModalOpen(false)}
          toggleDisabled={makeSectionRepeatable()}
        />
      )}

      {isOpen && (
        <PreviewCTASectionComponent
          showAddSection={false}
          isOpen={isOpen}
          setIsOpen={setIsOpen}
          setQuestionModalOpen={setQuestionModalOpen}
          setDataModalOpen={setDataModalOpen}
          setComponentsModalOpen={setComponentsModalOpen}
          mode={mode}
          includeSectionInSummaryToggle={include_in_summary}
          showComponent={!properties.is_repeatable}
        />
      )}
      <section
        ref={sectionRef}
        data-section-id={id}
        className={`flex flex-col ${
          inSummary ? "" : "p-1 sm:p-2"
        } relative border border-transparent border-solid  ${
          isHovered && mode === UserFormModeTypes.BUILD
            ? "hover:border-brand-urbint-40 "
            : ""
        } ${!!properties.title ? "mt-2 sm:mt-2.5" : "pt-0"}`}
        onMouseEnter={() =>
          mode === UserFormModeTypes.BUILD && setIsHovered(true)
        }
        onMouseLeave={() =>
          mode === UserFormModeTypes.BUILD && setIsHovered(false)
        }
        onClick={() =>
          mode === UserFormModeTypes.BUILD &&
          isMobileOrTablet() &&
          setIsHovered(!isHovered)
        }
      >
        {isHovered && mode === UserFormModeTypes.BUILD && (
          <div className="flex flex-col sm:flex-row gap-2">
            <div
              className={`${style.sectionDetailsAction} flex flex-row flex-wrap gap-2`}
            >
              {actions.map(action => (
                <button
                  className="text-xl text-neutral-shade-75 hover:text-brand-urbint-40 p-1"
                  key={action.id}
                >
                  <i
                    className={action?.icon}
                    onClick={() => onClickOfAction(action.id)}
                    aria-hidden="true"
                    title={action.displayName}
                  ></i>
                </button>
              ))}
            </div>
            {item.type !== CWFItemType.Summary && (
              <IncludeInSummaryToggle
                includeSectionInSummaryToggle={
                  include_in_summary ?? pageLevelIncludeInSummaryToggle
                }
                handleToggle={
                  ![
                    UserFormModeTypes.PREVIEW_PROPS,
                    UserFormModeTypes.PREVIEW,
                  ].some(formMode => mode.includes(formMode)) &&
                  handleSummaryToggle
                }
                mode={mode}
                item={item}
              />
            )}
          </div>
        )}
        {!properties.child_instance && !inSummary && (
          <div className="flex flex-col space-y-3 sm:space-y-0 sm:flex-row sm:items-center sm:justify-between w-full min-w-0">
            <legend className="w-full sm:flex-1 min-w-0">
              <SectionHeading
                className={`text-xl font-semibold p-2 sm:p-4 md:p-0 mb-2 break-words ${
                  inSummary ? "text-brand-gray-70" : ""
                }`}
              >
                {properties.title}
              </SectionHeading>
            </legend>
            {properties.is_repeatable && (
              <div className="flex justify-center sm:justify-end w-full sm:w-auto sm:flex-shrink-0">
                <ButtonSecondary
                  onClick={handleAddRepeatableSection}
                  label={"Add another " + properties.title}
                  iconStart="plus_circle_outline"
                  disabled={
                    mode === UserFormModeTypes.BUILD ||
                    mode === UserFormModeTypes.PREVIEW ||
                    mode === UserFormModeTypes.PREVIEW_PROPS
                  }
                  className="w-full"
                />
              </div>
            )}
          </div>
        )}
        {(!properties.is_repeatable ||
          !(
            mode === UserFormModeTypes.EDIT ||
            mode === UserFormModeTypes.PREVIEW
          )) && (
          <div
            className={`flex ${
              inSummary ? "" : "bg-brand-gray-10"
            } justify-start`}
          >
            <div
              className={`w-full ${
                inSummary ? "cursor-auto" : "p-2 sm:p-4 mt-1.5 cursor-pointer"
              } flex flex-col justify-start gap-3 sm:gap-4`}
            >
              {contents.map((c, index) => (
                <div key={c.id}>
                  {formGenerator(
                    c,
                    activePageDetails,
                    activeWidgetDetails,
                    mode,
                    {
                      previousContent: contents[index - 1],
                      nextContent: contents[index + 1],
                    },
                    projectDetails,
                    pageLevelIncludeInSummaryToggle,
                    setActiveWidgetDetails,
                    {
                      id,
                      type,
                      order,
                      properties,
                      contents,
                    },
                    properties.is_repeatable,
                    formObject,
                    undefined,
                    inSummary
                  )}
                </div>
              ))}
            </div>
            {properties.child_instance && !inSummary && (
              <button
                className="mr-2 absolute top-4 right-2 flex items-center text-sm text-red-500 gap-1"
                onClick={() => setDeleteSection(true)}
                disabled={disableDeleteSection}
              >
                <Icon
                  className={`text-sm ${
                    disableDeleteSection
                      ? "opacity-[0.25] cursor-not-allowed"
                      : ""
                  }`}
                  name="trash_empty"
                ></Icon>
                Delete
              </button>
            )}
          </div>
        )}
      </section>

      <Modal
        title="Delete Section"
        isOpen={isDeleteSectionOpen}
        closeModal={() => setDeleteSectionOpen(false)}
        size="md"
      >
        <div>
          <div>Delete the section?</div>
          <br />
          <br />
          <div className="flex self-end w-full pt-4 flex-row-reverse m-t-4 border-t-2 border-solid">
            <ButtonDanger label="Delete" onClick={() => onDeleteSection()} />
            <ButtonRegular
              className="mr-2"
              label="Cancel"
              onClick={() => setDeleteSectionOpen(false)}
            />
          </div>
        </div>
      </Modal>
      <Modal
        title="Are you sure you want to do this?"
        isOpen={mode === UserFormModeTypes.EDIT && deleteSection}
        closeModal={() => setDeleteSection(false)}
      >
        <div className="mb-10">
          <p>{`Deleting will remove this ${properties.title}.`}</p>
        </div>
        <div className="flex justify-end">
          <ButtonRegular
            className="mr-3"
            label="Cancel"
            onClick={() => setDeleteSection(false)}
          />

          <ButtonDanger label="Yes, delete" onClick={onDeleteSection} />
        </div>
      </Modal>
      <DynamicFormModal
        isOpen={isQuestionOpen}
        onClose={() => setIsQuestionOpen(false)}
        onAdd={content => {
          addContent(content);
          setIsQuestionOpen(false);
        }}
        isRepeatableSection={properties.is_repeatable}
      />
      <DataDisplayModal
        isOpen={isDataOpen}
        onClose={() => setIsDataOpen(false)}
        onAdd={content => {
          addContent(content);
          setIsDataOpen(false);
        }}
      />

      <FormComponentsPopUp
        isOpen={isComponentsOpen}
        onClose={() => setIsComponentsOpen(false)}
        onAdd={content => {
          addContent(content);
        }}
      />
    </>
  );
};

export default FormSection;
