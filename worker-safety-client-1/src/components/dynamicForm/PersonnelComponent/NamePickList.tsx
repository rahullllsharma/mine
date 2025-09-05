import type { PersonelRow } from "@/components/templatesComponents/customisedForm.types";
import { Icon } from "@urbint/silica";

type GroupMap = {
  [key: string]: { label: string; ids: string[] };
};

interface Props {
  allUsers: PersonelRow[];
  selectedIds: string[];
  disabledIds: string[];
  toggle: (id: string) => void;
  customNames?: PersonelRow[];
  groups?: GroupMap;
}

const NamePickList = ({
  allUsers,
  selectedIds,
  disabledIds,
  toggle,
  customNames = [],
  groups,
}: Props) => {
  const isCustom = (u: PersonelRow) =>
    customNames.find(cn => cn.id === u.id) !== undefined;

  const directoryUsers = allUsers.filter(u => !isCustom(u));
  const otherUsers = allUsers.filter(isCustom);

  const renderRow = (user: PersonelRow) => {
    const checked = selectedIds.includes(user.id);
    const disabled = disabledIds.includes(user.id);

    const rightText = user.employeeNumber ?? "";
    const jobInParens = user.jobTitle ? ` (${user.jobTitle})` : "";
    const leftText = `${user.name}${jobInParens}`;

    return (
      <li
        key={user.id}
        onClick={() => !disabled && toggle(user.id)}
        className={`
          flex items-center justify-between rounded-md border p-2
          ${
            disabled && !checked
              ? "cursor-not-allowed opacity-40"
              : "cursor-pointer hover:bg-neutral-50"
          }
          ${checked ? "border-blue-300" : "border-neutral-200"}
        `}
      >
        <span className="truncate text-sm font-medium text-neutral-900">
          {leftText}
        </span>

        <div className="flex items-center gap-2 text-sm text-neutral-700">
          {rightText && <span>{rightText}</span>}
          {checked && (
            <Icon
              name="check_bold"
              className="text-xl leading-none text-brand-urbint-40"
            />
          )}
        </div>
      </li>
    );
  };

  if (groups) {
    const sections = Object.values(groups).map(({ label, ids }) => ({
      label,
      rows: allUsers.filter(u => ids.includes(u.id)),
    }));

    return (
      <div className="flex flex-col overflow-y-auto">
        {sections.map(
          ({ label, rows }) =>
            rows.length > 0 && (
              <div key={label}>
                <div className="py-1 px-2 text-l font-semibold text-neutral-600">
                  {label}
                </div>
                <ul className="space-y-2">{rows.map(renderRow)}</ul>
                {label !== sections[sections.length - 1].label && (
                  <hr className="my-3" />
                )}
              </div>
            )
        )}
      </div>
    );
  }
  return (
    <div className="flex flex-col overflow-y-auto">
      <ul className="space-y-2 max-h-104">{directoryUsers.map(renderRow)}</ul>

      {otherUsers.length > 0 && (
        <>
          <hr className="my-3" />
          <span className="mb-1 text-xs font-semibold text-neutral-600">
            Other Names
          </span>
          <ul className="space-y-2">{otherUsers.map(renderRow)}</ul>
        </>
      )}
    </div>
  );
};

export default NamePickList;
