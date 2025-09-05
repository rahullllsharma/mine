import type { NavigationOption } from "../../../navigation/Navigation";
import type { TemplateSettings } from "../../customisedForm.types";
import { useContext, useEffect, useMemo, useState } from "react";
import { FormProvider, useForm } from "react-hook-form";
import PageFooter from "@/components/layout/pageFooter/PageFooter";
import Navigation from "@/components/navigation/Navigation";
import Button from "@/components/shared/button/Button";
import ToastContext from "@/components/shared/toast/context/ToastContext";
import TemplateSettingsForm from "@/components/templatesComponents/CreateTemplateLayout/TemplateSettingsComponent/TemplateSettingsForm/TemplateSettingsForm";
import FormHeading from "@/components/templatesComponents/FormPreview/Components/FormHeading";
import CustomisedFromStateContext from "@/context/CustomisedDataContext/CustomisedFormStateContext";
import { CF_REDUCER_CONSTANTS } from "@/utils/customisedFormUtils/customisedForm.constants";

interface TemplateSettingsProps {
  showSettings: boolean;
  onClose: () => void;
  onWorkTypesVisited?: () => void;
  onWorkTypesModified?: () => void;
}

const defaultSettings: TemplateSettings = {
  availability: {
    adhoc: {
      selected: true,
    },
    work_package: {
      selected: false,
    },
  },
  edit_expiry_days: 0,
  report_date: {
    required: false,
    field_id: "",
    field_path: "",
  },
  copy_and_rebrief: {
    is_copy_enabled: false,
    is_rebrief_enabled: false,
  }
};

const TemplateSettingsComponent: React.FC<TemplateSettingsProps> = ({
  showSettings,
  onClose,
  onWorkTypesVisited,
  onWorkTypesModified,
}) => {
  const { state, dispatch } = useContext(CustomisedFromStateContext)!;
  const [selectedTab, setSelectedTab] = useState(0);
  const settings = state.form.settings || defaultSettings;
  const toastCtx = useContext(ToastContext);

  const methods = useForm({
    defaultValues: settings,
    mode: "onChange",
  });

  const {
    handleSubmit,
    formState: { errors, isValid },
    trigger,
    reset,
    getValues,
  } = methods;

  const formObject = useMemo(() => {
    return state.form;
  }, [state.form]);

  const tabsOptions: NavigationOption[] = [
    {
      id: 0,
      name: "Template Availability",
    },
    {
      id: 1,
      name: "Edit Period",
    },
    {
      id: 2,
      name: "Work Types",
    },
    {
      id: 3,
      name: "Linked Forms",
    },
  ];

  // Reset selectedTab to 0 whenever settings screen is opened
  useEffect(() => {
    if (showSettings) {
      setSelectedTab(0);
    }
  }, [showSettings]);

  // Track if user has visited work types tab
  useEffect(() => {
    if (selectedTab === 2) {
      onWorkTypesVisited?.();
    }
  }, [selectedTab, onWorkTypesVisited]);

  // Handle tab change with validation
  const handleTabChange = async (newTab: number) => {
    // Validate current tab before allowing change
    const isCurrentTabValid = await trigger();
    const currentValues = getValues();

    if (isCurrentTabValid) {
      // Update the form state with current values before changing tabs
      dispatch({
        type: CF_REDUCER_CONSTANTS.CHANGE_INITIAL_STATE,
        payload: {
          ...state.form,
          settings: currentValues,
        },
      });
      setSelectedTab(newTab);
    }
  };

  const handleClose = async () => {
    const isFormValid = await trigger();
    const currentValues = getValues();

    if (!isFormValid || Object.keys(errors).length > 0) {
      toastCtx?.pushToast(
        "error",
        "At least one or more required settings have been left unfilled. Please go back and verify your settings."
      );
      return;
    }

    // Update the form state with current values before closing
    dispatch({
      type: CF_REDUCER_CONSTANTS.CHANGE_INITIAL_STATE,
      payload: {
        ...state.form,
        settings: currentValues,
      },
    });
    onClose();
  };

  const onSubmit = async () => {
    const isFormValid = await trigger();

    if (isFormValid) {
      const updatedData = getValues();

      dispatch({
        type: CF_REDUCER_CONSTANTS.CHANGE_INITIAL_STATE,
        payload: {
          ...state.form,
          settings: updatedData,
        },
      });
      toastCtx?.pushToast("success", "Settings updated successfully");
      onClose();
    } else {
      console.log("Validation failed. Fix errors before saving.");
    }
  };

  // Update form values when settings change
  useEffect(() => {
    if (settings) {
      reset(settings);
    }
  }, [settings, reset]);

  return (
    <div className="flex flex-col w-full min-h-screen">
      <header className="flex flex-row justify-between bg-white w-full shadow-md py-4 px-6 relative items-center">
        <div>
          {showSettings && (
            <Button
              label="Template Home"
              onClick={handleClose}
              className="font-medium text-brand-urbint-50 active:text-brand-urbint-60 hover:text-brand-urbint-40"
              iconStart="chevron_big_left"
            />
          )}
          <FormHeading formObject={formObject} />
        </div>
      </header>
      <div className="flex-1 overflow-y-auto">
        <section className="responsive-padding-x flex md:flex-row flex-col h-full">
          <Navigation
            options={tabsOptions}
            onChange={handleTabChange}
            selectedIndex={selectedTab}
            sidebarClassNames="bg-white p-3 min-w-[200px] !block"
            selectClassNames="ml-3 w-60 mb-4 !hidden"
          />
          <div className="p-0 bg-white w-full max-h-[calc(100vh-10rem)] overflow-y-auto">
            <FormProvider {...methods}>
              <TemplateSettingsForm
                selectedTab={selectedTab}
                settings={settings}
                onWorkTypesModified={onWorkTypesModified}
              />
            </FormProvider>
          </div>
        </section>
      </div>
      <PageFooter
        onPrimaryClick={handleSubmit(onSubmit)}
        primaryActionLabel="Save"
        isPrimaryActionDisabled={!isValid || Object.keys(errors).length > 0}
        className="fixed bottom-0 left-0 w-full z-50"
      />
    </div>
  );
};

export default TemplateSettingsComponent;
