import type { CustomisedFromContextStateType } from "@/context/CustomisedDataContext/CustomisedFormStateContext";
import type {
  ActivePageObjType,
  FormElementsType,
  FormType,
  ModeTypePageSection,
  TemplateMetaData,
  WidgetType,
} from "../../customisedForm.types";
import { cloneDeep, isEmpty } from "lodash-es";
import { useContext, useEffect, useState } from "react";
import { v4 as uuidv4 } from "uuid";
import DynamicFormModal from "@/components/dynamicForm";
import { DataDisplayModal } from "@/components/dynamicForm/dataDisplay";
import ButtonDanger from "@/components/shared/button/danger/ButtonDanger";
import ButtonRegular from "@/components/shared/button/regular/ButtonRegular";
import Modal from "@/components/shared/modal/Modal";
import ToastContext from "@/components/shared/toast/context/ToastContext";
import CustomisedFromStateContext from "@/context/CustomisedDataContext/CustomisedFormStateContext";
import { CF_REDUCER_CONSTANTS } from "@/utils/customisedFormUtils/customisedForm.constants";
import {
  getMasterToggleState,
  hasAnyComponentsIncludedInSummary,
} from "@/utils/summaryToggleUtils";
import { CWFItemType } from "../../customisedForm.types";
import FormComponentsPopUp from "../../FormComponents/FormComponentsPopUp";
import AddSectionComponent from "./AddSection";
import FormRenderer from "./FormRenderer";
import NoContentAdded from "./NoContentAdded";
import PreviewCTASectionComponent from "./PreviewCTASectionComponent";

type PreviewComponentProps = {
  activeContents: any[];
  activePageDetails: ActivePageObjType;
  activeWidgetDetails: WidgetType;
  setActiveWidgetDetails: (item: WidgetType) => void;
  setMode: (item: ModeTypePageSection) => void;
  setActivePageDetails: (item: ActivePageObjType) => void;
  templateMetadata?: TemplateMetaData;
};

const getOrderCount = (state: FormType, target: ActivePageObjType) => {
  let currentCount = 0;
  if (target!.type === CWFItemType.SubPage) {
    for (let i = 0; i < state.contents.length; i++) {
      if (state.contents[i].id === target?.parentId) {
        for (let j = 0; j < state.contents[i].contents.length; j++) {
          if (
            state.contents[i].contents[j].type === CWFItemType.SubPage &&
            state.contents[i].contents[j].id === target?.id
          ) {
            const currentContent: Array<any> =
              state.contents[i].contents[j].contents;
            if (!isEmpty(currentContent)) {
              currentCount = currentContent[currentContent.length - 1].order;
            }
          }
        }
      }
    }
  } else {
    for (let i = 0; i < state.contents.length; i++) {
      if (state.contents[i].id === target?.id) {
        const currentContent = state.contents[i].contents;
        if (!isEmpty(currentContent)) {
          currentCount = currentContent[currentContent.length - 1].order;
        }
      }
    }
  }

  return currentCount;
};

const getActivePageIndex = (
  state: CustomisedFromContextStateType,
  activePageDetails: ActivePageObjType
) => {
  return state.form.contents.findIndex(
    (page: FormElementsType) => page.id === activePageDetails?.id
  );
};

const getSubPageIndex = (
  state: CustomisedFromContextStateType,
  activePageDetails: ActivePageObjType
) => {
  if (activePageDetails?.type === CWFItemType.SubPage) {
    const parentPageIndex = state.form.contents.findIndex(
      (page: FormElementsType) =>
        page.contents?.some(
          (subPage: FormElementsType) => subPage.id === activePageDetails?.id
        )
    );

    if (parentPageIndex !== -1) {
      const subPageIndex = state.form.contents[
        parentPageIndex
      ].contents.findIndex(
        (subPage: FormElementsType) => subPage.id === activePageDetails?.id
      );

      return { parentPageIndex, subPageIndex };
    }
  }
  return { parentPageIndex: -1, subPageIndex: -1 };
};

const getSummaryToggleState = (
  activePageDetails: ActivePageObjType,
  state: CustomisedFromContextStateType
) => {
  if (activePageDetails?.type === CWFItemType.Page) {
    return (
      state.form.contents[getActivePageIndex(state, activePageDetails)]
        ?.properties.include_in_summary ?? false
    );
  }
  const { parentPageIndex, subPageIndex } = getSubPageIndex(
    state,
    activePageDetails
  );

  return parentPageIndex !== -1 && subPageIndex !== -1
    ? state.form.contents[parentPageIndex].contents[subPageIndex]?.properties
        .include_in_summary ?? false
    : false;
};

// Removed: areAnyComponentsIncludedInSummaryRecursive - replaced with utility function
const PreviewComponent = ({
  activePageDetails,
  setActivePageDetails,
  activeContents,
  activeWidgetDetails,
  setActiveWidgetDetails,
  setMode,
}: PreviewComponentProps) => {
  const [isOpen, setIsOpen] = useState(false);
  const [isQuestionOpen, setIsQuestionOpen] = useState<boolean>(false);
  const [isDataOpen, setIsDataOpen] = useState<boolean>(false);
  const [isComponentsOpen, setIsComponentsOpen] = useState<boolean>(false);
  const [isSectionClicked, setSectionClicked] = useState(false);
  const { state, dispatch } = useContext(CustomisedFromStateContext)!;
  const [isDeletePageModalOpen, setDeletePageModalOpen] = useState(false);
  const [deletedPageInfo, setDeletedPageInfo] = useState({
    parentPage: "",
    id: "",
    title: "",
    type: "",
  });

  const [pageLevelIncludeInSummaryToggle, setPageLevelIncludeInSummaryToggle] =
    useState(getSummaryToggleState(activePageDetails, state) ?? false);

  const toastCtx = useContext(ToastContext);

  const getCurrentPageIndex = (currentActivePageDetails: ActivePageObjType) => {
    return state.form.contents.findIndex(
      page => page.id === currentActivePageDetails?.id
    );
  };

  const onSubmit = (name: string, is_repeatable: boolean) => {
    setSectionClicked(false);
    const currentOrder = getOrderCount(state.form, activePageDetails) + 1;
    const shouldIncludeInSummary = getMasterToggleState(state.form.contents);

    dispatch({
      type: CF_REDUCER_CONSTANTS.ADD_SECTION,
      payload: {
        parentData: activePageDetails,
        sectionData: {
          id: uuidv4(),
          type: CWFItemType.Section,
          order: currentOrder,
          properties: {
            title: name,
            is_repeatable: is_repeatable,
            child_instance: false,
            include_in_summary: shouldIncludeInSummary,
          },
          contents: [],
        },
      },
    });
  };

  const onOpenOfDeletePageModal = () => {
    let deletePageDetails;

    if (activePageDetails?.type === CWFItemType.Page) {
      const activePage = state.form.contents.find(
        page => page.id === activePageDetails?.id
      );

      if (activePage) {
        deletePageDetails = {
          parentPage: activePage.id,
          id: activePage.id,
          title: activePage.properties.title,
          type: CWFItemType.Page,
        };
      }
    } else if (activePageDetails?.type === CWFItemType.SubPage) {
      const activeParentPage = state.form.contents.find(
        page => page.id === activePageDetails?.parentId
      );

      if (activeParentPage) {
        const subPageRecord = activeParentPage.contents.find(
          subPage => subPage.id === activePageDetails?.id
        );

        if (subPageRecord) {
          deletePageDetails = {
            parentPage: activePageDetails.parentId,
            id: subPageRecord.id,
            title: subPageRecord.properties.title,
            type: CWFItemType.SubPage,
          };
        }
      }
    }
    if (deletePageDetails) {
      setDeletedPageInfo(deletePageDetails);
      setDeletePageModalOpen(true);
    }
  };

  const checkAndSetMetadata = (pagedetails: any) => {
    if (!pagedetails?.contents) return;
    const typesToCheck = [
      CWFItemType.HazardsAndControls,
      CWFItemType.ActivitiesAndTasks,
      CWFItemType.Summary,
      CWFItemType.SiteConditions,
      CWFItemType.Location,
      CWFItemType.NearestHospital,
      CWFItemType.Region,
      CWFItemType.Contractor,
      CWFItemType.ReportDate,
    ];
    const results: any = {};

    function searchForTypes(contents: any): void {
      if (!contents || !Array.isArray(contents)) return;

      for (const item of contents) {
        if (typesToCheck.includes(item.type)) {
          results[item.type] = true;
        }

        if (item.contents && Array.isArray(item.contents)) {
          searchForTypes(item.contents);
        }
      }
    }
    searchForTypes(pagedetails.contents);

    const updatedMetadata = {
      ...state.form.metadata,
    };

    if (results[CWFItemType.HazardsAndControls]) {
      updatedMetadata.is_hazards_and_controls_included = false;
    }

    if (results[CWFItemType.ActivitiesAndTasks]) {
      updatedMetadata.is_activities_and_tasks_included = false;
    }

    if (results[CWFItemType.Summary]) {
      updatedMetadata.is_summary_included = false;
    }

    if (results[CWFItemType.SiteConditions]) {
      updatedMetadata.is_site_conditions_included = false;
    }

    if (results[CWFItemType.Location]) {
      updatedMetadata.is_location_included = false;
    }

    if (results[CWFItemType.NearestHospital]) {
      updatedMetadata.is_nearest_hospital_included = false;
    }

    if (results[CWFItemType.Region]) {
      updatedMetadata.is_region_included = false;
    }

    if (results[CWFItemType.Contractor]) {
      updatedMetadata.is_contractor_included = false;
    }

    if (results[CWFItemType.ReportDate]) {
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

  const countAndDecrementWidgetItems = (pageDetails: any) => {
    if (!pageDetails?.contents) return;

    let widgetItemsCount = 0;

    function countWidgetItemsRecursively(contents: any): void {
      if (!contents || !Array.isArray(contents)) return;

      for (const item of contents) {
        // Check if the current item is marked for widget inclusion
        if (item.properties?.include_in_widget) {
          widgetItemsCount++;
        }

        // Recursively check nested contents (for sections within sections)
        if (item.contents && Array.isArray(item.contents)) {
          countWidgetItemsRecursively(item.contents);
        }
      }
    }

    countWidgetItemsRecursively(pageDetails.contents);

    // Decrement widget count if there are items to remove
    if (widgetItemsCount > 0) {
      const currentWidgetCount = state.form.settings?.widgets_added || 0;
      const newWidgetCount = Math.max(currentWidgetCount - widgetItemsCount, 0);

      dispatch({
        type: CF_REDUCER_CONSTANTS.UPDATE_WIDGET_SETTINGS,
        payload: {
          widgets_added: newWidgetCount,
        },
      });
    }
  };

  const resetActivePageDetails = (
    currentActivePageDetails: ActivePageObjType
  ) => {
    if (state.form.contents.length > 0 && currentActivePageDetails) {
      const currentIndex = getCurrentPageIndex(currentActivePageDetails);
      let newActivePageDetails;
      if (currentActivePageDetails.type === CWFItemType.Page) {
        if (currentIndex === 0) {
          newActivePageDetails =
            state.form.contents.length > 1
              ? {
                  id: state.form.contents[1].id,
                  parentId: "root",
                  type: CWFItemType.Page,
                }
              : currentActivePageDetails;
        } else {
          newActivePageDetails = {
            id: state.form.contents[currentIndex - 1].id,
            parentId: "root",
            type: CWFItemType.Page,
          };
        }
      } else {
        newActivePageDetails = {
          id: currentActivePageDetails.parentId,
          parentId: "root",
          type: CWFItemType.Page,
        };
      }
      setActivePageDetails(newActivePageDetails);
    }
  };

  const onConfirmOfDeletePage = () => {
    const activePage =
      activePageDetails?.type === CWFItemType.Page
        ? state.form.contents.find(page => page.id === activePageDetails?.id)
        : state.form.contents
            .find(page => page.id === activePageDetails?.parentId)
            ?.contents.find(subPage => subPage.id === activePageDetails?.id);

    if (activePage) {
      checkAndSetMetadata(activePage);
      // Count and decrement widget items before deletion
      countAndDecrementWidgetItems(activePage);
    }

    dispatch({
      type:
        activePageDetails?.type === CWFItemType.Page
          ? CF_REDUCER_CONSTANTS.DELETE_PAGE
          : CF_REDUCER_CONSTANTS.DELETE_SUBPAGE,
      payload: {
        ...deletedPageInfo,
      },
    });

    toastCtx?.pushToast(
      "success",
      "Page deleted. Make sure to tap Save button to keep your changes intact"
    );
    resetActivePageDetails(activePageDetails);
    setDeletePageModalOpen(false);
  };

  const updatePageComponentSummaryToggle = (
    visibility: boolean,
    pageIndex: number,
    isSubpage: boolean,
    subPageIndex: number
  ) => {
    setPageLevelIncludeInSummaryToggle(visibility);

    let page;
    if (isSubpage) {
      page = state.form.contents[pageIndex].contents[subPageIndex];
    } else {
      page = state.form.contents[pageIndex];
    }

    const updateAllNestedComponents = (
      component: FormElementsType,
      currentSection: FormElementsType | null = null
    ) => {
      const updatedComponent = {
        ...component,
        properties: {
          ...component.properties,
          include_in_summary: visibility,
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

      if (component.type === CWFItemType.Section && component.contents) {
        component.contents.forEach((childItem: FormElementsType) => {
          updateAllNestedComponents(childItem, component);
        });
      }
    };

    page.contents.forEach((component: FormElementsType) => {
      updateAllNestedComponents(component);
    });
  };

  const onTogglePageVisibleInSummary = (visibility: boolean) => {
    if (!activePageDetails) return;

    if (activePageDetails.type === CWFItemType.Page) {
      const data = cloneDeep(state.form.contents);
      const pageIndex = getActivePageIndex(state, activePageDetails);
      data[pageIndex].properties.include_in_summary = visibility;
      dispatch({
        type: CF_REDUCER_CONSTANTS.PAGE_SUMMARY_VISIBILITY_TOGGLE,
        payload: data,
      });

      updatePageComponentSummaryToggle(visibility, pageIndex, false, -1);
    }

    if (activePageDetails.type === CWFItemType.SubPage) {
      const { parentPageIndex, subPageIndex } = getSubPageIndex(
        state,
        activePageDetails
      );
      if (parentPageIndex !== -1 && subPageIndex !== -1) {
        const data = cloneDeep(state.form.contents);
        data[parentPageIndex].contents[
          subPageIndex
        ].properties.include_in_summary = visibility;

        dispatch({
          type: CF_REDUCER_CONSTANTS.SUBPAGE_SUMMARY_VISIBILITY_TOGGLE,
          payload: data,
        });

        updatePageComponentSummaryToggle(
          visibility,
          parentPageIndex,
          true,
          subPageIndex
        );
      }
    }

    toastCtx?.pushToast(
      "success",
      `${activePageDetails.type === CWFItemType.Page ? "Page" : "Subpage"} ${
        visibility ? "included in" : "excluded from"
      } summary. Please click on Publish button to save the changes.`
    );
  };

  const setQuestionModalOpen = () => {
    setIsOpen(false);
    setIsQuestionOpen(true);
  };

  const setDataDisplayModalOpen = () => {
    setIsOpen(false);
    setIsDataOpen(true);
  };

  const setComponentsModalOpen = () => {
    setIsOpen(false);
    setIsComponentsOpen(true);
  };

  /**
   * Adds new content to the form with proper summary inclusion state
   * Uses master toggle state to determine appropriate default state
   */
  const addContent = (value: any, type = "ADD_FIELD"): void => {
    const shouldIncludeInSummary = getMasterToggleState(state.form.contents);

    if (type === CF_REDUCER_CONSTANTS.ADD_COMPONENTS) {
      dispatch({
        type: CF_REDUCER_CONSTANTS.ADD_COMPONENTS,
        payload: {
          parentData: activePageDetails,
          fieldData: {
            ...value,
            order: activeContents.length + 1,
            is_mandatory: value.is_mandatory ?? false,
            properties: {
              ...value.properties,
              include_in_summary: shouldIncludeInSummary,
            },
          },
        },
      });
    } else {
      const field = {
        ...value,
        order: activeContents.length + 1,
        properties: {
          ...value.properties,
          include_in_summary: shouldIncludeInSummary,
        },
      };

      dispatch({
        type: CF_REDUCER_CONSTANTS.ADD_FIELD,
        payload: {
          parentData: activePageDetails,
          fieldData: field,
        },
      });
    }
  };

  useEffect(() => {
    let page: FormElementsType | undefined;
    if (activePageDetails?.type === CWFItemType.Page) {
      page = state.form.contents.find(
        (p: FormElementsType) => p.id === activePageDetails.id
      );
    } else if (activePageDetails?.type === CWFItemType.SubPage) {
      const parentPage = state.form.contents.find(
        (p: FormElementsType) => p.id === activePageDetails.parentId
      );
      page = parentPage?.contents?.find(
        (sp: FormElementsType) => sp.id === activePageDetails.id
      );
    }

    if (page && Array.isArray(page.contents)) {
      const anyIncluded = hasAnyComponentsIncludedInSummary(page.contents);
      setPageLevelIncludeInSummaryToggle(anyIncluded);
    }
  }, [state.form.contents, activePageDetails]);

  useEffect(() => {
    const data = cloneDeep(state.form.contents);
    const pageIndex = getActivePageIndex(state, activePageDetails);
    if (data[pageIndex]?.properties) {
      data[pageIndex].properties.include_in_summary =
        pageLevelIncludeInSummaryToggle;
      dispatch({
        type: CF_REDUCER_CONSTANTS.PAGE_SUMMARY_VISIBILITY_TOGGLE,
        payload: data,
      });
    }
  }, [pageLevelIncludeInSummaryToggle]);

  const shouldRenderComponent = () => {
    return (
      activePageDetails !== null &&
      Array.isArray(state.form.contents) &&
      state.form.contents.length > 0
    );
  };

  return (
    <div className="h-full">
      {shouldRenderComponent() ? (
        <PreviewCTASectionComponent
          isOpen={isOpen}
          setIsOpen={setIsOpen}
          setQuestionModalOpen={setQuestionModalOpen}
          onClickOfSection={setSectionClicked}
          onClickOfDeletePage={onOpenOfDeletePageModal}
          setDataModalOpen={setDataDisplayModalOpen}
          setComponentsModalOpen={setComponentsModalOpen}
          onToggleSummary={onTogglePageVisibleInSummary}
          mode={state.formBuilderMode}
          includeSectionInSummaryToggle={getSummaryToggleState(
            activePageDetails,
            state
          )}
        />
      ) : null}
      {isSectionClicked && (
        <AddSectionComponent
          setSectionName={onSubmit}
          onCancel={() => setSectionClicked(false)}
        />
      )}
      <div className="h-full">
        {activeContents.length === 0 ? (
          <NoContentAdded setIsOpen={setIsOpen} setMode={setMode} />
        ) : (
          <FormRenderer
            activeContents={activeContents}
            activePageDetails={activePageDetails}
            activeWidgetDetails={activeWidgetDetails}
            setActiveWidgetDetails={setActiveWidgetDetails}
            mode={state.formBuilderMode}
            pageLevelIncludeInSummaryToggle={pageLevelIncludeInSummaryToggle}
          />
        )}
      </div>
      <DynamicFormModal
        isOpen={isQuestionOpen}
        onClose={() => setIsQuestionOpen(false)}
        onAdd={content => {
          addContent(content);
          setIsQuestionOpen(false);
        }}
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
          addContent(content, CF_REDUCER_CONSTANTS.ADD_COMPONENTS);
        }}
      />

      <Modal
        title="Delete Pages"
        isOpen={isDeletePageModalOpen}
        closeModal={() => setDeletePageModalOpen(false)}
        size={"md"}
      >
        <div>
          <div>Do you want to delete the selected pages?</div>
          <div className="flex self-end w-full pt-4 flex-row-reverse m-t-4 border-t-2 border-solid mt-4">
            <ButtonDanger
              label={"Delete"}
              onClick={() => onConfirmOfDeletePage()}
            />
            <ButtonRegular
              className="mr-2"
              label="Cancel"
              onClick={() => setDeletePageModalOpen(false)}
            />
          </div>
        </div>
      </Modal>
    </div>
  );
};

export default PreviewComponent;
