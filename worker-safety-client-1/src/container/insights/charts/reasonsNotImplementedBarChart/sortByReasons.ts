import type { ReasonNotImplementedCount } from "./ReasonsNotImplementedBarChart";
import find from "lodash/find";
import { getControlNotPerformedOptions } from "@/container/report/jobHazardAnalysis/constants";

export const sortByReasons = (
  data: ReasonNotImplementedCount[]
): ReasonNotImplementedCount[] =>
  getControlNotPerformedOptions()
    .map(opt => opt.id)
    .map(rsn => {
      const found = find(data, ({ reason }) => rsn === reason);
      if (found) return found;
      return { reason: rsn, count: 0 };
    })
    .slice()
    // should not happen, but if the backend sends an unsupported reason, we filter it here
    .filter(x => x !== undefined)
    .reverse() as ReasonNotImplementedCount[];
