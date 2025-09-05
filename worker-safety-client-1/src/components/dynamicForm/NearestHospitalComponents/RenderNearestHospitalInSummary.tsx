import type { CWFNearestHospitalType } from "@/components/templatesComponents/customisedForm.types";
import { BodyText, Icon } from "@urbint/silica";
import { useContext } from "react";
import CustomisedFromStateContext from "@/context/CustomisedDataContext/CustomisedFormStateContext";

export const RenderNearestHospitalInSummary = ({
  item,
}: {
  item: CWFNearestHospitalType;
}) => {
  const { state } = useContext(CustomisedFromStateContext)!;
  const { nearest_hospital } = state.form?.component_data ?? {};

  if (nearest_hospital?.other) {
    return (
      <div className="flex flex-col gap-4">
        <div className="w-full">
          <BodyText className="text-[20px] font-semibold">
            {item.properties.title ?? `Nearest Hospital`}
          </BodyText>
        </div>
        <BodyText className="text-base font-normal text-neutral-shade-100">
          {nearest_hospital?.name}
        </BodyText>
      </div>
    );
  }
  return (
    <div className="flex flex-col gap-4">
      <div className="w-full">
        <BodyText className="text-[20px] font-semibold">
          {item.properties.title ?? `Nearest Hospital`}
        </BodyText>
      </div>
      <div className="flex flex-col gap-1">
        <div className="flex flex-row gap-1">
          <BodyText className="text-base font-medium text-neutral-shade-100">
            Health Care Center: {nearest_hospital?.name}
          </BodyText>
          {nearest_hospital?.distance && (
            <BodyText className="text-base font-normal text-neutral-shade-100">
              ({nearest_hospital?.distance})
            </BodyText>
          )}
        </div>
        {nearest_hospital?.description && (
          <div className="flex flex-row gap-1 items-center">
            <Icon name="location" className="text-xl text-neutral-shade-100" />
            <BodyText className="text-base font-normal text-neutral-shade-100">
              {nearest_hospital?.description}
            </BodyText>
          </div>
        )}
        {nearest_hospital?.phone_number && (
          <a
            href={`tel:${nearest_hospital?.phone_number}`}
            className="flex flex-row gap-1 items-center"
          >
            <Icon name="phone" className="text-xl text-brand-urbint-50" />
            <BodyText className="text-base font-normal text-brand-urbint-50">
              {nearest_hospital?.phone_number}
            </BodyText>
          </a>
        )}
      </div>
    </div>
  );
};
