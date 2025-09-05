import type { DebouncedFunc } from "lodash-es";
import type { ChangeEvent } from "react";
import router from "next/router";
import { useState } from "react";
import axiosRest from "@/api/customFlowApi";
import { handleFormViewMode } from "@/components/forms/Utils";
import ButtonPrimary from "@/components/shared/button/primary/ButtonPrimary";
import ButtonSecondary from "@/components/shared/button/secondary/ButtonSecondary";
import useRestMutation from "@/hooks/useRestMutation";
import { useAuthStore } from "@/store/auth/useAuthStore.store";
import Input from "../../shared/input/Input";
import AddTemplateForm from "./AddTemplateForm/AddTemplateForm";
import SelectWorkTypeModal from "./SelectWorkTypeModal/SelectWorkTypeModal";

type TemplateFormListHeaderProps = {
  pageTitle: string;
  inputPlaceHolder: string;
  toggleFilters: () => void;
  totalFilterSelected?: number;
  resultsCount?: number | null;
  totalFormsCount?: number | null;
  onChange: DebouncedFunc<(event: ChangeEvent<HTMLInputElement>) => void>;
};

type TemplateData = {
  id: string;
  templateName: string;
  workTypes: workTypes[];
};
type workTypes = {
  id: string;
  name: string;
  prepopulate?: boolean;
};

function TemplateFormListHeader({
  pageTitle,
  inputPlaceHolder,
  toggleFilters,
  totalFilterSelected,
  resultsCount,
  totalFormsCount,
  onChange,
}: TemplateFormListHeaderProps) {
  const [searchTerm, setSearchTerm] = useState<string>("");
  const [templateList, setTemplateList] = useState<any[]>([]);
  const [isFetchingTemplates, setIsFetchingTemplates] = useState(false);
  const [openAddForm, setOpenAddForm] = useState<boolean>(false);
  const [openSelectWorktypeModal, setOpenSelectWorktypeModal] =
    useState<boolean>(false);
  const [
    selectedTemplatedForWorktypeSelection,
    setSelectedTemplatedForWorktypeSelection,
  ] = useState<TemplateData | null>(null);

  const {
    me: { permissions: userPermissions },
  } = useAuthStore();

  const handleTemplatesSuccess = (responseData: any) => {
    if (responseData) {
      const mappedTemplates = responseData?.data?.data
        ?.map(
          (item: { id: string; name: string; work_types: workTypes[] }) => ({
            id: item.id,
            templateName: item.name,
            workTypes: item.work_types,
          })
        )
        ?.sort((a: any, b: any) =>
          a.templateName.localeCompare(b.templateName)
        );
      setTemplateList(mappedTemplates);
      setIsFetchingTemplates(false);
    }
  };

  const { mutate: fetchTemplatesList } = useRestMutation<any>({
    endpoint: "templates/list/add-options",
    method: "post",
    axiosInstance: axiosRest,
    dtoFn: _data => ({
      // Data transformation function
      status: "published",
      availability: "adhoc",
    }),
    mutationOptions: {
      onSuccess: handleTemplatesSuccess,
      onError: () => {
        setIsFetchingTemplates(false);
      },
    },
  });

  const handleSearchChange = (event: ChangeEvent<HTMLInputElement>) => {
    setSearchTerm(event.target.value);
    onChange(event);
  };

  const onClickOfAddForm = () => {
    setIsFetchingTemplates(true);
    fetchTemplatesList({});
    setOpenAddForm(true);
  };
  const onClickOfTemplate = (template: TemplateData) => {
    //When template has multiple work type opening work type modal
    //else skipping worktype selection & navigating to formlist
    localStorage.removeItem("selectedWorkTypes");
    if (template.workTypes.length > 1) {
      setSelectedTemplatedForWorktypeSelection(template);
      setOpenSelectWorktypeModal(true);
    } else {
      setSelectedTemplatedForWorktypeSelection(null);

      navigateToFormListPage(template.id, template.workTypes);
    }
  };

  const resetTemplateWorktypeState = () => {
    setSelectedTemplatedForWorktypeSelection(null);
    setOpenSelectWorktypeModal(false);
  };

  const navigateToFormListPage = (
    templateId: string,
    workTypes: workTypes[]
  ) => {
    resetTemplateWorktypeState();
    localStorage.setItem("selectedWorkTypes", JSON.stringify(workTypes));
    router.push(`template-forms/add/?templateId=${templateId}`);
  };

  return (
    <div>
      <AddTemplateForm
        isFetchingTemplates={isFetchingTemplates}
        isOpen={openAddForm}
        templateList={templateList}
        onClickOfTemplate={onClickOfTemplate}
        onClose={() => setOpenAddForm(false)}
      />
      <SelectWorkTypeModal
        showModal={openSelectWorktypeModal}
        selectedTemplate={selectedTemplatedForWorktypeSelection || null}
        closeModal={resetTemplateWorktypeState}
        cancel={resetTemplateWorktypeState}
        continueToForm={selectedWorkTypes => {
          navigateToFormListPage(
            selectedTemplatedForWorktypeSelection?.id || "",
            selectedWorkTypes
          );
        }}
      />

      <section className="mb-6 w-full">
        <div className="flex flex-wrap lg:flex-nowrap items-center gap-2 w-full">
          <div className="flex flex-wrap items-center gap-2 flex-1 min-w-0">
            <h4 className="text-neutral-shade-100 break-words">{pageTitle}</h4>
            <Input
              containerClassName="
            hidden lg:flex
            flex-shrink-0
            lg:w-60 max-h-[40px]"
              placeholder={inputPlaceHolder}
              value={searchTerm}
              onChange={handleSearchChange}
              icon="search"
            />
            <ButtonSecondary
              iconStart="filter"
              label={
                totalFilterSelected
                  ? `Filters (${totalFilterSelected})`
                  : "Filters"
              }
              controlStateClass="text-base p-1.5"
              className="hidden lg:flex text-neutral-shade-100 flex-shrink-0 h-[2.3rem]"
              onClick={toggleFilters}
            />
            {totalFormsCount !== null && !totalFilterSelected && (
              <p className="ml-4">
                {totalFormsCount} {totalFormsCount === 1 ? "result" : "results"}
              </p>
            )}
            {resultsCount !== null && !!totalFilterSelected && (
              <p className="ml-4">
                {resultsCount} {resultsCount === 1 ? "result" : "results"}
              </p>
            )}
          </div>
          {handleFormViewMode(userPermissions) && (
            <div className="flex flex-shrink-0 lg:ml-auto">
              <ButtonPrimary
                label="Add Form"
                onClick={() => onClickOfAddForm()}
                iconStart="plus"
              />
            </div>
          )}
        </div>
        <div className="lg:hidden mt-4">
          <Input
            containerClassName="w-full max-h-[40px] mb-2"
            placeholder={inputPlaceHolder}
            value={searchTerm}
            onChange={handleSearchChange}
            icon="search"
          />
        </div>
        <div className="lg:hidden flex justify-end w-full mb-4">
          <ButtonSecondary
            iconStart="filter"
            label={
              totalFilterSelected
                ? `Filters (${totalFilterSelected})`
                : "Filters"
            }
            controlStateClass="text-base p-1.5"
            className="text-neutral-shade-100 flex-shrink-0 h-[2.3rem]"
            onClick={toggleFilters}
          />
        </div>
      </section>
    </div>
  );
}

export default TemplateFormListHeader;
