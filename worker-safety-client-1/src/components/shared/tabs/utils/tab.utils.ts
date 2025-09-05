import type { TabsOption } from "../Tabs";

export const parseOptions = (options: TabsOption[] | string[]): TabsOption[] =>
  options.length > 0 && typeof options[0] === "string"
    ? options.map((option, index) => ({
        id: `${index}`,
        name: option as string,
      }))
    : (options as TabsOption[]);
