import type { CWFLocationType } from "@/components/templatesComponents/customisedForm.types";
import React, { useContext, useState } from "react";
import { BodyText, ComponentLabel } from "@urbint/silica";
import { CWFItemType } from "@/components/templatesComponents/customisedForm.types";
import CustomisedFromStateContext from "@/context/CustomisedDataContext/CustomisedFormStateContext";
import CWFLocationMapView from "./CWFLocationMapView";
import LocationMapViewModal from "./LocationMapViewModal";

const LocationInSummary = ({
  item,
  type,
}: {
  item: CWFLocationType;
  type: string;
}): JSX.Element => {
  const [isLocationMapViewModalOpen, setIsLocationMapViewModalOpen] =
    useState(false);
  const { state } = useContext(CustomisedFromStateContext)!;
  const { name, gps_coordinates, description } =
    state.form.component_data?.location_data ?? {};

  const handleSummaryRender = () => {
    if (type === CWFItemType.InputLocation && item.properties.user_value) {
      return {
        name: (item.properties.user_value as any)?.name,
        gps_coordinates: (item.properties.user_value as any)?.gps_coordinates,
      };
    }
    return {
      name: name,
      gps_coordinates: gps_coordinates,
      description: description,
    };
  };

  const handleLocationMapViewModal = () => {
    setIsLocationMapViewModalOpen(!isLocationMapViewModalOpen);
  };

  return (
    <div className="flex flex-col gap-2">
      <div className="flex flex-row">
        <div className="w-full">
          <ComponentLabel className="text-[20px] cursor-auto">
            {item.properties.title ?? `Location`}
          </ComponentLabel>
        </div>
      </div>
      <div className="flex flex-col sm:flex-row py-2 gap-4">
        {handleSummaryRender().gps_coordinates?.latitude &&
          handleSummaryRender().gps_coordinates?.longitude && (
            <div
              className="relative w-full sm:w-[280px] md:w-[320px] lg:w-[350px] cursor-pointer group flex-shrink-0"
              onClick={handleLocationMapViewModal}
            >
              <CWFLocationMapView
                selectedLocationLatitude={
                  handleSummaryRender().gps_coordinates?.latitude ?? ""
                }
                selectedLocationLongitude={
                  handleSummaryRender().gps_coordinates?.longitude ?? ""
                }
                modalMapView={true}
              />
            </div>
          )}

        <div className="w-full flex flex-col gap-4 min-w-0">
          <div className="w-full flex flex-col gap-2">
            <BodyText className="text-sm font-semibold">Location</BodyText>
            <BodyText className="text-base break-words">
              {handleSummaryRender().name}
            </BodyText>
          </div>

          <div className="w-full flex flex-col sm:flex-row gap-4 sm:gap-6">
            {handleSummaryRender().gps_coordinates?.latitude && (
              <div className="flex flex-col gap-2 min-w-0">
                <BodyText className="text-sm font-semibold">Latitude</BodyText>
                <BodyText className="text-base break-words">
                  {handleSummaryRender().gps_coordinates?.latitude}
                </BodyText>
              </div>
            )}
            {handleSummaryRender().gps_coordinates?.longitude && (
              <div className="flex flex-col gap-2 min-w-0">
                <BodyText className="text-sm font-semibold">Longitude</BodyText>
                <BodyText className="text-base break-words">
                  {handleSummaryRender().gps_coordinates?.longitude}
                </BodyText>
              </div>
            )}
          </div>

          {description && (
            <div className="w-full flex flex-col gap-2">
              <BodyText className="text-sm font-semibold">
                Location Description
              </BodyText>
              <BodyText className="text-base break-words">
                {description}
              </BodyText>
            </div>
          )}
        </div>
      </div>
      <LocationMapViewModal
        latitude={handleSummaryRender().gps_coordinates?.latitude ?? ""}
        longitude={handleSummaryRender().gps_coordinates?.longitude ?? ""}
        isOpen={isLocationMapViewModalOpen}
        closeModal={handleLocationMapViewModal}
        location={name ?? ""}
        locationDescription={description ?? ""}
        modalMapView={false}
      />
    </div>
  );
};
export default LocationInSummary;
