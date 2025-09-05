import type {
  PersonelRow,
  PersonnelNameSelectorProps,
  WorkosUser,
} from "@/components/templatesComponents/customisedForm.types";
import { useQuery } from "@apollo/client";
import { useEffect, useMemo, useState } from "react";
import { useRouter } from "next/router";
import axios from "axios";
import { useSession } from "next-auth/react";
import { v4 as uuidv4 } from "uuid";
import Modal from "@/components/shared/modal/Modal";
import { useTenantStore } from "@/store/tenant/useTenantStore.store";
import Loader from "@/components/shared/loader/Loader";
import { InputRaw } from "@/components/forms/Basic/Input";
import ButtonPrimary from "@/components/shared/button/primary/ButtonPrimary";
import ButtonSecondary from "@/components/shared/button/secondary/ButtonSecondary";
import workosDirectoryUsers from "../../../../graphql/workosDirectoryUsers.gql";
import { config } from "../../../../src/config";
import AddOtherNameField from "./AddOtherNameField";
import NamePickList from "./NamePickList";

const PersonnelNameSelectorPopUp = ({
  isOpen,
  closeModal,
  onSelectName,
  disabledIds,
}: PersonnelNameSelectorProps) => {
  const { data: session } = useSession({ required: true });
  const [workosDirectoryIds, setWorkosDirectoryIds] = useState<string[]>([]);
  const [selectedIds, setSelectedIds] = useState<string[]>([]);
  const [customNames, setCustomNames] = useState<PersonelRow[]>([]);
  const [suggestions, setSuggestions] = useState<PersonelRow[]>([]);
  const [loadingApi, setLoadingApi] = useState(false);
  const [apiErr, setApiErr] = useState<string | null>(null);
  const router = useRouter();
  const templateId = router.query.templateId || router.query.id || "";
  const token = session?.accessToken;
  const { data: crewMemberData, loading: loadingCrewMemberData } = useQuery(
    workosDirectoryUsers,
    {
      variables: { directoryIds: workosDirectoryIds },
      skip: !workosDirectoryIds.length,
    }
  );

  useEffect(() => {
    if (isOpen) {
      setSelectedIds([]);
    }
    const tenantWorkOSIds = (
      useTenantStore.getState().tenant.workos as unknown as {
        workosDirectoryId: string;
      }[]
    ).map(entry => entry.workosDirectoryId);
    setWorkosDirectoryIds(tenantWorkOSIds);
  }, [crewMemberData, isOpen]);
  useEffect(() => {
    if (!isOpen || !templateId) return;

    const fetchSuggestions = async () => {
      try {
        setLoadingApi(true);
        setApiErr(null);

        const { data } = await axios.post(
          config.workerSafetyCustomWorkFlowUrlRest + "/forms/suggestions/",
          {
            template_id: templateId,
            element_type: "personnel_component",
            suggestion_type: "recently_selected_crew_details",
          },
          {
            headers: {
              "Content-Type": "application/json",
              Authorization: `Bearer ${token}`,
            },
          }
        );

        const rows: PersonelRow[] = (data ?? []).map((u: PersonelRow) => {
          const empNum = (u.employee_number || "").trim();
          const id = empNum.length > 0 ? empNum : u.external_id || uuidv4();

          return {
            id,
            name: u.name,
            jobTitle: u.job_title || null,
            employeeNumber: empNum || null,
            type: "Suggested",
            displayName: u.display_name || u.name,
            email: u.email || null,
            departmentName: u.departmentName || null,
            managerId: u.managerId || null,
            managerEmail: u.managerEmail || null,
            managerName: u.managerName || null,
            signature: null,
            attrIds: [],
          };
        });

        setSuggestions(rows);
      } catch {
        setApiErr("Couldn’t load recently-added crew.");
      } finally {
        setLoadingApi(false);
      }
    };

    fetchSuggestions();
  }, [isOpen, templateId, token]);

  // eslint-disable-next-line react-hooks/exhaustive-deps
  const getManagerName = (id?: string) => {
    const foundUser = crewMemberData?.workosDirectoryUsers?.data.find(
      (user: WorkosUser) => user.idpId === id
    );
    return foundUser?.customAttributes.displayName ?? "";
  };

  const suggestionEmpNums = useMemo(
    () => new Set(suggestions.map(s => s.employeeNumber).filter(Boolean)),
    [suggestions]
  );

  const workosUsers: PersonelRow[] = useMemo(() => {
    return (
      crewMemberData?.workosDirectoryUsers?.data
        .filter((u: WorkosUser) => {
          const empNum = u.customAttributes?.employeeNumber;
          return !suggestionEmpNums.has(empNum ?? "");
        })
        .map((user: WorkosUser) => {
          const {
            employeeNumber,
            displayName,
            emails,
            department_name: departmentName,
            manager_id: managerId,
            manager_email: managerEmail,
          } = user.customAttributes ?? {};

          return {
            id: user.id,
            name:
              user.firstName && user.lastName
                ? `${user.firstName} ${user.lastName}`
                : user.username,
            jobTitle: user.jobTitle ?? null,
            employeeNumber: employeeNumber ?? null,
            type: "Personnel",
            displayName: displayName ?? null,
            email: emails?.find(e => e.primary)?.value ?? null,
            departmentName: departmentName ?? null,
            managerId: managerId ?? null,
            managerEmail: managerEmail ?? null,
            managerName: getManagerName(managerId),
            signature: null,
            attrIds: [],
          };
        }) ?? []
    );
  }, [crewMemberData, getManagerName]);

  const allUsers: PersonelRow[] = useMemo(() => {
    const seen = new Set<string>();
    return [...suggestions, ...workosUsers, ...customNames].filter(u => {
      const k = (u.employeeNumber ?? u.email ?? u.id).toLowerCase();
      if (seen.has(k)) return false;
      seen.add(k);
      return true;
    });
  }, [suggestions, workosUsers, customNames]);

  const [search, setSearch] = useState("");
  const filtered = useMemo(() => {
    if (!search.trim()) return allUsers;
    const q = search.toLowerCase();

    return allUsers.filter(user => {
      const idMatch = user.id.toLowerCase().includes(q);
      const nameMatch = user.name.toLowerCase().includes(q);
      const empMatch = (user.employeeNumber ?? "")
        .toString()
        .toLowerCase()
        .includes(q);
      return idMatch || nameMatch || empMatch;
    });
  }, [allUsers, search]);

  const recentIds = suggestions.map(s => s.id);
  const groups =
    recentIds.length > 0
      ? {
          recent: { label: "Recently Added", ids: recentIds },
          remaining: {
            label: "Remaining Names",
            ids: filtered.filter(u => !recentIds.includes(u.id)).map(u => u.id),
          },
        }
      : undefined;

  const toggle = (id: string) =>
    setSelectedIds(prev =>
      prev.includes(id) ? prev.filter(x => x !== id) : [...prev, id]
    );

  const clearAndClose = () => {
    setSearch("");
    setSelectedIds([]);
    closeModal();
  };

  if (!isOpen) return null;

  return (
    <Modal
      title={"Add Names"}
      isOpen={isOpen}
      closeModal={() => {
        setSearch("");
        clearAndClose();
      }}
    >
      <div className="flex flex-col gap-4">
        <InputRaw
          icon="search"
          type="text"
          placeholder="Search by name or ID number"
          value={search}
          onChange={setSearch}
        />
        <div className="flex flex-col flex-grow" style={{ height: 400 }}>
          {(loadingCrewMemberData || loadingApi) && <Loader />}

          {!loadingCrewMemberData && filtered.length > 0 && (
            <NamePickList
              allUsers={filtered}
              customNames={customNames}
              selectedIds={selectedIds}
              disabledIds={disabledIds}
              toggle={toggle}
              groups={groups}
            />
          )}

          {!loadingApi && apiErr && (
            <p className="mt-2 text-sm text-red-600">{apiErr}</p>
          )}
        </div>
        <hr />

        <AddOtherNameField
          onSave={row => {
            setCustomNames(prev =>
              prev.some(p => p.id === row.id)
                ? prev
                : [
                    ...prev,
                    {
                      ...row,
                      type: "Other",
                      displayName: row.name,
                      signature: null,
                      attrIds: [],
                    },
                  ]
            );
            setSelectedIds(prev =>
              prev.includes(row.id) ? prev : [...prev, row.id]
            );
          }}
        />
        <div className="flex justify-end gap-2 mt-2">
          <ButtonSecondary onClick={clearAndClose} label="Cancel" />
          <ButtonPrimary
            label={`Add Names (${selectedIds.length})`}
            disabled={!selectedIds.length}
            onClick={() => {
              const picked: PersonelRow[] = allUsers
                .filter(user => selectedIds.includes(user.id))
                .map(user => ({
                  id: user.id,
                  name: user.name,
                  jobTitle: user.jobTitle,
                  employeeNumber: user.employeeNumber,
                  signature: null,
                  attrIds: [],
                  type: user.type,
                  displayName: user.displayName,
                  email: user.email,
                  departmentName: user.departmentName,
                  managerId: user.managerId,
                  managerEmail: user.managerEmail,
                  managerName: user.managerName,
                }));

              onSelectName(picked);
              clearAndClose();
            }}
          />
        </div>
      </div>
    </Modal>
  );
};

export default PersonnelNameSelectorPopUp;
