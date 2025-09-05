import type { RegisterOptions } from "react-hook-form";
import { messages } from "@/locales/messages";

export const FieldRules: Record<string, RegisterOptions> = {
  REQUIRED: {
    required: messages.required,
  },
  /**
   * This should be used with a Radio/Checkbox with only 2 choices.
   */
  BOOLEAN_REQUIRED: {
    validate: value => typeof value === "boolean" || messages.required,
  },
  NOT_ONLY_WHITESPACE: {
    pattern: {
      value: /.*[^ ].*/g,
      message: messages.emptyString,
    },
  },
  ALPHANUMERIC: {
    pattern: {
      value: /^[a-zA-Z0-9]*$/g,
      message: messages.alphanumeric,
    },
  },
  URL: {
    pattern: {
      value:
        /https?:\/\/(www\.)?[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b([-a-zA-Z0-9()@:%_\+.~#?&//=]*)/gi,
      message: messages.url,
    },
  },
};
