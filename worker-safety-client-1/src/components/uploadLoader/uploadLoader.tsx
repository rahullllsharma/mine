import { Icon } from "@urbint/silica";

const CircularLoader = ({ className }: { className?: string }) => {
  return (
    <div className="flex justify-center">
      <div className="relative">
        <div className="flex justify-center">
          <Icon
            name="spinner"
            className={`animate-spin absolute text-2xl text-white ${className}`}
          />
        </div>
        <Icon name="short_up" className="animate-up-fade relative text-white" />
      </div>
    </div>
  );
};

export { CircularLoader };
