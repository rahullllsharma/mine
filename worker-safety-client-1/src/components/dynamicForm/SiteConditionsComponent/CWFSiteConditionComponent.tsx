import type {
  SiteCondition,
  CWFSiteConditionsType,
  SiteConditionsData,
  UserFormMode,
  ActivePageObjType,
  Hazards,
} from "@/components/templatesComponents/customisedForm.types";
import { BodyText, SectionHeading } from "@urbint/silica";
import { useQuery } from "@apollo/client";
import { useContext, useEffect, useState } from "react";
import { v4 as uuidv4 } from "uuid";
import router from "next/router";
import { UserFormModeTypes } from "@/components/templatesComponents/customisedForm.types";
import Checkbox from "@/components/shared/checkbox/Checkbox";
import { TagCard } from "@/components/forms/Basic/TagCard";
import SiteConditions from "@/graphql/queries/siteConditions.gql";
import CustomisedFromStateContext from "@/context/CustomisedDataContext/CustomisedFormStateContext";
import { convertDateToString } from "@/utils/date/helper";
import {
  FORM_EVENTS,
  formEventEmitter,
} from "@/context/CustomisedDataContext/CustomisedFormStateProvider";
import { CF_REDUCER_CONSTANTS } from "@/utils/customisedFormUtils/customisedForm.constants";
import useCWFFormState from "@/hooks/useCWFFormState";
import LocationSiteConditions from "@/graphql/queries/locationSiteConditions.gql";
import CardLazyLoader from "@/components/shared/cardLazyLoader/CardLazyLoader";
import ButtonSecondary from "@/components/shared/button/secondary/ButtonSecondary";
import { Dialog } from "@/components/forms/Basic/Dialog";
import { useFormRendererContext } from "@/components/templatesComponents/FormPreview/Components/FormRendererContext";
import { DialogContent, DialogHeader } from "./utils";

const CWFSiteConditionComponent = ({
  item,
  mode,
  inSummary,
}: {
  item: CWFSiteConditionsType;
  activePageDetails: ActivePageObjType;
  section: any;
  mode: UserFormMode;
  inSummary?: boolean;
}): JSX.Element => {
  const { state, dispatch } = useContext(CustomisedFromStateContext)!;

  const locationIdFromMetadata = state.form.metadata?.location?.id ?? "";
  const { location: workPackageLocationId, startDate: startDateFromQuery } =
    router.query || {};
  const locationIdFromQuery = workPackageLocationId
    ? String(workPackageLocationId)
    : "";
  const locationId = locationIdFromMetadata || locationIdFromQuery;
  const startDate = startDateFromQuery ? String(startDateFromQuery) : "";
  const reportingDate = convertDateToString(
    state.form.properties?.report_start_date || startDate || new Date()
  );
  const { gps_coordinates, manual_location } =
    state.form?.component_data?.location_data || {};
  const { data = { siteConditions: [], locationSiteConditions: [] }, loading } =
    useQuery<SiteConditionsData>(
      manual_location ? LocationSiteConditions : SiteConditions,
      {
        fetchPolicy:
          inSummary ||
          mode === UserFormModeTypes.PREVIEW ||
          mode === UserFormModeTypes.PREVIEW_PROPS
            ? "cache-first"
            : "network-only",
        variables: manual_location
          ? {
              latitude: gps_coordinates?.latitude,
              longitude: gps_coordinates?.longitude,
              date: reportingDate,
            }
          : {
              locationId: locationId,
              date: reportingDate,
              filterTenantSettings: true,
            },
        skip:
          mode === UserFormModeTypes.PREVIEW ||
          mode === UserFormModeTypes.PREVIEW_PROPS,
      }
    );

  const librarySiteConditionIds = data?.siteConditions?.map(
    condition => condition.librarySiteCondition.id
  );

  const { librarySiteConditionsData } = useFormRendererContext();
  const [siteConditions, setSiteConditions] = useState<SiteCondition[]>([]);
  const [showSiteConditionsDialog, setShowSiteConditionsDialog] =
    useState(false);
  const [dataInitialized, setDataInitialized] = useState<boolean>(false);
  const { setCWFFormStateDirty } = useCWFFormState();

  const cwfSiteConditions: SiteCondition[] =
    state.form?.component_data?.site_conditions || [];
  const getUpdatedSiteConditions = (
    apiSiteConditions: SiteCondition[],
    existingSiteConditions: SiteCondition[]
  ) => {
    const apiSiteConditionsMap = new Map(
      apiSiteConditions?.map(condition => [
        condition.librarySiteCondition.id,
        condition,
      ])
    );
    const existingConditionMap = new Map(
      existingSiteConditions?.map(condition => [
        condition.librarySiteCondition.id,
        condition,
      ])
    );
    // "selected" field is used to select site conditions and "checked" field is used add site conditions from dialog
    const updatedConditions =
      librarySiteConditionsData?.tenantAndWorkTypeLinkedLibrarySiteConditions?.map(
        condition => {
          if (existingConditionMap.has(condition.id)) {
            return {
              ...existingConditionMap.get(condition.id),
              checked: true,
              hazards: (() => {
                const apiHazards = apiSiteConditionsMap?.get(
                  condition.id
                )?.hazards;
                return apiHazards?.length
                  ? apiHazards
                  : condition.hazards ?? [];
              })(),
            };
          } else if (apiSiteConditionsMap.has(condition.id)) {
            return {
              id: apiSiteConditionsMap.get(condition.id)?.id,
              isManuallyAdded: apiSiteConditionsMap.get(condition.id)
                ?.isManuallyAdded,
              librarySiteCondition: apiSiteConditionsMap.get(condition.id)
                ?.librarySiteCondition,
              name: apiSiteConditionsMap.get(condition.id)?.name,
              hazards: (() => {
                const apiHazards = apiSiteConditionsMap?.get(
                  condition.id
                )?.hazards;
                return apiHazards?.length
                  ? apiHazards
                  : condition.hazards ?? [];
              })(),
              selected: !inSummary,
              checked: true,
            };
          } else {
            return {
              id: uuidv4(),
              isManuallyAdded: false,
              librarySiteCondition: condition,
              name: condition.name,
              hazards: condition.hazards ?? [],
              selected: false,
              checked: false,
            };
          }
        }
      ) || [];

    setSiteConditions(updatedConditions as SiteCondition[]);
    setDataInitialized(true);
  };
  useEffect(() => {
    if (
      !loading &&
      (data?.siteConditions || data?.locationSiteConditions) &&
      librarySiteConditionsData?.tenantAndWorkTypeLinkedLibrarySiteConditions &&
      !dataInitialized
    ) {
      getUpdatedSiteConditions(
        data.siteConditions || data.locationSiteConditions || [],
        cwfSiteConditions
      );
    }
  }, [
    loading,
    data,
    librarySiteConditionsData,
    cwfSiteConditions,
    dataInitialized,
    inSummary,
  ]);

  const handleCheckboxChange = (itemId: string) => {
    setSiteConditions(prevConditions =>
      prevConditions.map(condition =>
        condition.id === itemId
          ? { ...condition, selected: !condition.selected }
          : condition
      )
    );
    setCWFFormStateDirty(true);
  };

  const handleSelectAll = (e: React.ChangeEvent<HTMLInputElement>) => {
    setSiteConditions(prevConditions =>
      prevConditions.map(condition => ({
        ...condition,
        selected: condition.checked ? e.target.checked : condition.selected,
      }))
    );
    setCWFFormStateDirty(true);
  };

  useEffect(() => {
    const handleSaveAndContinue = () => {
      if (inSummary) {
        return;
      }
      const newHazardsFromAPI = siteConditions
        .filter(condition => condition.selected && condition.checked)
        .flatMap(condition => condition.hazards || []);

      const existingHazards =
        state.form.component_data?.hazards_controls?.site_conditions || [];

      const existingHazardsMap = new Map(
        existingHazards.map(hazard => [hazard.id, hazard])
      );

      const newHazardsMap = new Map(
        newHazardsFromAPI.map(hazard => [
          hazard.libraryHazard ? hazard.libraryHazard?.id : hazard?.id,
          hazard.libraryHazard || hazard,
        ])
      );

      const updatedHazards = Array.from(newHazardsMap.values()).map(hazard => {
        if (existingHazardsMap.has(hazard.id ?? "")) {
          return existingHazardsMap.get(hazard.id ?? "");
        }
        return {
          ...hazard,
          controls: hazard.controls?.map(control => ({
            ...control,
            selected: control.selected ?? false,
          })),
          noControlsImplemented: false,
        };
      });

      dispatch({
        type: CF_REDUCER_CONSTANTS.SET_SITE_CONDITIONS_HAZARD_DATA,
        payload: updatedHazards as Hazards[],
      });

      dispatch({
        type: CF_REDUCER_CONSTANTS.SITE_CONDITIONS_VALUE_CHANGE,
        payload: siteConditions
          .filter(condition => condition.checked)
          .map(condition => ({
            id: condition.id,
            name: condition.name,
            librarySiteCondition: condition.librarySiteCondition,
            selected: condition.selected,
          })),
      });
    };
    const token = formEventEmitter.addListener(
      FORM_EVENTS.SAVE_AND_CONTINUE,
      handleSaveAndContinue
    );

    return () => {
      token.remove();
    };
  }, [
    siteConditions,
    dispatch,
    loading,
    state.form.component_data?.hazards_controls?.site_conditions,
  ]);

  const handleOnAddDialogSiteConditions = (
    dialogSiteConditions: SiteCondition[]
  ) => {
    setSiteConditions(dialogSiteConditions);
  };

  const displayConditions =
    mode === UserFormModeTypes.EDIT ? siteConditions : cwfSiteConditions;

  return (
    <>
      <div className="flex justify-between flex-col gap-4">
        <div className="flex justify-between items-center">
          <SectionHeading
            className={`${
              inSummary ? "text-[20px]" : "text-xl"
            } text-neutral-shade-100 font-semibold`}
          >
            {item.properties.title ?? "Site Conditions"}
          </SectionHeading>
          {!(
            mode === UserFormModeTypes.PREVIEW ||
            mode === UserFormModeTypes.PREVIEW_PROPS
          ) && (
            <ButtonSecondary
              label="Add Site Conditions"
              iconStart="plus_circle_outline"
              onClick={() => setShowSiteConditionsDialog(true)}
            />
          )}
        </div>

        {!inSummary && (
          <BodyText>
            Review the site conditions below and see if they apply to your
            location.
          </BodyText>
        )}
        {loading ? (
          <CardLazyLoader cards={2} rowsPerCard={2} rowClassName="ml-12" />
        ) : (
          <>
            {displayConditions?.some(
              condition => condition.checked || condition.selected
            ) ? (
              <div
                className={`flex flex-col gap-4 ${
                  displayConditions?.some(
                    condition => condition.checked || condition.selected
                  ) && !inSummary
                    ? "p-4 bg-gray-100"
                    : ""
                }`}
              >
                {displayConditions?.some(condition => condition.checked) &&
                  !inSummary && (
                    <div className="flex w-full gap-4 flex-row items-center">
                      <Checkbox
                        className="w-full gap-4"
                        checked={displayConditions
                          ?.filter(condition => condition.checked)
                          ?.every(condition => condition.selected)}
                        onChange={handleSelectAll}
                        disabled={
                          mode === UserFormModeTypes.PREVIEW ||
                          mode === UserFormModeTypes.PREVIEW_PROPS
                        }
                      />
                      <BodyText className="font-semibold">Select all</BodyText>
                    </div>
                  )}
                {displayConditions
                  ?.filter((condition: SiteCondition) =>
                    inSummary
                      ? condition.selected
                      : condition.checked || condition.selected
                  )
                  ?.sort((a: SiteCondition, b: SiteCondition) =>
                    a.name.localeCompare(b.name)
                  )
                  ?.map((condition: SiteCondition) => {
                    return (
                      <div
                        key={condition.id}
                        className="flex flex-row w-full gap-4 items-center"
                      >
                        {!inSummary && (
                          <Checkbox
                            className="w-full gap-4"
                            checked={condition.selected}
                            disabled={
                              mode === UserFormModeTypes.PREVIEW ||
                              mode === UserFormModeTypes.PREVIEW_PROPS
                            }
                            onClick={() => handleCheckboxChange(condition.id)}
                          ></Checkbox>
                        )}
                        <TagCard
                          className={`border-data-blue-30 w-full ${
                            !inSummary && mode === UserFormModeTypes.EDIT
                              ? "hover:bg-gray-100 cursor-pointer"
                              : ""
                          }`}
                          onClick={() => {
                            if (!inSummary && mode === UserFormModeTypes.EDIT) {
                              handleCheckboxChange(condition.id);
                            }
                          }}
                        >
                          <BodyText className="font-semibold">
                            {condition.name}
                          </BodyText>
                        </TagCard>
                      </div>
                    );
                  })}
              </div>
            ) : (
              <div className="p-6 bg-gray-100">
                <BodyText className="text-center">
                  No site conditions avalible for selected date and location
                </BodyText>
              </div>
            )}
          </>
        )}
      </div>
      {showSiteConditionsDialog && (
        <Dialog
          header={
            <DialogHeader onClose={() => setShowSiteConditionsDialog(false)} />
          }
        >
          <DialogContent
            siteConditions={[...siteConditions].sort(
              (a: SiteCondition, b: SiteCondition) =>
                a.name.localeCompare(b.name)
            )}
            librarySiteConditionIds={librarySiteConditionIds || []}
            locationId={locationId}
            onAdd={handleOnAddDialogSiteConditions}
            onCancel={() => setShowSiteConditionsDialog(false)}
            manual_location={!!manual_location}
          />
        </Dialog>
      )}
    </>
  );
};

export default CWFSiteConditionComponent;
