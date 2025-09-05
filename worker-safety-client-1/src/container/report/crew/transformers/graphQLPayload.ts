import type { UploadItem } from "@/components/upload/Upload";
import type { CrewInputs } from "@/types/report/DailyReportInputs";

export type CrewGraphQLPayloadParams = {
  crew: {
    [k in keyof CrewInputs]: NonNullable<CrewInputs[k]>;
  };
};

type ReturnedTasksGraphQLPayload = {
  crew: CrewInputs;
};

type CrewNullableKeys = keyof Omit<
  CrewGraphQLPayloadParams["crew"],
  "documents"
>;

export default function transformGraphQLPayload(
  formData: CrewGraphQLPayloadParams
): ReturnedTasksGraphQLPayload {
  const { crew } = formData || {};

  return {
    crew: Object.entries(crew).reduce((acc, [key, value]) => {
      if (key === "documents") {
        acc["documents"] = value as UploadItem[];
      } else {
        acc[key as CrewNullableKeys] = (value as any) ?? null;
      }

      return acc;
    }, {} as CrewInputs) as CrewInputs,
  };
}
