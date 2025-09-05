import ButtonSecondary from "@/components/shared/button/secondary/ButtonSecondary";

type EmptySectionProps = {
  text: string;
  buttonLabel: string;
  onClick?: () => void;
};

export default function EmptySection({
  text,
  buttonLabel,
  onClick,
}: EmptySectionProps): JSX.Element {
  return (
    <div className="flex items-center py-2 text-neutral-shade-100 text-base">
      <p className="flex-1">{text}</p>

      {onClick && (
        <ButtonSecondary
          label={buttonLabel}
          onClick={onClick}
          className="flex-shrink-0"
        />
      )}
    </div>
  );
}
