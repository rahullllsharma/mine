import type { FC, HTMLProps } from "react";
import { SectionHeading } from "@urbint/silica";
import classnames from "classnames";

type FieldGroupProps = HTMLProps<HTMLFieldSetElement> & {
  id?: string;
  className?: string;
  legend?: string;
};

const FieldGroup: FC<FieldGroupProps> = ({
  children,
  id,
  legend,
  className,
}) => {
  return (
    <fieldset id={id} className="flex flex-col gap-3">
      {legend && (
        <legend>
          <SectionHeading className="text-xl font-semibold p-4 md:p-0">
            {legend}
          </SectionHeading>
        </legend>
      )}
      <div
        className={classnames(
          "p-2 sm:p-4 flex flex-col gap-3 bg-brand-gray-10",
          className
        )}
      >
        {children}
      </div>
    </fieldset>
  );
};

export { FieldGroup };
