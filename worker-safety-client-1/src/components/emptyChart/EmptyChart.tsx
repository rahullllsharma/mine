import cx from "classnames";

type EmptyChartProps = {
  title: string;
  description?: string;
  small?: boolean;
};

export default function EmptyChart({
  title,
  description = "There is currently no data available for this chart",
  small = false,
}: EmptyChartProps): JSX.Element {
  return (
    <section className="flex flex-col items-center w-full text-center px-6 mb-6">
      <h2 className="text-neutral-shade-100 text-xl font-semibold mb-6">
        {title}
      </h2>
      <div
        className={cx("w-full bg-brand-gray-10 relative rounded", {
          ["max-w-4xl"]: !small,
          ["max-w-lg"]: small,
        })}
      >
        <div className="absolute h-full w-full flex items-center justify-center">
          <p className="text-neutral-shade-100 text-sm font-semibold max-w-md">
            {description}
          </p>
        </div>
        <div
          className={cx(
            "flex flex-row items-baseline pt-20 pb-14 justify-center",
            {
              ["gap-x-8"]: !small,
              ["gap-x-4"]: small,
            }
          )}
        >
          {!small && (
            <>
              <div className="h-80 w-14 xl:w-20 bg-neutral-shade-7" />
              <div className="h-64 w-14 xl:w-20 bg-neutral-shade-7" />
            </>
          )}
          <div
            className={cx("h-52 bg-neutral-shade-7", {
              ["w-14 xl:w-20"]: !small,
              ["w-8"]: small,
            })}
          />
          <div
            className={cx("h-36 bg-neutral-shade-7", {
              ["w-14 xl:w-20 "]: !small,
              ["w-8"]: small,
            })}
          />
          <div
            className={cx("h-20 bg-neutral-shade-7", {
              ["w-14 xl:w-20"]: !small,
              ["w-8"]: small,
            })}
          />
          {small && (
            <>
              <div className="h-14 w-8 bg-neutral-shade-7" />
              <div className="h-10 w-8 bg-neutral-shade-7" />
            </>
          )}
        </div>
      </div>
    </section>
  );
}
