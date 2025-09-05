import { Icon } from "@urbint/silica";

type PrintReportHeaderProps = {
  subtitle: string;
};

/**
 * Header component for the Daily Report PDF.
 *
 * Since this is passed as a html string, it doesn't inherit any styling properties from the inner document like styles nor custom fonts.
 * Thus we need to set everything (font-size, font-family, etc) and avoid having relative units like rem (em is ok tho).
 */
export default function PrintReportHeader({
  subtitle,
}: PrintReportHeaderProps): JSX.Element {
  return (
    <header className="flex items-start justify-between font-base font-sans px-[12px] w-full">
      <div className="flex flex-col gap-0.5">
        <h1 className="text-base font-semibold leading-6 text-neutral-shade-100">
          Daily Inspection Report
        </h1>
        {subtitle && (
          <p className="text-xs text-neutral-shade-75">{subtitle}</p>
        )}
      </div>
      <div className="flex items-center w-auto font-base">
        <Icon
          name="urbint"
          className="text-brand-urbint-40 text-base mr-[8px]"
        />
        <span className="text-tiny font-medium uppercase">worker safety</span>
      </div>
    </header>
  );
}
