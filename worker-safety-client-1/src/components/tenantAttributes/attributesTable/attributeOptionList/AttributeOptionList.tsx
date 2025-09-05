import { Icon } from "@urbint/silica";

type AttributeOptionListProps = {
  isFilterable: boolean;
  isRequired: boolean;
  isVisible: boolean;
};

function AttributeOptionList({
  isFilterable,
  isRequired,
  isVisible,
}: AttributeOptionListProps): JSX.Element {
  const iconStyles = "text-xl leading-5 text-neutral-shade-75";

  if (!isVisible) {
    return <Icon name="hide" className={iconStyles} />;
  }

  return (
    <ul className="flex gap-2">
      <li key="visible">
        <Icon name="show" className={iconStyles} />
      </li>
      {isRequired && (
        <li key="required">
          <Icon name="asterisk" className={iconStyles} />
        </li>
      )}
      {isFilterable && (
        <li key="filterable">
          <Icon name="filter" className={iconStyles} />
        </li>
      )}
    </ul>
  );
}

export { AttributeOptionList };
export type { AttributeOptionListProps };
