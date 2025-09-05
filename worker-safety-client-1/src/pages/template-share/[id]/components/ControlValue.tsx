import type {
  HexColor,
  InputSelectOption,
} from "@/components/shared/inputSelect/InputSelect";
import { BodyText } from "@urbint/silica";
import { hexToRgba } from "@/components/templatesComponents/customisedForm.utils";

type ControlValueProps = {
  options: InputSelectOption[];
  customColor: HexColor;
  noControlsImplemented: boolean;
};

const ControlValue = ({
  options,
  customColor = "#CCCCCC",
  noControlsImplemented,
}: ControlValueProps): JSX.Element => {
  return (
    <>
      {options.length > 0 && !noControlsImplemented ? (
        <>
          <div className="mb-1 text-sm font-semibold">Controls</div>
          <div className=" flex flex-wrap items-center gap-1 no-scrollbar">
            {options.map(option => (
              <div
                className={`relative flex items-center px-2 pr-1   rounded-md  border-[1px] text-[13px] text-center  text-gray-700 sm`}
                key={option.id}
                style={{
                  borderColor: customColor,
                  backgroundColor: hexToRgba(customColor, 0.4),
                }}
              >
                <span className="mr-2">{option.name}</span>
              </div>
            ))}
          </div>
        </>
      ) : (
        <div className="flex mb-3 mt-3">
          <BodyText className="text-neutrals-tertiary text-sm font-semibold">
            No controls implemented
          </BodyText>
        </div>
      )}
    </>
  );
};

export default ControlValue;
