import type {
  ActivePageObjType,
  Attribute,
  CrewRow,
  FormElementsType,
  FormType,
  Hazards,
  PageIteratorType,
  PageType,
} from "../../customisedForm.types";
import cloneDeep from "lodash/cloneDeep";
import router from "next/router";
import { useContext, useEffect, useRef, useState } from "react";
import axiosRest from "@/api/customFlowApi";
import RecommendedHazardsModal from "@/components/dynamicForm/HazardAndControlsComponents/RecommendedHazardsModal";
import ButtonPrimary from "@/components/shared/button/primary/ButtonPrimary";
import ToastContext from "@/components/shared/toast/context/ToastContext";
import CustomisedFromStateContext from "@/context/CustomisedDataContext/CustomisedFormStateContext";
import {
  FORM_EVENTS,
  formEventEmitter,
} from "@/context/CustomisedDataContext/CustomisedFormStateProvider";
import useCWFFormState from "@/hooks/useCWFFormState";
import useRestMutation from "@/hooks/useRestMutation";
import { CF_REDUCER_CONSTANTS } from "@/utils/customisedFormUtils/customisedForm.constants";

import ButtonRegular from "@/components/shared/button/regular/ButtonRegular";
import Modal from "@/components/shared/modal/Modal";
import { CWFItemType, FormStatus } from "../../customisedForm.types";
import {
  getFormComponentData,
  getRegionMetadata,
  isFormValid,
  validateAllHazards,
  validateField,
  validateInputData,
  getVisibleHazards,
  scrollToField,
} from "../../customisedForm.utils";
import { useFormRendererContext } from "./FormRendererContext";

const getPagesIterationArr = (pages: PageType[]) => {
  const titlesArray: PageIteratorType[] = [];
  function iterate(page: PageIteratorType) {
    page.parentId = "root";
    titlesArray.push(page);
    page.contents.forEach(content => {
      if (content.type === CWFItemType.SubPage) {
        content.parentId = page.id;
        titlesArray.push(content);
      } else if (content.type === CWFItemType.Page) {
        iterate(content);
      }
    });
  }
  pages.forEach(page => iterate(page));
  return titlesArray;
};

const SaveAndContinue = ({
  activePageDetails,
  formObject,
  setActivePageDetails,
  onSaveAndContinue,
  isFirstSave,
  creatingForm,
}: {
  activePageDetails: ActivePageObjType;
  formObject: FormType;
  setActivePageDetails: (item: ActivePageObjType) => void;
  onSaveAndContinue: (status: FormStatus) => void;
  isFirstSave: boolean;
  creatingForm?: boolean;
}) => {
  const {
    hasRecommendedHazards,
    selectedHazards,
    isHazardsAndControlsPage,
    setShowMissingControlsError,
    manuallyAddHazardsHandler,
  } = useFormRendererContext();
  const { state, dispatch } = useContext(CustomisedFromStateContext)!;
  const { setCWFFormStateDirty } = useCWFFormState();

  const [waitingForCreate, setWaitingForCreate] = useState(false);

  const [pageIterationList, setPageIterationList] = useState<
    PageIteratorType[]
  >([]);
  const [currentIndex, setCurrentIndex] = useState<number>(0);
  const toastCtx = useContext(ToastContext);
  const [formStatus, setFormStatus] = useState("in_progress");
  const { project, location, startDate } = router.query;
  const [isRecommendedHazardsModalOpen, setIsRecommendedHazardsModalOpen] =
    useState(false);
  const [showCompleteFormModal, setShowCompleteFormModal] =
    useState<boolean>(false);

  const [formContentBeforeFormSubmit, setFormContentBeforeFormSubmit] =
    useState<FormElementsType[]>([]);

  const isFormSubmisionModalActionTaken = useRef(false);

  useEffect(() => {
    if (formObject.contents.length) {
      setPageIterationList(getPagesIterationArr(formObject.contents));
    }
  }, [formObject]);

  const {
    mutate: updateForm,
    isLoading,
    error,
    responseData,
  } = useRestMutation<any>({
    endpoint: `/forms/${state.form?.id || formObject.id}`,
    method: "put",
    axiosInstance: axiosRest,
    dtoFn: dataForm => dataForm,
  });

  useEffect(() => {
    const token = formEventEmitter.addListener(
      "createFormCompleted",
      (newFormId?: string) => {
        if (isFormSubmisionModalActionTaken.current) {
          if (project)
            router.push(
              `/projects/${project}?location=${location}&startDate=${startDate}`
            );
          else {
            const formId = newFormId || state.form?.id || formObject.id;
            router.push(`/template-forms/view?formId=${formId}`);
          }
          isFormSubmisionModalActionTaken.current = false;

          return;
        } else {
          const formId = newFormId || state.form?.id || formObject.id;
          if (formId && creatingForm) {
            const newUrl = `/template-forms/view?formId=${formId}${
              project
                ? `&project=${project}&location=${location}&startDate=${startDate}`
                : ""
            }`;
            window.history.replaceState(null, "", newUrl);
          }

          //normal save and continue flow
          formEventEmitter.emit(FORM_EVENTS.SAVE_AND_CONTINUE);
          setTimeout(() => {
            formEventEmitter.emit("formUpdated");
          }, 0);
        }
        setWaitingForCreate(false);
      }
    );

    return () => {
      token.remove();
    };
  }, []);

  const { mutate: updateFormWithNewId, isLoading: isLoadingNewId } =
    useRestMutation<any>({
      endpoint: `/forms/${state.form?.id}`,
      method: "put",
      axiosInstance: axiosRest,
      dtoFn: dataForm => dataForm,
    });

  useEffect(() => {
    const newIndex = pageIterationList.findIndex(
      obj => obj.id === activePageDetails?.id
    );
    if (newIndex != currentIndex && newIndex != -1) {
      setCurrentIndex(newIndex);
    }
  }, [activePageDetails]);

  useEffect(() => {
    if (formObject.contents) {
      setPageIterationList(getPagesIterationArr(formObject.contents));
    }
  }, [formObject]);

  useEffect(() => {
    if (currentIndex > 0) {
      setActivePageDetails({
        id: pageIterationList[currentIndex].id,
        parentId: pageIterationList[currentIndex].parentId!,
        type: pageIterationList[currentIndex].type,
        returnToSummaryPage: activePageDetails?.returnToSummaryPage ?? false, // Preserve the flag
        summaryPageId: activePageDetails?.summaryPageId, // Preserve the summary page ID
      });
    }
  }, [currentIndex]);

  const updateFormData = (status: string, data: PageType[]) => {
    if (waitingForCreate) {
      return;
    }

    const currentStatus = formObject?.properties?.status;
    const newStatus = currentStatus === "completed" ? "completed" : status;
    getFormComponentData(formObject, CWFItemType.ReportDate);

    const apiData = {
      contents: cloneDeep([...data]),
      properties: {
        ...formObject.properties,
        status: newStatus,
        report_start_date: formObject?.properties?.report_start_date || null,
      },
      metadata: {
        ...formObject.metadata,
        ...getRegionMetadata(formObject),
      },
      template_id: formObject.template_id,
      created_at: responseData ? (responseData as FormType).created_at : null,
      created_by: formObject.created_by,
      updated_at: responseData ? (responseData as FormType).updated_at : null,
      updated_by: responseData ? (responseData as FormType).updated_by : null,
      component_data: formObject.component_data || null,
    };
    const shouldUseNewId = state.form?.id && state.form.id !== formObject.id;

    if (shouldUseNewId) {
      updateFormWithNewId(apiData);
    } else {
      updateForm(apiData);
    }

    setCWFFormStateDirty(false);
    if (status === "completed") {
      setFormStatus("completed");
    }
  };

  const getToNextPage = (newContentsData: PageType[]) => {
    // Check if we should return to a summary page
    const shouldReturnToSummary =
      activePageDetails?.returnToSummaryPage &&
      activePageDetails?.summaryPageId;

    // Check if there are more pages to navigate through
    const hasMorePages = currentIndex < pageIterationList.length - 1;

    if (shouldReturnToSummary) {
      // Navigate back to the summary page
      navigateToSummaryPage();
      updateFormData("in_progress", newContentsData);
    } else if (hasMorePages) {
      // Move to the next page in sequence
      updateFormData("in_progress", newContentsData);
      navigateToNextSequentialPage(newContentsData);
    }
  };
  const navigateToSummaryPage = () => {
    setActivePageDetails({
      id: activePageDetails?.summaryPageId || "",
      parentId: "root",
      type: CWFItemType.Summary,
    });
  };

  const navigateToNextSequentialPage = (newContentsData: PageType[]) => {
    setCurrentIndex(currentIndex + 1);
    setFormContentBeforeFormSubmit(newContentsData);
  };

  const showFormCompletionModal = (newContentsData: PageType[]) => {
    setShowCompleteFormModal(true);
    setFormContentBeforeFormSubmit(newContentsData);
  };

  useEffect(() => {
    setTimeout(() => {
      if (isFormSubmisionModalActionTaken.current) {
        if (project)
          router.push(
            `/projects/${project}?location=${location}&startDate=${startDate}`
          );
        else router.push("/template-forms");
      }
    }, 50);
  }, [responseData, formStatus]);

  useEffect(() => {
    if (error) {
      toastCtx?.pushToast("error", "Something went wrong");
    }
  }, [error]);

  const decideToMove = (currentPage: PageType | null) => {
    let result = true;
    let errorMessage = "";
    const newContentsArray: PageType[] = [];
    if (currentPage) {
      const listOfWidgets: FormElementsType[] = [];
      for (const content of currentPage.contents) {
        if (
          content.type === CWFItemType.Section &&
          !content.properties.is_repeatable
        ) {
          for (const sectionItem of content.contents) {
            listOfWidgets.push(sectionItem);
          }
        } else {
          if (content.type != CWFItemType.SubPage) {
            listOfWidgets.push(content);
          }
        }
      }

      // Validate all fields at once
      const validationResult = validateField(
        listOfWidgets,
        formObject.component_data
      );
      if (!validationResult.isValid) {
        result = false;
        errorMessage =
          validationResult.errorMessage || "Please enter the required values";

        const hasActivitiesAndTasksError = listOfWidgets.some(
          widget =>
            (widget.type === CWFItemType.ActivitiesAndTasks &&
              validationResult.errorMessage?.includes("activity")) ||
            validationResult.errorMessage?.includes("task")
        );

        if (hasActivitiesAndTasksError) {
          result = false;
          errorMessage = "";
        }
        if (validationResult.itemId) {
          scrollToField(validationResult.itemId);
        }
      }

      if (result) {
        for (let i = 0; i < formObject.contents.length; i++) {
          if (currentPage.type === CWFItemType.Page) {
            if (formObject.contents[i].id === currentPage.id) {
              newContentsArray.push({
                ...currentPage,
                properties: {
                  ...currentPage.properties,
                  page_update_status: "saved",
                },
              });
            } else {
              newContentsArray.push({ ...formObject.contents[i] });
            }
          } else {
            if (formObject.contents[i].id === currentPage.parentId) {
              newContentsArray.push({
                ...formObject.contents[i],
                contents: formObject.contents[i].contents.map(
                  pageContentItem => {
                    if (pageContentItem.id === currentPage.id) {
                      return {
                        ...pageContentItem,
                        properties: {
                          ...pageContentItem.properties,
                          page_update_status: "saved",
                        },
                      };
                    } else {
                      return { ...pageContentItem };
                    }
                  }
                ),
              });
            } else {
              newContentsArray.push({ ...formObject.contents[i] });
            }
          }
        }
        dispatch({
          type: CF_REDUCER_CONSTANTS.PAGE_STATUS_CHANGE,
          payload: newContentsArray,
        });
      }
    }
    return {
      result: result,
      errorMessage: errorMessage,
      newContentsData: newContentsArray,
    };
  };

  const checkIfAllPageSubmittable = (pages: PageType[]) => {
    return pages.every(page => page.properties.page_update_status !== "error");
  };

  const hasEmptyPersonnelComponent = (
    pages: PageType[]
  ): { missing: boolean; firstEmptyFieldId: string } => {
    let missing = false;
    let firstEmptyFieldId = "";

    walk(pages, node => {
      if (node.type === CWFItemType.PersonnelComponent) {
        const rows = node.properties.user_value ?? [];
        if (rows.length === 0 && !missing) {
          missing = true;
          firstEmptyFieldId = node.id;
        }
      }
    });

    return { missing, firstEmptyFieldId };
  };

  useEffect(() => {
    const token = formEventEmitter.addListener("formUpdated", () => {
      const currentActivePage = pageIterationList[currentIndex];

      const { result, errorMessage, newContentsData } =
        decideToMove(currentActivePage);
      if (result) {
        getToNextPage(newContentsData);
        if (checkIfAllPageSubmittable(newContentsData)) {
          handleFormValid();
        }
      } else {
        // Only show toast if there's an error message (skip for ActivitiesAndTasks errors)
        if (errorMessage) {
          toastCtx?.pushToast("error", errorMessage);
        }
        setFormStatusToError(currentActivePage);

        // Reset waitingForCreate if validation fails
        setWaitingForCreate(false);
      }
    });

    return () => {
      token.remove();
    };
  }, [decideToMove, getToNextPage, currentIndex, pageIterationList]);

  const validateCurrentPage = () => {
    let isPageValid = true;
    let errorMessage = "";
    const currentPage = pageIterationList[currentIndex];

    const listOfWidgets: FormElementsType[] = [];
    for (const content of currentPage.contents) {
      if (
        content.type === CWFItemType.Section &&
        !content.properties.is_repeatable
      ) {
        for (const sectionItem of content.contents) {
          listOfWidgets.push(sectionItem);
        }
      } else {
        if (content.type != CWFItemType.SubPage) {
          listOfWidgets.push(content);
        }
      }
    }
    const validationResult = validateField(
      listOfWidgets,
      formObject.component_data
    );
    if (!validationResult.isValid) {
      isPageValid = false;
      errorMessage =
        validationResult.errorMessage || "Please enter the required values";
    }

    return {
      isPageValid,
      errorMessage,
    };
  };

  const handleFormValid = () => {
    dispatch({ type: CF_REDUCER_CONSTANTS.SET_FORM_VALIDITY, payload: true });
  };

  const getHazardSubtitle = () => {
    const currentPage = pageIterationList[currentIndex];
    if (!currentPage) return "";
    for (const content of currentPage.contents) {
      if (content.type === CWFItemType.HazardsAndControls) {
        return content.properties.sub_title;
      }
    }
  };

  const handleSaveAndContinue = async () => {
    setCWFFormStateDirty(false);

    const hasMorePages = currentIndex < pageIterationList.length - 1;
    isFormSubmisionModalActionTaken.current = false;
    formEventEmitter.emit(FORM_EVENTS.SAVE_AND_CONTINUE);
    if (hasMorePages) {
      //when first page saving from form ,we are creating new form
      if (isFirstSave && creatingForm && validateCurrentPage()) {
        setWaitingForCreate(true);
        saveTheFormFistTime(FormStatus.InProgress);
      } else {
        await new Promise(resolve => setTimeout(resolve, 0));
        formEventEmitter.emit("formUpdated");
      }
    } else {
      // Reached the end - show completion modal
      const { isValid, errorMessage } = validateLastPageInputData();
      if (isValid) {
        showFormCompletionModal(state.form.contents);
      } else {
        toastCtx?.pushToast("error", errorMessage || "");
      }
    }
  };
  //TO:DO: This is quick fix , we will modify this functionality once we pick up UX/UI Validations
  const validateLastPageInputData = (): {
    isValid: boolean;
    errorMessage?: string;
  } => {
    const currentPage = pageIterationList[currentIndex];

    const formElements: FormElementsType[] = [];
    for (const content of currentPage.contents) {
      if (
        content.type === CWFItemType.Section &&
        !content.properties.is_repeatable
      ) {
        for (const sectionItem of content.contents) {
          formElements.push(sectionItem);
        }
      } else {
        if (content.type != CWFItemType.SubPage) {
          formElements.push(content);
        }
      }
    }
    // Validate each form element individually
    for (const element of formElements) {
      const result = validateInputData([element]);
      if (!result.isValid) {
        return { isValid: false, errorMessage: result.errorMessage };
      }
    }
    return { isValid: true };
  };

  /**
   * Validates personnel-component attribute rules.
   *
   * Rules enforced
   * ────────────────────────────────────────────────────────────
   * 1.  “single_name”  attributes → at least one crew member owns each.
   * 2.  “multiple_names” attributes → every crew member owns each.
   * 3.  At least one attribute (of any kind) must be selected
   *     for every crew-member row.
   */
  const walk = (nodes: any[], fn: (node: any) => void) => {
    nodes.forEach(node => {
      fn(node);
      if (Array.isArray(node.contents) && node.contents.length) {
        walk(node.contents, fn);
      }
    });
  };

  const validatePersonnelAttributes = (
    pages: PageType[]
  ): { ok: boolean; message?: string } => {
    let firstError: string | undefined;
    let foundValidatableComponent = false;
    const currentPage = pageIterationList[currentIndex];
    const { missing, firstEmptyFieldId } = hasEmptyPersonnelComponent([
      currentPage,
    ]);
    if (missing) {
      formEventEmitter.emit(FORM_EVENTS.SHOW_CREW_ERRORS);
      scrollToField(firstEmptyFieldId);
      return { ok: false, message: "At least one name must be added" };
    }

    walk(pages, node => {
      if (node.type !== "personnel_component") return;

      const attrs = node.properties.attributes ?? [];
      const rows = node.properties.user_value ?? [];
      if (attrs.length === 0 || rows.length === 0) return;
      foundValidatableComponent = true;

      const reqSingle = attrs.filter(
        (a: Attribute) =>
          a.is_required_for_form_completion &&
          a.applies_to_user_value === "single_name"
      );
      const reqMulti = attrs.filter(
        (a: Attribute) =>
          a.is_required_for_form_completion &&
          a.applies_to_user_value === "multiple_names"
      );

      reqSingle.forEach((attr: Attribute) => {
        const owned = rows.some((r: CrewRow) =>
          (r.selected_attribute_ids ?? []).includes(attr.attribute_id)
        );
        if (!owned && !firstError) {
          firstError = `“${attr.attribute_name}” must be checked for at least one crew member.`;
        }
      });

      reqMulti.forEach((attr: Attribute) => {
        const atLeastOneHasIt = rows.some((r: any) =>
          (r.selected_attribute_ids ?? []).includes(attr.attribute_id)
        );
        if (!atLeastOneHasIt && !firstError) {
          firstError = `Select “${attr.attribute_name}” for one or more people.`;
        }
      });
    });

    if (!foundValidatableComponent) return { ok: true };

    return { ok: !firstError, message: firstError };
  };
  const hasUnsignedCrew = (pages: PageType[]): boolean => {
    const hasUnsignedInContents = (nodes: PageType[]): boolean =>
      nodes.some(page =>
        page.contents.some(child => {
          if (child.type === "personnel_component") {
            const rows = child.properties.user_value ?? [];
            const unsignedRow = rows.some(
              (row: any) => !row.crew_details?.signature
            );
            if (unsignedRow) {
              scrollToField(child.id);
            }
            return unsignedRow;
          }
          if (child.type === "page" || child.type === "sub_page") {
            return hasUnsignedInContents([child]);
          }
          return false;
        })
      );

    return hasUnsignedInContents(pages);
  };

  const findFirstHazardNeedingControls = (
    hazards: Hazards[]
  ): string | null => {
    for (const hazard of hazards) {
      if (hazard.noControlsImplemented === true) {
        continue;
      }

      const hasSelectedControls =
        hazard.controls &&
        hazard.controls.some((control: any) => control.selected === true);

      if (!hasSelectedControls) {
        return hazard.id;
      }
    }
    return null;
  };

  const handleButtonClick = () => {
    const currentPage = pageIterationList[currentIndex];
    const attrCheck = validatePersonnelAttributes([currentPage]);
    if (!attrCheck.ok) {
      formEventEmitter.emit(FORM_EVENTS.SHOW_ATTR_ERRORS);
      toastCtx?.pushToast("error", attrCheck.message!);
      return;
    }

    if (hasUnsignedCrew([currentPage])) {
      toastCtx?.pushToast("error", "Please sign all selected crew members.");
      return;
    }

    if (
      isHazardsAndControlsPage &&
      !validateAllHazards(
        getVisibleHazards(selectedHazards, state.form?.component_data)
      )
    ) {
      setShowMissingControlsError(true);

      const firstHazardNeedingControls = findFirstHazardNeedingControls(
        getVisibleHazards(selectedHazards, state.form?.component_data)
      );

      if (firstHazardNeedingControls) {
        scrollToField(firstHazardNeedingControls);
      }

      return;
    }
    if (isHazardsAndControlsPage && hasRecommendedHazards) {
      setIsRecommendedHazardsModalOpen(true);
    } else {
      handleSaveAndContinue();
    }
  };

  const setFormStatusToError = (currentActivePage: any) => {
    const newContentsArray = formObject.contents.map(page => {
      if (currentActivePage.type === CWFItemType.Page) {
        return page.id === currentActivePage.id
          ? {
              ...currentActivePage,
              properties: {
                ...currentActivePage.properties,
                page_update_status: "error",
              },
            }
          : { ...page };
      }
    });

    dispatch({
      type: CF_REDUCER_CONSTANTS.PAGE_STATUS_CHANGE,
      payload: newContentsArray,
    });
  };

  const keepFormInProgress = () => {
    setShowCompleteFormModal(false);
    isFormSubmisionModalActionTaken.current = true;

    // Set page status to 'default' unless already completed ('saved')
    const updatedFormContents = formContentBeforeFormSubmit.map(element => ({
      ...element,
      properties: {
        ...element.properties,
        page_update_status:
          element.properties.page_update_status === "saved"
            ? "saved"
            : "default",
      },
    }));
    if (isFirstSave && creatingForm) {
      saveTheFormFistTime(FormStatus.InProgress);
    } else {
      updateFormData("in_progress", updatedFormContents);
    }
  };
  const completeForm = () => {
    isFormSubmisionModalActionTaken.current = true;
    setShowCompleteFormModal(false);

    if (validateAllPagesOnComplete()) {
      //Changing page status to completed (if we have optional fields)
      const updatedFormContents = formContentBeforeFormSubmit.map(element => ({
        ...element,
        properties: {
          ...element.properties,
          page_update_status: "saved",
        },
      }));
      isFormSubmisionModalActionTaken.current = true;

      if (isFirstSave && creatingForm) {
        saveTheFormFistTime(FormStatus.Completed);
      } else {
        updateFormData("completed", updatedFormContents);
      }
    } else {
      dispatch({
        type: CF_REDUCER_CONSTANTS.SET_FORM_VALIDITY,
        payload: false,
      });
      // toastCtx?.pushToast(
      //   "error",
      //   "Please Enter all required values in the form"
      // );
    }
  };

  const saveTheFormFistTime = (status: FormStatus) => {
    setWaitingForCreate(true);
    onSaveAndContinue(status);
  };

  const validateAllPagesOnComplete = () => {
    //Validate Hazards
    const pageWithHazards = formContentBeforeFormSubmit.find(page =>
      page.contents.some(item => item.type === CWFItemType.HazardsAndControls)
    );

    //Validate Hazards & controls only if Hazards & control component added to form
    if (
      pageWithHazards &&
      !validateAllHazards(
        getVisibleHazards(selectedHazards, state.form?.component_data)
      )
    ) {
      pageWithHazards.properties = {
        ...pageWithHazards.properties,
        page_update_status: "error",
      };
      setShowMissingControlsError(true);

      const firstHazardNeedingControls = findFirstHazardNeedingControls(
        getVisibleHazards(selectedHazards, state.form?.component_data)
      );

      if (firstHazardNeedingControls) {
        scrollToField(firstHazardNeedingControls);
      }

      return false;
    }
    //Validate All Other fields
    if (!isFormValid(formContentBeforeFormSubmit, state.form.component_data)) {
      return false;
    }
    return true;
  };

  return (
    <>
      <footer className="flex flex-col">
        <ButtonPrimary
          loading={
            state.form.isDisabled ||
            isLoading ||
            isLoadingNewId ||
            waitingForCreate
          }
          label={
            currentIndex < pageIterationList.length - 1
              ? "Save and Continue"
              : "Complete Form"
          }
          onClick={handleButtonClick}
        />
      </footer>
      <RecommendedHazardsModal
        isOpen={isRecommendedHazardsModalOpen}
        setOpen={setIsRecommendedHazardsModalOpen}
        save={handleSaveAndContinue}
        manuallyAddHazardsHandler={manuallyAddHazardsHandler}
        subTitle={getHazardSubtitle()}
      />
      <Modal
        title="Complete Form?"
        size="lg"
        isOpen={showCompleteFormModal}
        closeModal={() => setShowCompleteFormModal(false)}
      >
        <div className="mb-3 border-b pb-4">
          Confirming this will mark the form as completed. Alternatively, you
          can keep the form in progress and complete it later.
        </div>

        <div className="flex justify-end gap-3">
          <ButtonRegular
            label="Keep Form In progress"
            className="border"
            onClick={keepFormInProgress}
          />
          <ButtonPrimary label={`Complete Form`} onClick={completeForm} />
        </div>
      </Modal>
    </>
  );
};

export default SaveAndContinue;
