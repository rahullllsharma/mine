import { useState } from "react";
import Image from "next/image";
import { IconSpinner } from "../../iconSpinner";
import FieldTextArea from "../../shared/field/fieldTextArea/FieldTextArea";
import Button from "../../shared/button/Button";
import { PhotoItemErrorOverlay } from "./PhotoItemErrorOverlay"; 

type OnDescriptionChange = (value: string) => void;

export const PhotoItem = ({
  url = "",
  name,
  onDelete,
  readOnly = false,
  description,
  onDescriptionChange,
}: {
  url?: string;
  name: string;
  onDelete: (event: React.MouseEvent<HTMLButtonElement>) => void;
  readOnly?: boolean;
  description?: string;
  onDescriptionChange: OnDescriptionChange;
}): JSX.Element => {
  const [isImageLoaded, setIsImageLoaded] = useState<boolean>(false);
  const [imageError, setImageError] = useState<boolean>(false);
  const [reloadKey, setReloadKey] = useState<number>(0);
  const currentSrc = url ? `${url}${reloadKey}` : "";

  const handleImageEvent = (isError: boolean) => {
    setIsImageLoaded(true);
    setImageError(isError);
  };

  const reloadImage = () => {
    setIsImageLoaded(false); 
    setImageError(false);    
    setReloadKey((prevKey) => prevKey + 1); 
  };

  const showSpinner = !isImageLoaded && !imageError;

  return (
      <div className="relative w-full" data-testid="photo-item"> 

        {showSpinner && (
          <div className="absolute rounded w-[120px] h-[120px] flex justify-center items-center m-4 bg-brand-urbint-60">
            <IconSpinner className={"text-2xl text-gray-200"} />
          </div>
        )}
        <div className="flex flex-row gap-4 p-4 bg-brand-gray-10">
          {url && (
            <div className="relative">
              <Image
                key={reloadKey}
                src={currentSrc}
                alt={name}
                width={120}
                height={120}
                className="rounded"
                placeholder="blur"
                blurDataURL={url}
                onLoadingComplete={() => handleImageEvent(false)}
                onError={() => handleImageEvent(true)}
              />       
            
              {imageError && (
                <PhotoItemErrorOverlay 
                  onReload={reloadImage} 
                  showSpinner={showSpinner} 
                />
              )}
            </div>
          )}

          {url && (
            <div className="flex-1 px-2 max-w-lg">
              <FieldTextArea
                htmlFor="description"
                label="Description"
                placeholder="Add a description"
                initialValue={description}
                onChange={onDescriptionChange}
                rows={2}
                isDisabled={readOnly}
              />
            </div>
          )}

          {!readOnly && (
            <Button
              iconStart="trash_empty"
              className="text-xl mb-8"
              onClick={onDelete}
              aria-label="Delete photo"
            />
          )}
        </div>
      </div>
  );
};