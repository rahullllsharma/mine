import type {
  EntityAttributes,
  EntityAttributeKey,
} from "@/types/tenant/TenantEntities";
import { useMemo } from "react";
import { Icon } from "@urbint/silica";
import Table from "@/components/table/Table";
import ButtonIcon from "@/components/shared/button/icon/ButtonIcon";
import Tooltip from "@/components/shared/tooltip/Tooltip";
import { AttributeOptionList } from "./attributeOptionList/AttributeOptionList";

export type AttributesTableProps = {
  data: EntityAttributes[];
  onEdit: (attributeKey: EntityAttributeKey) => void;
};

type TableData = {
  key: EntityAttributeKey;
  name: string;
  defaultName: string;
  isMandatory: boolean;
  isVisible: boolean;
  isRequired: boolean;
  isFilterable: boolean;
};

function AttributesTable({ data, onEdit }: AttributesTableProps): JSX.Element {
  const tableData = useMemo<TableData[]>(
    () =>
      data.map(entry => ({
        key: entry.key,
        name: entry.label,
        defaultName: entry.defaultLabel,
        isMandatory: entry.mandatory,
        isVisible: entry.visible,
        isRequired: entry.required,
        isFilterable: entry.filterable,
      })),
     
    [data]
  );
  const tableColumns = [
    {
      id: "attribute_name",
      isLocked: false,
      Header: "Attribute Name",
      width: 380,
      accessor: ({ name, defaultName }: TableData) => {
        const isTooltipVisible = defaultName !== name;

        return (
          <div className="flex gap-2">
            <span className="text-base font-semibold text-brand-urbint-50">
              {name}
            </span>
            {isTooltipVisible && (
              <Tooltip
                title={`Original value: "${defaultName}"`}
                position="top"
                containerClasses="ml-2 flex"
              >
                <Icon name="info_circle" className="text-xl leading-5" />
              </Tooltip>
            )}
          </div>
        );
      },
    },
    {
      id: "options",
      isLocked: false,
      Header: "Options",
      width: 100,
      accessor: ({
        isMandatory,
        isRequired,
        isVisible,
        isFilterable,
      }: TableData) => (
        <AttributeOptionList
          isVisible={isMandatory || isVisible}
          isRequired={isMandatory || isRequired}
          isFilterable={isFilterable}
        />
      ),
    },
    {
      id: "actions",
      isLocked: false,
      Header: "Actions",
      width: 50,
      accessor: ({ key }: TableData) => (
        <div className="w-full flex justify-end">
          <ButtonIcon
            iconName="edit"
            className="p-1"
            onClick={() => {
              onEdit(key);
            }}
          />
        </div>
      ),
    },
  ];

  return <Table columns={tableColumns} data={tableData} />;
}

export { AttributesTable };
