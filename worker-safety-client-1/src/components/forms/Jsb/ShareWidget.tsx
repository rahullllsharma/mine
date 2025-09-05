import { useRouter } from "next/router";
import QRCode from "react-qr-code";
import Image from "next/image";
import { useContext } from "react";
import ShareIcon from "@/publicAssets/JSB/Share.svg";
import ToastContext from "@/components/shared/toast/context/ToastContext";

export default function ShareWidget({
  withAction = true,
  externalJsbId,
  link,
}: Readonly<{
  withAction?: boolean;
  externalJsbId?: string;
  link?: string;
}>) {
  const {
    query: { jsbId, id, locationId },
  } = useRouter();
  const toastCtx = useContext(ToastContext);

  const domain =
    typeof window !== "undefined" && window.location.origin
      ? window.location.origin
      : "https://www.urbint.com";
  const staticPageAddress = `${domain}/jsb-share/${
    jsbId || id || externalJsbId
  }${locationId ? `?locationId=${locationId}` : ""}`;

  const hasShareSupport = typeof navigator !== "undefined" && !!navigator.share;
  return (
    <div className="w-32 flex-grow border rounded items-center content-center flex flex-col flex-wrap">
      <div className="p-2">
        <QRCode
          value={link || staticPageAddress}
          size={112}
          viewBox={`16 16 128 128`}
        />
      </div>
      {withAction ? (
        hasShareSupport ? (
          <button
            className="text-brand-urbint-50 flex items-center justify-center bg-gray-100 py-1 w-full rounded-b flex-1"
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
        )
      ) : null}
    </div>
  );
}
