import type {
  CWFLocationType,
  LocationUserValueType,
} from "@/components/templatesComponents/customisedForm.types";
import React, { useState } from "react";
import { BodyText } from "@urbint/silica";
import Labeled from "@/components/forms/Basic/Labeled";
import CWFLocationMapView from "@/components/dynamicForm/LocationComponent/CWFLocationMapView";
import LocationMapViewModal from "@/components/dynamicForm/LocationComponent/LocationMapViewModal";

const Location = ({
  item,
  locationData,
}: {
  item: CWFLocationType;
  locationData: LocationUserValueType | undefined;
}): JSX.Element => {
  const [isLocationMapViewModalOpen, setIsLocationMapViewModalOpen] =
    useState(false);
  const { name, gps_coordinates, description } = locationData ?? {};
  const { latitude, longitude } = gps_coordinates ?? {};

  const handleLocationMapViewModal = () => {
    setIsLocationMapViewModalOpen(!isLocationMapViewModalOpen);
  };

  return (
    <div className="flex flex-col gap-4 bg-brand-gray-10 rounded-lg p-4">
      {name ? (
        <>
          <div className="flex flex-row">
            <div className="w-full">
              <BodyText className="text-[20px] font-semibold">
                {item.properties.title ?? `Location`}
              </BodyText>
            </div>
          </div>
          <div className="flex flex-col sm:flex-row gap-4">
            {latitude && longitude && (
              <div
                className="relative w-[300px] cursor-pointer group"
                onClick={handleLocationMapViewModal}
              >
                <CWFLocationMapView
                  selectedLocationLatitude={latitude ?? ""}
                  selectedLocationLongitude={longitude ?? ""}
                  modalMapView={true}
                />
              </div>
            )}

            <div className="w-full flex flex-col gap-6">
              <div className="w-full">
                <Labeled label="Location">
                  <BodyText className="text-sm">{name}</BodyText>
                </Labeled>
              </div>

              <div className="w-full flex flex-row">
                {latitude && (
                  <div className="w-full">
                    <Labeled label="Latitude">
                      <BodyText className="text-sm">{latitude}</BodyText>
                    </Labeled>
                  </div>
                )}
                {longitude && (
                  <div className="w-full">
                    <Labeled label="Longitude">
                      <BodyText className="text-sm">{longitude}</BodyText>
                    </Labeled>
                  </div>
                )}
              </div>

              {description && (
                <div className="flex flex-row gap-4">
                  <div className="w-full">
                    <BodyText>Location Description</BodyText>
                    <BodyText className="text-sm">{description}</BodyText>
                  </div>
                </div>
              )}
            </div>
          </div>
          <LocationMapViewModal
            latitude={latitude ?? ""}
            longitude={longitude ?? ""}
            isOpen={isLocationMapViewModalOpen}
            closeModal={handleLocationMapViewModal}
            location={name ?? ""}
            locationDescription={description ?? ""}
            modalMapView={false}
          />
        </>
      ) : (
        <BodyText className="flex text-base font-semibold text-neutrals-tertiary">
          No information provided
        </BodyText>
      )}
    </div>
  );
};
export default Location;
