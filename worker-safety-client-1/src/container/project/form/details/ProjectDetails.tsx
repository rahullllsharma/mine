import type { SelectOption } from "@/components/shared/select/Select";
import type { ProjectFormProps } from "@/pages/projects/create";
import type { User } from "@/types/User";
import type { FormFieldError } from "@/types/form/FormFieldError";
import type { ProjectInputs } from "@/types/form/Project";
import type { Contractor } from "@/types/project/Contractor";
import type { LibraryAssetType } from "@/types/project/LibraryAssetType";
import type { LibraryDivision } from "@/types/project/LibraryDivision";
import type { LibraryProjectType } from "@/types/project/LibraryProjectType";
import type { LibraryRegion } from "@/types/project/LibraryRegion";
import type { ProjectStatusOption } from "@/types/project/ProjectStatus";
import type { PropsWithChildren } from "react";
import type { TenantWorkTypes } from "../../../../types/project/TenantWorkTypes";
import { Controller, useFormContext } from "react-hook-form";
import { projectStatusOptions } from "@/types/project/ProjectStatus";
import { useTenantStore } from "@/store/tenant/useTenantStore.store";
import { usePageContext } from "@/context/PageProvider";
import {
  getRequiredFieldRules,
  requiredFieldRules,
} from "@/container/project/form/utils";
//TODO: Replace FieldTextArea with FieldTextEditor => import FieldTextEditor from "@/components/shared/field/fieldTextEditor/FieldTextEditor";
import FieldTextArea from "@/components/shared/field/fieldTextArea/FieldTextArea";
import FieldSelect from "@/components/shared/field/fieldSelect/FieldSelect";
import FieldSearchSelect from "@/components/shared/field/fieldSearchSelect/FieldSearchSelect";
import FieldMultiSelect from "@/components/shared/field/fieldMultiSelect/FieldMultiSelect";
import FieldInput from "@/components/shared/field/fieldInput/FieldInput";
import FieldDatePicker from "@/components/shared/field/fieldDatePicker/FieldDatePicker";
import { getDatesBoundaries } from "./utils";

type ProjectDetailsProps = {
  readOnly?: boolean;
};

type FieldTemplateProps = PropsWithChildren<{
  testId: string;
}>;

const getProjectStatusOptions = (
  options: ProjectStatusOption
): SelectOption[] => {
  return options.map(option => option);
  /*
    Making the Completed option selectable in the Work Package 
    even if the Activity status ain't Complete as per the requirement for WORK-2322 
    As of now this feature has been temporarily removed to keep CodeBase clean. 
    */
};

const FieldTemplate = ({
  testId,
  children,
}: FieldTemplateProps): JSX.Element => {
  return (
    <div data-testid={testId} className="flex flex-col pb-4">
      {children}
    </div>
  );
};

const getOptions = (collection: User[] | Contractor[]) =>
  collection.map(({ id, name }) => ({ id, name }));

const projectDateCaption = (
  workPackageLabel: string,
  activitiesLabel: string
) =>
  `${workPackageLabel} contains ${activitiesLabel.toLowerCase()} that might limit the date range`;

export default function ProjectDetails({
  readOnly = false,
}: ProjectDetailsProps): JSX.Element {
  const { getAllEntities } = useTenantStore();
  const { workPackage, activity } = getAllEntities();
  const {
    formState: { errors },
    getValues,
    watch,
  } = useFormContext<ProjectInputs>();

  const {
    project,
    divisionsLibrary,
    regionsLibrary,
    projectTypesLibrary,
    assetTypesLibrary,
    managers,
    supervisors,
    contractors,
    tenantWorkTypes,
  } = usePageContext<ProjectFormProps>();

  const { minimumTaskDate: minProjectDate, maximumTaskDate: maxProjectDate } =
    project || {};

  const {
    name,
    status,
    startDate,
    endDate,
    libraryDivisionId,
    libraryRegionId,
    libraryProjectTypeId,
    tenantWorkTypesId,
    externalKey,
    description = "",
    managerId,
    supervisorId,
    additionalSupervisors,
    contractorId,
    contractReference,
    contractName,
    libraryAssetTypeId,
    engineerName,
    projectZipCode,
  } = getValues();

  const { minStartDate, minEndDate } = getDatesBoundaries(
    watch("startDate"),
    minProjectDate,
    maxProjectDate
  );

  const shouldShowDateCaption = minProjectDate || maxProjectDate;

  const watchSupervisorId = watch("supervisorId");
  const watchAdditionalSupervisors = watch("additionalSupervisors");

  const projectAvailableStatus: SelectOption[] = getProjectStatusOptions(
    projectStatusOptions()
  );

  const managersOptions = getOptions(managers);
  const supervisorsOptions = getOptions(supervisors);
  const contractorOptions = getOptions(contractors);

  return (
    <div>
      <h6 data-testid="work-package-details">{`${workPackage.label} Details`}</h6>

      <div className="mt-4">
        <FieldTemplate testId="work-package-name">
          <Controller
            name="name"
            rules={requiredFieldRules}
            defaultValue={name}
            render={({ field }) => (
              <FieldInput
                htmlFor="name"
                id="name"
                label={workPackage.attributes.name.label}
                error={errors.name?.message}
                placeholder={workPackage.attributes.name.label}
                required
                readOnly={readOnly}
                {...field}
              />
            )}
          />
        </FieldTemplate>

        {workPackage.attributes.externalKey.visible && (
          <FieldTemplate testId="work-package-external-key">
            <Controller
              name="externalKey"
              defaultValue={externalKey}
              rules={getRequiredFieldRules(
                workPackage.attributes.externalKey.required
              )}
              render={({ field }) => (
                <FieldInput
                  htmlFor="externalKey"
                  id="externalKey"
                  label={workPackage.attributes.externalKey.label}
                  placeholder="Ex. 3591283"
                  error={errors.externalKey?.message}
                  required={workPackage.attributes.externalKey.required}
                  readOnly={readOnly}
                  {...field}
                />
              )}
            />
          </FieldTemplate>
        )}

        {workPackage.attributes.workPackageType.visible && (
          <FieldTemplate testId="work-package-type">
            <Controller
              name="libraryProjectTypeId"
              rules={getRequiredFieldRules(
                workPackage.attributes.workPackageType.required
              )}
              defaultValue={libraryProjectTypeId}
              render={({ field: { onChange, ref } }) => (
                <FieldSelect
                  htmlFor="libraryProjectTypeId"
                  label={workPackage.attributes.workPackageType.label}
                  placeholder={`Select ${workPackage.attributes.workPackageType.label.toLowerCase()}`}
                  options={projectTypesLibrary}
                  defaultOption={projectTypesLibrary.find(
                    (option: LibraryProjectType) =>
                      option.id === libraryProjectTypeId
                  )}
                  isInvalid={!!errors.libraryProjectTypeId}
                  error={errors.libraryProjectTypeId?.message}
                  required={workPackage.attributes.workPackageType.required}
                  buttonRef={ref}
                  onSelect={(option: SelectOption) => onChange(option.id)}
                  readOnly={readOnly}
                />
              )}
            />
          </FieldTemplate>
        )}

        {workPackage.attributes.workTypes.visible && (
          <FieldTemplate testId="work-package-type">
            <Controller
              name="tenantWorkTypesId"
              rules={getRequiredFieldRules(
                workPackage.attributes.workTypes.required
              )}
              defaultValue={tenantWorkTypesId}
              render={({ field: { onChange, ref } }) => {
                const multiSelectErrors = errors as FormFieldError;

                return (
                  <FieldMultiSelect
                    htmlFor="tenantWorkTypesId"
                    label={workPackage.attributes.workTypes.label}
                    placeholder={`Select ${workPackage.attributes.workTypes.label.toLowerCase()}(s)`}
                    options={tenantWorkTypes}
                    defaultOption={tenantWorkTypes.filter(
                      (option: TenantWorkTypes) =>
                        tenantWorkTypesId?.includes(option.id)
                    )}
                    buttonRef={ref}
                    onSelect={selectedOptions => {
                      onChange(selectedOptions.map(option => option.id));
                    }}
                    error={multiSelectErrors.tenantWorkTypesId?.message}
                    isInvalid={!!multiSelectErrors.tenantWorkTypesId}
                    required={workPackage.attributes.workTypes.required}
                    readOnly={readOnly}
                  />
                );
              }}
            />
          </FieldTemplate>
        )}

        {workPackage.attributes.assetType.visible && (
          <FieldTemplate testId="work-package-asset-type">
            <Controller
              name="libraryAssetTypeId"
              defaultValue={libraryAssetTypeId}
              rules={getRequiredFieldRules(
                workPackage.attributes.assetType.required
              )}
              render={({ field: { onChange, ref } }) => (
                <FieldSelect
                  htmlFor="libraryAssetTypeId"
                  label={workPackage.attributes.assetType.label}
                  placeholder={`Select ${workPackage.attributes.assetType.label.toLowerCase()}`}
                  options={assetTypesLibrary}
                  defaultOption={assetTypesLibrary.find(
                    (option: LibraryAssetType) =>
                      option.id === libraryAssetTypeId
                  )}
                  buttonRef={ref}
                  onSelect={(option: SelectOption) => onChange(option.id)}
                  required={workPackage.attributes.assetType.required}
                  isInvalid={!!errors.libraryAssetTypeId}
                  error={errors.libraryAssetTypeId?.message}
                  readOnly={readOnly}
                />
              )}
            />
          </FieldTemplate>
        )}

        <FieldTemplate testId="work-package-status">
          <Controller
            name="status"
            rules={requiredFieldRules}
            defaultValue={status}
            render={({ field: { onChange, ref } }) => (
              <FieldSelect
                htmlFor="status"
                label={workPackage.attributes.status.label}
                options={projectAvailableStatus}
                defaultOption={projectAvailableStatus.find(
                  option => option.id === status
                )}
                isInvalid={!!errors.status}
                error={errors.status?.message}
                required
                buttonRef={ref}
                onSelect={(option: SelectOption) => onChange(option.id)}
                readOnly={readOnly}
              />
            )}
          />
        </FieldTemplate>

        {workPackage.attributes.zipCode.visible && (
          <FieldTemplate testId="work-package-zip-code">
            <Controller
              name="projectZipCode"
              defaultValue={projectZipCode}
              rules={getRequiredFieldRules(
                workPackage.attributes.zipCode.required
              )}
              render={({ field }) => (
                <FieldInput
                  htmlFor="projectZipCode"
                  id="projectZipCode"
                  label={workPackage.attributes.zipCode.label}
                  placeholder="Ex. 10010"
                  error={errors.projectZipCode?.message}
                  required={workPackage.attributes.zipCode.required}
                  readOnly={readOnly}
                  {...field}
                />
              )}
            />
          </FieldTemplate>
        )}

        <div className="flex pb-4 gap-4">
          <div
            className="flex flex-1 flex-col"
            data-testid="work-package-start-date"
          >
            <Controller
              name="startDate"
              rules={requiredFieldRules}
              defaultValue={startDate}
              render={({ field }) => (
                <FieldDatePicker
                  htmlFor="startDate"
                  id="startDate"
                  label={workPackage.attributes.startDate.label}
                  error={errors.startDate?.message}
                  required
                  readOnly={readOnly}
                  {...field}
                  max={minStartDate}
                  caption={
                    shouldShowDateCaption
                      ? projectDateCaption(
                          workPackage.label,
                          activity.labelPlural
                        )
                      : ""
                  }
                />
              )}
            />
          </div>

          <div
            className="flex flex-1 flex-col"
            data-testid="work-package-end-date"
          >
            <Controller
              name="endDate"
              rules={{
                ...requiredFieldRules,
                min: {
                  value: minEndDate ?? "",
                  message: `Date cannot be before ${workPackage.attributes.startDate.label.toLowerCase()}`,
                },
              }}
              defaultValue={endDate}
              render={({ field }) => (
                <FieldDatePicker
                  htmlFor="endDate"
                  id="endDate"
                  label={workPackage.attributes.endDate.label}
                  error={errors.endDate?.message}
                  required
                  readOnly={readOnly}
                  {...field}
                  min={minEndDate}
                />
              )}
            />
          </div>
        </div>

        {workPackage.attributes.division.visible && (
          <FieldTemplate testId="work-package-division">
            <Controller
              name="libraryDivisionId"
              rules={getRequiredFieldRules(
                workPackage.attributes.division.required
              )}
              defaultValue={libraryDivisionId}
              render={({ field: { onChange, ref } }) => (
                <FieldSelect
                  htmlFor="libraryDivisionId"
                  label={workPackage.attributes.division.label}
                  placeholder="Ex. Gas"
                  options={divisionsLibrary}
                  defaultOption={divisionsLibrary.find(
                    (option: LibraryDivision) => option.id === libraryDivisionId
                  )}
                  isInvalid={!!errors.libraryDivisionId}
                  error={errors.libraryDivisionId?.message}
                  required={workPackage.attributes.division.required}
                  buttonRef={ref}
                  onSelect={(option: SelectOption) => onChange(option.id)}
                  readOnly={readOnly}
                />
              )}
            />
          </FieldTemplate>
        )}

        {workPackage.attributes.region.visible && (
          <FieldTemplate testId="work-package-region">
            <Controller
              name="libraryRegionId"
              rules={getRequiredFieldRules(
                workPackage.attributes.region.required
              )}
              defaultValue={libraryRegionId}
              render={({ field: { onChange, ref } }) => (
                <FieldSelect
                  htmlFor="libraryRegionId"
                  label={workPackage.attributes.region.label}
                  placeholder="Ex. Northeast"
                  options={regionsLibrary}
                  defaultOption={regionsLibrary.find(
                    (option: LibraryRegion) => option.id === libraryRegionId
                  )}
                  isInvalid={!!errors.libraryRegionId}
                  error={errors.libraryRegionId?.message}
                  required={workPackage.attributes.region.required}
                  buttonRef={ref}
                  onSelect={(option: SelectOption) => onChange(option.id)}
                  readOnly={readOnly}
                />
              )}
            />
          </FieldTemplate>
        )}

        {workPackage.attributes.description.visible && (
          <FieldTemplate testId="work-package-description">
            <Controller
              name="description"
              rules={getRequiredFieldRules(
                workPackage.attributes.description.required
              )}
              render={({ field }) => (
                <FieldTextArea
                  htmlFor="description"
                  id="description"
                  label={workPackage.attributes.description.label}
                  placeholder={`Add a ${workPackage.attributes.description.label.toLowerCase()}...`}
                  initialValue={description?.trim()}
                  required={workPackage.attributes.description.required}
                  hasError={!!errors.description}
                  error={errors.description?.message}
                  readOnly={readOnly}
                  {...field}
                />
              )}
            />
          </FieldTemplate>
        )}

        <h6
          className="py-4"
          data-testid="work-package-team-members"
        >{`${workPackage.label} Team Members`}</h6>

        {workPackage.attributes.projectManager.visible && (
          <FieldTemplate testId="work-package-manager">
            <Controller
              name="managerId"
              rules={getRequiredFieldRules(
                workPackage.attributes.projectManager.required
              )}
              defaultValue={managerId}
              render={({ field: { onChange, ref } }) => (
                <FieldSearchSelect
                  htmlFor="projectManager"
                  label={workPackage.attributes.projectManager.label}
                  placeholder={`Select a ${workPackage.attributes.projectManager.label.toLowerCase()}`}
                  icon="user"
                  options={managersOptions}
                  defaultOption={managersOptions.find(
                    manager => manager.id === managerId
                  )}
                  isInvalid={!!errors.managerId}
                  error={errors.managerId?.message}
                  required={workPackage.attributes.projectManager.required}
                  buttonRef={ref}
                  onSelect={(option: SelectOption) => onChange(option.id)}
                  readOnly={readOnly}
                />
              )}
            />
          </FieldTemplate>
        )}

        {workPackage.attributes.primaryAssignedPerson.visible && (
          <FieldTemplate testId="work-package-assigned-person">
            <Controller
              name="supervisorId"
              rules={getRequiredFieldRules(
                workPackage.attributes.primaryAssignedPerson.required
              )}
              defaultValue={supervisorId}
              render={({ field: { onChange, ref } }) => (
                <FieldSearchSelect
                  htmlFor="supervisor"
                  label={workPackage.attributes.primaryAssignedPerson.label}
                  placeholder={`Select a ${workPackage.attributes.primaryAssignedPerson.label.toLowerCase()}`}
                  icon="user"
                  options={supervisorsOptions.filter(
                    option => !watchAdditionalSupervisors?.includes(option.id)
                  )}
                  defaultOption={supervisorsOptions.find(
                    supervisor => supervisor.id === supervisorId
                  )}
                  isInvalid={!!errors.supervisorId}
                  error={errors.supervisorId?.message}
                  required={
                    workPackage.attributes.primaryAssignedPerson.required
                  }
                  buttonRef={ref}
                  onSelect={(option: SelectOption) => onChange(option.id)}
                  readOnly={readOnly}
                />
              )}
            />
          </FieldTemplate>
        )}

        {workPackage.attributes.additionalAssignedPerson.visible && (
          <FieldTemplate testId="work-package-additional-assigned-person">
            <Controller
              name="additionalSupervisors"
              defaultValue={additionalSupervisors}
              rules={getRequiredFieldRules(
                workPackage.attributes.additionalAssignedPerson.required
              )}
              render={({ field: { onChange, ref } }) => {
                const multiSelectErrors = errors as FormFieldError;

                return (
                  <FieldMultiSelect
                    htmlFor="additionalSupervisors"
                    label={`${workPackage.attributes.additionalAssignedPerson.label}(s)`}
                    placeholder={`Select ${workPackage.attributes.additionalAssignedPerson.label.toLowerCase()}(s)`}
                    icon="user"
                    options={supervisorsOptions.filter(
                      options => options.id !== watchSupervisorId
                    )}
                    defaultOption={supervisorsOptions.filter(option =>
                      additionalSupervisors?.includes(option.id)
                    )}
                    buttonRef={ref}
                    onSelect={option => {
                      onChange(option.map(supervisor => supervisor.id));
                    }}
                    error={multiSelectErrors.additionalSupervisors?.message}
                    isInvalid={!!multiSelectErrors.additionalSupervisors}
                    required={
                      workPackage.attributes.additionalAssignedPerson.required
                    }
                    readOnly={readOnly}
                  ></FieldMultiSelect>
                );
              }}
            />
          </FieldTemplate>
        )}

        <FieldTemplate testId="work-package-engineer">
          <Controller
            name="engineerName"
            defaultValue={engineerName}
            render={({ field }) => (
              <FieldInput
                htmlFor="engineerName"
                id="engineerName"
                label="Engineer"
                placeholder="Engineer name"
                readOnly={readOnly}
                {...field}
              />
            )}
          />
        </FieldTemplate>

        <h6 className="py-4" data-testid="work-package-contract-information">
          Contract Information
        </h6>

        {workPackage.attributes.contractReferenceNumber.visible && (
          <FieldTemplate testId="work-package-contract-reference-number">
            <Controller
              name="contractReference"
              defaultValue={contractReference}
              rules={getRequiredFieldRules(
                workPackage.attributes.contractReferenceNumber.required
              )}
              render={({ field }) => (
                <FieldInput
                  htmlFor="contractReference"
                  id="contractReference"
                  label={workPackage.attributes.contractReferenceNumber.label}
                  placeholder="Ex. ABC-1234"
                  required={
                    workPackage.attributes.contractReferenceNumber.required
                  }
                  error={errors.contractReference?.message}
                  readOnly={readOnly}
                  {...field}
                />
              )}
            />
          </FieldTemplate>
        )}

        {workPackage.attributes.contractName.visible && (
          <FieldTemplate testId="work-package-contract-name">
            <Controller
              name="contractName"
              defaultValue={contractName}
              rules={getRequiredFieldRules(
                workPackage.attributes.contractName.required
              )}
              render={({ field }) => (
                <FieldInput
                  htmlFor="contractName"
                  id="contractName"
                  label={workPackage.attributes.contractName.label}
                  placeholder={workPackage.attributes.contractName.label}
                  required={workPackage.attributes.contractName.required}
                  error={errors.contractName?.message}
                  readOnly={readOnly}
                  {...field}
                />
              )}
            />
          </FieldTemplate>
        )}

        {workPackage.attributes.primeContractor.visible && (
          <FieldTemplate testId="work-package-contractor">
            <Controller
              name="contractorId"
              rules={getRequiredFieldRules(
                workPackage.attributes.primeContractor.required
              )}
              defaultValue={contractorId}
              render={({ field: { onChange, ref } }) => (
                <FieldSearchSelect
                  htmlFor="contractor"
                  label={workPackage.attributes.primeContractor.label}
                  placeholder={`Select a ${workPackage.attributes.primeContractor.label.toLowerCase()}`}
                  icon="user"
                  options={contractorOptions}
                  defaultOption={contractorOptions.find(
                    contractor => contractor.id === contractorId
                  )}
                  isInvalid={!!errors.contractorId}
                  error={errors.contractorId?.message}
                  required={workPackage.attributes.primeContractor.required}
                  buttonRef={ref}
                  onSelect={(option: SelectOption) => onChange(option.id)}
                  readOnly={readOnly}
                />
              )}
            />
          </FieldTemplate>
        )}
      </div>
    </div>
  );
}
