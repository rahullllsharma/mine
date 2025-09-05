// import type {
//   InputLocationPropertiesType,
//   UserLocationValue,
// } from "@/components/templatesComponents/customisedForm.types";
// import React, { useState } from "react";
// import { ComponentLabel, BodyText } from "@urbint/silica";
// import CWFLocationMapView from "@/components/dynamicForm/LocationComponent/CWFLocationMapView";
// import LocationMapViewModal from "@/components/dynamicForm/LocationComponent/LocationMapViewModal";

// const LocationInput = ({ locationProperties }: {locationProperties: InputLocationPropertiesType}) => {
//   const [isLocationMapViewModalOpen, setIsLocationMapViewModalOpen] =
//     useState(false);

//   const handleLocationMapViewModal = () => {
//     setIsLocationMapViewModalOpen(!isLocationMapViewModalOpen);
//   };

//   const EmptyState = (
//     <BodyText className="text-sm text-gray-500">No answer</BodyText>
//   )

//   const userValue = locationProperties.user_value as UserLocationValue;
//   if (!userValue?.name && !userValue?.gps_coordinates) return EmptyState;
//   const lat = userValue?.gps_coordinates?.latitude;
//   const long = userValue?.gps_coordinates?.longitude;
//   return (
//     <div className="flex flex-col gap-2">
//       <BodyText>{userValue.name}</BodyText>
//       <div className="flex flex-row w-full">
//         <div className="w-full">
//           <ComponentLabel className="text-md font-semibold">
//             Latitude
//           </ComponentLabel>
//           <BodyText className="mt-1">{lat}</BodyText>
//         </div>
//         <div className="w-full">
//           <ComponentLabel className="text-md font-semibold">
//             Longitude
//           </ComponentLabel>
//           <BodyText className="mt-1">{long}</BodyText>
//         </div>
//       </div>
//       {locationProperties.is_show_map_preview && lat && long && (
//         <div className="flex flex-row gap-6">
//           <div
//             className="relative w-full cursor-pointer group"
//             onClick={handleLocationMapViewModal}
//           >
//             <CWFLocationMapView
//               selectedLocationLatitude={lat.toString()}
//               selectedLocationLongitude={long.toString()}
//               modalMapView={true}
//             />
//           </div>
//         </div>
//       )}
//       {locationProperties.is_show_map_preview && lat && long && (
//         <LocationMapViewModal
//           latitude={lat.toString()}
//           longitude={long.toString()}
//           isOpen={isLocationMapViewModalOpen}
//           closeModal={handleLocationMapViewModal}
//           location={userValue.name || ""}
//           locationDescription={""}
//           modalMapView={false}
//         />
//       )}
//     </div>
//   );
// }

// export default LocationInput;

import type {
  InputLocationPropertiesType,
  UserLocationValue,
} from "@/components/templatesComponents/customisedForm.types";
import React, { useState } from "react";
import { BodyText, ComponentLabel } from "@urbint/silica";
import Labeled from "@/components/forms/Basic/Labeled";
import CWFLocationMapView from "@/components/dynamicForm/LocationComponent/CWFLocationMapView";
import LocationMapViewModal from "@/components/dynamicForm/LocationComponent/LocationMapViewModal";

const LocationInput = ({
  locationProperties,
}: {
  locationProperties: InputLocationPropertiesType;
}): JSX.Element => {
  const [isLocationMapViewModalOpen, setIsLocationMapViewModalOpen] =
    useState(false);

  const handleLocationMapViewModal = () => {
    setIsLocationMapViewModalOpen(!isLocationMapViewModalOpen);
  };

  const EmptyState = (
    <BodyText className="text-sm text-gray-500">No answer</BodyText>
  );

  const userValue = locationProperties.user_value as UserLocationValue;
  if (!userValue?.name && !userValue?.gps_coordinates) return EmptyState;
  const lat = userValue?.gps_coordinates?.latitude;
  const long = userValue?.gps_coordinates?.longitude;

  return (
    <div className="flex flex-col gap-4 bg-brand-gray-10 p-4">
      {userValue.name ? (
        <>
          <div className="flex flex-row">
            <div className="w-full">
              <ComponentLabel className="text-lg">
                {locationProperties.title ?? `Location`}
              </ComponentLabel>
            </div>
          </div>
          <div className="flex flex-col sm:flex-row gap-4">
            {lat && long && (
              <div
                className="relative w-[300px] cursor-pointer group"
                onClick={handleLocationMapViewModal}
              >
                <CWFLocationMapView
                  selectedLocationLatitude={lat ?? ""}
                  selectedLocationLongitude={long ?? ""}
                  modalMapView={true}
                />
              </div>
            )}

            <div className="w-full flex flex-col gap-6">
              <div className="w-full">
                <Labeled label="Location">
                  <BodyText className="text-sm">{userValue.name}</BodyText>
                </Labeled>
              </div>

              <div className="w-full flex flex-row">
                {lat && (
                  <div className="w-full">
                    <Labeled label="Latitude">
                      <BodyText className="text-sm">{lat}</BodyText>
                    </Labeled>
                  </div>
                )}
                {long && (
                  <div className="w-full">
                    <Labeled label="Longitude">
                      <BodyText className="text-sm">{long}</BodyText>
                    </Labeled>
                  </div>
                )}
              </div>
            </div>
          </div>
          <LocationMapViewModal
            latitude={lat ?? ""}
            longitude={long ?? ""}
            isOpen={isLocationMapViewModalOpen}
            closeModal={handleLocationMapViewModal}
            location={userValue.name ?? ""}
            modalMapView={false}
          />
        </>
      ) : (
        <BodyText className="flex text-sm font-semibold">
          No location added
        </BodyText>
      )}
    </div>
  );
};
export default LocationInput;
