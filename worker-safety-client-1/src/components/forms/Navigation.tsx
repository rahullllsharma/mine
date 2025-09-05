import cx from "classnames";

export type Props = {
  wizardNavigation: React.ReactElement;
  children: React.ReactNode;
};

export function View(props: Props): JSX.Element {
  return (
    <div
      className={cx(
        "flex flex-col md:flex-row md:gap-4 flex-1",
        "w-full max-w-screen-lg",
        "overflow-hidden"
      )}
    >
      <nav
        className={cx(
          "flex flex-col items-start gap-2",
          "w-full md:min-w-[254px] md:max-w-[254px]",
          "px-3 md:py-6",
          "overflow-y-auto",
          "md:bg-white",
          "h-16 md:h-auto"
        )}
      >
        {props.wizardNavigation}
      </nav>
      <section
        className={cx(
          "flex-1 w-full",
          "overflow-y-auto",
          "bg-white",
          "md:py-8 md:px-6"
        )}
      >
        {props.children}
      </section>
    </div>
  );
}
