import type {
  FormBuilderActionModeType,
  FormBuilderAlertType,
  FormType,
  PageType,
} from "../../customisedForm.types";
import React, { useContext, useEffect, useState } from "react";
import cx from "classnames";
import router from "next/router";
import { isMobile, isTablet } from "react-device-detect";
import { get, trim } from "lodash-es";
import { useQuery } from "@apollo/client";
import ButtonPrimary from "@/components/shared/button/primary/ButtonPrimary";
import ButtonSecondary from "@/components/shared/button/secondary/ButtonSecondary";
import useRestMutation from "@/hooks/useRestMutation";
import axiosRest from "@/api/customFlowApi";
import CustomisedFromStateContext from "@/context/CustomisedDataContext/CustomisedFormStateContext";
import ToastContext from "@/components/shared/toast/context/ToastContext";
import { config } from "@/config";
import { calculatePrePopulationPath } from "@/context/CustomisedDataContext/helpers/customisedFormStateProviderhelpers";
import TenantWorkTypes from "@/graphql/queries/tenantWorkTypes.gql";
import { CWFItemType, UserFormModeTypes } from "../../customisedForm.types";
import CSFLoader from "../../LoaderComponent/CSFLoader";
import style from "./cfactionStyles.module.scss";
import ActionAlertPopUp from "./ActionAlertPopUp";

interface CSActionButtonsProps {
  actionModeProp: FormBuilderActionModeType;
  templateId?: string | string[] | undefined;
  hasVisitedWorkTypes?: boolean;
  hasModifiedWorkTypes?: boolean;
}

const CSActionButtons = ({
  actionModeProp,
  templateId,
  hasVisitedWorkTypes = false,
  hasModifiedWorkTypes = false,
}: CSActionButtonsProps) => {
  const { state, dispatch } = useContext(CustomisedFromStateContext)!;
  const [alertPopUp, setAlertPopUp] = useState(false);
  const [alertMode, setAlertMode] = useState<FormBuilderAlertType | null>(null);
  const [actionMode, setActionMode] =
    useState<FormBuilderActionModeType>(actionModeProp);
  const toastCtx = useContext(ToastContext);
  const [savedId, setSavedId] = useState(templateId || null);
  const [templateUniqueId, setTemplateUniqueId] = useState(
    state.form.properties?.template_unique_id || null
  );

  const { data: workTypesData } = useQuery(TenantWorkTypes, {
    fetchPolicy: "cache-and-network",
  });

  const getAPIEndpoint = (type: FormBuilderActionModeType): string => {
    if (templateUniqueId) {
      return `${config.workerSafetyCustomWorkFlowUrlRest}/templates/` + savedId;
    } else {
      if (type === "UPDATE") {
        return (
          `${config.workerSafetyCustomWorkFlowUrlRest}/templates/` + savedId
        );
      } else {
        return `${config.workerSafetyCustomWorkFlowUrlRest}/templates/`;
      }
    }
  };

  const getMethodForAPICall = (type: FormBuilderActionModeType) => {
    if (templateUniqueId) {
      return "put";
    } else {
      if (type === "UPDATE") {
        return "put";
      } else {
        return "post";
      }
    }
  };

  const {
    mutate: apiCallForTemplate,
    isLoading,
    error,
    responseData,
  } = useRestMutation<any>({
    endpoint: getAPIEndpoint(actionMode),
    method: getMethodForAPICall(actionMode),
    axiosInstance: axiosRest,
    dtoFn: data => data,
  });

  useEffect(() => {
    if (state.form) {
      setTemplateUniqueId(state.form.properties.template_unique_id || null);
    }
  }, [state]);

  const getAlert = (data: any) => {
    if (actionMode === "PUBLISH") {
      toastCtx?.pushToast(
        "success",
        `${data.properties.title} version ${data.version} was published successfully`
      );
      router.push("/templates");
    } else {
      if (data.id) {
        setSavedId(data.id);
      }
      if (data.properties.template_unique_id) {
        setTemplateUniqueId(data.properties.template_unique_id);
      }
      setActionMode("UPDATE");
      if (actionMode === "SAVE") {
        router.push(`/templates/create?templateId=${data.id}`);
      }

      toastCtx?.pushToast("success", "Your template has been saved");
      if (alertMode === "CLOSE") {
        router.push("/templates?tab=draft");
      }
    }
  };

  useEffect(() => {
    if (error) {
      console.log(error);
    }
    if (responseData) {
      getAlert(responseData);
    }
  }, [error, responseData]);

  const apiCall = async (type: FormBuilderActionModeType) => {
    const title = get(state, "form.properties.title");
    if (!title || !trim(title)) {
      toastCtx?.pushToast(
        "error",
        "Please enter a title for the template, If already entered click on ✔ icon to confirm "
      );
      return;
    }
    setActionMode(type);

    let updatedSettings = { ...state.form.settings };
    if (
      actionModeProp === "SAVE" &&
      workTypesData &&
      workTypesData.tenantWorkTypes
    ) {
      if (hasVisitedWorkTypes && hasModifiedWorkTypes) {
        updatedSettings = {
          ...updatedSettings,
          work_types: state.form.settings.work_types || [],
        };
      } else {
        updatedSettings = {
          ...updatedSettings,
          work_types: workTypesData.tenantWorkTypes.map((wt: any) => ({
            id: wt.id,
            name: wt.name,
            tenantId: wt.tenantId,
            __typename: wt.__typename,
          })),
        };
      }
    }

    const apiData = {
      contents: [...state.form.contents],
      properties: {
        ...state.form.properties,
        status: type === "PUBLISH" ? "published" : "draft",
      },
      settings: updatedSettings,
      created_at: responseData ? (responseData as FormType).created_at : null,
      created_by: responseData ? (responseData as FormType).created_by : null,
      updated_at: responseData ? (responseData as FormType).updated_at : null,
      pre_population_rule_paths: calculatePrePopulationPath(
        state.form.contents
      ),
      updated_by: responseData ? (responseData as FormType).updated_by : null,
      metadata: state.form.metadata,
    };
    apiCallForTemplate(apiData);
  };

  const moveAheadForAPICall = (contentsArray: PageType[]) => {
    if (!contentsArray.length) {
      return {
        moveAhead: false,
        message: "Empty Templates cannot be published",
      };
    }

    for (const page of contentsArray) {
      const { type, contents } = page;
      if (type === CWFItemType.Page) {
        if (!contents.length) {
          return {
            moveAhead: false,
            message: `Empty Templates cannot be published, Check page '${page.properties.title}'`,
          };
        }

        for (const content of page.contents) {
          const { type: contentType, contents: sectionContentsArray } = content;
          if (
            contentType === CWFItemType.Section &&
            !sectionContentsArray.length
          ) {
            return {
              moveAhead: false,
              message: `Empty Templates cannot be published, Check section '${content.properties.title}' of page'${page.properties.title}'`,
            };
          }
        }
      }
    }

    return { moveAhead: true, message: "" };
  };

  return alertPopUp ? (
    <ActionAlertPopUp
      isOpen={alertPopUp}
      setIsOpen={setAlertPopUp}
      mode={alertMode}
      closeAction={
        alertMode === "CLOSE"
          ? () => {
              router.push("/templates?tab=draft");
            }
          : () => {
              setAlertPopUp(false);
            }
      }
      successAction={
        alertMode === "CLOSE"
          ? () => {
              apiCall("SAVE");
              setAlertPopUp(false);
            }
          : () => {
              const { moveAhead, message } = moveAheadForAPICall(
                state.form.contents
              );
              if (moveAhead) {
                apiCall("PUBLISH");
              } else {
                toastCtx?.pushToast("error", message);
              }

              setAlertPopUp(false);
            }
      }
    />
  ) : isLoading ? (
    <CSFLoader />
  ) : (
    <div
      className={
        state.formBuilderMode === UserFormModeTypes.BUILD
          ? style.actionButtonParent
          : style.actionButtonParentPreview
      }
    >
      <div
        className={cx(
          state.formBuilderMode === UserFormModeTypes.BUILD
            ? style.buttonContainer
            : style.buttonContainerPreview,
          { ["mb-16"]: isMobile || isTablet }
        )}
      >
        {state.formBuilderMode === UserFormModeTypes.BUILD ? (
          <ButtonSecondary
            label="Close"
            onClick={() => {
              setAlertMode("CLOSE");
              setAlertPopUp(true);
            }}
          />
        ) : null}
        {state.formBuilderMode === UserFormModeTypes.BUILD ? (
          <ButtonSecondary
            label={actionMode === "UPDATE" ? "Update" : "Save"}
            onClick={() => apiCall("SAVE")}
          />
        ) : null}
        <ButtonSecondary
          label={
            state.formBuilderMode === UserFormModeTypes.BUILD
              ? "Preview"
              : "Back to Builder Mode"
          }
          onClick={() => {
            dispatch({
              type: "CHANGE_BUILDER_MODE",
              payload:
                state.formBuilderMode === UserFormModeTypes.BUILD
                  ? UserFormModeTypes.PREVIEW
                  : UserFormModeTypes.BUILD,
            });
          }}
        />
        {state.formBuilderMode === UserFormModeTypes.BUILD ? (
          <ButtonPrimary
            label="Publish"
            onClick={() => {
              setAlertMode("PUBLISH");
              setAlertPopUp(true);
            }}
          />
        ) : null}
      </div>
    </div>
  );
};

export default CSActionButtons;
