import type {
  FormComponentData,
  FormElementsType,
  FormType,
  HazardControl,
  Hazards,
  PageType,
  ProjectDetailsType,
  RegionMetadata,
  SelectedActivity,
  SelectedTask,
  Task,
  UserFormMode,
} from "./customisedForm.types";
import { COMPONENTS_TYPES } from "@/utils/customisedFormUtils/customisedForm.constants";
import { CWFItemType, UserFormModeTypes } from "./customisedForm.types";
import {
  getValidationPattern,
  isEmailValid,
  REGEX_VALIDATOR,
  validateInput,
} from "./PreviewComponents/textUtils";

export const isValidEmail = (email: string) => {
  const pattern = /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/;
  return pattern.test(email);
};

export const areValuesFilled = (contents: FormElementsType[]) => {
  for (const item of contents) {
    switch (item.type) {
      case CWFItemType.InputDateTime:
      case CWFItemType.ReportDate:
      case CWFItemType.InputLocation:
      case CWFItemType.InputText:
      case CWFItemType.InputNumber:
        if (!String(item.properties.user_value || "").trim()) {
          return false;
        }
        break;
      case CWFItemType.InputPhoneNumber:
        if (!item.properties.user_value) {
          return false;
        }
        if (item.properties?.user_value?.length != 10) {
          return false;
        }
        break;
      case CWFItemType.InputEmail:
        if (!item.properties.user_value) {
          return false;
        }
        if (!isValidEmail(item.properties?.user_value.trim())) {
          return false;
        }
        break;
      case CWFItemType.YesOrNo:
        if (!item.properties.user_value) {
          return false;
        }
        if (![true, false].includes(item.properties.user_value)) {
          return false;
        }
        break;
      case CWFItemType.Choice:
      case CWFItemType.Dropdown:
      case CWFItemType.Contractor:
      case CWFItemType.Region:
        if (!item.properties.user_value) {
          return false;
        }
        break;
      default:
        break;
    }
  }
  return true;
};

export const isMandatoryFilled = (
  contents: FormElementsType[],
  componentData?: any
) => {
  for (const item of contents) {
    switch (item.type) {
      case CWFItemType.InputDateTime:
      case CWFItemType.ReportDate:
      case CWFItemType.InputText:
      case CWFItemType.InputNumber:
        if (
          item.properties.is_mandatory &&
          !String(item.properties.user_value || "").trim()
        ) {
          return false;
        }
        break;
      case CWFItemType.InputLocation:
        if (
          item.properties.is_mandatory &&
          !item.properties.user_value?.name?.trim()
        ) {
          return false;
        }
        break;
      case CWFItemType.InputPhoneNumber:
        if (item.properties.is_mandatory && !item.properties.user_value) {
          return false;
        }
        // if (item.properties?.user_value?.length != 10) {
        //   return false;
        // }
        break;
      case CWFItemType.InputEmail:
        if (item.properties.is_mandatory && !item.properties.user_value) {
          return false;
        }
        // if (!isValidEmail(item.properties?.user_value?.trim())) {
        //   return false;
        // }
        break;
      case CWFItemType.YesOrNo:
        if (
          item.properties.is_mandatory &&
          ![true, false].includes(item.properties.user_value)
        ) {
          return false;
        }
        break;
      case CWFItemType.Choice:
      case CWFItemType.Dropdown:
      case CWFItemType.Contractor:
      case CWFItemType.Region:
        if (
          item.properties.is_mandatory &&
          !item.properties.user_value?.length
        ) {
          return false;
        }

        if (
          item.properties.is_mandatory &&
          item.properties.user_value?.includes("other") &&
          !item.properties.user_other_value?.trim()
        ) {
          return false;
        }
        break;
      case CWFItemType.Checkbox:
        if (
          item.properties.is_mandatory &&
          (!item.properties.user_value || !item.properties.user_value.length)
        ) {
          return false;
        }
        break;
      case CWFItemType.Location:
        if (
          item.properties.is_mandatory &&
          (!componentData?.location_data.name.trim() ||
            !componentData?.location_data?.gps_coordinates?.latitude.trim() ||
            !componentData?.location_data?.gps_coordinates?.longitude.trim())
        ) {
          return false;
        }
        break;
      case CWFItemType.NearestHospital:
        if (
          item.properties.is_mandatory &&
          !componentData?.nearest_hospital?.name.trim()
        ) {
          return false;
        }
        break;
      case CWFItemType.ActivitiesAndTasks:
        if (item.properties.is_mandatory) {
          const activities = componentData?.activities_tasks || [];

          const hasSelectedActivities = activities.some(
            (activity: SelectedActivity) => {
              return activity.tasks.some((task: SelectedTask) => {
                return task.selected === true;
              });
            }
          );

          if (!hasSelectedActivities) {
            return {
              isValid: false,
              errorMessage: "Please select at least one activity",
            };
          }
        }
        break;
      default:
        break;
    }
  }
  return true;
};

export const areAllValuesFilled = (arr: FormElementsType[]) => {
  for (const item of arr) {
    // if (!areValuesFilled([item])) {
    if (!isMandatoryFilled([item])) {
      return false;
    }
  }
  return true;
};

export const isAllMandatoryFilled = (
  arr: FormElementsType[],
  component_data: any
) => {
  for (const item of arr) {
    if (!isMandatoryFilled([item], component_data)) {
      return false;
    }
  }
  return true;
};

type AnyFunction = (...args: any[]) => any;
export function debounce<T extends AnyFunction>(
  func: T,
  delay: number
): (...args: Parameters<T>) => void {
  let timeoutId: ReturnType<typeof setTimeout>;

  return function (this: ThisParameterType<T>, ...args: Parameters<T>): void {
    clearTimeout(timeoutId);
    timeoutId = setTimeout(() => {
      func.apply(this, args);
    }, delay);
  };
}

export const extractPageIds = (
  pages: PageType[],
  result: Record<string, boolean>
) => {
  pages.forEach(page => {
    result[page.id] = false;
    if (page.contents) {
      const subpages = page.contents.filter(
        content => content.type === CWFItemType.SubPage
      );
      extractPageIds(subpages, result);
    }
  });
  return result;
};

export const removeDuplicatesByName = (
  data: Array<{ id: string; name: string }>
) => {
  const uniqueNames = new Set<string>();
  return data
    ?.filter(item => {
      if (uniqueNames.has(item.name)) {
        return false;
      }
      uniqueNames.add(item.name);
      return true;
    })
    .sort((a, b) => a.name.localeCompare(b.name));
};

export const removeDuplicatesById = (
  data: Array<{ id: string; name: string }>
) => {
  const uniqueIds = new Set<string>();
  return data?.filter(item => {
    if (uniqueIds.has(item.id)) {
      return false;
    }
    uniqueIds.add(item.id);
    return true;
  });
};

/**
 * Extracts and processes user data from specific form components within a form object.
 *
 * @param formObject:FormType - The form object containing pages, components, and their properties
 *
 * @param component_type - The type of component to process
 *
 * @returns {FormType | false} Returns the updated form object with processed component data
 *                            Returns false if the form object has no contents
 * @example
 * const updatedForm = getFormComponentData(formObject, "report_date");
 */

export const getFormComponentData = (
  formObject: FormType,
  component_type: string
) => {
  if (!formObject?.contents) return false;

  const updatedForm = { ...formObject };

  updatedForm.contents.forEach(page => {
    (page.contents || []).forEach(component => {
      if (component.type === component_type) {
        switch (component_type) {
          case CWFItemType.ReportDate:
            if (component.properties?.user_value) {
              updatedForm.properties.report_start_date =
                component.properties.date_type === "date_range"
                  ? component.properties.user_value.from ?? null
                  : component.properties.user_value.value ?? null;
            }
            break;
          case "location":
            // if (component.properties?.user_value) {
            //     updatedForm.properties.location = component.properties.user_value;
            // }
            break;
        }
      }
    });
  });

  return updatedForm;
};

export const componentTypeUtils = (componentTag: string) => {
  switch (componentTag) {
    case COMPONENTS_TYPES.PHOTO_ATTACHMENTS:
    case COMPONENTS_TYPES.DOCUMENT_ATTACHMENTS:
      return CWFItemType.Attachment;
    case COMPONENTS_TYPES.ACTIVITIES_AND_TASKS:
      return CWFItemType.ActivitiesAndTasks;
    case COMPONENTS_TYPES.HAZARDS_AND_CONTROLS:
      return CWFItemType.HazardsAndControls;
    case COMPONENTS_TYPES.SUMMARY:
      return CWFItemType.Summary;
    case COMPONENTS_TYPES.SITE_CONDITIONS:
      return CWFItemType.SiteConditions;
    case COMPONENTS_TYPES.LOCATION:
      return CWFItemType.Location;
    case COMPONENTS_TYPES.NEAREST_HOSPITAL:
      return CWFItemType.NearestHospital;
    case COMPONENTS_TYPES.PERSONNEL_COMPONENT:
      return CWFItemType.PersonnelComponent;
    default:
      return componentTag;
  }
};

export const addAttachmentsJSON = (
  id: string,
  attachmentType: string,
  selectedComponent: string
) => {
  return {
    id: id,
    order: 0,
    type: componentTypeUtils(selectedComponent),
    is_mandatory: false,
    properties: {
      title: attachmentType === "PHOTO_ATTACHMENTS" ? "Photos" : "Documents",
      attachment_type:
        attachmentType === "PHOTO_ATTACHMENTS" ? "photo" : "document",
      attachments_max_count: 20,
      description: "",
      user_value: [],
    },
    contents: [],
  };
};

export const validateField = (
  items: FormElementsType[],
  componentData?: FormComponentData
): { isValid: boolean; errorMessage?: string; itemId?: string } => {
  for (const item of items) {
    // Check mandatory validation first
    if (item.properties.is_mandatory) {
      switch (item.type) {
        case CWFItemType.InputDateTime:
        case CWFItemType.ReportDate:
        case CWFItemType.InputText:
        case CWFItemType.InputNumber:
          if (!String(item.properties.user_value || "").trim()) {
            return {
              isValid: false,
              errorMessage: "This field is required",
              itemId: item.id,
            };
          }
          break;
        case CWFItemType.InputLocation:
          if (!item.properties.user_value?.name?.trim()) {
            return {
              isValid: false,
              errorMessage: "This field is required",
              itemId: item.id,
            };
          }
          break;
        case CWFItemType.InputPhoneNumber:
          if (!item.properties.user_value) {
            return {
              isValid: false,
              errorMessage: "This field is required",
              itemId: item.id,
            };
          }
          if (item.properties.user_value.length !== 10) {
            return {
              isValid: false,
              errorMessage: "Phone number must be 10 digits",
              itemId: item.id,
            };
          }
          break;
        case CWFItemType.InputEmail:
          if (!item.properties.user_value) {
            return {
              isValid: false,
              errorMessage: "This field is required",
              itemId: item.id,
            };
          }
          if (!isValidEmail(item.properties.user_value.trim())) {
            return {
              isValid: false,
              errorMessage: "Please enter a valid email address",
              itemId: item.id,
            };
          }
          break;
        case CWFItemType.YesOrNo:
          if (![true, false].includes(item.properties.user_value)) {
            return {
              isValid: false,
              errorMessage: "This field is required",
              itemId: item.id,
            };
          }
          break;
        case CWFItemType.Choice:
        case CWFItemType.Dropdown:
        case CWFItemType.Contractor:
        case CWFItemType.Region:
          if (!item.properties.user_value?.length) {
            return {
              isValid: false,
              errorMessage: "This field is required",
              itemId: item.id,
            };
          }

          if (item.properties.user_value.includes("other")) {
            if (!item.properties.user_other_value?.trim()) {
              return {
                isValid: false,
                errorMessage: "Please specify your response for 'Other' option",
                itemId: item.id,
              };
            }
          }
          break;

        case CWFItemType.Location:
          const { latitude, longitude } =
            componentData?.location_data?.gps_coordinates || {};
          if (!componentData?.location_data?.name?.trim()) {
            return {
              isValid: false,
              errorMessage: "This field is required",
              itemId: item.id,
            };
          }

          const hasLatitude = String(latitude)?.trim();
          const hasLongitude = String(longitude)?.trim();

          if (hasLatitude && !hasLongitude) {
            return {
              isValid: false,
              errorMessage: "Longitude is required when latitude is provided",
              itemId: item.id,
            };
          }

          if (!hasLatitude && hasLongitude) {
            return {
              isValid: false,
              errorMessage: "Latitude is required when longitude is provided",
              itemId: item.id,
            };
          }

          break;
        case CWFItemType.NearestHospital:
          if (!componentData?.nearest_hospital?.name.trim()) {
            return {
              isValid: false,
              errorMessage: "This field is required",
              itemId: item.id,
            };
          }
          break;
        case CWFItemType.ActivitiesAndTasks:
          const activities = componentData?.activities_tasks || [];

          const hasSelectedActivities = activities.some(
            (activity: SelectedActivity) => {
              return activity.tasks.some((task: SelectedTask) => {
                return task.selected === true;
              });
            }
          );

          if (!hasSelectedActivities) {
            return {
              isValid: false,
              errorMessage: "At least one Task must be added",
              itemId: item.id,
            };
          }
          break;
        case CWFItemType.Checkbox:
          if (
            !item.properties.user_value ||
            !item.properties.user_value.length
          ) {
            return {
              isValid: false,
              errorMessage: "This is required",
              itemId: item.id,
            };
          }
          break;
      }
    }

    // Additional pattern validation for text fields if they have a value
    if (item.type === CWFItemType.InputText && item.properties.user_value) {
      const { response_option, validation, user_value } = item.properties;

      if (response_option === "alphanumeric") {
        if (!REGEX_VALIDATOR.alphanumeric.test(user_value)) {
          return {
            isValid: false,
            errorMessage: "Alphabets and Numbers only allowed",
            itemId: item.id,
          };
        }
      } else if (validation?.[0]) {
        const pattern = getValidationPattern(response_option, validation);

        if (validateInput(user_value, pattern)) {
          return {
            isValid: false,
            errorMessage: "Must match the pattern",
            itemId: item.id,
          };
        }
      }
    }
  }

  return { isValid: true };
};

export const isDisabledMode = (mode: UserFormMode) => {
  return (
    mode === UserFormModeTypes.BUILD || mode === UserFormModeTypes.PREVIEW_PROPS
  );
};

export const disabledField = (mode: UserFormMode) => {
  return (
    mode === UserFormModeTypes.BUILD ||
    mode === UserFormModeTypes.PREVIEW ||
    mode === UserFormModeTypes.PREVIEW_PROPS
  );
};

export const hexToRgba = (hex: string, alpha = 1) => {
  // Remove the hash if it exists
  hex = hex.replace("#", "");

  // Parse the hex values
  let r, g, b;
  if (hex.length === 3) {
    // For shorthand hex (#RGB)
    r = parseInt(hex.charAt(0) + hex.charAt(0), 16);
    g = parseInt(hex.charAt(1) + hex.charAt(1), 16);
    b = parseInt(hex.charAt(2) + hex.charAt(2), 16);
  } else {
    // For full hex (#RRGGBB)
    r = parseInt(hex.substring(0, 2), 16);
    g = parseInt(hex.substring(2, 4), 16);
    b = parseInt(hex.substring(4, 6), 16);
  }

  return `rgba(${r}, ${g}, ${b}, ${alpha})`;
};

export const getRegionMetadata = (
  formObject: FormType,
  projectDetails?: ProjectDetailsType
): RegionMetadata => {
  const selectedRegion = formObject.metadata?.region;

  if (selectedRegion) {
    return {
      region: {
        name: selectedRegion?.name || "",
        id: selectedRegion?.id || "",
      },
    };
  }

  // Case 2: No region component but projectDetails exists
  if (projectDetails?.project?.libraryRegion) {
    return {
      region: {
        name: projectDetails.project.libraryRegion.name,
        id: projectDetails.project.libraryRegion.id,
      },
    };
  }

  // Case 3: Neither exists - return empty object
  return {};
};
export const isFormValid = (
  formPages: FormElementsType[],
  componentData?: FormComponentData
) => {
  let allValid = true;
  formPages.forEach(page => {
    const currentPage = page;

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

    const { isValid } = validateField(listOfWidgets, componentData);
    page.properties.page_update_status = isValid
      ? page.properties.page_update_status
      : "error";
    if (!isValid) {
      allValid = false;
    }
  });
  return allValid;
};
const isHazardSubmittable = (hazardItem: Hazards) => {
  // Check if controlsImplemented is true
  if (hazardItem.noControlsImplemented === true) {
    return true;
  }

  // Check if there's at least one selected control
  const hasSelectedControls =
    hazardItem.controls &&
    hazardItem.controls.some(control => control.selected === true);

  return hasSelectedControls;
};

export const validateAllHazards = (selectedHazards: Hazards[]) =>
  selectedHazards.every(isHazardSubmittable);

/**
 * Filters out hidden hazards (those with selected: false) for tasks and site conditions
 * Only visible hazards are returned for validation purposes
 */
export const getVisibleHazards = (
  hazards: Hazards[],
  componentData?: { hazards_controls?: HazardControl }
): Hazards[] => {
  if (!componentData?.hazards_controls) {
    return hazards;
  }

  const { tasks = [], site_conditions = [] } = componentData.hazards_controls;

  const taskHazardIds = tasks.flatMap((task: Task) =>
    (task.hazards || []).map((hazard: Hazards) => hazard.id)
  );
  const siteConditionHazardIds = site_conditions.map(
    (hazard: Hazards) => hazard.id
  );

  return hazards.filter(hazard => {
    // Only include task/site condition hazards if selected is true
    if (
      taskHazardIds.includes(hazard.id) ||
      siteConditionHazardIds.includes(hazard.id)
    ) {
      return hazard.selected === true;
    }
    // Always include other hazards (manually added, etc.)
    return true;
  });
};

/**
 * Checks if a string is a valid http or https URL
 */
export const isValidHttpUrl = (url: string): boolean => {
  try {
    const parsed = new URL(url);
    return parsed.protocol === "http:" || parsed.protocol === "https:";
  } catch {
    return false;
  }
};
export const validateInputData = (
  items: FormElementsType[]
): { isValid: boolean; errorMessage?: string } => {
  for (const item of items) {
    const type = item.type;
    const { user_value, response_option, validation } = item.properties;
    // Only validate if user_value exists and contains non-whitespace content
    if (user_value === undefined || user_value === null || user_value === "") {
      continue;
    }
    switch (type) {
      case CWFItemType.InputEmail:
        if (!isEmailValid(user_value)) {
          return { isValid: false, errorMessage: "Please enter valid email" };
        }
        break;
      case CWFItemType.InputPhoneNumber:
        {
          const phone = String(user_value).trim();
          if (!/^\d{10}$/.test(phone)) {
            return {
              isValid: false,
              errorMessage: "Please enter valid phone number",
            };
          }
        }
        break;

      case CWFItemType.InputText:
        if (response_option === "alphanumeric") {
          if (!REGEX_VALIDATOR.alphanumeric.test(user_value)) {
            return {
              isValid: false,
              errorMessage: "Please enter Alphabets and Numbers",
            };
          }
        }
        if (response_option === "regex") {
          const pattern = new RegExp(validation?.[0]);

          if (validateInput(user_value, pattern)) {
            return {
              isValid: false,
              errorMessage: "Must match pattern",
            };
          }
        }
        break;
    }
  }
  return { isValid: true };
};

export const isValidPhoneNumberFormat = (phoneNumber: string): boolean => {
  const phoneRegex = /^\(\d{3}\) \d{3}-\d{4}$/;
  return phoneRegex.test(phoneNumber);
};

export const scrollToField = (itemId: string) => {
  const fieldElement = document.getElementById(itemId);
  if (fieldElement) {
    fieldElement.scrollIntoView({
      behavior: "smooth",
      block: "center",
      inline: "nearest",
    });
  }
};
