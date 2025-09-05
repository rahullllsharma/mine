import { useRouter } from "next/router";
import { useState } from "react";
import type { MenuItemProps } from "@/components/shared/dropdown/Dropdown";
import axiosRest from "@/api/customFlowApi";
import useRestMutation from "@/hooks/useRestMutation";
import { Subheading, IconName } from "@urbint/silica";
import StatusBadge from "@/components/statusBadge/StatusBadge";
import Dropdown from "@/components/shared/dropdown/Dropdown";
import ButtonIcon from "@/components/shared/button/icon/ButtonIcon";

const PageHeader = ({
  title,
  status
}: {title: string
  status: string
}) => {
  const {
    query: { id },
  } = useRouter();
  const [isDownloading, setIsDownloading] = useState(false); 

  const { mutate: downloadPDF } = useRestMutation<any>({
    endpoint: `/pdf_download/forms/${id}`,
    method: "get",
    axiosInstance: axiosRest,
    axiosConfig: {
      responseType: "blob",
    },
    mutationOptions: {
      onSuccess: async (response: any) => {
        setIsDownloading(false); 

        const blob = new Blob([response.data], { type: "application/pdf" });
        console.log("PDF disposition", response.headers);
        const disposition = response.headers?.["content-disposition"];
        let filename = `form-${Date.now()}.pdf`;
        if (disposition) {
          const match = disposition.match(/filename[^;=\n]*=((['"]).*?\2|[^;\n]*)/);
          if (match && match[1]) {
            filename = match[1].replace(/['"]/g, "");
          }
        }
        const url = window.URL.createObjectURL(blob);
        const link = document.createElement("a");
        link.href = url;
        link.setAttribute("download", filename);
        document.body.appendChild(link);
        link.click();
        link.remove();
        window.URL.revokeObjectURL(url);
      },
      onError: () => {
        setIsDownloading(false); // Stop loader on error
      },
    },
  });

  const handleDownloadPDF = () => {
    setIsDownloading(true);
    downloadPDF({});
  };

  const menuItems: MenuItemProps[] = [
    {
      label: isDownloading ? "Downloading..." : "Download PDF",
      icon: isDownloading ? ("spinner" as IconName) : ("download" as IconName),
      onClick: handleDownloadPDF,
      disabled: isDownloading, 
    },
  ];

  return (
    <div className="p-4 bg-white shadow-5 flex justify-between items-center">
      <div className="flex items-center relative">
        <Subheading className="text-[26px] py-2 m-0 mr-2">
          {title}
        </Subheading>
        <StatusBadge status={status} />
      </div>
      {status === "completed" && (
        <Dropdown
          className="z-10"
          menuItems={[menuItems]}
        >
          <ButtonIcon iconName="hamburger" />
        </Dropdown>
      )}
    </div>
  );
};

export default PageHeader;
