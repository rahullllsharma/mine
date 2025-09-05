import type { CommonAction } from "../../customisedForm.types";
import type { Dispatch } from "react";
import type { CustomisedFromContextStateType } from "@/context/CustomisedDataContext/CustomisedFormStateContext";
import { v4 as uuidv4 } from "uuid";
import {
  COMPONENTS_TYPES,
  CF_REDUCER_CONSTANTS,
} from "@/utils/customisedFormUtils/customisedForm.constants";
import {
  addAttachmentsJSON,
  componentTypeUtils,
} from "../../customisedForm.utils";

export const AddComponentsHandler = (
  selectedComponent: string,
  onAdd: (component: any) => void, //this any is coming from the onAdd prop in FormComponentsPopUp.tsx has to be changed
  dispatch: Dispatch<CommonAction>,
  state: CustomisedFromContextStateType
) => {
  switch (selectedComponent) {
    case COMPONENTS_TYPES.PHOTO_ATTACHMENTS:
      onAdd(
        addAttachmentsJSON(
          uuidv4(),
          COMPONENTS_TYPES.PHOTO_ATTACHMENTS,
          selectedComponent
        )
      );
      break;
    case COMPONENTS_TYPES.DOCUMENT_ATTACHMENTS:
      onAdd(
        addAttachmentsJSON(
          uuidv4(),
          COMPONENTS_TYPES.DOCUMENT_ATTACHMENTS,
          selectedComponent
        )
      );
      break;
    case COMPONENTS_TYPES.ACTIVITIES_AND_TASKS:
      dispatch({
        type: CF_REDUCER_CONSTANTS.CHANGE_INITIAL_STATE,
        payload: {
          ...state.form,
          metadata: {
            ...state.form.metadata,
            is_activities_and_tasks_included: true,
          },
        },
      });
      onAdd({
        id: uuidv4(),
        order: 0,
        type: componentTypeUtils(selectedComponent),
        properties: {
          is_mandatory: true,
          title: "Activities and Tasks",
          description: "",
          user_value: [],
        },
        contents: [],
      });
      break;

    case COMPONENTS_TYPES.HAZARDS_AND_CONTROLS:
      dispatch({
        type: CF_REDUCER_CONSTANTS.CHANGE_INITIAL_STATE,
        payload: {
          ...state.form,
          metadata: {
            ...state.form.metadata,
            is_hazards_and_controls_included: true,
          },
        },
      });
      onAdd({
        id: uuidv4(),
        order: 0,
        type: componentTypeUtils(selectedComponent),
        is_mandatory: false,
        properties: {
          title: "Hazards and Controls",
          description: "",
          user_value: [],
        },
        contents: [],
      });
      break;

    case COMPONENTS_TYPES.SUMMARY:
      dispatch({
        type: CF_REDUCER_CONSTANTS.CHANGE_INITIAL_STATE,
        payload: {
          ...state.form,
          metadata: {
            ...state.form.metadata,
            is_summary_included: true,
          },
        },
      });
      onAdd({
        id: uuidv4(),
        order: 0,
        type: componentTypeUtils(selectedComponent),
        is_mandatory: false,
        properties: {
          title: "Summary",
          description: "",
          user_value: [],
        },
        contents: [],
      });
      break;

    case COMPONENTS_TYPES.SITE_CONDITIONS:
      dispatch({
        type: CF_REDUCER_CONSTANTS.CHANGE_INITIAL_STATE,
        payload: {
          ...state.form,
          metadata: {
            ...state.form.metadata,
            is_site_conditions_included: true,
          },
        },
      });
      onAdd({
        id: uuidv4(),
        order: 0,
        type: componentTypeUtils(selectedComponent),
        is_mandatory: false,
        properties: {
          title: "Site Conditions",
          description: "",
          user_value: [],
        },
        contents: [],
      });
      break;

    case COMPONENTS_TYPES.LOCATION:
      dispatch({
        type: CF_REDUCER_CONSTANTS.CHANGE_INITIAL_STATE,
        payload: {
          ...state.form,
          metadata: {
            ...state.form.metadata,
            is_location_included: true,
          },
        },
      });
      onAdd({
        id: uuidv4(),
        order: 0,
        type: componentTypeUtils(selectedComponent),
        properties: {
          title: "Location",
          description: "",
          smart_address: true,
          is_mandatory: true,
          user_value: [],
        },
        contents: [],
      });
      break;
    case COMPONENTS_TYPES.NEAREST_HOSPITAL:
      dispatch({
        type: CF_REDUCER_CONSTANTS.CHANGE_INITIAL_STATE,
        payload: {
          ...state.form,
          metadata: {
            ...state.form.metadata,
            is_nearest_hospital_included: true,
          },
        },
      });
      onAdd({
        id: uuidv4(),
        order: 0,
        type: componentTypeUtils(selectedComponent),
        properties: {
          title: "Nearest Hospital",
          description: "",
          is_mandatory: true,
          user_value: [],
        },
        contents: [],
      });
      break;

    case COMPONENTS_TYPES.PERSONNEL_COMPONENT:
      onAdd({
        id: uuidv4(),
        order: 0,
        type: componentTypeUtils(selectedComponent),
        properties: {
          title: "Sign Off",
          include_in_summary: false,
          user_value: [],
        },
        contents: [],
      });
      break;

    default:
      break;
  }
};
