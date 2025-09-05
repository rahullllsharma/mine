import type { PropsWithClassName } from "@/types/Generic";
import type { ReactNode } from "react";
import { useRef } from "react";
import cx from "classnames";
import { isMobile, isTablet } from "react-device-detect";
import ButtonIcon from "@/components/shared/button/icon/ButtonIcon";
import useFullscreen from "@/hooks/useFullscreen";

type SectionPadding = "responsive" | "none";

export type PageLayoutProps = PropsWithClassName<{
  header?: ReactNode;
  footer?: ReactNode;
  sectionPadding?: SectionPadding;
  showExpand?: boolean;
}>;

export default function PageLayout({
  header,
  footer,
  sectionPadding = "responsive",
  children,
  className,
  showExpand = false,
}: PageLayoutProps): JSX.Element {
  const reportSectionRef = useRef<HTMLDivElement>(null);

  const { toggle: enterFullscreen } = useFullscreen(reportSectionRef);

  const isMobileOrTablet = isMobile || isTablet;
  return (
    <>
      {showExpand && (
        <section className="relative mb-8">
          <ButtonIcon
            iconName="expand"
            className="absolute top-0 right-4"
            onClick={enterFullscreen}
          />
        </section>
      )}

      <main
        className={cx(
          "flex flex-col bg-brand-gray-10 overflow-y-auto lg:overflow-hidden w-full"
        )}
        style={{
          minHeight: isMobileOrTablet ? "100dvh" : "",
        }}
      >
        {header}
        {/* This element will be scrollable while the navbar, header and footer will be pinned. */}
        <section
          id="page-layout"
          className={cx(
            "flex flex-col overflow-y-auto h-full",
            { "responsive-padding-y": sectionPadding === "responsive" },

            className
          )}
          ref={reportSectionRef}
          data-testid="page-layout"
        >
          {children}
        </section>
        {footer}
      </main>
    </>
  );
}
