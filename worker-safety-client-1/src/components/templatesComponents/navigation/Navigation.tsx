import type { ChangeEvent } from "react";
import router from "next/router";
import ButtonPrimary from "../../shared/button/primary/ButtonPrimary";
import ButtonSecondary from "../../shared/button/secondary/ButtonSecondary";
import Input from "../../shared/input/Input";

type ListNavigationParams = {
  toggleFilters: () => void;
  totalFilterSelected?: number;
  searchValue: string;
  onSearchChange?: (event: ChangeEvent<HTMLInputElement>) => void;
};

const ListNavigationBar = ({
  toggleFilters,
  totalFilterSelected,
  searchValue,
  onSearchChange,
}: ListNavigationParams): JSX.Element => {
  const createTemplate = () => {
    return router.push("templates/create");
  };

  return (
    <section className="flex mb-6">
      <div className="flex flex-1">
        <h4 className="text-neutral-shade-100">Templates</h4>
        <Input
          containerClassName="hidden lg:flex lg:w-60 ml-6"
          placeholder={`Search Templates`}
          value={searchValue}
          onChange={onSearchChange}
          icon="search"
        />
        <ButtonSecondary
          iconStart="filter"
          label={
            totalFilterSelected ? `Filters (${totalFilterSelected})` : "Filters"
          }
          controlStateClass="text-base p-1.5"
          className="text-neutral-shade-100 flex-shrink-0 ml-6 h-[2.3rem]"
          onClick={toggleFilters}
        />
      </div>
      <div className="flex">
        <ButtonPrimary label="Create Template" onClick={createTemplate} />
      </div>
    </section>
  );
};

export { ListNavigationBar };
