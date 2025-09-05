import type { Project } from "@/types/project/Project";
import type { DailyReport } from "@/types/report/DailyReport";
import type { SectionItem } from "./projectPrintSection/ProjectPrintSection";
import type { EntityAttributeMap } from "@/store/tenant/types";
import { convertDateToString } from "@/utils/date/helper";
import { projectStatusOptions } from "@/types/project/ProjectStatus";
import { useTenantStore } from "@/store/tenant/useTenantStore.store";
import ProjectPrintSection from "./projectPrintSection/ProjectPrintSection";

type ProjectPrintInfoProps = {
  project: Project;
  report: DailyReport;
};

const getProjectDetails = (
  {
    name,
    externalKey,
    libraryProjectType,
    libraryAssetType,
    status,
    projectZipCode,
    startDate,
    endDate,
    libraryDivision,
    libraryRegion,
    description,
  }: Project,
  report: DailyReport,
  attributes: EntityAttributeMap
): SectionItem[] => [
  { title: attributes.name.label, description: name },
  ...(attributes.externalKey.visible
    ? [{ title: attributes.externalKey.label, description: externalKey }]
    : []),
  ...(attributes.workPackageType.visible
    ? [
        {
          title: attributes.workPackageType.label,
          description: libraryProjectType?.name,
        },
      ]
    : []),
  ...(attributes.assetType.visible
    ? [
        {
          title: attributes.assetType.label,
          description: libraryAssetType?.name,
        },
      ]
    : []),
  {
    title: attributes.status.label,
    description: projectStatusOptions().find(option => option.id === status)
      ?.name,
  },
  ...(attributes.zipCode.visible
    ? [{ title: attributes.zipCode.label, description: projectZipCode }]
    : []),
  { title: attributes.startDate.label, description: startDate },
  { title: attributes.endDate.label, description: endDate },
  ...(attributes.division.visible
    ? [{ title: attributes.division.label, description: libraryDivision?.name }]
    : []),
  ...(attributes.region.visible
    ? [{ title: attributes.region.label, description: libraryRegion?.name }]
    : []),
  ...(attributes.description.visible
    ? [{ title: attributes.description.label, description: description }]
    : []),
  { title: "Record number", description: report.id },
  {
    title: "Report creation date",
    description: convertDateToString(report.createdAt),
  },
  { title: "Report creator", description: report.createdBy.name },
];

const getProjectTeamMembers = (
  { manager, supervisor, additionalSupervisors, engineerName }: Project,
  attributes: EntityAttributeMap
): SectionItem[] => [
  ...(attributes.projectManager.visible
    ? [{ title: attributes.projectManager.label, description: manager?.name }]
    : []),
  ...(attributes.primaryAssignedPerson.visible
    ? [
        {
          title: attributes.primaryAssignedPerson.label,
          description: supervisor?.name,
        },
      ]
    : []),
  ...(attributes.additionalAssignedPerson.visible
    ? [
        {
          title: `${attributes.additionalAssignedPerson.label}(s)`,
          description: additionalSupervisors?.map(user => user.name),
        },
      ]
    : []),
  { title: "Engineer", description: engineerName },
];

const getContractInformation = (
  { contractReference, contractName, contractor }: Project,
  attributes: EntityAttributeMap
): SectionItem[] => [
  ...(attributes.contractReferenceNumber.visible
    ? [
        {
          title: attributes.contractReferenceNumber.label,
          description: contractReference,
        },
      ]
    : []),
  ...(attributes.contractName.visible
    ? [{ title: attributes.contractName.label, description: contractName }]
    : []),
  ...(attributes.primeContractor.visible
    ? [
        {
          title: attributes.primeContractor.label,
          description: contractor?.name,
        },
      ]
    : []),
];

export default function ProjectPrintInfo({
  project,
  report,
}: ProjectPrintInfoProps): JSX.Element {
  const { workPackage } = useTenantStore(state => state.getAllEntities());
  return (
    <div className="flex flex-col gap-10">
      <ProjectPrintSection
        header={`${workPackage.label} details`}
        items={getProjectDetails(project, report, workPackage.attributes)}
      />
      <ProjectPrintSection
        header={`${workPackage.label} team members`}
        items={getProjectTeamMembers(project, workPackage.attributes)}
      />
      <ProjectPrintSection
        header="Contract information"
        items={getContractInformation(project, workPackage.attributes)}
      />
    </div>
  );
}
