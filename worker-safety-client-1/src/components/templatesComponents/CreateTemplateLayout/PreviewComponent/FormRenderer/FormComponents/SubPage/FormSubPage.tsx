import { Icon } from "@urbint/silica";
import { PageType } from "@/components/templatesComponents/customisedForm.types";

const FormSubPage = ({ item }: { item: PageType }) => {
  return (
    <div className="bg-white flex items-center shadow rounded-lg border-l-10 px-4 py-6 justify-between items-center gap-2">
      <div className="flex flex-col w-full gap-2">
        <div className="flex flex-row justify-between w-full gap-2">
          <span className="text-base text-neutral-shade-100 font-semibold">
            {item.properties.title}
          </span>
          <div
            className="flex items-center font-bold h-5 p-0.5 w-max uppercase whitespace-nowrap"
            role="note"
          >
            <Icon name="chevron_right" />
          </div>
        </div>
      </div>
    </div>
  );
};

export default FormSubPage;
