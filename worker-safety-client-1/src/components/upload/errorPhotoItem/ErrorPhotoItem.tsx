import { CaptionText, Icon } from "@urbint/silica";
import Button from "../../shared/button/Button";

export const ErrorPhotoItem = ({
  file,
  onRetry,
  onCancel,
}: {
  file: File;
  onRetry: () => void;
  onCancel: () => void;
}): JSX.Element => (
  <div className="flex gap-4 p-4 bg-brand-gray-10 w-full h-30">
    <div className="flex gap-4 flex-1 max-w-lg">
      <div className="w-28 h-28 rounded-md flex justify-center items-center m-1 bg-brand-urbint-60">
        <Icon name="warning_circle" className="text-red-500 text-2xl" />
      </div>
      <div className="flex-1 flex flex-col justify-center px-2 max-w-lg text-neutral-shade-75">
        <CaptionText className="md:text-sm font-semibold">Failed</CaptionText>
        <CaptionText>{file.name}</CaptionText>
      </div>
    </div>
    <div className="flex gap-2 items-center flex-col md:flex-row justify-center">
      <Button
        onClick={onRetry}
        className="md:text-sm text-neutral-shade-75"
        label="Try again"
      />
      <Button
        onClick={onCancel}
        className="md:text-sm text-neutral-shade-75"
        label="Cancel"
      />
    </div>
  </div>
);
