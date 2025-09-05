import type {
  FormElement,
  CWFLocationType,
  FormComponentPayloadType,
  SectionData,
  ReferenceContentType,
  FormComponentData,
  CheckboxQuestionPropertiesType,
  TemplateMetaData,
} from "@/components/templatesComponents/customisedForm.types";
import { Subheading } from "@urbint/silica";
import parse from "html-react-parser";
import { ErrorBoundary } from "react-error-boundary";
import { CWFItemType } from "@/components/templatesComponents/customisedForm.types";

import Attachment from "./Attachments";
import SiteConditions from "./SiteConditions";
import ActivitiesAndTasks from "./ActivitiesAndTasks";
import HazardsAndControls from "./HazardsAndControls";
import Location from "./Location";
import Section from "./Section";
import OptionsData from "./OptionsData";
import ComponentDataDisplay from "./ComponentDataDisplay";
import InputTypeDataDisplay from "./InputTypeDataDisplay";
import DropDownWithLabel from "./DropDownWithLabel";
import Personnel from "./Personnel";
import Checkbox from "./Checkbox";

import SummaryHistoricalIncident from "./SummaryHistoricalIncident";
import NearestHospital from "./NearestHospital";

const renderContent = (
  element: FormElement,
  componentData: FormComponentData | undefined,
  metadata: TemplateMetaData | undefined,
  parentElement?: any
): JSX.Element | string | undefined => {
  const content = (() => {
    switch (element.type) {
      case CWFItemType.Section:
        return (
          <Section
            sectionContent={element as SectionData}
            componentData={componentData}
            metaData={metadata}
            parentElement={parentElement}
          />
        );
      case CWFItemType.Choice:
        return <OptionsData content={element as FormComponentPayloadType} />;
      case CWFItemType.Dropdown:
        return <OptionsData content={element as FormComponentPayloadType} />;
      case CWFItemType.YesOrNo:
        return (
          <ComponentDataDisplay content={element as FormComponentPayloadType} />
        );
      case CWFItemType.Checkbox:
        return (
          <Checkbox
            checkboxProperties={
              element.properties as CheckboxQuestionPropertiesType
            }
          />
        );
      case CWFItemType.InputText:
      case CWFItemType.InputPhoneNumber:
      case CWFItemType.InputEmail:
      case CWFItemType.InputNumber:
      case CWFItemType.InputDateTime:
      case CWFItemType.InputLocation:
      case CWFItemType.ReportDate:
        return (
          <InputTypeDataDisplay content={element as FormComponentPayloadType} />
        );
      case CWFItemType.Contractor:
      case CWFItemType.Region:
        return <DropDownWithLabel content={element as ReferenceContentType} />;
      case CWFItemType.RichTextEditor:
        return (
          <div className="bg-brand-gray-10 p-4 list-disc">
            {parse(element.properties.data)}
          </div>
        );
      case CWFItemType.Page:
        if (element?.properties?.title === "Summary") {
          return "";
        } else {
          return (
            <Subheading className="text-[20px] py-2 m-0 mr-2">
              {element?.properties.title}
            </Subheading>
          );
        }
      case CWFItemType.Attachment:
        return (
          <Attachment
            attachment={element as FormComponentPayloadType}
          ></Attachment>
        );
      case CWFItemType.HazardsAndControls:
        return (
          <ErrorBoundary FallbackComponent={() => null}>
            <HazardsAndControls
              subTitle={element?.properties?.sub_title}
              hazardsAndControls={componentData?.hazards_controls}
              isEnergyWheelEnabled={metadata?.is_energy_wheel_enabled ?? true}
              item={element}
            />
          </ErrorBoundary>
        );
      case CWFItemType.ActivitiesAndTasks:
        return (
          <ActivitiesAndTasks
            item={element}
            activitiesAndTasks={componentData?.activities_tasks || []}
          />
        );
      case CWFItemType.SiteConditions:
        return (
          <SiteConditions
            item={element}
            siteCondition={componentData?.site_conditions || []}
          />
        );
      case CWFItemType.Location:
        return (
          <Location
            item={element as CWFLocationType}
            locationData={componentData?.location_data}
          />
        );
      case CWFItemType.NearestHospital:
        return (
          <NearestHospital
            element={element}
            nearestHospitalData={componentData?.nearest_hospital}
          />
        );
      case CWFItemType.PersonnelComponent:
        return <Personnel content={element as FormComponentPayloadType} />;
      case CWFItemType.Summary:
        return (
          <SummaryHistoricalIncident
            content={element as FormComponentPayloadType}
          />
        );
    }
  })();
  if (!content) return undefined;
  return content;
};

export default renderContent;
