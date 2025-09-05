/* eslint-disable @next/next/no-img-element */
import type {
  SuperSignOffProps,
  FileInputs,
} from "@/types/natgrid/jobsafetyBriefing";
import {
  ActionLabel,
  BodyText,
  ComponentLabel,
  SectionHeading,
} from "@urbint/silica";
import { useState, useEffect } from "react";
import { useRouter } from "next/router";
import { isMobile, isTablet } from "react-device-detect";
import { useQuery, useMutation, gql, useLazyQuery } from "@apollo/client";
import ButtonSecondary from "src/components/shared/button/secondary/ButtonSecondary";
import { FieldGroup } from "@/components/shared/FieldGroup";
import ButtonIcon from "@/components/shared/button/icon/ButtonIcon";
import Modal from "@/components/shared/modal/Modal";
import { Status } from "@/types/natgrid/jobsafetyBriefing";
import { SourceAppInformation } from "@/api/generated/types";
import SaveNatgridJobSafetyBriefing from "../../../../../graphql/mutations/natGrid/saveNatgridJobSafetyBriefing.gql";
import natgridJobSafetyBriefing from "../../../../../graphql/queries/natgrid.gql";
import packageJson from "../../../../../../package.json";
import SketchPadDialog from "./SketchPadDialog";

const GET_PERMISSIONS = gql`
  query Permissions {
    me {
      id
      name
      role
      email
      permissions
      opco {
        id
        name
      }
      tenant {
        name
        displayName
      }
    }
  }
`;

const SuperSignOff = ({
  onSignatureSave,
  supervisorSignOff,
  supervisorSignOffName,
  formStatus,
  supervisorSignOffSignature,
  // postSignatureName,
  jsbId,
  postJobBriefData,
}: SuperSignOffProps) => {
  const { data } = useQuery(GET_PERMISSIONS);
  const { id, email } = data.me;
  const loggedInName = data.me.name;
  const completedName = supervisorSignOffName;
  const displayUserName =
    formStatus === Status.COMPLETE ? completedName : loggedInName;
  const [signature, setSignature] = useState<FileInputs | null>(null);
  const [isDialogOpen, setIsDialogOpen] = useState(false);
  // const [managerName, setManagerName] = useState<string | undefined>(
  //   postSignatureName?.name
  // );
  const [uploadPolicy, setUploadPolicy] = useState<any | null>(null);
  const [signOffBtnDisabled, setsignOffBtnDisabled] = useState<boolean>(true);
  const [showCompletionModal, setShowCompletionModal] =
    useState<boolean>(false);
  const [saveSignOff] = useMutation(SaveNatgridJobSafetyBriefing);
  const [checkArchived] = useLazyQuery(natgridJobSafetyBriefing, {
    fetchPolicy: "network-only",
  });
  const postJobBriefDiscussionItemsData = postJobBriefData?.discussionItems;
  const {
    nearMissOccuredDuringActivities,
    nearMissOccuredDescription,
    jobBriefAdequateCommunication,
    jobBriefAdequateCommunicationDescription,
    safetyConcernsIdentifiedDuringWork,
    safetyConcernsIdentifiedDuringWorkDescription,
    changesInProcedureWork,
    changesInProcedureWorkDescription,
    crewMemebersAdequateTrainingProvided,
    crewMemebersAdequateTrainingProvidedDescription,
    otherLessonLearnt,
    otherLessonLearntDescription,
    jobWentAsPlanned,
    jobWentAsPlannedDescription,
  } = postJobBriefDiscussionItemsData || {};

  const generateImageName = () => {
    const uuid = crypto.randomUUID();
    return `${uuid}.png`;
  };

  useEffect(() => {
    const signedSignature = supervisorSignOff?.supervisor?.signatures;
    if (signedSignature) {
      const { signatures } = supervisorSignOff.supervisor;
      const signedUrl = signatures.signedUrl;
      if (signedUrl) {
        setSignature({
          id: signatures.id,
          name: signatures.name,
          displayName: signatures.displayName,
          size: signatures.size,
          url: signatures.url,
          signedUrl: signedUrl,
        });
      }
    }
  }, [supervisorSignOff]);

  // const { data, loading, error } = useQuery(managers, {
  //   variables: { orderByManager },
  // });
  const [isModalOpen, setIsModalOpen] = useState(false);
  // const managersList = data?.managers ?? [];
  // const getManagerId = (mgrName: string | undefined) => {
  //   const manager = managersList.find((mgr: Manager) => mgr.name === mgrName);
  //   return manager ? manager.id : null;
  // };

  const handleClearSignature = () => {
    setsignOffBtnDisabled(true);
    setSignature(null);
  };
  // const handleManagerSelect = (manager: Manager) => {
  //   setManagerName(manager.name);
  //   setIsModalOpen(false);
  //   handleClearSignature();
  // };

  const SignButtonSelect = () => {
    setIsDialogOpen(true);
  };
  const router = useRouter();

  const handleCompletionModalClose = () => {
    setShowCompletionModal(false);
    router.push("/forms");
  };

  const handleNatGridSignOff = async () => {
    try {
      const { data: latestData } = await checkArchived({
        variables: { id: jsbId },
      });

      const archivedAt = latestData?.natgridJobSafetyBriefing?.archivedAt;
      if (archivedAt !== null) {
        setShowCompletionModal(true);
        return;
      }
    } catch (error) {
      console.error("Error checking archived status:", error);
    }
    const currentDateTime = new Date().toISOString();
    const currentDate = new Date();
    const date = currentDate.toLocaleDateString("en-CA");
    const time = currentDate.toLocaleTimeString([], {
      hour: "2-digit",
      minute: "2-digit",
    });

    try {
      const policyId = uploadPolicy?.id;
      const policyUrl = uploadPolicy?.url;
      const policySignedUrl = signature?.signedUrl;

      const variables = {
        input: {
          jsbId,
          supervisorSignOff: {
            dateTime: currentDateTime,
            supervisor: {
              supervisorInfo: {
                id: id,
                name: loggedInName,
                email: email,
              },
              signature: {
                id: policyId,
                url: policyUrl + policyId,
                signedUrl: policySignedUrl,
                name: signature?.name,
                displayName: signature?.displayName,
                size: signature?.size,
                date,
                time,
                mimetype: null,
                md5: null,
                crc32c: null,
                category: null,
              },
            },
          },
          sourceInfo: {
            appVersion: packageJson.version,
            sourceInformation: SourceAppInformation.WebPortal,
          },
          postJobBrief: {
            postJobDiscussionNotes: postJobBriefData?.postJobDiscussionNotes,
            discussionItems: {
              nearMissOccuredDuringActivities: nearMissOccuredDuringActivities,
              nearMissOccuredDescription: nearMissOccuredDescription,
              jobBriefAdequateCommunication: jobBriefAdequateCommunication,
              jobBriefAdequateCommunicationDescription:
                jobBriefAdequateCommunicationDescription,
              safetyConcernsIdentifiedDuringWork:
                safetyConcernsIdentifiedDuringWork,
              safetyConcernsIdentifiedDuringWorkDescription:
                safetyConcernsIdentifiedDuringWorkDescription,
              changesInProcedureWork: changesInProcedureWork,
              changesInProcedureWorkDescription:
                changesInProcedureWorkDescription,
              crewMemebersAdequateTrainingProvided:
                crewMemebersAdequateTrainingProvided,
              crewMemebersAdequateTrainingProvidedDescription:
                crewMemebersAdequateTrainingProvidedDescription,
              otherLessonLearnt: otherLessonLearnt,
              otherLessonLearntDescription: otherLessonLearntDescription,
              jobWentAsPlanned: jobWentAsPlanned,
              jobWentAsPlannedDescription: jobWentAsPlannedDescription,
            },
            supervisorApprovalSignOff: {
              id: id,
              name: loggedInName,
              email: email,
            },
          },
        },
        formStatus: {
          status: "COMPLETE",
        },
        notificationInput: null,
      };

      await saveSignOff({ variables });
      router.push("/forms");
    } catch (err) {
      console.error("Error saving crew sign-off:", err);
    }
  };
  const handleModelPopUp = () => setIsModalOpen(true);

  return formStatus === Status.PENDING_POST_JOB_BRIEF ? (
    <BodyText className="overflow-auto p-2 sm:p-6 gap-2 sm:min-w-[300px]   max-w-[764px] bg-white h-[calc(100vh-96px)] mb-12 ">
      Post Job Brief must be completed prior to enabling Supervisor Sign-off
    </BodyText>
  ) : (
    <section className="overflow-auto p-2 sm:p-6 gap-2 sm:min-w-[300px]   max-w-[764px] bg-white h-[calc(100vh-96px)] mb-12 ">
      <SectionHeading className="text-xl">Supervisor Sign-off</SectionHeading>
      <FieldGroup>
        <div className="bg-white p-4">
          <ComponentLabel className="border-gray-10 text-gray-500">
            Supervisor
          </ComponentLabel>
          <Modal
            title="Select Manager"
            isOpen={isModalOpen}
            closeModal={() => setIsModalOpen(false)}
            className="h-full flex flex-col"
          >
            {/* <div className="bg-white w-full">
              {loading && (
                <p className="text-sm text-gray-500">Loading managers...</p>
              )}
              {error && (
                <p className="text-sm text-red-600">
                  Error fetching managers: {error.message}
                </p>
              )}
              {!loading && !error && managersList.length > 0 && (
                <div
                  className="flex flex-col flex-grow max-h-full overflow-y-auto"
                  style={{ height: "500px" }}
                >
                  {managersList.map((manager: Manager) => (
                    <div
                      key={manager.id}
                      onClick={() => handleManagerSelect(manager)}
                      className="p-3 hover:bg-gray-50 cursor-pointer border-b border-gray-100 transition-colors"
                    >
                      {manager.name}
                    </div>
                  ))}
                </div>
              )}
            </div> */}
          </Modal>
          <div className="flex flex-col gap-2">
            <div
              onClick={
                // eslint-disable-next-line no-negated-condition
                formStatus !== Status.COMPLETE ? handleModelPopUp : undefined
              }
              className={`flex flex-row justify-between ${
                formStatus === "COMPLETE"
                  ? "bg-gray-100 cursor-not-allowed"
                  : "bg-gray-50 cursor-pointer hover:bg-gray-50"
              } w-full max-h-36 mt-2 rounded-md border-solid border-[1px] border-brand-gray-40 p-2 cursor-pointer hover:bg-gray-50`}
            >
              <div>{displayUserName || "Select a Manager"}</div>
            </div>
            {supervisorSignOff?.dateTime && (
              <div className="text-sm text-gray-600">
                Signed on:{" "}
                {new Date(supervisorSignOff.dateTime).toLocaleDateString()} at{" "}
                {new Date(supervisorSignOff.dateTime).toLocaleTimeString()}
              </div>
            )}
            <div className="flex flex-row justify-between items-center">
              {formStatus === Status.COMPLETE ? (
                <img
                  width="50%"
                  height="50%"
                  src={supervisorSignOffSignature}
                  alt="Supervisor Signature"
                />
              ) : signature ? (
                <div className="flex flex-row gap-2 w-full justify-between items-end">
                  <div className="flex flex-col gap-1">
                    <ActionLabel className="text-gray-600 font-medium">
                      Signature
                    </ActionLabel>
                    <img
                      src={signature?.signedUrl}
                      alt="Signature"
                      className="w-[100px] h-[100px]"
                    />
                  </div>
                  <ButtonIcon
                    iconName="close_big"
                    onClick={handleClearSignature}
                    className="border-[1px] rounded-md border-brand-gray-40 flex flex-col items-center justify-center w-10 h-10 cursor-pointer"
                  />
                </div>
              ) : (
                <ButtonSecondary
                  iconStart="edit"
                  label={`Sign for ${displayUserName}`}
                  onClick={SignButtonSelect}
                />
              )}
            </div>
          </div>
          <SketchPadDialog
            isOpen={isDialogOpen}
            onClose={() => setIsDialogOpen(false)}
            name={displayUserName}
            onSave={(blob: Blob, policy: any) => {
              setUploadPolicy(policy);
              setsignOffBtnDisabled(false);
              const imageName = generateImageName();
              const newSignature: FileInputs = {
                name: imageName,
                displayName: imageName,
                signedUrl: URL.createObjectURL(blob),
                size: `${Math.round(blob.size / 1000)} KB`,
              };
              setSignature(newSignature);
              onSignatureSave?.(newSignature);
              setIsDialogOpen(false);
            }}
          />
          <footer
            className={`flex flex-col mt-auto md:max-w-screen-lg items-end ${
              isMobile || isTablet ? "p-2.5 h-[54px]" : "p-4 px-0"
            }`}
          >
            {formStatus !== Status.COMPLETE && (
              <button
                className="text-center truncate disabled:opacity-38 disabled:cursor-not-allowed  text-base rounded-md font-semibold text-white bg-brand-urbint-40 px-2.5 py-2"
                type="button"
                onClick={handleNatGridSignOff}
                disabled={signOffBtnDisabled}
              >
                Sign-off and Complete
              </button>
            )}
          </footer>
        </div>
      </FieldGroup>
      <Modal
        title="Job Safety Briefing Deleted"
        isOpen={showCompletionModal}
        closeModal={handleCompletionModalClose}
        dismissable={true}
      >
        <div className="p-2">
          <div className="flex items-center mb-4">
            <div className="ml-3"></div>
          </div>

          <div className="mb-6">
            <BodyText className="text-gray-600">
              You will be redirected to the forms page.
            </BodyText>
          </div>

          <div className="flex justify-end">
            <ButtonSecondary onClick={handleCompletionModalClose}>
              OK
            </ButtonSecondary>
          </div>
        </div>
      </Modal>
    </section>
  );
};
export default SuperSignOff;
