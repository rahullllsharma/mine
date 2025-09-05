import { Icon } from "@urbint/silica";

export default function UrbintLogo({
  className,
  color,
}: {
  className?: string;
  color?: string;
}): JSX.Element {
  return (
    <Icon
      name="urbint"
      title="Urbint"
      className={`h-auto ${className}`}
      style={{ color }}
    />
  );
}
