import type {
  FormType,
  UserFormMode,
} from "@/components/templatesComponents/customisedForm.types";
import { useEffect, useState } from "react";
import { useRouter } from "next/router";
import axiosRest from "@/api/customFlowApi";
import { handleFormMode } from "@/components/forms/Utils";
import { UserFormModeTypes } from "@/components/templatesComponents/customisedForm.types";
import CreateCustomisableForm from "@/components/templatesComponents/FormPreview/CreateCustomisableForm";
import CSFLoader from "@/components/templatesComponents/LoaderComponent/CSFLoader";
import useRestQuery from "@/hooks/useRestQuery";
import { useWorkPackageData } from "@/hooks/useWorkPackageData";
import { useAuthStore } from "@/store/auth/useAuthStore.store";
import { useTenantStore } from "@/store/tenant/useTenantStore.store";

const ViewFormInstance = () => {
  const [mode, setMode] = useState<UserFormMode>(UserFormModeTypes.PREVIEW);
  const router = useRouter();
  const { formId, project, location, startDate } = router.query;
  const {
    me: { id: userId, permissions: userPermissions },
  } = useAuthStore();

  const { workPackage } = useTenantStore(state => state.getAllEntities());

  const { data, isLoading } = useRestQuery<FormType>({
    key: [`data-${formId}`],
    endpoint: `/forms/${formId}`,
    axiosConfig: {},
    axiosInstance: axiosRest,
    queryOptions: {
      enabled: !!formId,
      staleTime: 0,
      cacheTime: 0,
    },
  });

  const isOwn = data?.created_by?.id === userId;
  const isCompleted = data?.properties?.status === "completed";
  const { getAllEntities } = useTenantStore();
  const { templateForm } = getAllEntities();

  useEffect(() => {
    setMode(handleFormMode(userPermissions, isOwn, isCompleted));
  }, [userPermissions, isOwn, isCompleted]);

  const cwfWorkPackageData = data?.metadata?.work_package
    ? {
        workPackageName: data?.metadata.work_package.name,
        locationName: data?.metadata?.location?.name || "",
        project: data?.metadata.work_package?.id,
        location: data?.metadata.location?.id,
      }
    : undefined;

  const shouldFetchProjectDetails =
    !!cwfWorkPackageData?.project && !!cwfWorkPackageData?.location;

  const { workPackageData } = useWorkPackageData({
    projectId: cwfWorkPackageData?.project,
    locationId: cwfWorkPackageData?.location,
    shouldFetch: shouldFetchProjectDetails,
  });

  if (isLoading || (shouldFetchProjectDetails && !workPackageData)) {
    return <CSFLoader />;
  }

  if (!data) {
    return null;
  }

  return (
    <div>
      <CreateCustomisableForm
        formObject={data}
        mode={mode}
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
                linkName: `${templateForm?.labelPlural}`,
              }
        }
        setMode={setMode}
        workPackageData={workPackageData}
      />
    </div>
  );
};

export default ViewFormInstance;
