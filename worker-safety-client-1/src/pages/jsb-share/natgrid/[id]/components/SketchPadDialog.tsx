import type { SketchPadDialogProps } from "@/types/natgrid/jobsafetyBriefing";
import { useState, useRef, useContext } from "react";
import SignatureCanvas from "react-signature-canvas";
import { ComponentLabel } from "@urbint/silica";
import { useMutation } from "@apollo/client";
import ReactDOM from "react-dom";
import { Dialog } from "@/components/forms/Basic/Dialog/Dialog";
import ButtonSecondary from "@/components/shared/button/secondary/ButtonSecondary";
import ButtonIcon from "@/components/shared/button/icon/ButtonIcon";
import ButtonPrimary from "@/components/shared/button/primary/ButtonPrimary";
import Labeled from "@/components/forms/Basic/Labeled";
import ToastContext from "@/components/shared/toast/context/ToastContext";
import FileUploadPolicies from "../../../../../graphql/queries/fileUploadPolicies.gql";

const SketchPadDialog = ({
  isOpen,
  onClose,
  onSave,
  name,
}: SketchPadDialogProps) => {
  const signatureRef = useRef<SignatureCanvas>(null);
  const [isSignAttempted, setIsSignAttempted] = useState(false);

  const [generateFileUploadPolicies] = useMutation(FileUploadPolicies);
  const isSignatureCanvasEmpty =
    !signatureRef.current || signatureRef.current.isEmpty();
  const [height, width] = [
    Math.min(window.innerHeight * 0.8, 300),
    Math.min(window.innerWidth * 0.8, 680),
  ];
  const toastCtx = useContext(ToastContext);
  const handleSign = async () => {
    setIsSignAttempted(true);
    if (!signatureRef.current || signatureRef.current.isEmpty()) return;

    const signatureData = signatureRef.current.toDataURL();
    const blob = pngToBinary(signatureData);
    try {
      const { data } = await generateFileUploadPolicies({
        variables: { count: 1 },
      });
      const policy = data?.fileUploadPolicies?.[0];
      if (!policy) {
        toastCtx?.pushToast("error", "No upload policy returned");
        return;
      }
      const uploadSuccess = await uploadToGcs(blob, policy);
      if (!uploadSuccess) {
        toastCtx?.pushToast("error", "File upload failed");
        return;
      }
      onSave(blob, policy);
    } catch (error) {
      toastCtx?.pushToast(
        "error",
        "Error generating file upload policies or uploading file"
      );
    }
  };

  const pngToBinary = (base64string: string): Blob => {
    const [, data] = base64string.split(",");
    const byteString = Buffer.from(data, "base64");
    return new Blob([byteString], { type: "image/png" });
  };

  const uploadToGcs = async (fileBlob: Blob, policy: any) => {
    try {
      const { url, fields } = policy;
      if (!url || !fields) {
        toastCtx?.pushToast("error", "Invalid policy fields or URL");
        return false;
      }

      const parsedFields =
        typeof fields === "string" ? JSON.parse(fields) : fields;

      const formData = new FormData();
      Object.keys(parsedFields).forEach(key => {
        formData.append(key, parsedFields[key]);
      });
      formData.append("file", fileBlob);
      const res = await fetch(url, {
        method: "POST",
        body: formData,
      });
      return res.ok;
    } catch (err) {
      toastCtx?.pushToast("error", "Error uploading to GCS:");
      return false;
    }
  };

  if (!isOpen) return null;

  return ReactDOM.createPortal(
    <div className="fixed inset-0 z-[9999] bg-black bg-opacity-30 flex items-center justify-center">
      <Dialog size="flex">
        <div className="flex flex-col gap-4">
          <div className="flex justify-between items-center">
            <ComponentLabel className="text-xl font-semibold">
              Sign for {name}
            </ComponentLabel>
            <ButtonIcon
              iconName="close_big"
              onClick={onClose}
              className="border border-gray-200 rounded-md flex items-center justify-center w-10 h-10 cursor-pointer"
            />
          </div>

          <div className="flex flex-col gap-4">
            <Labeled label="Please sign your name in the box below">
              <SignatureCanvas
                ref={signatureRef}
                canvasProps={{
                  width: width,
                  height: height,
                  className: "border border-gray-300 rounded",
                }}
              />
            </Labeled>
          </div>

          <div className="flex flex-col gap-2">
            {isSignAttempted && isSignatureCanvasEmpty && (
              <ComponentLabel className="text-red-500 text-sm">
                Signature is required.
              </ComponentLabel>
            )}
            <div className="flex flex-row justify-end gap-2">
              <ButtonSecondary label="Cancel" onClick={onClose} />
              <ButtonPrimary label="Sign" onClick={handleSign} />
            </div>
          </div>
        </div>
      </Dialog>
    </div>,
    document.body
  );
};

export default SketchPadDialog;
