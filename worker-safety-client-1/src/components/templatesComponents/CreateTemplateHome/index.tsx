import type { FormType } from "../customisedForm.types";
import React, { useContext, useEffect, useState } from "react";
import { useRouter } from "next/router";
import CustomisedFromStateContext from "@/context/CustomisedDataContext/CustomisedFormStateContext";
import useRestQuery from "@/hooks/useRestQuery";
import axiosRest from "@/api/customFlowApi";
import { CF_REDUCER_CONSTANTS } from "@/utils/customisedFormUtils/customisedForm.constants";
import { UserFormModeTypes } from "../customisedForm.types";
import LinkComponent from "../LinkComponent";
import TemplateFormNameInput from "../CreateTemplateLayout/TemplateFormNameInput";
import CreateTemplateLayout from "../CreateTemplateLayout";
import CSActionButtons from "../ButtonComponents/CFActionButtons";
import FormPreview from "../FormPreview";
import ButtonIcon from "../../shared/button/icon/ButtonIcon";
import TemplateSettingsComponent from "../CreateTemplateLayout/TemplateSettingsComponent";
import style from "./createTemplateHome.module.scss";

const CreateTemplateHome = () => {
  const { state, dispatch } = useContext(CustomisedFromStateContext)!;
  const router = useRouter();
  const { templateId } = router.query || null;
  const [showSettings, setShowSettings] = useState(false);
  const [hasVisitedWorkTypes, setHasVisitedWorkTypes] = useState(false);
  const [hasModifiedWorkTypes, setHasModifiedWorkTypes] = useState(false);

  const { data } = useRestQuery<FormType>({
    key: [`template-${templateId}`],
    endpoint: "/templates/" + templateId,
    axiosConfig: {
      params: {
        prepopulate: false,
      },
    },
    axiosInstance: axiosRest,
    queryOptions: {
      enabled: !!templateId,
      staleTime: Infinity,
    },
  });

  useEffect(() => {
    if (data) {
      dispatch({
        type: CF_REDUCER_CONSTANTS.CHANGE_INITIAL_STATE,
        payload: { ...data },
      });
    }
  }, [data]);

  const toggleSettings = () => {
    setShowSettings(!showSettings);
  };

  return (
    <div className="flex flex-col bg-brand-gray-10 overflow-y-auto lg:overflow-hidden w-full relative">
      <div
        className={`fixed inset-0 z-20 transition-transform duration-300 ease-in-out transform ${
          showSettings ? "translate-x-0" : "translate-x-full"
        }`}
      >
        <div
          className={`absolute inset-0 transition-transform duration-300 ease-in-out ${
            showSettings ? "translate-x-0" : "translate-x-full"
          } bg-white`}
        >
          <TemplateSettingsComponent
            showSettings={showSettings}
            onClose={() => setShowSettings(false)}
            onWorkTypesVisited={() => setHasVisitedWorkTypes(true)}
            onWorkTypesModified={() => setHasModifiedWorkTypes(true)}
          />
        </div>
      </div>
      <div
        className={`relative z-10 transition-transform duration-300 ease-in-out transform h-screen ${
          showSettings ? "-translate-x-full" : "translate-x-0"
        }`}
      >
        {state.formBuilderMode === UserFormModeTypes.BUILD ? (
          <div className="h-full">
            <header className="shadow-5 py-4 px-6 bg-white relative">
              <LinkComponent
                href={templateId ? "/templates?tab=drafts" : "/templates"}
                labelName="Templates"
              />
              <TemplateFormNameInput />
              <ButtonIcon
                iconName="settings_filled"
                className="leading-5 absolute right-6 top-4"
                onClick={toggleSettings}
                title="Settings"
              />
            </header>
            <CreateTemplateLayout />
          </div>
        ) : (
          <div className={style.previewComponentHolder}>
            <FormPreview
              formObject={state.form}
              mode={UserFormModeTypes.PREVIEW}
              linkObj={{ linkHref: "/templates", linkName: "Templates" }}
            />
          </div>
        )}
        <CSActionButtons
          actionModeProp={templateId ? "UPDATE" : "SAVE"}
          templateId={templateId}
          hasVisitedWorkTypes={hasVisitedWorkTypes}
          hasModifiedWorkTypes={hasModifiedWorkTypes}
        />
      </div>
    </div>
  );
};

export default CreateTemplateHome;
