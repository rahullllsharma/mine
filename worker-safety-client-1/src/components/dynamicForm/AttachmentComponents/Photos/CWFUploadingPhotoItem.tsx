import { CaptionText } from "@urbint/silica";
import Button from "@/components/shared/button/Button";
import { CircularLoader } from "@/components/uploadLoader/uploadLoader";

const CWFUploadingPhotoItem = ({
  file,
  onCancel,
}: {
  file: File;
  onCancel: () => void;
}): JSX.Element => (
  <div className="mb-4 flex gap-4 p-4 bg-brand-gray-10 w-full">
    <div className="inset-0 flex items-center justify-center rounded w-[120px] h-[120px] bg-brand-urbint-60">
      <CircularLoader />
    </div>
    <div className="flex-1 flex flex-col justify-center px-2 max-w-lg text-neutral-shade-75">
      <CaptionText className="md:text-sm font-semibold">Uploading</CaptionText>
      <CaptionText>{file.name}</CaptionText>
    </div>
    <div className="flex items-center">
      <Button
        onClick={onCancel}
        className="md:text-sm text-neutral-shade-75 w-auto"
        label="Cancel"
      />
    </div>
  </div>
);

export default CWFUploadingPhotoItem;
