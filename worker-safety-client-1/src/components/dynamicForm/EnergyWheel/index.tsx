import type { EnergyWheelProps } from "@/components/templatesComponents/customisedForm.types";
import { useFormRendererContext } from "@/components/templatesComponents/FormPreview/Components/FormRendererContext";
import EnergyWheelComponent from "./EnergyWheelComponent";
import EnergyWheelSkeleton from "./EnergyWheelSkeleton";

const EnergyWheel = (props: EnergyWheelProps) => {
  const { isLoading } = useFormRendererContext();
  return (
    <>
      {isLoading ? (
        <EnergyWheelSkeleton />
      ) : (
        <EnergyWheelComponent {...props} />
      )}
    </>
  );
};

export default EnergyWheel;
