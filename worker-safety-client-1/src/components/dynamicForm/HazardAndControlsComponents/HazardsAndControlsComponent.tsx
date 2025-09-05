import type {
  HazardControl,
  HazardsAndControlsComponentProps,
} from "../../templatesComponents/customisedForm.types";
import { SectionHeading } from "@urbint/silica";
import HazardsAndControlsForm from "./HazardsAndControlsForm";

export default function HazardsAndControlsComponent({
  configs,
  mode,
  formData,
  inSummary,
}: Readonly<
  HazardsAndControlsComponentProps & {
    formData: HazardControl | undefined;
    inSummary?: boolean;
  }
>): JSX.Element {
  const { title, subTitle } = configs;
  return (
    <>
      <div className="flex justify-between">
        <SectionHeading
          className={`${inSummary ? "text-[20px]" : "text-[14px] md:text-lg"}`}
        >
          {title}
        </SectionHeading>
      </div>
      <div>
        <HazardsAndControlsForm
          mode={mode}
          formData={formData}
          inSummary={inSummary}
          subTitle={subTitle}
        />
      </div>
    </>
  );
}
