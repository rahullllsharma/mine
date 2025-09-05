import type { PropsWithClassName } from "@/types/Generic";
import cx from "classnames";

type ParagraphProps = PropsWithClassName<{
  text?: string;
}>;

//TODO Once we start tackling HHDS 2.0, we should revisit this component
export default function Paragraph({
  text = "",
  className,
}: ParagraphProps): JSX.Element {
  return (
    <p className={cx("text-base text-neutral-shade-100", className)}>{text}</p>
  );
}
