import type { DailyReportInputs } from "@/types/report/DailyReportInputs";
import { Controller, useFormContext } from "react-hook-form";
import FieldTextArea from "@/components/shared/field/fieldTextArea/FieldTextArea";

export type AdditionalInformationInputs = {
  progress?: string;
  lessons?: string;
};

type AdditionalInformationProps = {
  isCompleted?: boolean;
};

const additionalInformationFormInputPrefix = "additionalInformation";

export default function AdditionalInformation({
  isCompleted,
}: AdditionalInformationProps): JSX.Element {
  const { getValues } =
    useFormContext<Pick<DailyReportInputs, "additionalInformation">>();

  return (
    <>
      <section>
        <h5 className="font-semibold mb-4">Progress Updates</h5>
        <Controller
          name={`${additionalInformationFormInputPrefix}.progress`}
          render={({ field }) => (
            <FieldTextArea
              {...field}
              className="mb-4"
              label="Comments"
              initialValue={getValues(
                `${additionalInformationFormInputPrefix}.progress`
              )}
              readOnly={isCompleted}
            />
          )}
        />
      </section>
      <section>
        <h5 className="font-semibold mb-4">Lessons Learned</h5>
        <Controller
          name={`${additionalInformationFormInputPrefix}.lessons`}
          render={({ field }) => (
            <FieldTextArea
              {...field}
              label="Comments"
              initialValue={getValues(
                `${additionalInformationFormInputPrefix}.lessons`
              )}
              readOnly={isCompleted}
            />
          )}
        />
      </section>
    </>
  );
}
