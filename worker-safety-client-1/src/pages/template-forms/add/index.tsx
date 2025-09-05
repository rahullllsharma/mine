import axiosRest from "@/api/customFlowApi";
import { UserFormModeTypes, type FormType } from "@/components/templatesComponents/customisedForm.types";
import CSFLoader from "@/components/templatesComponents/LoaderComponent/CSFLoader";
import useRestQuery from "@/hooks/useRestQuery";
import { useRouter } from "next/router";
import { useRef } from "react";

import CreateCustomisableForm from "@/components/templatesComponents/FormPreview/CreateCustomisableForm";
import { useWorkPackageData } from "@/hooks/useWorkPackageData";
import { useTenantStore } from "@/store/tenant/useTenantStore.store";

const GeneratedFormInstance = () => {
  const router = useRouter();
  const { templateId, project, location, startDate } = router.query;
  const shouldFetchProjectDetails = !!project && !!location;

  const { workPackageData, projectDetails } = useWorkPackageData({
    projectId: project,
    locationId: location,
    shouldFetch: shouldFetchProjectDetails,
  });

  const projectDescription = projectDetails?.project?.description;

  const { workPackage, templateForm } = useTenantStore(state =>
    state.getAllEntities()
  );

  const hasCreatedForm = useRef(false);

  const { data, isLoading } = useRestQuery<FormType>({
    key: [`data-${templateId}`],
    endpoint: `/templates/${templateId}`,
    axiosConfig: {},
    axiosInstance: axiosRest,
    queryOptions: {
      enabled: !!templateId,
      cacheTime: 0,
      staleTime: 0,
      onSuccess: templateData => {
        // Only proceed if we have all required data and haven't created the form yet
        if (
          !templateData ||
          (shouldFetchProjectDetails && !projectDetails) ||
          hasCreatedForm.current
        ) {
          return;
        }
        hasCreatedForm.current = true;
      },
    },
  });

  const mergedFormObject = {
    ...data,
    properties: {
      ...data?.properties,
      description: projectDescription,
    },
  };

  return (
    <div>
      {isLoading || (shouldFetchProjectDetails && !workPackageData) ? (
        <CSFLoader />
      ) : data ? (
        <div>
          {data ? (
            <CreateCustomisableForm
              formObject={mergedFormObject as FormType}
              mode={UserFormModeTypes.EDIT}
              linkObj={
                project
                  ? {
                      linkHref: `/projects/${project}?location=${location}&startDate=${startDate}`,
                      linkName:
                        `${workPackage?.label} Summary View` ||
                        "Work Package Summary View",
                    }
                  : {
                      linkHref: "/template-forms",
                      linkName: templateForm?.labelPlural,
                    }
              }
              workPackageData={workPackageData}
              projectDetails={projectDetails}
              creatingForm={true}
            />
          ) : null}
        </div>
      ) : null}
    </div>
  );
};

export default GeneratedFormInstance;
