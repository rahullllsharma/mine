import type {
  HexColor,
  InputSelectOption,
} from "@/components/shared/inputSelect/InputSelect";
import { hexToRgba } from "@/components/templatesComponents/customisedForm.utils";
import { Icon } from "@urbint/silica";

type ControlValueSelectComponentProps = {
  options: InputSelectOption[];
  customColor: HexColor;
  readOnly?: boolean;

  openModal: () => void;
  onRemoveOption: (id: string) => void;
  isSummaryView?: boolean;
};

function ControlValueSelectComponent({
  options,
  customColor = "#CCCCCC",
  onRemoveOption,
  openModal,
  isSummaryView = false,
  readOnly,
}: ControlValueSelectComponentProps) {
  const removeOption = (id: string, e: React.MouseEvent) => {
    onRemoveOption(id);
    e.stopPropagation();
  };

  return (
    <>
      <div className="w-full mx-auto  ">
        <div
          className={`rounded-md pt-1 pb-1 pl-2 pr-2 ${
            isSummaryView ? "" : "border-[1px] border-gray-200 shadow-sm"
          }
              bg-white
            `}
          onClick={readOnly ? undefined : openModal}
        >
          {options.length > 0 ? (
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
                  {!isSummaryView && (
                    <button
                      disabled={readOnly}
                      onClick={e => removeOption(option.id, e)}
                      className={`text-gray-400 hover:text-gray-600 rounded-full p-1 ${
                        readOnly ? "pointer-events-none opacity-60" : ""
                      }`}
                      title={`Remove ${option.name}`}
                    >
                      <Icon
                        name={"close_small"}
                        className="border-[1px]  border-gray-500 rounded-full  text-[11px] mt-[20px] leading-none text-gray-500 hover:text-black hover:border-black"
                      />
                    </button>
                  )}
                </div>
              ))}
            </div>
          ) : (
            <div className="p-2 flex items-center justify-between cursor-pointer ">
              <div>Please select a control</div>
              <div>
                <Icon
                  name="chevron_big_down"
                  className="text-gray-500 hover:text-gray-700"
                />
              </div>
            </div>
          )}
        </div>
      </div>
    </>
  );
}

export default ControlValueSelectComponent;
