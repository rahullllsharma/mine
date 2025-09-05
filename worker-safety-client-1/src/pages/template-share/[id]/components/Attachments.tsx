import type {
  UploadItem,
  FormComponentPayloadType,
} from "@/components/templatesComponents/customisedForm.types";
import { CaptionText, Icon, BodyText } from "@urbint/silica";
import React, { useState } from "react";
import Image from "next/image";
import { convertToPhotoUploadItem } from "@/components/dynamicForm/AttachmentComponents/Photos/utils";

type PhotoWidgetProps = {
  attachment: FormComponentPayloadType;
};

const Attachment = ({ attachment }: PhotoWidgetProps) => {
  const [selectedPhotoIndex, setSelectedPhotoIndex] = useState(0);
  const photos = convertToPhotoUploadItem(attachment.properties.user_value);
  const isPhotoAvailable = photos?.length > 0;

  const handleNavigation = (direction: "next" | "prev") => {
    setSelectedPhotoIndex(prev =>
      direction === "next"
        ? prev === photos.length - 1
          ? 0
          : prev + 1
        : prev === 0
        ? photos.length - 1
        : prev - 1
    );
  };

  const documentDetails = (photo: UploadItem) => {
    const { size, category, date, time } = photo;
    return [size, category, date, time].filter(Boolean).join(" • ");
  };

  return attachment.properties.attachment_type === "photo" ? (
    <div className="p-4 gap-4 flex flex-col bg-brand-gray-10 rounded-lg">
      <BodyText className="text-[20px] font-semibold">
        {attachment.properties.title ?? "Photos"}{" "}
        {isPhotoAvailable ? `(${selectedPhotoIndex + 1}/${photos.length})` : ""}
      </BodyText>
      {isPhotoAvailable ? (
        <>
          <div className="flex flex-col gap-4">
            <div className="relative w-full group">
              <div
                className="absolute left-0 top-0 h-full w-1/3 cursor-pointer opacity-0 z-10"
                onClick={() => handleNavigation("prev")}
              ></div>
              <Icon
                name="chevron_big_left"
                className="absolute left-2 drop-shadow-2xl text-white cursor-pointer text-[30px] p-2 top-1/2 transform -translate-y-1/2 transition-colors hover:text-[#4ABCDC]"
                role="button"
              />
              <Image
                src={photos[selectedPhotoIndex].signedUrl}
                alt={photos[selectedPhotoIndex].displayName}
                className="bg-[#003F53] object-contain rounded-sm"
                width={800}
                height={600}
              />
              <div
                className="absolute right-0 top-0 h-full w-1/3 cursor-pointer opacity-0 z-10"
                onClick={() => handleNavigation("next")}
              ></div>
              <Icon
                name="chevron_big_right"
                className="absolute right-2 text-white drop-shadow-2xl cursor-pointer text-[30px] p-2 top-1/2 transform -translate-y-1/2 transition-colors hover:text-[#4ABCDC]"
                role="button"
              />
            </div>

            <BodyText className="text-sm text-gray-600 text-left">
              {photos[selectedPhotoIndex].description ||
                "No description available"}
            </BodyText>
          </div>
          <div className="w-full flex flex-row gap-4 overflow-x-auto pb-2">
            {photos.map((photo, index) => (
              <Image
                key={photo.id}
                src={photo.signedUrl}
                alt={photo.displayName}
                onClick={() => setSelectedPhotoIndex(index)}
                width={24}
                height={24}
                className={`
                    rounded-xs cursor-pointer object-cover 
                    transition-all duration-200
                    ${
                      selectedPhotoIndex === index
                        ? "border-2 border-[#005870] opacity-100"
                        : "border border-transparent opacity-70 hover:opacity-100"
                    }
                  `}
              />
            ))}
          </div>
        </>
      ) : (
        <BodyText className="flex text-base font-semibold text-neutrals-tertiary">
          No information provided
        </BodyText>
      )}
    </div>
  ) : (
    <div className="p-4 gap-4 flex flex-col bg-brand-gray-10 rounded-lg">
      <BodyText className="text-[20px] font-semibold">
        {attachment.properties.title ?? "Documents"}{" "}
        {isPhotoAvailable ? photos.length : ""}
      </BodyText>
      {isPhotoAvailable ? (
        <div className="space-y-2">
          {photos.map(photo => (
            <div
              key={photo.id}
              className="h-14 w-full border border-neutral-shade-38 rounded flex items-center px-2 bg-white"
              data-testid="document-item"
            >
              <Icon
                name="file_blank_outline"
                className="text-2xl flex-shrink-0"
              />
              <div className="ml-2 truncate flex-1 min-w-0">
                <BodyText className="block truncate">
                  {photo.displayName ||
                    attachment.properties.title ||
                    "Document"}
                </BodyText>
                <CaptionText className="text-xs text-gray-600">
                  {documentDetails(photo)}
                </CaptionText>
              </div>
            </div>
          ))}
        </div>
      ) : (
        <BodyText className="flex text-base font-semibold text-neutrals-tertiary">
          No information provided
        </BodyText>
      )}
    </div>
  );
};

export default Attachment;
