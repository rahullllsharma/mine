import { BodyText } from "@urbint/silica";
import Modal from "@/components/shared/modal/Modal";
import CWFLocationMapView from "./CWFLocationMapView";

interface LocationMapViewModalProps {
  latitude: string | number;
  longitude: string | number;
  location: string;
  locationDescription?: string;
  isOpen: boolean;
  closeModal: () => void;
  modalMapView: boolean;
}

const LocationMapViewModal = ({
  latitude,
  longitude,
  isOpen,
  closeModal,
  location,
  locationDescription,
  modalMapView,
}: LocationMapViewModalProps) => {
  return (
    <Modal
      title="Location Map"
      isOpen={isOpen}
      size="xl"
      closeModal={closeModal}
    >
      <div className="flex gap-6 border-b-2 border-solid cursor-pointer">
        <CWFLocationMapView
          selectedLocationLatitude={latitude}
          selectedLocationLongitude={longitude}
          modalMapView={modalMapView}
        />
      </div>
      <div className="p-4 flex flex-col gap-8 bg-[#F8F8F8]">
        <div className="text-lg mb-2">
          <BodyText className="text-sm font-semibold">{location}</BodyText>
          {locationDescription && (
            <BodyText className="text-sm text-neutral-shade-100">
              {locationDescription}
            </BodyText>
          )}
        </div>
        <div className="text-lg mb-2 flex flex-row gap-20">
          <div>
            <BodyText className="text-sm font-semibold">Latitude</BodyText>
            <BodyText className="text-sm">{latitude}</BodyText>
          </div>
          <div>
            <BodyText className="text-sm font-semibold">Longitude</BodyText>
            <BodyText className="text-sm">{longitude}</BodyText>
          </div>
        </div>
      </div>
    </Modal>
  );
};
export default LocationMapViewModal;