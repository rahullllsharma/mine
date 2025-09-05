import Plans from "@/components/report/jobReport/safetyAndCompliance/plans/Plans";
import JobBrief from "@/components/report/jobReport/safetyAndCompliance/jobBrief/JobBrief";
import WorkMethods from "@/components/report/jobReport/safetyAndCompliance/workMethods/WorkMethods";
import DigSafeMarkOuts from "@/components/report/jobReport/safetyAndCompliance/digSafeMarkOuts/DigSafeMarkOuts";
import SystemOperatingProcedures from "@/components/report/jobReport/safetyAndCompliance/systemOperatingProcedures/SystemOperatingProcedures";
import SpottersSafetyObserver from "@/components/report/jobReport/safetyAndCompliance/spottersSafetyObserver/SpottersSafetyObserver";
import PrivateProtectionEquipment from "@/components/report/jobReport/safetyAndCompliance/privateProtectionEquipment/PrivateProtectionEquipment";
import OperatorQualifications from "@/components/report/jobReport/safetyAndCompliance/operatorQualifications/OperatorQualifications";

export type SafetyAndComplianceProps = {
  isCompleted?: boolean;
};

export default function SafetyAndCompliance({
  isCompleted,
}: SafetyAndComplianceProps): JSX.Element {
  return (
    <>
      <Plans isCompleted={isCompleted} />
      <JobBrief isCompleted={isCompleted} />
      <WorkMethods isCompleted={isCompleted} />
      <DigSafeMarkOuts isCompleted={isCompleted} />
      <SystemOperatingProcedures isCompleted={isCompleted} />
      <SpottersSafetyObserver isCompleted={isCompleted} />
      <PrivateProtectionEquipment isCompleted={isCompleted} />
      <OperatorQualifications isCompleted={isCompleted} />
    </>
  );
}
