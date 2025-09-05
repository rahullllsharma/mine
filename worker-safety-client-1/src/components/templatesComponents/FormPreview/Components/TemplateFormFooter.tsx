import type {
  ActivePageObjType,
  ApiFormDataType,
  FormStatus,
  FormType,
  ProjectDetailsType,
  RestMutationResponse,
  UserFormMode,
} from "../../customisedForm.types";
import { useContext, useState } from "react";
import useRestMutation from "@/hooks/useRestMutation";

import axiosRest from "@/api/customFlowApi";
import ButtonPrimary from "@/components/shared/button/primary/ButtonPrimary";
import ButtonSecondary from "@/components/shared/button/secondary/ButtonSecondary";
import CustomisedFromStateContext from "@/context/CustomisedDataContext/CustomisedFormStateContext";
import { formEventEmitter } from "@/context/CustomisedDataContext/CustomisedFormStateProvider";
import { CF_REDUCER_CONSTANTS } from "@/utils/customisedFormUtils/customisedForm.constants";
import { UserFormModeTypes } from "../../customisedForm.types";
import { getRegionMetadata } from "../../customisedForm.utils";
import SaveAndContinue from "./SaveAndContinue";

type TemplateFormFooterProps = {
  mode: UserFormMode;
  setActivePageDetails: (item: ActivePageObjType) => void;
  onClickSaveAndDraft: (data: any) => void;
  activePageDetails: ActivePageObjType;
  formObject: FormType;
  isEditOrTemplateMode: boolean;
  handleClickOnClose: () => void;
  projectDetails?: ProjectDetailsType;
  creatingForm: boolean; // Added type annotation for clarity
};

export default function TemplateFormFooter({
  mode,
  setActivePageDetails,
  onClickSaveAndDraft,
  isEditOrTemplateMode,
  activePageDetails,
  formObject,
  handleClickOnClose,
  projectDetails,
  creatingForm,
}: TemplateFormFooterProps) {
  const [isFirstSave, setIsFirstSave] = useState(true);
  const { dispatch } = useContext(CustomisedFromStateContext)!;

  const { mutate: createForm } = useRestMutation<ApiFormDataType>({
    endpoint: "/forms/",
    method: "post",
    axiosInstance: axiosRest,
    dtoFn: dataForm => dataForm,
    mutationOptions: {
      onSuccess: (data: any) => {
        if (data) {
          dispatch({
            type: CF_REDUCER_CONSTANTS.CHANGE_INITIAL_STATE,
            payload: { ...data.data },
          });
          setIsFirstSave(false);
          setTimeout(() => {
            formEventEmitter.emit("createFormCompleted", data.data.id);
          }, 100);
        }
      },
    },
  }) as RestMutationResponse<ApiFormDataType>;

  const getWorkTypesAssociatedWithTemplate = () => {
    const value = localStorage.getItem("selectedWorkTypes");
    if (value) {
      return JSON.parse(value);
    } else {
      return [];
    }
  };

  const workTypesData = {
    work_types:
      formObject.metadata?.work_types || getWorkTypesAssociatedWithTemplate(),
  };

  const supervisorMetaData = {
    supervisor: formObject.metadata?.supervisor || [],
  };

  const handleSaveAndContinue = (status: FormStatus) => {
    if (isFirstSave && creatingForm) {
      const hazardMetaData = {
        is_energy_wheel_enabled:
          formObject.metadata?.is_energy_wheel_enabled ?? true,
      };

      const apiData: ApiFormDataType = {
        contents: [...formObject.contents],
        properties: {
          ...formObject.properties,
          status: status,
          ...((projectDetails?.startDate
            ? {
                report_start_date: new Date(projectDetails.startDate) as Date,
              }
            : {}) as { report_start_date?: Date }),
        },
        metadata: projectDetails
          ? {
              work_package: {
                name: String(projectDetails?.project?.name),
                id: String(projectDetails?.project?.id),
              },
              location: {
                name: String(projectDetails?.project?.locations?.[0]?.name),
                id: String(projectDetails?.project?.locations?.[0]?.id),
              },
              ...getRegionMetadata(formObject, projectDetails),
              ...hazardMetaData,
              ...workTypesData,
            }
          : {
              ...getRegionMetadata(formObject),
              ...hazardMetaData,
              ...workTypesData,
              ...supervisorMetaData,
            },
        template_id: formObject.id,
        component_data: formObject.component_data,
      };
      createForm(apiData);
    } else {
      // If not creating form, immediately emit the createFormCompleted event
      // to trigger the normal save and continue flow
      setTimeout(() => {
        formEventEmitter.emit("createFormCompleted");
      }, 0);
    }
  };

  return (
    <div className="">
      {isEditOrTemplateMode &&
        (mode === UserFormModeTypes.PREVIEW ||
        mode === UserFormModeTypes.PREVIEW_PROPS ? (
          <div className="flex gap-2 justify-end mt-2">
            <ButtonSecondary
              label="Close"
              onClick={() => handleClickOnClose()}
            />
            <ButtonPrimary
              label="Copy as Draft"
              onClick={() => {
                const apiData = {
                  contents: [...formObject.contents],
                  properties: { ...formObject.properties, status: "draft" },
                  settings: { ...formObject.settings },
                  pre_population_rule_paths:
                    formObject.pre_population_rule_paths
                      ? { ...formObject.pre_population_rule_paths }
                      : null,
                  metadata: formObject.metadata,
                };
                onClickSaveAndDraft(apiData);
              }}
            />
          </div>
        ) : (
          <SaveAndContinue
            formObject={formObject}
            activePageDetails={activePageDetails}
            setActivePageDetails={setActivePageDetails}
            onSaveAndContinue={handleSaveAndContinue}
            isFirstSave={isFirstSave}
            creatingForm={creatingForm}
          />
        ))}
    </div>
  );
}
