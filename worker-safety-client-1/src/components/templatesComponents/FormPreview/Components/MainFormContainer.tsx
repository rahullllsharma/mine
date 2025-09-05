import type {
  ActivePageObjType,
  FormElementsType,
  FormType,
  PageType,
  ProjectDetailsType,
  UserFormMode,
} from "../../customisedForm.types";
import { useQuery } from "@apollo/client";
import { Icon } from "@urbint/silica";
import router from "next/router";
import { useContext, useEffect, useRef } from "react";
import axiosRest from "@/api/customFlowApi";
import IncludeInSummaryToggle from "@/components/dynamicForm/SummaryComponent/IncludeInSummaryToggle";
import ToastContext from "@/components/shared/toast/context/ToastContext";
import CustomisedFromStateContext from "@/context/CustomisedDataContext/CustomisedFormStateContext";
import TenantLibrarySiteConditions from "@/graphql/queries/tenantLibrarySiteConditions.gql";
import TenantLinkedHazardsLibrary from "@/graphql/queries/tenantLinkedHazardsLibrary.gql";
import { orderByName } from "@/graphql/utils";
import useRestMutation from "@/hooks/useRestMutation";
import { CF_REDUCER_CONSTANTS } from "@/utils/customisedFormUtils/customisedForm.constants";
import {
  getMasterToggleState,
  updateComponentsSummaryState,
} from "@/utils/summaryToggleUtils";
import { UserFormModeTypes } from "../../customisedForm.types";
import styles from "../formPreview.module.scss";
import FormPages from "./FormPages";
import {
  FormRendererProvider,
  useFormRendererContext,
} from "./FormRendererContext";
import FormWidgetSection from "./FormWidgetsSection";
import PagesDropdown from "./PagesDropdown";
import TemplateFormFooter from "./TemplateFormFooter";

type MainFormContainerProps = {
  formObject: FormType;
  activePageDetails: ActivePageObjType;
  setActivePageDetails: (item: ActivePageObjType) => void;
  mode: UserFormMode;
  projectDetails?: ProjectDetailsType;
  creatingForm?: boolean;
};
type MainFormContainerInnerProps = {
  projectDetails?: ProjectDetailsType;
  creatingForm?: boolean;
};

// Separate the internal component from the wrapper that provides context
const MainFormContainerInner = ({
  projectDetails,
  creatingForm = false,
}: MainFormContainerInnerProps) => {
  const {
    formObject,
    activePageDetails,
    setActivePageDetails,
    mode,
    getFormContents,
  } = useFormRendererContext();
  const { state, dispatch } = useContext(CustomisedFromStateContext)!;

  const toastCtx = useContext(ToastContext);
  const { templateId } = router.query || "";

  // Ref for scrollable container
  const scrollContainerRef = useRef<HTMLDivElement>(null);

  // Reset scroll position to top when activePageDetails changes
  useEffect(() => {
    if (scrollContainerRef.current) {
      scrollContainerRef.current.scrollTop = 0;
    }
  }, [activePageDetails]);

  const {
    mutate: saveAsADraft,
    error,
    responseData,
  } = useRestMutation<any>({
    endpoint: "/templates/" + templateId,
    method: "put",
    axiosInstance: axiosRest,
    dtoFn: data => data,
  });
  /**
   * Determines the appropriate toggle state for display purposes
   * For master toggle (no targetId), uses utility function
   * For page-specific toggles, checks page properties
   */
  const getToggleState = (content: PageType[], targetId?: string): boolean => {
    // Master toggle - use utility function
    if (!targetId) {
      return getMasterToggleState(content);
    }

    const pageId = targetId || activePageDetails?.id;
    if (!pageId) return false;

    // Find specific page toggle state
    const topLevelPage = content.find((page: PageType) => page.id === pageId);
    if (topLevelPage) {
      return topLevelPage.properties.include_in_summary ?? false;
    }

    // Check subpages
    for (const page of content) {
      if (page.contents?.length > 0) {
        const subPage = page.contents.find(
          (item: FormElementsType) => item.id === pageId
        );
        if (subPage) {
          return subPage.properties.include_in_summary ?? false;
        }
      }
    }

    return false;
  };

  /**
   * Master toggle handler that systematically updates all eligible components
   * Uses utility functions for proper state management and updates
   */
  const handleMasterToggle = (): void => {
    const currentMasterState = getMasterToggleState(formObject.contents);
    const newInclusionState = !currentMasterState;

    // Update callback for each component that needs to be modified
    const updateComponentCallback = (
      component: FormElementsType,
      parentSection?: FormElementsType
    ): void => {
      const updatedComponent: FormElementsType = {
        ...component,
        properties: {
          ...component.properties,
          include_in_summary: newInclusionState,
        },
      };

      dispatch({
        type: CF_REDUCER_CONSTANTS.EDIT_FIELD,
        payload: {
          parentData: findParentPage(component.id),
          section: parentSection,
          fieldData: updatedComponent,
        },
      });
    };

    // Process all pages systematically
    formObject.contents.forEach((page: PageType) => {
      if (page.contents?.length > 0) {
        updateComponentsSummaryState(
          page.contents,
          newInclusionState,
          updateComponentCallback
        );
      }
    });

    // Provide user feedback
    toastCtx?.pushToast(
      "success",
      `All components ${
        newInclusionState ? "will be" : "will not be"
      } included in summary. Please click on Publish button to save the changes.`
    );
  };

  /**
   * Helper function to find the parent page for a given component
   * Used by the update callback to provide proper parentData to the reducer
   */
  const findParentPage = (componentId: string): PageType | null => {
    for (const page of formObject.contents) {
      if (
        page.contents?.some(
          (component: FormElementsType) => component.id === componentId
        )
      ) {
        return page;
      }

      // Check nested components in sections
      for (const component of page.contents || []) {
        if (
          component.contents?.some(
            (nested: FormElementsType) => nested.id === componentId
          )
        ) {
          return page;
        }
      }
    }
    return null;
  };

  const isEditOrTemplateMode = () => {
    return (
      mode === UserFormModeTypes.EDIT || router.pathname.includes("/templates/")
    );
  };

  useEffect(() => {
    if (error) {
      toastCtx?.pushToast("error", "Error ! , Please try again");
    }
    if (responseData) {
      toastCtx?.pushToast("success", "This Template has been saved as draft");
      router.push("/templates?tab=draft");
    }
  }, [error, responseData]);

  const handleClickOnClose = () => {
    if (router.pathname.includes("/template-forms")) {
      return router.push("/template-forms");
    } else {
      return router.push("/templates");
    }
  };

  const handleFormValid = () => {
    dispatch({ type: CF_REDUCER_CONSTANTS.SET_FORM_VALIDITY, payload: true });
  };

  return (
    <div className="flex flex-col h-screen overflow-hidden">
      {/* showing error banner in case of Mandatory fields are not filled */}
      {!state.isFormIsValid && (
        <div className="border border-system-error-40 bg-system-error-10 box-border p-2">
          <div className="flex justify-between items-center">
            <div className="text-sm">
              <Icon name={"error"} className={`text-system-error-40 mr-2`} />
              Review all pages and fill in missing required information to
              complete this form.
            </div>
            <button className="ml-4" aria-label="Close error banner">
              <Icon
                name={"close_big"}
                className={`text-gray-400`}
                onClick={handleFormValid}
              />
            </button>
          </div>
        </div>
      )}
      <div className="flex justify-center flex-grow">
        <div className="max-w-[1040px]   w-full">
          {/* Main content area */}
          <main className="h-full w-min tab-md:w-full pb-24 pt-4 flex flex-col tab-md:grid tab-md:grid-cols-12 tab-md:gap-4">
            <div className="col-span-12 h-auto tab-md:col-span-4 tab-md:h-full">
              {/* Mobile version – show only on small screens */}
              <div className="block tab-md:hidden p-1">
                <PagesDropdown
                  formObject={formObject}
                  onSelectOfDropdown={setActivePageDetails}
                  activePageDetails={activePageDetails}
                />
              </div>

              {/* Desktop version – show only on medium and larger screens */}
              <nav className="hidden tab-md:block rounded-md h-[calc(100vh-265px)] flex-col">
                <div className="flex-grow overflow-y-auto no-scrollbar h-full bg-white">
                  <FormPages
                    formPages={formObject.contents}
                    activePageDetails={activePageDetails}
                    setActivePageDetails={setActivePageDetails}
                    mode={mode}
                  />
                </div>
              </nav>
            </div>

            <section
              className={`col-span-12 tab-md:col-span-8 rounded-md ${styles.formContentWidth} bg-white h-[calc(100vh-250px)] overflow-hidden`}
            >
              {formObject.contents?.length > 0 &&
                router.pathname.includes("/templates") && (
                  <div className="flex items-center justify-end cursor-default">
                    <IncludeInSummaryToggle
                      includeSectionInSummaryToggle={getToggleState(
                        formObject.contents
                      )}
                      mode={mode}
                      handleToggle={handleMasterToggle}
                    />
                  </div>
                )}
              <div
                ref={scrollContainerRef}
                className="overflow-y-auto overflow-x-hidden pb-20 h-full pt-4"
              >
                <FormWidgetSection
                  activeContents={getFormContents(
                    formObject.contents,
                    activePageDetails
                  )}
                  activePageDetails={activePageDetails}
                  mode={mode}
                  formObject={formObject}
                  setActivePageDetails={setActivePageDetails}
                  projectDetails={projectDetails}
                />
              </div>
            </section>
          </main>
        </div>
      </div>
      {/* Page Footer section */}
      <div className="w-full fixed bottom-0 left-0 right-0 z-10 bg-brand-gray-10">
        <div className="flex justify-center">
          <div className="max-w-[840px] lg:max-w-[990px] w-full">
            <div className="flex flex-col tab-md:flex-row tab-md:justify-between">
              <div className="hidden tab-md:block"></div>
              <div
                className={`flex justify-end ${styles.formContentWidth} my-4 mx-auto tab-md:mx-0`}
              >
                {mode !== UserFormModeTypes.PREVIEW && (
                  <TemplateFormFooter
                    onClickSaveAndDraft={saveAsADraft}
                    handleClickOnClose={handleClickOnClose}
                    mode={mode}
                    formObject={formObject}
                    setActivePageDetails={setActivePageDetails}
                    isEditOrTemplateMode={isEditOrTemplateMode()}
                    activePageDetails={activePageDetails}
                    projectDetails={projectDetails}
                    creatingForm={creatingForm}
                  />
                )}
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

// Main component that wraps everything with the context provider
const MainFormContainer = ({
  formObject,
  activePageDetails,
  setActivePageDetails,
  mode,
  projectDetails,
  creatingForm,
}: MainFormContainerProps) => {
  const { state } = useContext(CustomisedFromStateContext)!;

  const { data, loading: loadingHazards } = useQuery(
    TenantLinkedHazardsLibrary,
    {
      fetchPolicy: "cache-and-network",
      variables: { orderBy: orderByName, controlsOrderBy: orderByName },
      skip:
        mode === UserFormModeTypes.PREVIEW ||
        mode === UserFormModeTypes.PREVIEW_PROPS,
    }
  );

  // Get work type IDs for library site conditions query
  const selectedWorkTypesFromLocalStorage = JSON.parse(
    localStorage.getItem("selectedWorkTypes") || "[]"
  );
  const workTypes = state.form.metadata?.work_types ?? [];
  const workTypeIds = (
    workTypes.length > 0 ? workTypes : selectedWorkTypesFromLocalStorage || []
  ).map((workType: any) => workType.id);

  const {
    data: librarySiteConditionsData,
    loading: librarySiteConditionsLoading,
  } = useQuery(TenantLibrarySiteConditions, {
    fetchPolicy: "cache-and-network",
    variables: {
      tenantWorkTypeIds: workTypeIds,
    },
    skip:
      mode === UserFormModeTypes.PREVIEW ||
      mode === UserFormModeTypes.PREVIEW_PROPS,
  });

  const hazardsData = data?.tenantLinkedHazardsLibrary || [];
  const tasksHazardData =
    state.form?.component_data?.hazards_controls?.tasks || [];
  return (
    <FormRendererProvider
      formObject={formObject}
      activePageDetails={activePageDetails}
      setActivePageDetails={setActivePageDetails}
      mode={mode}
      hazardsData={hazardsData}
      tasksHazardData={tasksHazardData}
      isLoading={loadingHazards}
      librarySiteConditionsData={librarySiteConditionsData}
      librarySiteConditionsLoading={librarySiteConditionsLoading}
    >
      <MainFormContainerInner
        projectDetails={projectDetails}
        creatingForm={creatingForm}
      />
    </FormRendererProvider>
  );
};

export default MainFormContainer;
