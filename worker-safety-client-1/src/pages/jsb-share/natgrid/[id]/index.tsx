/* eslint-disable @typescript-eslint/no-non-null-assertion */
import type { PageListItemType } from "@/utils/jsbShareUtils/jsbShare.type";
import type { FileInputs } from "@/types/natgrid/jobsafetyBriefing";
import { isEmpty } from "lodash-es";
import { useRouter } from "next/router";
import { gql, useLazyQuery, useQuery } from "@apollo/client";
import { useEffect, useState } from "react";
import * as O from "fp-ts/lib/Option";
import cx from "classnames";
import { Status } from "@/types/natgrid/jobsafetyBriefing";
import Loader from "@/components/shared/loader/Loader";
import { DataDisplayComponent } from "@/components/natgrid-jsb/components";
import ErrorContainer from "@/components/shared/error/ErrorContainer";
import SuperSignOff from "src/pages/jsb-share/natgrid/[id]/components/CrewSignOffComponent";
import {
  NETWORK_POLICY,
  PAGE_LIST_ITEMS,
  PAGE_LIST_ITEM,
} from "@/utils/jsbShareUtils/jsbShare.constants";
import { useAuthStore } from "@/store/auth/useAuthStore.store";
import UrbintLogo from "@/components/shared/urbintLogo/UrbintLogo";
import natgridJobSafetyBriefing from "../../../../graphql/queries/natgrid.gql";
import PageList from "./components/PageList";
import SharePageHeader from "./components/SharePageHeader";
import print from "./print.module.scss";

const HAZARDS_QUERY = gql`
  query HazardsLibrary {
    hazardsLibrary(type: TASK) {
      id
      name
      imageUrl
    }
  }
`;

const JSBSharePage = () => {
  const { isManager, isAdmin } = useAuthStore();
  const {
    query: { id, printPage },
  } = useRouter();
  const [activePage, setActivePage] = useState<number>(1);
  const [, setSignature] = useState<O.Option<{ signedUrl: string }>>(O.none);
  const [fetchNatgrid, { data: natgridData, loading }] = useLazyQuery(
    natgridJobSafetyBriefing,
    {
      fetchPolicy: NETWORK_POLICY,
    }
  );
  const handleSignatureSave = (signatureData: FileInputs) => {
    setSignature(O.some({ signedUrl: signatureData.signedUrl! }));
  };
  const { data: hazards, loading: loadingHazards } = useQuery(HAZARDS_QUERY);
  const hazardsLibrary = hazards?.hazardsLibrary || [];
  const router = useRouter();

  useEffect(() => {
    if (!printPage) return;

    const headerElement = document.querySelector(
      "header"
    ) as HTMLElement | null;
    const nextElement = document.getElementById("__next") as HTMLElement | null;

    const origStyles = {
      headerDisplay: headerElement?.style.display ?? "",
      bodyOverflow: document.body.style.overflowY,
      nextHeight: nextElement?.style.height ?? "",
      nextPosition: nextElement?.style.position ?? "",
      nextOverflow: nextElement?.style.overflow ?? "",
    };

    const beforePrint = () => {
      headerElement && (headerElement.style.display = "none");
      document.body.style.overflowY = "visible";
      if (nextElement) {
        nextElement.style.height = "auto";
        nextElement.style.position = "static";
        nextElement.style.overflow = "visible";
      }
      const loaderElements = document.querySelectorAll(
        '[class*="loader"], [class*="Loader"], [class*="spinner"], [class*="Spinner"]'
      );
      loaderElements.forEach(element => {
        (element as HTMLElement).style.display = "none";
      });
    };

    const afterPrint = () => {
      headerElement && (headerElement.style.display = origStyles.headerDisplay);
      document.body.style.overflowY = origStyles.bodyOverflow;
      if (nextElement) {
        nextElement.style.height = origStyles.nextHeight;
        nextElement.style.position = origStyles.nextPosition;
        nextElement.style.overflow = origStyles.nextOverflow;
      }
      if (printPage) {
        router.replace(`/jsb-share/natgrid/${id as string}`, undefined, {
          shallow: false,
        });
      }
    };

    window.addEventListener("beforeprint", beforePrint);
    window.addEventListener("afterprint", afterPrint);

    const tryPrint = () => {
      const imgs = Array.from(document.images);
      const ready = imgs.every(img => img.complete);
      if (ready) {
        window.print();
      } else {
        imgs.forEach(img => {
          img.addEventListener("load", tryPrint, { once: true });
          img.addEventListener("error", tryPrint, { once: true });
        });
      }
    };

    tryPrint();
    return () => {
      window.removeEventListener("beforeprint", beforePrint);
      window.removeEventListener("afterprint", afterPrint);
      afterPrint();
    };
  }, [printPage, id]);

  useEffect(() => {
    if (id) fetchNatgrid({ variables: { id } });
  }, [id, fetchNatgrid]);

  if (loading || loadingHazards) return <Loader />;

  const natgridJobSafetyBriefingData = natgridData?.natgridJobSafetyBriefing;
  const data = natgridJobSafetyBriefingData?.contents;
  const createdAt = natgridJobSafetyBriefingData?.createdAt;
  const archivedAt = natgridJobSafetyBriefingData?.archivedAt;
  const statusRaw = natgridJobSafetyBriefingData?.status?.toString();
  const signatureImageData =
    data?.supervisorSignOff?.supervisor?.signature?.signedUrl?.toString();
  const supervisorSignOffName =
    data?.supervisorSignOff?.supervisor?.supervisorInfo?.name;
  const postSignatureName = data?.postJobBrief?.supervisorApprovalSignOff;
  const jsbId = natgridJobSafetyBriefingData?.id;
  const postJobBriefData = data?.postJobBrief;
  const barnLocation = natgridData?.natgridJobSafetyBriefing?.barnLocation;
  const supervisorSignOff = data?.supervisorSignOff;
  const siteConditionData = data?.siteConditions?.siteConditionSelections;
  const status: Status =
    statusRaw && Object.values(Status).includes(statusRaw as Status)
      ? (statusRaw as Status)
      : Status.NOT_EXISTS;

  if (isEmpty(natgridData) || archivedAt !== null)
    return <ErrorContainer notFoundError={true} />;
  const onSelectOfPage = (page: PageListItemType) => setActivePage(page.id);

  const JSBSharePageDetails = () => {
    return data ? (
      <div
        className={cx("flex flex-col items-start bg-brand-gray-10", {
          "p-2": printPage,
        })}
      >
        <div
          className={cx("w-full flex flex-col items-start overflow-scroll", {
            "bg-white p-4": printPage,
          })}
        >
          <DataDisplayComponent
            siteCondition={siteConditionData}
            data={data}
            hazardsLibrary={hazardsLibrary}
            createdAt={createdAt}
            onUpdate={onSelectOfPage}
            status={status}
            printPdf={!!printPage}
            barnLocation={barnLocation}
          />
        </div>
      </div>
    ) : (
      <Loader />
    );
  };

  const disableSupervisorSignOff = (): PageListItemType[] => {
    if (isManager() === true || isAdmin()) {
      if (status === "IN_PROGRESS") return PAGE_LIST_ITEM;
      return PAGE_LIST_ITEMS;
    }
    return PAGE_LIST_ITEM;
  };

  return (
    <div>
      <div
        className={cx(print.topHeader, "hidden w-full bg-brand-urbint-60 p-4")}
      >
        <UrbintLogo className="text-white w-7 h-7 text-2xl" />
        <div className="pl-1 text-white">WORKER SAFETY</div>
      </div>
      <SharePageHeader printPdf={!!printPage} />
      <div
        className={cx(
          {
            "flex flex-col md:flex-row gap-[10px] pt-4 pl-2 pr-4 bg-brand-gray-10 h-full":
              !printPage,
          },
          "bg-white"
        )}
      >
        {!printPage && (
          <div className="w-full md:w-[250px] flex-shrink-0 p-2 sm:p-4">
            <PageList
              listItems={disableSupervisorSignOff()}
              onSelectOfPage={onSelectOfPage}
              activePage={activePage}
              rawStatus={statusRaw}
            />
          </div>
        )}
        {activePage === 1 || printPage ? (
          <JSBSharePageDetails />
        ) : (
          <div className="flex-1 overflow-y-auto  bg-brand-gray-10">
            <SuperSignOff
              onSignatureSave={handleSignatureSave}
              formStatus={status}
              supervisorSignOffSignature={signatureImageData}
              postSignatureName={postSignatureName}
              jsbId={jsbId}
              postJobBriefData={postJobBriefData}
              supervisorSignOffName={supervisorSignOffName}
              supervisorSignOff={supervisorSignOff}
            />
          </div>
        )}
      </div>
    </div>
  );
};

export default JSBSharePage;
