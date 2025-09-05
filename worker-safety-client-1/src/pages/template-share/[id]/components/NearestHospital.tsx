import type {
  FormElement,
  NearestHospitalUserValueType,
} from "@/components/templatesComponents/customisedForm.types";
import React from "react";
import { BodyText, Icon } from "@urbint/silica";

const NearestHospital = ({
  element,
  nearestHospitalData,
}: {
  element: FormElement;
  nearestHospitalData: NearestHospitalUserValueType | undefined;
}): JSX.Element => {
  if (!nearestHospitalData || !nearestHospitalData.name) {
    return (
      <div className="flex flex-col gap-4 p-4 bg-brand-gray-10 rounded-lg">
        <div className="w-full">
          <BodyText className="text-[20px] font-semibold">
            {element.properties.title ?? `Nearest Hospital`}
          </BodyText>
        </div>
        <BodyText className="text-base font-normal text-neutrals-tertiary">
          No information provided
        </BodyText>
      </div>
    );
  }

  if (nearestHospitalData?.other) {
    return (
      <div className="flex flex-col gap-4 p-4">
        <div className="w-full">
          <BodyText className="text-[20px] font-semibold">
            {element.properties.title ?? `Nearest Hospital`}
          </BodyText>
        </div>
        <BodyText className="text-base font-normal text-neutral-shade-100">
          {nearestHospitalData?.name}
        </BodyText>
      </div>
    );
  }
  return (
    <div className="flex flex-col gap-4 p-4">
      <div className="w-full">
        <BodyText className="text-[20px] font-semibold">
          {element.properties.title ?? `Nearest Hospital`}
        </BodyText>
      </div>
      <div className="flex flex-col gap-1">
        <div className="flex flex-row gap-1">
          <BodyText className="text-base font-medium text-neutral-shade-100">
            Health Care Center: {nearestHospitalData?.name}
          </BodyText>
          {nearestHospitalData?.distance && (
            <BodyText className="text-base font-normal text-neutral-shade-100">
              ({nearestHospitalData?.distance})
            </BodyText>
          )}
        </div>
        {nearestHospitalData?.description && (
          <div className="flex flex-row gap-1 items-center">
            <Icon name="location" className="text-xl text-neutral-shade-100" />
            <BodyText className="text-base font-normal text-neutral-shade-100">
              {nearestHospitalData?.description}
            </BodyText>
          </div>
        )}
        {nearestHospitalData?.phone_number && (
          <a
            href={`tel:${nearestHospitalData?.phone_number}`}
            className="flex flex-row gap-1 items-center"
          >
            <Icon name="phone" className="text-xl text-brand-urbint-50" />
            <BodyText className="text-base font-normal text-brand-urbint-50">
              {nearestHospitalData?.phone_number}
            </BodyText>
          </a>
        )}
      </div>
    </div>
  );
};

export default NearestHospital;
