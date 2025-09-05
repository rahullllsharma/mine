import type { PhotoUploadItem } from "@/components/templatesComponents/customisedForm.types";
import { Icon } from "@urbint/silica";
import React, { useState } from "react";

type PhotoWidgetProps = {
  photos: PhotoUploadItem[];
  title?: string;
  isInputAttachment?: boolean;
  inSummary?: boolean;
};

const ImageGallery = ({
  photos,
  title,
  isInputAttachment,
  inSummary,
}: PhotoWidgetProps) => {
  const [selectedPhotoIndex, setSelectedPhotoIndex] = useState(0);

  if (photos.length === 0) {
    return <p className="text-center text-gray-500">No photos uploaded</p>;
  }

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

  return (
    <div className="max-w-4xl mx-auto rounded-sm">
      <h2
        className={`${
          inSummary ? "text-[20px]" : "text-xl"
        } font-semibold text-[#041E25] mb-4`}
      >
        {title ? title : "Photos"}({selectedPhotoIndex + 1}/{photos.length})
      </h2>

      <div className="flex flex-col gap-5">
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
          <img
            src={
              isInputAttachment
                ? (photos[selectedPhotoIndex] as unknown as string)
                : photos[selectedPhotoIndex].signedUrl
            }
            alt={photos[selectedPhotoIndex].displayName}
            className="w-[800px] h-[600px] bg-[#003F53] object-contain rounded-sm"
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

        {!isInputAttachment && (
          <div className="mt-4">
            <p className="text-sm text-gray-600 mt-2 text-left">
              {photos[selectedPhotoIndex].description ||
                "No description available"}
            </p>
          </div>
        )}

        <div className="w-full flex flex-row gap-4 overflow-x-auto pb-2">
          {photos.map((photo, index) => (
            <img
              key={index}
              src={
                isInputAttachment
                  ? (photo as unknown as string)
                  : photo.signedUrl
              }
              alt={photo.displayName}
              onClick={() => setSelectedPhotoIndex(index)}
              className={`
                rounded-xs w-24 h-24 cursor-pointer object-cover 
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
      </div>
    </div>
  );
};

export default ImageGallery;
