import type {
  RenderOptionFn,
  SelectOption,
} from "@/components/shared/select/Select";
import type { NavItemProps } from "./navItem/NavItem";
import cx from "classnames";
import { Select } from "@/components/shared/select/Select";
import { defaultRenderOptionFn } from "../shared/select/selectPrimary/SelectPrimary";
import Sidebar from "../sidebar/Sidebar";
import NavItem from "./navItem/NavItem";

export type NavigationStatus =
  | "default"
  | "completed"
  | "saved"
  | "saved_current"
  | "error";

export type SelectStatusAndIcon =
  | {
      status: "default";
      icon: "circle";
    }
  | {
      status: "completed";
      icon: "circle_check";
    }
  | {
      status: "error";
      icon: "error";
    };

export type NavigationOption = Pick<
  NavItemProps,
  "name" | "icon" | "iconSize" | "status" | "isSubStep"
> & {
  id: number;
  onSelect?: () => void;
};

export type NavigationProps = {
  options: NavigationOption[];
  selectedIndex: number;
  withStatus?: boolean;
  sidebarClassNames?: string;
  selectClassNames?: string;
  onChange: (index: number) => void;
};

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

export default function Navigation({
  options,
  selectedIndex,
  withStatus = false,
  sidebarClassNames,
  selectClassNames,
  onChange,
}: NavigationProps): JSX.Element {
  const navigationSelectHandler = (option: SelectOption<NavigationOption>) => {
    const index = options.findIndex(opt => opt.id === option.id);
    onChange(index);
  };

  return (
    <>
      <div className={cx("hidden md:block", sidebarClassNames)}>
        <Sidebar
          options={options}
          selectedIndex={selectedIndex}
          onChange={onChange}
        />
      </div>
      <Select
        className={cx("md:hidden block", selectClassNames)}
        options={options}
        onSelect={navigationSelectHandler}
        defaultOption={options[selectedIndex]}
        optionsClassNames="py-2"
        renderOptionFn={withStatus ? renderOptionFn : defaultRenderOptionFn}
      />
    </>
  );
}
