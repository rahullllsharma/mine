import type { IconName } from "@urbint/silica";
import { useState } from "react";
import { flow } from "fp-ts/lib/function";
import { nanoid } from "nanoid";
import { Icon } from "@urbint/silica";
import cx from "classnames";
import * as O from "fp-ts/lib/Option";
import { IconSpinner } from "@/components/iconSpinner";

export type UploadButtonConfigs = {
  icon: IconName;
  label: string;
  isLoading: boolean;
  allowMultiple: boolean;
  allowedExtensions: string;
  maxFileSize?: number;
};

type Props = {
  configs: UploadButtonConfigs;
  className: string;
  onUpload: (fs: FileList) => void;
};

const generateRandomKey = (): string => {
  return Math.random().toString(36);
};

export const View = ({ configs, className, onUpload }: Props) => {
  const [key, setKey] = useState(generateRandomKey());
  const inputId = nanoid();

  return (
    <>
      <label
        htmlFor={inputId}
        className={cx(
          "px-2.5 py-2 rounded-md cursor-pointer",
          "flex items-center justify-center",
          "bg-neutral-light-100 border border-neutral-shade-26 shadow-5 hover:shadow-10",
          "hover:bg-neutral-light-16 focus:bg-neutral-shade-7 active:bg-neutral-shade-7",
          {
            ["opacity-38 cursor-not-allowed"]: configs.isLoading,
          },
          className
        )}
        onClick={() => setKey(generateRandomKey())}
      >
        {configs.icon && (
          <Icon
            className="text-base leading-5 text-neutral-shade-75"
            name={configs.icon}
          />
        )}
        <span className="mx-1 truncate text-base leading-5 text-neutral-shade-75 font-semibold">
          {configs.label}
        </span>
        {configs.isLoading && <IconSpinner />}
      </label>
      <input
        id={inputId}
        key={key}
        type="file"
        className="hidden"
        multiple={configs.allowMultiple}
        accept={configs.allowedExtensions}
        onChange={flow(
          e => O.fromNullable(e.target.files),
          fs => O.isSome(fs) && onUpload(fs.value)
        )}
      />
    </>
  );
};
