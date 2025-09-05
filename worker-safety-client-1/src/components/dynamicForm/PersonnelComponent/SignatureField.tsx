import type { FileInputsCWF } from "@/types/natgrid/jobsafetyBriefing";
import { useState } from "react";
import { BodyText, ComponentLabel, Icon } from "@urbint/silica";
import Image from "next/image";
import ButtonSecondary from "@/components/shared/button/secondary/ButtonSecondary";
import SketchPadDialog from "@/pages/jsb-share/natgrid/[id]/components/SketchPadDialog";
import { formatLocal } from "@/components/templatesComponents/PreviewComponents/dateUtils";

export interface SignatureFieldProps {
  displayName: string;
  initialFile?: FileInputsCWF | null;
  onSignature?: (file: FileInputsCWF) => void;
  disabled?: boolean;
}

const generateImageName = () => {
  const uuid = crypto.randomUUID();
  return `${uuid}.png`;
};

export default function SignatureField({
  displayName,
  initialFile = null,
  onSignature,
  disabled = false,
}: SignatureFieldProps) {
  const [sig, setSig] = useState<FileInputsCWF | null>(initialFile);
  const [isOpen, setOpen] = useState(false);
  const imageName = generateImageName();
  const handleSignatureSave = (blob: Blob, uploadPolicy: any) => {
    const isoUtc = new Date().toISOString();
    const [utcDate, utcClock] = isoUtc.split("T");
    const utcTime = utcClock.slice(0, 8);

    const meta: FileInputsCWF = {
      id: uploadPolicy.id,
      signedUrl: uploadPolicy.signedUrl,
      name: imageName,
      displayName: imageName,
      size: `${Math.round(blob.size / 1000)} KB`,

      date: utcDate,
      time: utcTime,
    };

    setSig(meta);
    onSignature?.(meta);
    setOpen(false);
  };

  return (
    <>
      {sig ? (
        <div className="mt-2">
          <ComponentLabel className="mb-1">Signature</ComponentLabel>
          <div className="relative w-full bg-white border border-neutral-200 rounded">
            <Image
              src={sig?.signedUrl || sig?.url || ""}
              alt={`${displayName} signature`}
              width={800}
              height={128}
              className="w-full h-32 object-contain"
              unoptimized
              priority
            />

            {!disabled && (
              <Icon
                name="edit"
                className={`absolute top-2 right-2 text-neutral-600 ${
                  disabled
                    ? "opacity-50 cursor-not-allowed"
                    : "cursor-pointer hover:text-neutral-800"
                }`}
                onClick={() => !disabled && setOpen(true)}
              />
            )}
          </div>
          {sig?.date && sig?.time && (
            <BodyText className="mt-1 text-xs text-neutral-500">
              Signed on {formatLocal(sig.date, sig.time)}
            </BodyText>
          )}
        </div>
      ) : (
        <ButtonSecondary
          iconStart="edit"
          label={`Sign for ${displayName}`}
          onClick={() => !disabled && setOpen(true)}
          disabled={disabled}
        />
      )}

      <SketchPadDialog
        isOpen={isOpen}
        onClose={() => setOpen(false)}
        name={displayName}
        onSave={handleSignatureSave}
      />
    </>
  );
}
