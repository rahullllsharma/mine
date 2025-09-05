import type { MenuItemProps } from "@/components/shared/dropdown/Dropdown";
import NextLink from "next/link";
import { DateTime } from "luxon";
import { CaptionText, Subheading } from "@urbint/silica";
import { useEffect } from "react";
import { useLazyQuery } from "@apollo/client";
import router, { useRouter } from "next/router";
import Link from "@/components/shared/link/Link";
import StatusBadge from "@/components/statusBadge/StatusBadge";
import Dropdown from "@/components/shared/dropdown/Dropdown";
import ButtonIcon from "@/components/shared/button/icon/ButtonIcon";
import { NETWORK_POLICY } from "@/utils/jsbShareUtils/jsbShare.constants";
import natgridJobSafetyBriefing from "../../../../../graphql/queries/natgrid.gql";

const SharePageHeader = ({ printPdf }: { printPdf: boolean }) => {
  const {
    query: { id },
  } = useRouter();
  const [fetchNatgrid, { data: natgridData }] = useLazyQuery(
    natgridJobSafetyBriefing,
    {
      fetchPolicy: NETWORK_POLICY,
    }
  );
  useEffect(() => {
    if (id) {
      fetchNatgrid({ variables: { id } });
    }
  }, [id, fetchNatgrid]);

  const statusBadge = natgridData?.natgridJobSafetyBriefing?.status;
  const natgridAddress = natgridData?.natgridJobSafetyBriefing?.locationName;
  const updatedAt = DateTime.fromISO(
    natgridData?.natgridJobSafetyBriefing?.updatedAt
  );
  const updatedBy = natgridData?.natgridJobSafetyBriefing?.updatedBy;
  const menuItems: MenuItemProps[] = [
    {
      label: "Download PDF",
      icon: "download",
      onClick: () => {
        router.push(`/jsb-share/natgrid/${id}?printPage=true`);
      },
    },
  ];

  const statusLevels = [
    "COMPLETE",
    "PENDING_POST_JOB_BRIEF",
    "PENDING_SIGN_OFF",
  ];

  const canDownloadPDF = !printPdf && statusLevels.includes(statusBadge);
  return (
    <header className="flex flex-row justify-between bg-white p-2 sm:p-6">
      <div className="flex flex-col w-full">
        {!printPdf && (
          <NextLink href={"/forms"} passHref>
            <Link
              label={"All Forms"}
              iconLeft="chevron_big_left"
              className="mb-3"
            />
          </NextLink>
        )}
        <div className="flex justify-between w-full">
          <div>
            <div className="flex items-center min-w-[300px] relative">
              <Subheading className="text-[24px] py-2 m-0 mr-2">
                Distribution Job Safety Briefing
              </Subheading>
              <StatusBadge status={statusBadge} />
            </div>
            <CaptionText className="text-sm text-neutral-600 mt-1">
              {printPdf && (
                <>
                  <span className="font-semibold">
                    Last updated by {updatedBy?.name}{" "}
                  </span>
                  <span className="font-thin"> | </span>
                </>
              )}
              {natgridAddress}
            </CaptionText>
            {printPdf && (
              <CaptionText className="text-sm text-neutral-600 mt-1">
                Last updated at:
                {updatedAt.toLocaleString(DateTime.DATE_HUGE)},
                {updatedAt.toLocaleString(DateTime.TIME_WITH_SHORT_OFFSET)}
              </CaptionText>
            )}
          </div>
          {canDownloadPDF && (
            <div>
              <Dropdown className="z-10" menuItems={[menuItems]}>
                <ButtonIcon iconName="hamburger" />
              </Dropdown>
            </div>
          )}
        </div>
      </div>
    </header>
  );
};

export default SharePageHeader;
