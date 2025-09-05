import { Icon } from "@urbint/silica";

type WarningBannerProps = {
  message: string;
  onClose: () => void;
  className?: string;
};

export default function WarningBanner({
  message,
  className,
  onClose,
}: WarningBannerProps) {
  return (
    <div
      className={`border border-yellow-200 bg-yellow-50 box-border p-3 rounded-md ${className}`}
    >
      <div className="flex justify-between items-center">
        <div className="text-sm">
          <Icon name={"warning"} className={`text-system-warning-30 mr-2`} />
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
