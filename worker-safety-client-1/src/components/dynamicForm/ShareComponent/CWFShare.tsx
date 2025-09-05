import type { UserFormMode } from "@/components/templatesComponents/customisedForm.types";
import QRCode from "react-qr-code";
import Image from "next/image";
import { useContext } from "react";
import { UserFormModeTypes } from "@/components/templatesComponents/customisedForm.types";
import ShareIcon from "@/publicAssets/JSB/Share.svg";
import ToastContext from "@/components/shared/toast/context/ToastContext";

export default function CWFShare({
  formId,
  link,
  mode,
}: Readonly<{
  formId?: string;
  link?: string;
  mode?: UserFormMode;
}>) {
  const toastCtx = useContext(ToastContext);

  const isTemplate =
    mode === UserFormModeTypes.BUILD ||
    mode === UserFormModeTypes.PREVIEW ||
    mode === UserFormModeTypes.PREVIEW_PROPS;

  const domain =
    typeof window !== "undefined" && window.location.origin
      ? window.location.origin
      : "https://www.urbint.com";
  const staticPageAddress = `${domain}/template-share/${formId}`;

  const hasShareSupport = typeof navigator !== "undefined" && !!navigator.share;
  return (
    <div className="w-32 border rounded items-center content-center flex flex-col flex-wrap">
      <div className="p-2">
        <QRCode
          value={isTemplate ? "" : link || staticPageAddress}
          size={112}
          viewBox={`16 16 128 128`}
        />
      </div>
      {hasShareSupport ? (
        <button
          disabled={isTemplate}
          className={`text-brand-urbint-50 flex items-center justify-center bg-gray-100 py-1 w-full rounded-b flex-1 ${
            isTemplate ? "cursor-not-allowed" : ""
          }`}
          onClick={async () => {
            try {
              await navigator.share({
                url: staticPageAddress,
              } as ShareData);
            } catch (error) {}
          }}
        >
          <Image src={ShareIcon} alt="share" />
          Share
        </button>
      ) : (
        <button
          className="text-brand-urbint-50 flex items-center justify-center bg-gray-100 py-1 w-full rounded-b flex-1"
          onClick={async () => {
            try {
              await navigator.clipboard.writeText(staticPageAddress);
              toastCtx?.pushToast("success", "Copied URL");
            } catch (error) {}
          }}
        >
          <Image src={ShareIcon} alt="share" />
          Copy Link
        </button>
      )}
    </div>
  );
}
