import type { DailyReportInputs } from "@/types/report/DailyReportInputs";
import type { RouterLink } from "@/types/Generic";
import type { PageHeaderAction } from "@/components/layout/pageHeader/components/headerActions/HeaderActions";
import type { BaseSyntheticEvent } from "react";
import type { FormViewTabStates } from "@/components/forms/Utils";
import cx from "classnames";
import { useMutation } from "@apollo/client";
import { useRouter } from "next/router";
import { useContext, useState } from "react";
import { isMobileOnly } from "react-device-detect";
import PageHeader from "@/components/layout/pageHeader/PageHeader";
import ButtonDanger from "@/components/shared/button/danger/ButtonDanger";
import ButtonRegular from "@/components/shared/button/regular/ButtonRegular";
import Modal from "@/components/shared/modal/Modal";
import Paragraph from "@/components/shared/paragraph/Paragraph";
import ToastContext from "@/components/shared/toast/context/ToastContext";
import DeleteReport from "@/graphql/queries/deleteDailyReport.gql";
import { IconSpinner } from "@/components/iconSpinner";
import { generateExportedProjectFilename } from "@/utils/files/shared";
import { downloadContentAsFile } from "@/components/fileDownloadDropdown/utils";
import { getUpdatedRouterQuery } from "@/utils/router";
import { useAuthStore } from "@/store/auth/useAuthStore.store";
import { useTenantStore } from "@/store/tenant/useTenantStore.store";
import { ProjectDescriptionHeader } from "@/container/projectSummaryView/PojectDescriptionHeader";
import { canDownloadReports } from "../../permissions";

const downloadContent = (
  content: Blob,
  projectName: string,
  projectNumber: string,
  extension: "zip" | "pdf"
) => {
  downloadContentAsFile(
    content,
    `${generateExportedProjectFilename({
      title: "Daily Inspection Report Export",
      project: { name: projectName, number: projectNumber },
    })}.${extension}`
  );
};

type DailyInspectionPageHeaderProps = {
  id?: string;
  reportId?: string;
  reportCreatedUserId?: string;
  sections?: DailyReportInputs;
  projectName: string;
  projectDescription?: string;
  projectNumber?: string;
  locationId: string;
  locationName: string;
  isReportSaved: boolean;
  isReportComplete: boolean;
  onReopen: () => void;
  selectedTab?: FormViewTabStates;
  setSelectedTab?: (selectedTab: FormViewTabStates) => void;
};

export default function DailyInspectionPageHeader({
  id,
  reportId,

  projectName,
  projectDescription = "",
  projectNumber = "",
  locationId,
  locationName,

  isReportComplete,
  selectedTab,
  setSelectedTab,
}: DailyInspectionPageHeaderProps): JSX.Element {
  const { workPackage } = useTenantStore(state => state.getAllEntities());
  const router = useRouter();
  const projectUrl: RouterLink = {
    pathname: "/projects/[id]",
    query: getUpdatedRouterQuery(
      {
        id,
        location: locationId,
        activeTab: router.query.activeTab,
        startDate: router.query.startDate,
      },
      { key: "source", value: router.query.source }
    ),
  };
  const [deleteReport] = useMutation(DeleteReport, {
    onCompleted: () => {
      toastCtx?.pushToast("success", "Report deleted");
      router.push(projectUrl);
    },
  });

  const toastCtx = useContext(ToastContext);
  const { me } = useAuthStore();

  const [isDeleteModalOpen, setIsDeleteModalOpen] = useState(false);
  const [isDownloading, setIsDownloading] = useState(false);
  const [isDownloadingPDF, setIsDownloadingPDF] = useState(false);
  const canPrintReport = isReportComplete && canDownloadReports(me);

  const closeReportModalHandler = () => setIsDeleteModalOpen(false);

  const confirmDeleteHandler = async () => {
    deleteReport({
      variables: {
        deleteDailyReportId: reportId,
      },
    });
  };

  const downloadReportHandler = (event: BaseSyntheticEvent) => {
    event.stopPropagation();
    setIsDownloading(true);

    try {
      fetch(`/api/daily-report/${reportId}`, {
        headers: {
          "Content-Type": "application/zip",
        },
      })
        .then(response => {
          if (!response.ok) {
            toastCtx?.pushToast(
              "error",
              "It was not possible to download the pdf, please try again"
            );
            return;
          }

          return response.blob();
        })
        .then(content => {
          if (content) {
            downloadContent(content, projectName, projectNumber, "zip");
          }
        })
        .finally(() => {
          setIsDownloading(false);
        });
    } catch (err) {
      toastCtx?.pushToast(
        "error",
        "It was not possible to download the pdf, please try again"
      );
    }
  };

  const downloadPDFReportHandler = (event: BaseSyntheticEvent) => {
    event.stopPropagation();
    setIsDownloadingPDF(true);

    try {
      fetch(`/api/daily-report/${reportId}/pdf`, {
        headers: {
          "Content-Type": "application/pdf",
        },
      })
        .then(response => {
          if (!response.ok) {
            toastCtx?.pushToast(
              "error",
              "It was not possible to download the pdf, please try again"
            );
            return;
          }

          return response.blob();
        })
        .then(content => {
          if (content) {
            downloadContent(content, projectName, projectNumber, "pdf");
          }
        })
        .finally(() => {
          setIsDownloadingPDF(false);
        });
    } catch (err) {
      toastCtx?.pushToast(
        "error",
        "It was not possible to download the pdf, please try again"
      );
    }
  };

  const getHeaderActions = (): PageHeaderAction[] => {
    const headerActions: PageHeaderAction[] = [];
    if (canPrintReport) {
      headerActions.push({
        title: "Download PDF",
        icon: "download",
        onClick: downloadPDFReportHandler,
        rightSlot: (
          <IconSpinner
            className={cx({
              ["invisible"]: !isDownloadingPDF,
              ["visible"]: isDownloadingPDF,
            })}
          />
        ),
      });
      headerActions.push({
        title: "Download",
        icon: "download",
        onClick: downloadReportHandler,
        rightSlot: (
          <IconSpinner
            className={cx({
              ["invisible"]: !isDownloading,
              ["visible"]: isDownloading,
            })}
          />
        ),
      });
    }
    return headerActions;
  };

  const headerActions = getHeaderActions();
  return (
    <>
      <PageHeader
        linkText={
          router.query?.pathOrigin === "workPackage"
            ? `${workPackage.label} Summary View`
            : "All forms"
        }
        linkRoute={
          router.query?.pathOrigin === "workPackage" ? projectUrl : "/forms"
        }
        setSelectedTab={(selectedFormTab: FormViewTabStates) => {
          setSelectedTab && setSelectedTab(selectedFormTab);
        }}
        selectedTab={selectedTab}
        actions={headerActions}
        additionalInfo={
          <ProjectDescriptionHeader
            maxCharacters={isMobileOnly ? 35 : 80}
            description={projectDescription}
          />
        }
      >
        <div className="flex items-center justify-between">
          <div className="flex-col">
            <h2 className="block text-2xl text-neutral-shade-100">
              Daily Inspection Report
            </h2>
            <h3 className="block text-sm text-neutral-shade-58">
              {projectName} • {locationName}
            </h3>
          </div>
        </div>
      </PageHeader>
      <Modal
        title="Are you sure you want to delete this report?"
        isOpen={isDeleteModalOpen}
        closeModal={closeReportModalHandler}
      >
        <>
          <Paragraph text="Once removed, you will no longer have access to edit this specific report." />
          <div className="flex justify-end mt-10">
            <ButtonRegular
              className="mr-3 text-sm"
              label="Cancel"
              onClick={closeReportModalHandler}
            />
            <ButtonDanger
              label="Delete Report"
              onClick={confirmDeleteHandler}
            />
          </div>
        </>
      </Modal>
    </>
  );
}
