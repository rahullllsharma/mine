import type { ComponentMeta, ComponentStory } from "@storybook/react";
import { RiskLevel } from "../riskBadge/RiskLevel";
import CardItem from "./CardItem";

export default {
  title: "components/CardItem",
  component: CardItem,
} as ComponentMeta<typeof CardItem>;

const TemplateCardItem: ComponentStory<typeof CardItem> = ({
  project,
  ...tailProps
}) => <CardItem project={project} {...tailProps} />;

export const Playground = TemplateCardItem.bind({});

Playground.args = {
  project: {
    id: "7114445f-966a-42e2-aa3b-0e4d5365075d",
    name: "5th Street Main Relocation",
    riskLevel: RiskLevel.HIGH,
    region: "Northeast",
    status: "Active",
    libraryProjectType: { id: "1", name: "Main replacement" },
    libraryDivision: { id: "1", name: "Gas" },
    libraryRegion: { id: "1", name: "NE (New England)" },
    startDate: "2021-12-28",
    endDate: "2022-12-31",
    locations: [],
    externalKey: "231321312",
    manager: { id: "123", name: "Jakob Aminoff" },
    supervisor: {
      id: "123",
      name: "Jakob Aminoff",
    },
    additionalSupervisors: [
      { id: "234", name: "Raymond Holt" },
      { id: "235", name: "Sirius Goldberg" },
      { id: "236", name: "Hailey Quinn" },
    ],
    contractor: {
      id: "383fbe30-2eef-441f-898e-b07f8c53bb68",
      name: "Kiewit Power",
    },
    contractReference: "AAA",
    libraryAssetType: {
      id: "1",
      name: "Global Application",
    },
    contractName: "some name",
    projectZipCode: "84847-323",
    engineerName: "Paul Engineer",
  },
  isLoading: false,
};
