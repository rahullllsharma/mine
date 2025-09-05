import clx from "classnames";

interface InsightsListItemProps {
  name: string;
  isActive?: boolean;
  onClick: () => void;
}

const InsightsListItem = ({
  name,
  isActive = false,
  onClick,
}: InsightsListItemProps): JSX.Element => {
  return (
    <button
      className={clx(
        "p-3 bg-neutral-shade-3 rounded flex w-full items-center text-left text-gray-700 transition-colors hover:text-black",
        {
          "border-2 border-black": isActive,
        }
      )}
      onClick={onClick}
    >
      <span className="break-words max-w-full">{name}</span>
    </button>
  );
};

export default InsightsListItem;
