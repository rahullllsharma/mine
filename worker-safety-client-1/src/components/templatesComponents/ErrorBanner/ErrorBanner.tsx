import { Icon } from "@urbint/silica";

type ErrorBannerProps = {
  message: string;
  onClose: () => void;
  className?: string;
};
export default function ErrorBanner({
  message,
  className,
  onClose,
}: ErrorBannerProps) {
  return (
    <div
      className={`border border-system-error-40 bg-system-error-10 box-border p-2 ${className}`}
    >
      <div className="flex justify-between items-center">
        <div className="text-sm">
          <Icon name={"error"} className={`text-system-error-40 mr-2`} />
          {message}
        </div>
        <button className="ml-4" aria-label="Close error banner">
          <Icon
            name={"close_big"}
            className={`text-gray-400`}
            onClick={onClose}
          />
        </button>
      </div>
    </div>
  );
}
