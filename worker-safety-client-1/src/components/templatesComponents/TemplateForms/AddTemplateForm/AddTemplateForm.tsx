import Flyover from "@/components/flyover/Flyover";

type TemplateData = {
  id: string;
  templateName: string;
  workTypes: workTypes[];
};
type workTypes = {
  id: string;
  name: string;
};

type AddTemplateFormProps = {
  isFetchingTemplates: boolean;
  templateList: TemplateData[];
  isOpen: boolean;
  onClickOfTemplate: (template: any) => void;
  onClose: () => void;
};

function renderWorkTypesSummary(workTypes: workTypes[]) {
  const maxToShow = 3;
  const shown = workTypes.slice(0, maxToShow);
  const remaining = workTypes.length - maxToShow;
  return (
    <>
      {shown.map((workType, idx) => (
        <span key={workType.id}>
          {workType.name}
          {idx < shown.length - 1 ? ", " : ""}
        </span>
      ))}
      {remaining > 0 && <span>...+{remaining}</span>}
    </>
  );
}

const AddTemplateForm = ({
  isFetchingTemplates,
  isOpen,
  templateList,
  onClickOfTemplate,
  onClose,
}: AddTemplateFormProps): JSX.Element => {
  return (
    <>
      <Flyover
        isOpen={isOpen}
        title="Select Form"
        unmount
        onClose={onClose}
        footerStyle={"!relative right-0 !bottom-[1.5rem]"}
        className={"h-full pb-5 md:!w-[25rem]"}
      >
        {isFetchingTemplates ? (
          "Loading"
        ) : (
          <>
            {templateList.map(template => (
              <div
                key={template.id}
                className="border border-gray-200 p-4 rounded-sm cursor-pointer mt-2 hover:bg-gray-100"
                onClick={() => onClickOfTemplate(template)}
              >
                <div
                  className="font-semibold"
                  style={{
                    display: "-webkit-box",
                    WebkitLineClamp: 2,
                    WebkitBoxOrient: "vertical",
                    overflow: "hidden",
                    textOverflow: "ellipsis",
                    whiteSpace: "normal",
                  }}
                >
                  {template.templateName}
                </div>
                <div className="text-gray-400 text-[13px] mt-1">
                  {renderWorkTypesSummary(template?.workTypes || [])}
                </div>
              </div>
            ))}
          </>
        )}
      </Flyover>
    </>
  );
};

export default AddTemplateForm;
