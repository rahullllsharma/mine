import type { FormType } from "../customisedForm.types";

//file for test delete post API integration
export const MOCK_DATA: FormType = {
  id: "form_1",
  isDisabled: false,
  type: "form",
  settings: {
    availability: {
      adhoc: {
        selected: true,
      },
      work_package: {
        selected: true,
      },
    },
    edit_expiry_days: 7,
    copy_and_rebrief: {
      is_copy_enabled: false,
      is_rebrief_enabled: false,
    }
  },
  properties: {
    title: "Job Safety Briefing",
    status: "",
    description: "",
  },
  contents: [],
};
