import type { PropsWithClassName } from "@/types/Generic";
import type { IconName } from "@urbint/silica";
import type { ComponentProps, MouseEventHandler, ReactNode } from "react";
import { Menu, Transition } from "@headlessui/react";
import { Icon, CaptionText } from "@urbint/silica";
import cx from "classnames";
import { Fragment, useEffect, useRef, useState } from "react";
import ButtonRegular from "../button/regular/ButtonRegular";

type HeadlessMenuItemProps = ComponentProps<typeof Menu.Item>;

export type MenuItemProps = Pick<HeadlessMenuItemProps, "disabled"> & {
  label: string;
  icon?: IconName;
  rightSlot?: ReactNode;
  onClick?: MouseEventHandler<HTMLButtonElement>;
  infoText?: string;
};

export type DropdownProps = PropsWithClassName<{
  icon?: IconName;
  label?: string;
  menuItems: MenuItemProps[][];
  dropdownClassName?: string;
  onOpenChange?: (open: boolean) => void;
  simple?: boolean;
}>;

function MenuItem({
  menuItem: { label, icon, onClick, disabled, rightSlot, infoText },
}: {
  menuItem: MenuItemProps;
}): JSX.Element {
  return (
    <Menu.Item as="li" className="flex items-center" disabled={disabled}>
      <button
        className={cx(
          "flex flex-1 items-center justify-between gap-2 px-3 py-2 text-base",
          {
            "text-neutral-shade-100 hover:bg-neutral-shade-3": !disabled,
            "disabled:text-neutral-shade-38 disabled:hover:bg-none disabled:cursor-default":
              disabled,
          }
        )}
        disabled={disabled}
        onClick={onClick}
      >
        <div className="flex items-center gap-2">
          {icon && <Icon name={icon} />}
          <div className="flex flex-col items-start">
            <p className="text-left flex-shrink-0 flex-grow">{label}</p>
            <CaptionText className="text-neutral-shade-75">{infoText}</CaptionText>
          </div>
        </div>
        {rightSlot}
      </button>
    </Menu.Item>
  );
}

function MenuSection({
  menuItems,
}: {
  menuItems: MenuItemProps[];
}): JSX.Element {
  return (
    <ul className="py-2">
      {menuItems.map((item, index) => (
        <MenuItem key={index} menuItem={item} />
      ))}
    </ul>
  );
}

// Separate component to handle the open state and useEffect
function MenuContent({
  open,
  button,
  menuItems,
  dropdownClassName,
  onOpenChange,
}: {
  open: boolean;
  button: ReactNode;
  menuItems: MenuItemProps[][];
  dropdownClassName?: string;
  onOpenChange?: (open: boolean) => void;
}) {
  useEffect(() => {
    onOpenChange?.(open);
  }, [open, onOpenChange]);

  return (
    <>
      <Menu.Button as={Fragment}>{button}</Menu.Button>
      <Transition
        as={Fragment}
        enter="transition ease-out duration-100"
        enterFrom="transform opacity-0 scale-95"
        enterTo="transform opacity-100 scale-100"
        leave="transition ease-in duration-75"
        leaveFrom="transform opacity-100 scale-100"
        leaveTo="transform opacity-0 scale-95"
      >
        <Menu.Items
          as="div"
          className={cx(
            "absolute right-0 mt-1 bg-white shadow-20 rounded-md w-max divide-y divide-solid divide-neutral-shade-18 outline-none z-10",
            dropdownClassName
          )}
        >
          {menuItems.map((items, index) => (
            <MenuSection key={index} menuItems={items} />
          ))}
        </Menu.Items>
      </Transition>
    </>
  );
}

// Simple dropdown implementation without Headless UI
function SimpleDropdownContent({
  open,
  setOpen,
  button,
  menuItems,
  dropdownClassName,
  onOpenChange,
}: {
  open: boolean;
  setOpen: (open: boolean) => void;
  button: ReactNode;
  menuItems: MenuItemProps[][];
  dropdownClassName?: string;
  onOpenChange?: (open: boolean) => void;
}) {
  const ref = useRef<HTMLDivElement>(null);

  useEffect(() => {
    function handleClickOutside(event: MouseEvent) {
      if (ref.current && !ref.current.contains(event.target as Node)) {
        setOpen(false);
      }
    }
    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, [setOpen]);

  useEffect(() => {
    onOpenChange?.(open);
  }, [open, onOpenChange]);

  return (
    <div className="relative" ref={ref}>
      <div onClick={() => setOpen(!open)}>{button}</div>
      {open && (
        <div
          className={cx(
            "absolute right-0 mt-1 bg-white shadow-20 rounded-md w-48 z-10",
            dropdownClassName
          )}
        >
          {menuItems.map((items, sectionIndex) => (
            <div key={sectionIndex}>
              {items.map((item, index) => (
                <div key={`${sectionIndex}-${index}`}>
                  <button
                    className={cx(
                      "w-full text-left px-4 py-3 text-base font-medium text-neutral-shade-100 hover:bg-neutral-shade-3 focus:outline-none",
                      {
                        "disabled:text-neutral-shade-38 disabled:hover:bg-none disabled:cursor-default":
                          item.disabled,
                      }
                    )}
                    onClick={event => {
                      setOpen(false);
                      if (item.onClick) {
                        item.onClick(event);
                      }
                    }}
                    disabled={item.disabled}
                  >
                    {item.icon && <Icon name={item.icon} />}
                    <span className="ml-2">{item.label}</span>
                    {item.rightSlot}
                  </button>
                  {index < items.length - 1 && (
                    <div className="border-b border-neutral-shade-18" />
                  )}
                </div>
              ))}
              {sectionIndex < menuItems.length - 1 && (
                <div className="border-b border-neutral-shade-18" />
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

export default function Dropdown({
  children,
  icon,
  label,
  menuItems,
  className,
  dropdownClassName,
  onOpenChange,
  simple = false,
}: DropdownProps): JSX.Element {
  const button = children ?? <ButtonRegular label={label} iconStart={icon} />;
  const [simpleOpen, setSimpleOpen] = useState(false);

  if (simple) {
    return (
      <SimpleDropdownContent
        open={simpleOpen}
        setOpen={setSimpleOpen}
        button={button}
        menuItems={menuItems}
        dropdownClassName={dropdownClassName}
        onOpenChange={onOpenChange}
      />
    );
  }

  return (
    <Menu as="div" className={cx("relative", className)} data-testid="dropdown">
      {({ open }) => (
        <MenuContent
          open={open}
          button={button}
          menuItems={menuItems}
          dropdownClassName={dropdownClassName}
          onOpenChange={onOpenChange}
        />
      )}
    </Menu>
  );
}
