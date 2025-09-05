import type {
  FieldTypes,
  UserFormMode,
} from "../templatesComponents/customisedForm.types";
import cn from "classnames";
import { useContext, useMemo, useState, createContext } from "react";
import { v4 as uuidv4 } from "uuid";
import BooleanComponent from "@/components/dynamicForm/boolean";
import ReportDateComponent from "@/components/dynamicForm/reportDate";
import ContractorComponent from "@/components/dynamicForm/contractor";
import Choice from "@/components/dynamicForm/choice";
import Dropdown from "@/components/dynamicForm/dropdown";
import LocationInput from "@/components/dynamicForm/locationInput";
import Text from "@/components/dynamicForm/text";
import ButtonPrimary from "@/components/shared/button/primary/ButtonPrimary";
import ButtonRegular from "@/components/shared/button/regular/ButtonRegular";
import DropDownField from "@/components/shared/dropdown/Dropdown";
import DateTime from "@/components/dynamicForm/dateTime";
import Email from "@/components/dynamicForm/email";
import NumberInput from "@/components/dynamicForm/numberInput";
import PhoneNumber from "@/components/dynamicForm/phoneNumber";
import Modal from "@/components/shared/modal/Modal";
import ToastContext from "@/components/shared/toast/context/ToastContext";
import RegionComponent from "@/components/dynamicForm/region";
import CheckboxComponent from "@/components/dynamicForm/checkbox";
import { UserFormModeTypes } from "../templatesComponents/customisedForm.types";
import CustomisedFromStateContext from "../../context/CustomisedDataContext/CustomisedFormStateContext";
import { CF_REDUCER_CONSTANTS } from "../../utils/customisedFormUtils/customisedForm.constants";

type TabItem = {
  name: string;
  component: (props: any) => JSX.Element;
  type: FieldTypes;
};

const fields: TabItem[] = [
  { name: "Choice", component: Choice, type: "choice" },
  { name: "Checkbox", component: CheckboxComponent, type: "checkbox" },
  { name: "Dropdown", component: Dropdown, type: "dropdown" },
  { name: "Yes or No", component: BooleanComponent, type: "yes_or_no" },
];

const inputTypes: TabItem[] = [
  { name: "Text", component: Text, type: "input_text" },
  { name: "Number", component: NumberInput, type: "input_number" },
  { name: "Phone number", component: PhoneNumber, type: "input_phone_number" },
  { name: "Date & Time", component: DateTime, type: "input_date_time" },
  { name: "Location", component: LocationInput, type: "input_location" },
  { name: "Email", component: Email, type: "input_email" },
];

// Helper function to determine initial dropdown state
const getInitialDropdownState = (
  type: FieldTypes | undefined
): "input" | "reference" | null => {
  if (!type) return null;
  if (inputTypes.some(t => t.type === type)) return "input";
  if (referenceTypes.some(t => t.type === type)) return "reference";
  return null;
};
// Reference Fields (Inside Reference Dropdown)
const referenceTypes: TabItem[] = [
  { name: "Contractor", component: ContractorComponent, type: "contractor" },
  { name: "Region", component: RegionComponent, type: "region" },
  { name: "Report Date", component: ReportDateComponent, type: "report_date" },
];

type TabLabel = TabItem["type"];

const getComponent = (tab: TabLabel) => {
  const foundTab = [...fields, ...inputTypes, ...referenceTypes].find(
    t => t.type === tab
  );
  return foundTab ? foundTab.component : undefined;
};

type Props = {
  isOpen: boolean;
  onClose: () => void;
  onAdd: (value: any) => void;
  mode?: UserFormMode;
  content?: any;
  isRepeatableSection?: boolean;
  //activeWidgetDetails: WidgetType;
};

export const RepeatSectionContext = createContext<boolean>(false);

function DynamicFormModal(props: Props) {
  const [currentTab, setTab] = useState<TabLabel>(
    props.mode === UserFormModeTypes.EDIT ||
      props.mode === UserFormModeTypes.PREVIEW
      ? props.content?.type
      : "choice"
  );
  // Initialize activeDropdown based on the current tab type
  const [activeDropdown, setActiveDropdown] = useState<
    "input" | "reference" | null
  >(getInitialDropdownState(props.content?.type));
  // Track if any data has been entered/changed
  const [hasDataEntered, setHasDataEntered] = useState(false);
  const { state, dispatch } = useContext(CustomisedFromStateContext)!;
  const Component = useMemo(() => getComponent(currentTab), [currentTab]);
  const toastCtx = useContext(ToastContext);

  const filteredReferenceTypes = useMemo(() => {
    return referenceTypes.filter(type => {
      switch (type.type) {
        case "report_date":
          if (state.form.metadata?.is_report_date_included) {
            return false;
          }
          break;
        case "contractor":
          if (state.form.metadata?.is_contractor_included) {
            return false;
          }
          break;
        case "region":
          if (state.form.metadata?.is_region_included) {
            return false;
          }
          break;
      }
      return true;
    });
  }, [
    state.form.metadata?.is_report_date_included,
    state.form.metadata?.is_contractor_included,
    state.form.metadata?.is_region_included,
  ]);

  const resetTabState = () => {
    if (
      props.mode !== UserFormModeTypes.EDIT &&
      props.mode !== UserFormModeTypes.PREVIEW
    ) {
      setTab("choice");
      setActiveDropdown(null);
      setHasDataEntered(false);
    }
  };

  // Callback for child components to indicate data has been entered
  const handleDataChange = () => {
    setHasDataEntered(true);
  };

  const onAdd = (propertiesState: any) => {
    switch (currentTab) {
      case "report_date":
        dispatch({
          type: CF_REDUCER_CONSTANTS.CHANGE_INITIAL_STATE,
          payload: {
            ...state.form,
            metadata: {
              ...state.form.metadata,
              is_report_date_included: true,
            },
          },
        });
        break;
      case "contractor":
        dispatch({
          type: CF_REDUCER_CONSTANTS.CHANGE_INITIAL_STATE,
          payload: {
            ...state.form,
            metadata: {
              ...state.form.metadata,
              is_contractor_included: true,
            },
          },
        });
        break;
      case "region":
        dispatch({
          type: CF_REDUCER_CONSTANTS.CHANGE_INITIAL_STATE,
          payload: {
            ...state.form,
            metadata: {
              ...state.form.metadata,
              is_region_included: true,
            },
          },
        });
        break;
    }

    props.onAdd({
      type: currentTab,
      properties: propertiesState,
      id: props.mode === UserFormModeTypes.EDIT ? props.content.id : uuidv4(),
    });
    toastCtx?.pushToast("success", "Question added successfully.");
    resetTabState();
  };

  const closeModal = () => {
    if (props.mode === UserFormModeTypes.PREVIEW) {
      props.onClose();
      return;
    }

    // Only show confirmation if data has been entered
    if (hasDataEntered) {
      const confirmed = confirm(
        "Are you sure you want to cancel the data entered?"
      );
      if (confirmed) {
        resetTabState();
        props.onClose();
      }
    } else {
      // No data entered, close without confirmation
      resetTabState();
      props.onClose();
    }
  };

  return (
    <Modal
      title="Add Question"
      isOpen={props.isOpen}
      size="lg"
      closeModal={closeModal}
    >
      <div className="flex gap-6 border-b-2 border-solid cursor-pointer">
        {fields.map(tab => (
          <div
            key={tab.type}
            onClick={() => {
              if (
                props.mode !== UserFormModeTypes.EDIT &&
                props.mode !== UserFormModeTypes.PREVIEW
              ) {
                setTab(tab.type);
                setActiveDropdown(null);
              }
            }}
            className={cn(
              "text-sm text-neutral-shade-100 box-border md:text-sm text-neutral-shade-75 font-semibold mb-2 leading-normal",
              {
                ["border-b-2 border-solid border-brand-urbint-40 text-brand-urbint-40"]:
                  currentTab === tab.type && !activeDropdown,
              }
            )}
          >
            {tab.name}
          </div>
        ))}

        <DropDownField
          menuItems={
            props.mode !== UserFormModeTypes.EDIT &&
            props.mode !== UserFormModeTypes.PREVIEW
              ? [
                  inputTypes.map(t => ({
                    label: t.name,
                    onClick: () => {
                      if (
                        props.mode !== UserFormModeTypes.EDIT &&
                        props.mode !== UserFormModeTypes.PREVIEW
                      ) {
                        setTab(t.type);
                        setActiveDropdown("input");
                      }
                    },
                  })),
                ]
              : []
          }
        >
          <div
            className={cn(
              "text-sm text-neutral-shade-100 box-border md:text-sm text-neutral-shade-75 font-semibold mb-2 leading-normal",
              {
                ["border-b-2 border-solid border-brand-urbint-40 text-brand-urbint-40"]:
                  activeDropdown === "input" &&
                  inputTypes.some(t => t.type === currentTab),
              }
            )}
          >
            Input
          </div>
        </DropDownField>
        {!props.isRepeatableSection && (
          <DropDownField
            menuItems={
              props.mode !== UserFormModeTypes.EDIT &&
              props.mode !== UserFormModeTypes.PREVIEW
                ? [
                    filteredReferenceTypes.map(t => ({
                      label: t.name,
                      onClick: () => {
                        if (
                          props.mode !== UserFormModeTypes.EDIT &&
                          props.mode !== UserFormModeTypes.PREVIEW
                        ) {
                          setTab(t.type);
                          setActiveDropdown("reference");
                        }
                      },
                    })),
                  ]
                : []
            }
          >
            <div
              className={cn(
                "text-sm text-neutral-shade-100 box-border md:text-sm text-neutral-shade-75 font-semibold mb-2 leading-normal",
                {
                  ["border-b-2 border-solid border-brand-urbint-40 text-brand-urbint-40"]:
                    activeDropdown === "reference" &&
                    referenceTypes.some(t => t.type === currentTab),
                }
              )}
            >
              Reference
            </div>
          </DropDownField>
        )}
      </div>

      {/* Dynamic Component Render */}
      {Component && (
        <RepeatSectionContext.Provider
          value={props.isRepeatableSection || false}
        >
          <Component
            onAdd={onAdd}
            onClose={props.onClose}
            initialState={props.content?.properties}
            disabled={props.mode === UserFormModeTypes.PREVIEW}
            isRepeatableSection={props.isRepeatableSection}
            mode={props.mode}
            onDataChange={handleDataChange}
          />
        </RepeatSectionContext.Provider>
      )}
    </Modal>
  );
}

type FooterProps = {
  onAdd: (value: any) => void;
  onClose: () => void;
  disabled?: boolean;
  mode?: UserFormMode;
  hasDataEntered?: boolean;
};

export const Foooter = (props: FooterProps) => {
  const closeModal = () => {
    if (props.mode === UserFormModeTypes.PREVIEW) {
      props.onClose();
      return;
    }

    // Only show confirmation if data has been entered
    if (props.hasDataEntered) {
      const confirmed = confirm(
        "Are you sure you want to cancel the data entered?"
      );
      if (confirmed) {
        props.onClose();
      }
    } else {
      // No data entered, close without confirmation
      props.onClose();
    }
  };

  return (
    <div className="flex self-end w-full pt-4 flex-row-reverse m-t-4 border-t-2 border-solid">
      <ButtonPrimary
        label="Add"
        onClick={props.onAdd}
        disabled={props.disabled}
      />
      <ButtonRegular className="mr-2" label="Cancel" onClick={closeModal} />
    </div>
  );
};

export default DynamicFormModal;
