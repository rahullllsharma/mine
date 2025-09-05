import type { AddPageListItemProps } from "../../customisedForm.types";
import { Icon } from "@urbint/silica";

const AddPageListItem = ({
  newPageTitle,
  setNewPageTitle,
}: AddPageListItemProps) => {
  return (
    <div>
      <div className="relative p-3 flex w-full items-center text-base font-normal text-neutral-shade-100 rounded-md border border-solid lg:flex  border-neutral-shade-26 rounded-md focus-within:ring-1 focus-within:ring-brand-gray-60 bg-neutral-light-100">
        <Icon
          name="circle"
          className="text-neutral-shade-58 border-2 border-transparent box-border"
        />

        <input
          type="text"
          placeholder="Page Title"
          value={newPageTitle}
          onChange={e => {
            setNewPageTitle(e.target.value);
          }}
          className="flex-auto rounded-md appearance-none focus:outline-none disabled:bg-neutral-light-77 read-only:cursor-default disabled:cursor-not-allowed disabled:opacity-38 min-w-0 pl-2"
        />
      </div>
    </div>
  );
};

export default AddPageListItem;
