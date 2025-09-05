import Input from "@/components/shared/input/Input";
import { IconName } from "@urbint/silica";

type LoadingFiltersComponentProps = {
  icon: IconName;
};

const LoadingFiltersComponent = ({ icon }: LoadingFiltersComponentProps) => (
  <Input placeholder="Loading, Please Wait" icon={icon} disabled />
);

export default LoadingFiltersComponent;
