import type { ModeTypePageSection } from "../../customisedForm.types";
import { Icon } from "@urbint/silica";
import { Checkbox } from "@/components/forms/Basic/Checkbox";
import { StepItem } from "@/components/forms/Basic/StepItem";

type PageDelete = {
  status: any;
  label: string;
  mode: ModeTypePageSection;
  onSelectOfPage: () => void;
  selected: boolean;
  onSelectOfCheckbox: () => void;
};

export default function withDeletePage({
  status,
  label,
  mode,
  onSelectOfPage,
  selected,
  onSelectOfCheckbox,
}: PageDelete) {
  return (
    <>
      <div className="relative">
        {mode === "deletePage" && (
          <div className="absolute" style={{ top: "15px", left: "13px" }}>
            <Checkbox
              checked={selected}
              onClick={() => onSelectOfCheckbox()}
            ></Checkbox>
          </div>
        )}
        {mode === "dragPage" && (
          <>
            <div
              className="absolute"
              style={{
                top: "9px",
                left: "13px",
                fontSize: "22px",
                background: "whitesmoke",
              }}
            >
              <Icon name="grid_vertical_round" />
            </div>
          </>
        )}
        <StepItem status={status} label={label} onClick={onSelectOfPage} />
      </div>
    </>
  );
}
