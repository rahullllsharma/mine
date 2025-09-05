import type { DailyInspectionReport as DailyInspectionReportProps } from "@/container/report/dailyInspection/types";
import type { AuthUser } from "@/types/auth/AuthUser";
import type { TenantEntity } from "@/types/tenant/TenantEntities";
import { FormProvider, useForm } from "react-hook-form";
import PrintReport from "@/container/report/print/PrintReport";
import { useTenantStore } from "@/store/tenant/useTenantStore.store";

export type DailyReportPrintTemplateProps = {
  user: AuthUser & { entities: TenantEntity[] };
  dailyReport: Required<
    NonNullable<DailyInspectionReportProps["dailyReport"]>
  > & {
    location: DailyInspectionReportProps["location"] &
      Pick<DailyInspectionReportProps, "project">;
  };
};

const DailyReportPrintTemplate = (
  props: DailyReportPrintTemplateProps
): JSX.Element => {
  const { setTenant } = useTenantStore.getState();

  setTenant({
    name: "",
    displayName: "Urbint",
    entities: props.user.entities,
    workos: [],
  });
  const { dailyReport } = props;

  const {
    sections: {
      safetyAndCompliance,
      jobHazardAnalysis,
      crew,
      additionalInformation,
    },
    location,
  } = dailyReport;

  const methods = useForm({
    defaultValues: {
      safetyAndCompliance,
      jobHazardAnalysis,
      crew,
      additionalInformation,
    },
  });

  return (
    <FormProvider {...methods}>
      <PrintReport project={location.project} report={dailyReport} />
    </FormProvider>
  );
};

export { DailyReportPrintTemplate };
