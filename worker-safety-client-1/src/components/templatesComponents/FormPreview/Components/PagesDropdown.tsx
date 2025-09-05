import type { NavigationOption } from "@/components/navigation/Navigation";
import NavItem from "@/components/navigation/navItem/NavItem";
import type {
  RenderOptionFn,
  SelectOption,
} from "@/components/shared/select/Select";
import { Select } from "@/components/shared/select/Select";
import { Icon } from "@urbint/silica";
import cx from "classnames";
import { useEffect, useState } from "react";
import type { ActivePageObjType, FormType } from "../../customisedForm.types";

const statusIconClassNames = {
  default: {
    icon: "circle",
    iconClassName: "text-neutral-shade-58",
    buttonClassName: "border-2 border-transparent box-border",
  },
  current: {
    icon: "circle",
    iconClassName: "text-neutral-shade-58",
    buttonClassName: "border-2 border-neutral-shade-100 box-border",
  },
  saved: {
    icon: "circle_check",
    iconClassName: "text-brand-urbint-40",
    buttonClassName: "border-2 border-transparent bg-brand-urbint-10",
  },
  saved_current: {
    icon: "circle_check",
    iconClassName: "text-brand-urbint-40",
    buttonClassName:
      "border-2 bg-brand-urbint-10 border-brand-urbint-30 box-border",
  },
  completed: {
    icon: "circle_check",
    iconClassName: "text-brand-urbint-40",
    buttonClassName: "border-2 border-transparent bg-brand-urbint-10",
  },
  error: {
    icon: "error",
    iconClassName: "text-system-error-40",
    buttonClassName:
      "border-2 border-system-error-40 bg-system-error-10 box-border",
  },
};

type PagesDropdownProps = {
  formObject: FormType;
  onSelectOfDropdown: (option: any) => void;
  activePageDetails?: ActivePageObjType;
};

function PagesDropdown({
  onSelectOfDropdown,
  formObject,
  activePageDetails,
}: PagesDropdownProps) {
  const renderOptionFn: RenderOptionFn<NavigationOption> = ({
    listboxOptionProps: { selected },
    option: { name, icon, status },
  }) => (
    <NavItem
      as="li"
      icon={icon}
      name={name}
      status={status}
      markerType="left"
      isSelected={selected}
    />
  );

  // Custom render for the selected value in the button
  const renderSelectedValue = (option: NavigationOption | undefined) => {
    if (!option) return null;
    const statusProps = statusIconClassNames[option.status || "default"];
    return (
      <div className="relative flex items-center  py-3 rounded h-12 w-full hover:shadow-10   text-neutral-shade-100 cursor-pointer  ">
        <div className="mr-2">
          <Icon
            name={statusProps.icon as any}
            className={`${statusProps.iconClassName} text-xl`}
          />
        </div>
        <div>{option.name}</div>
      </div>
    );
  };

  const [pageInfoForDropdownOptions, setPageInfoForDropdownOptions] = useState<
    NavigationOption[]
  >([]);
  const [selectedPageFromDropdown, setSelectedPageFromDropdown] = useState<
    NavigationOption | undefined
  >(undefined);

  useEffect(() => {
    const dropdownOptions: NavigationOption[] = formObject.contents
      .map((item, index) => {
        if (item.type === "page") {
          const status = item.properties.page_update_status || "default";
          const statusProps = statusIconClassNames[status];
          return {
            id: index,
            icon: statusProps.icon,
            iconSize: "md",
            name: item.properties.title,
            status: status,
          };
        }
        return null;
      })
      .filter(Boolean) as NavigationOption[];

    setPageInfoForDropdownOptions(dropdownOptions);

    if (dropdownOptions.length > 0 && !selectedPageFromDropdown) {
      setSelectedPageFromDropdown(dropdownOptions[0]);
    }
  }, [formObject]);

  useEffect(() => {
    if (activePageDetails && pageInfoForDropdownOptions.length > 0) {
      const pageIndex = formObject.contents.findIndex(
        item => item.id === activePageDetails.id
      );

      if (pageIndex !== -1) {
        const matchingOption = pageInfoForDropdownOptions.find(
          option => option.id === pageIndex
        );

        if (matchingOption) {
          setSelectedPageFromDropdown(matchingOption);
        }
      }
    }
  }, [activePageDetails, pageInfoForDropdownOptions, formObject.contents]);

  const onSelectPageDropdown = (option: SelectOption<NavigationOption>) => {
    const index = pageInfoForDropdownOptions.findIndex(
      opt => opt.id === option.id
    );
    onSelectOfDropdown(formObject.contents[index]);
    setSelectedPageFromDropdown(pageInfoForDropdownOptions[index]);
  };

  return (
    <>
      <Select
        className={cx("tab-md:hidden flex-col tab-md:bg-white w-100 mb-1")}
        options={pageInfoForDropdownOptions}
        onSelect={onSelectPageDropdown}
        defaultOption={selectedPageFromDropdown}
        renderOptionFn={renderOptionFn}
        renderSelectedValue={renderSelectedValue}
      />
    </>
  );
}

export default PagesDropdown;
