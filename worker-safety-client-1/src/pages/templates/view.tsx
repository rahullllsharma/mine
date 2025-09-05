import type { FormType } from "@/components/templatesComponents/customisedForm.types";
import React from "react";
import { useRouter } from "next/router";
import { UserFormModeTypes } from "@/components/templatesComponents/customisedForm.types";
import useRestQuery from "@/hooks/useRestQuery";
import axiosRest from "@/api/customFlowApi";
import CSFLoader from "@/components/templatesComponents/LoaderComponent/CSFLoader";
import CreateCustomisableForm from "@/components/templatesComponents/FormPreview/CreateCustomisableForm";

const TemplateView = () => {
  const router = useRouter();
  const { templateId } = router.query;

  const { data, isLoading } = useRestQuery<FormType>({
    key: [`data-${templateId}`],
    endpoint: "/templates/" + templateId,
    axiosConfig: {
      params: {
        prepopulate: false,
      },
    },
    axiosInstance: axiosRest,
    queryOptions: {
      enabled: !!templateId,
      staleTime: Infinity,
    },
  });

  return (
    <div>
      {isLoading ? (
        <CSFLoader />
      ) : data ? (
        <div>
          <CreateCustomisableForm
            formObject={data}
            mode={UserFormModeTypes.PREVIEW_PROPS}
            linkObj={{ linkHref: "/templates", linkName: "Templates" }}
          />
        </div>
      ) : null}
    </div>
  );
};

export default TemplateView;
