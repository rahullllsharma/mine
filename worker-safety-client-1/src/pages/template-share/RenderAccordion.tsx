import type { FormElement } from "@/components/templatesComponents/customisedForm.types";
import { Icon } from "@urbint/silica";

const RenderAccordion = ({
  isOpen,
  setIsOpen,
  element,
}: {
  isOpen: boolean;
  setIsOpen: (isOpen: boolean) => void;
  element: FormElement;
}) => {
  return (
    <div className="w-full flex-1 flex flex-row">
      <button
        className={`flex w-full items-center gap-2 text-left p-2`}
        onClick={() => setIsOpen(!isOpen)}
      >
        <Icon
          name="chevron_big_right"
          className={`text-[20px] transform transition-transform duration-200 ${
            isOpen ? "rotate-90" : ""
          }`}
        />
        <div className={`flex items-center text-[20px] font-semibold`}>
          {element.properties.title}
        </div>
      </button>
    </div>
  );
};

export default RenderAccordion;
