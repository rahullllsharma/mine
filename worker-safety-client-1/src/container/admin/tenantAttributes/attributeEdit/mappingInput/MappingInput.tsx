import { Badge } from "@urbint/silica";
import { TextContent } from "@/container/admin/tenantAttributes/attributeEdit/mappingInput/textContent/TextContent";

type MappingInputProps = {
  defaultLabel: string;
  label: string;
  badgeNumber: number;
  isDefault?: boolean;
  onSubmit: (label: string) => void;
  onEditOpen?: () => void;
  onEditClose?: () => void;
};

const MappingInput = ({
  label,
  defaultLabel,
  badgeNumber,
  isDefault,
  onSubmit,
  onEditOpen,
  onEditClose,
}: MappingInputProps) => {
  return (
    <div className="flex items-center gap-2">
      <Badge
        className="px-0 py-3 bg-brand-urbint-40 text-white"
        label={badgeNumber.toString()}
      />
      <TextContent
        label={label}
        defaultLabel={defaultLabel}
        isDefault={isDefault}
        onSubmit={onSubmit}
        onEditOpen={onEditOpen}
        onEditClose={onEditClose}
      />
    </div>
  );
};

export { MappingInput };
