import type { ComponentMeta, ComponentStory } from "@storybook/react";
import type { PropsWithClassName } from "@/types/Generic";

import type { Location } from "@/types/project/Location";
import type { ProjectInputs } from "@/types/form/Project";
import type { TaskHazardAggregator } from "@/types/project/HazardAggregator";
import { FormProvider, useForm } from "react-hook-form";
import { action } from "@storybook/addon-actions";
import { useProjects } from "@/hooks/useProjects";
import ButtonPrimary from "@/components/shared/button/primary/ButtonPrimary";
import { PageProvider } from "@/context/PageProvider";
import ProjectDetails from "./ProjectDetails";

export default {
  title: "Container/ProjectForm",
  component: ProjectDetails,
} as ComponentMeta<typeof ProjectDetails>;

type FormattedLocations =
  | {
      id: string;
      name: string;
      latitude: number;
      longitude: number;
      externalKey?: string;
      supervisorId?: string;
      additionalSupervisors?: string[];
      tasks: TaskHazardAggregator[];
    }
  | {
      name: string;
      longitude: null;
      latitude: null;
      externalKey?: string;
      supervisorId: string;
      tasks: TaskHazardAggregator[];
    };

function getLocations(locations: Location[]): FormattedLocations[] {
  if (locations.length === 0)
    return [
      {
        name: "",
        longitude: null,
        latitude: null,
        supervisorId: "",
        externalKey: "",
        tasks: [],
      },
    ];

  return locations.map(
    ({
      id,
      name,
      latitude,
      longitude,
      supervisor,
      externalKey,
      additionalSupervisors,
      tasks,
    }) => {
      return {
        id,
        name: name.trim(),
        latitude,
        longitude,
        externalKey,
        supervisorId: supervisor?.id,
        additionalSupervisors: additionalSupervisors?.map(
          additionalSupervisor => additionalSupervisor.id
        ),
        tasks,
      };
    }
  );
}

const divisionsLibrary = [
  {
    id: "1",
    name: "Gas",
  },
  {
    id: "2",
    name: "Electric",
  },
];
const projectTypesLibrary = [
  {
    id: "1",
    name: "LNG/CNG",
  },
  {
    id: "2",
    name: "Distribution",
  },
  {
    id: "3",
    name: "Other",
  },
];
const regionsLibrary = [
  {
    id: "1",
    name: "DNY (Downstate New York)",
  },
  {
    id: "2",
    name: "UNY (Upstate New York)",
  },
  {
    id: "3",
    name: "NE (New England)",
  },
];
const assetTypesLibrary = [
  { id: "1", name: "CNG" },
  { id: "2", name: "Distribution Piping" },
];
const managers = [
  { id: "1", name: "Homer" },
  { id: "2", name: "J" },
  { id: "3", name: "Simpson" },
];
const supervisors = [
  { id: "1", name: "El" },
  { id: "2", name: "Barto" },
  { id: "3", name: "Barney Gumble" },
  { id: "4", name: "Moe Szyslak" },
];
const contractors = [
  {
    id: "1",
    name: "Kiewit Power",
  },
  {
    id: "2",
    name: "Kiewit Energy Group Inc. And Subsidiaries",
  },
];

function Wrapper({
  children,
  withSubmit = false,
  withProject = false,
}: PropsWithClassName<{
  withSubmit?: boolean;
  withProject?: boolean;
  readOnly?: boolean;
}>): JSX.Element {
  const project = useProjects()[0];

  const defaultValues: ProjectInputs = {
    name: withProject ? project.name : "",
    status: withProject ? project.status : "",
    startDate: withProject ? project.startDate : "",
    endDate: withProject ? project.endDate : "",
    locations: getLocations(withProject ? project.locations : []),
    libraryDivisionId: withProject ? project.libraryDivision?.id : "",
    libraryRegionId: withProject ? project.libraryRegion?.id : "",
    libraryProjectTypeId: withProject ? project.libraryProjectType?.id : "",
    externalKey: withProject ? project.externalKey : "",
    description: withProject ? project.description : "",
    managerId: withProject ? project.manager?.id : "",
    supervisorId: withProject ? project.supervisor?.id : "",
    additionalSupervisors: withProject
      ? project.additionalSupervisors?.map(supervisor => supervisor.id)
      : [],
    contractorId: withProject ? project.contractor?.id : "",
    contractReference: withProject ? project.contractReference : "",
    libraryAssetTypeId: withProject ? project.libraryAssetType?.id : "",
    contractName: withProject ? project.contractName : "",
    projectZipCode: withProject ? project.projectZipCode : "",
    engineerName: withProject ? project.projectZipCode : "",
  };

  const methods = useForm<ProjectInputs>({
    defaultValues,
  });
  return (
    <PageProvider
      props={{
        divisionsLibrary,
        regionsLibrary,
        projectTypesLibrary,
        assetTypesLibrary,
        managers,
        supervisors,
        contractors,
      }}
    >
      <FormProvider {...methods}>
        <div className="h-screen overflow-auto">
          <form>
            {withSubmit && (
              <ButtonPrimary
                onClick={methods.handleSubmit(data =>
                  action("on submit")(data)
                )}
                label="Submit"
              />
            )}
            {children}
          </form>
        </div>
      </FormProvider>
    </PageProvider>
  );
}

const Template: ComponentStory<typeof Wrapper> = args => (
  <Wrapper {...args}>
    <ProjectDetails readOnly={args.readOnly} />
  </Wrapper>
);

export const CreateProject = Template.bind({});
CreateProject.args = {
  withSubmit: true,
};

export const EditProject = Template.bind({});
EditProject.args = {
  withSubmit: true,
  withProject: true,
};

export const Readonly = Template.bind({});
Readonly.args = {
  withProject: true,
  readOnly: true,
};
