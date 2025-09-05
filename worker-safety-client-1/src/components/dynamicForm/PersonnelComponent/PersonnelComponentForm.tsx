import type {
  PersonelRow,
  PersonnelComponentType,
  PersonnelUserValue,
  PersonnelRowType,
  AttributeMeta,
  UserFormMode,
} from "@/components/templatesComponents/customisedForm.types";
import type { FileInputsCWF } from "@/types/natgrid/jobsafetyBriefing";
import { useContext, useEffect, useState } from "react";
import { BodyText, SectionHeading } from "@urbint/silica";
import cx from "classnames";
import ButtonSecondary from "@/components/shared/button/secondary/ButtonSecondary";
import CustomisedFromStateContext from "@/context/CustomisedDataContext/CustomisedFormStateContext";
import { CF_REDUCER_CONSTANTS } from "@/utils/customisedFormUtils/customisedForm.constants";
import Modal from "@/components/shared/modal/Modal";
import ButtonDanger from "@/components/shared/button/danger/ButtonDanger";
import { UserFormModeTypes } from "@/components/templatesComponents/customisedForm.types";
import {
  formEventEmitter,
  FORM_EVENTS,
} from "@/context/CustomisedDataContext/CustomisedFormStateProvider";
import EmptyPersonnelDescription from "./EmptyPersonnelDescription";
import PersonelRowCard from "./PersonnelRowCard";
import PersonnelNameSelectorPopUp from "./PersonnelNameSelectorPopUp";
import { getUniqueManagers, getCrewDetails } from "./Utils";

export default function PersonnelComponentForm({
  item,
  mode,
  inSummary = false,
}: {
  item: PersonnelComponentType;
  mode: UserFormMode;
  inSummary?: boolean;
}) {
  const { state, dispatch } = useContext(CustomisedFromStateContext)!;
  const isPreviewMode = mode === UserFormModeTypes.PREVIEW;

  const [people, setPeople] = useState<PersonnelRowType[]>([]);
  const [isModalOpen, setModalOpen] = useState(false);
  const [singleAttrMap, setSingleAttrMap] = useState<Record<string, string>>(
    {}
  );
  const [pendingDelete, setPendingDelete] = useState<PersonnelRowType | null>(
    null
  );

  const [showNoNameErr, setShowNoNameErr] = useState(false);
  useEffect(() => {
    const handleCrewError = () => setShowNoNameErr(true);
    const token = formEventEmitter.addListener(
      FORM_EVENTS.SHOW_CREW_ERRORS,
      handleCrewError
    );
    if (people.length > 0) {
      setShowNoNameErr(false);
    }
    return () => token.remove();
  }, [people.length]);

  useEffect(() => {
    const rows: PersonelRow[] = (item.properties.user_value ?? []).map(
      (u: PersonnelUserValue) => ({
        id: u.crew_details.external_id,
        name: u.crew_details.display_name || u.crew_details.name,
        signature: u.crew_details.signature
          ? {
              id: u.crew_details.signature.id,
              name: u.crew_details.signature.name,
              displayName: u.crew_details.signature.display_name,
              size: u.crew_details.signature.size,
              url: u.crew_details.signature.url,
              signedUrl: u.crew_details.signature.signedUrl,
              date: u.crew_details.signature.date,
              time: u.crew_details.signature.time,
            }
          : null,
        jobTitle: u.crew_details.job_title || null,
        employeeNumber: u.crew_details.employee_number || null,
        type: u.crew_details.type,
        displayName: u.crew_details.display_name,
        email: u.crew_details.email,
        departmentName: u.crew_details.department,
        managerId: u.crew_details.manager_id,
        managerEmail: u.crew_details.manager_email,
        managerName: u.crew_details.manager_name,
        attrIds: u.selected_attribute_ids || [],
      })
    );

    if (rows.length === 0) {
      return;
    }

    const map: Record<string, string> = {};
    rows.forEach((row: PersonelRow) => {
      (row.attrIds ?? []).forEach((attrId: string) => {
        const meta: AttributeMeta | undefined =
          item.properties.attributes?.find(
            (a: AttributeMeta) => a.attribute_id === attrId
          );

        if (meta?.applies_to_user_value === "single_name") {
          map[attrId] = row.id;
        }
      });
    });

    setPeople(rows);
    setSingleAttrMap(map);
  }, [item]);

  const addPersonnelData = (data: PersonnelRowType) => ({
    name: data.name,
    employeeNumber: data.employeeNumber ?? "",
    jobTitle: data.jobTitle ?? "",
    type: data.type ?? "",
    displayName: data.displayName ?? "",
    email: data.email ?? "",
    departmentName: data.departmentName ?? "",
    managerId: data.managerId ?? "",
    managerEmail: data.managerEmail ?? "",
    managerName: data.managerName ?? "",
  });

  const handleSigUpdate = (rowId: string, sig: FileInputsCWF) => {
    setPeople(prev => {
      const updated = prev.map(p =>
        p.id === rowId ? { ...p, signature: sig } : p
      );

      const person = updated.find(p => p.id === rowId)!;

      dispatch({
        type: CF_REDUCER_CONSTANTS.PERSONNEL_COMPONENT_ADD_DATA,
        payload: {
          componentId: item.id,
          rowId,
          signature: sig,
          ...addPersonnelData(person),
          attrIds: person.attrIds ?? [],
        },
      });

      return updated;
    });
  };

  const handleAddNames = (rows: PersonnelRowType[]) => {
    setPeople(prev => {
      const seen = new Set(prev.map(peopleObj => peopleObj.id));
      const merged = [...prev, ...rows.filter(r => !seen.has(r.id))];
      dispatch({
        type: CF_REDUCER_CONSTANTS.CHANGE_INITIAL_STATE,
        payload: {
          ...state.form,
          metadata: {
            ...state.form.metadata,
            supervisor: getUniqueManagers(merged, state.form),
          },
        },
      });
      rows.forEach(peopleObj =>
        dispatch({
          type: CF_REDUCER_CONSTANTS.PERSONNEL_COMPONENT_ADD_DATA,
          payload: {
            componentId: item.id,
            rowId: peopleObj.id,
            signature: null,
            ...addPersonnelData(peopleObj),
            attrIds: peopleObj.attrIds ?? [],
          },
        })
      );

      return merged;
    });
  };

  const handleRemove = (rowId: string) => {
    const updatedPeople = people.filter(p => p.id !== rowId);
    setPeople([...updatedPeople]);
    dispatch({
      type: CF_REDUCER_CONSTANTS.CHANGE_INITIAL_STATE,
      payload: {
        ...state.form,
        metadata: {
          ...state.form.metadata,
          supervisor: getCrewDetails(rowId, state.form),
        },
      },
    });
    setSingleAttrMap(prev => {
      const clone = { ...prev };
      Object.entries(clone).forEach(([attrId, owner]) => {
        if (owner === rowId) delete clone[attrId];
      });
      return clone;
    });

    dispatch({
      type: CF_REDUCER_CONSTANTS.PERSONNEL_COMPONENT_REMOVE_DATA,
      payload: { componentId: item.id, rowId },
    });
  };

  const handleToggleAttr = (rowId: string, attrId: string) => {
    const meta = item.properties.attributes?.find(
      a => a.attribute_id === attrId
    );
    const isSingle = meta?.applies_to_user_value === "single_name";

    setPeople(prev =>
      prev.map(p =>
        p.id === rowId
          ? {
              ...p,
              attrIds: p.attrIds?.includes(attrId)
                ? p.attrIds.filter(id => id !== attrId)
                : [...(p.attrIds ?? []), attrId],
            }
          : /* if single-name and we're assigning to another row, remove from previous owner */
          isSingle && p.attrIds?.includes(attrId)
          ? { ...p, attrIds: p.attrIds.filter(id => id !== attrId) }
          : p
      )
    );

    /* keep the single-name map accurate */
    setSingleAttrMap(prev => {
      if (!isSingle) return prev; // no change for multi attributes
      const clone = { ...prev };
      if (clone[attrId] === rowId) {
        delete clone[attrId]; // un-tick
      } else {
        clone[attrId] = rowId; // re-assign
      }
      return clone;
    });

    const current = people.find(r => r.id === rowId)!;
    const nextIds = current.attrIds?.includes(attrId)
      ? current.attrIds.filter(id => id !== attrId)
      : [...(current.attrIds ?? []), attrId];

    dispatch({
      type: CF_REDUCER_CONSTANTS.PERSONNEL_COMPONENT_ADD_DATA,
      payload: {
        componentId: item.id,
        rowId,
        signature: current.signature ?? null,
        ...addPersonnelData(current),
        attrIds: nextIds,
      },
    });
  };

  return (
    <div className="flex flex-col gap-6" id={item.id}>
      <div className="flex items-center justify-between">
        <SectionHeading
          className={cx({
            "text-lg font-semibold": !inSummary,
          })}
        >
          {item.properties.title}
        </SectionHeading>
        {mode !== UserFormModeTypes.PREVIEW && (
          <ButtonSecondary
            label="Add Names"
            iconStart="plus_circle_outline"
            onClick={() => !isPreviewMode && setModalOpen(true)}
            disabled={isPreviewMode}
          />
        )}
      </div>
      {showNoNameErr && people.length === 0 && (
        <BodyText className="text-sm text-red-600">
          At least one name must be added
        </BodyText>
      )}
      {people.length === 0 ? (
        <EmptyPersonnelDescription />
      ) : (
        <div className="flex flex-col gap-2">
          {people.map(person => (
            <PersonelRowCard
              key={person.id}
              person={person}
              item={item}
              mode={mode}
              onRequestDelete={() => !isPreviewMode && setPendingDelete(person)}
              onSignatureUpdate={sig =>
                !isPreviewMode && handleSigUpdate(person.id, sig)
              }
              onToggleAttr={attrId =>
                !isPreviewMode && handleToggleAttr(person.id, attrId)
              }
              singleAttrMap={singleAttrMap}
            />
          ))}
        </div>
      )}
      {pendingDelete && !isPreviewMode && (
        <Modal
          isOpen={!!pendingDelete}
          closeModal={() => setPendingDelete(null)}
          title={`Delete ${pendingDelete.name}?`}
        >
          <p className="mb-6 text-sm">
            Proceeding will delete this name and its associated signature. Are
            you sure you want to continue?
          </p>

          <div className="flex justify-end gap-3">
            <ButtonSecondary
              label="Cancel"
              onClick={() => setPendingDelete(null)}
            />
            <ButtonDanger
              label="Delete Name"
              onClick={() => {
                handleRemove(pendingDelete.id);
                setPendingDelete(null);
              }}
            />
          </div>
        </Modal>
      )}
      <PersonnelNameSelectorPopUp
        isOpen={isModalOpen && !isPreviewMode}
        closeModal={() => setModalOpen(false)}
        disabledIds={people.map(p => p.id)}
        onSelectName={rows => {
          handleAddNames(rows as PersonnelRowType[]);
          setModalOpen(false);
        }}
      />
    </div>
  );
}
