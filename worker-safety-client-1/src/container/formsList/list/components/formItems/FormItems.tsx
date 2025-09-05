// import { useRouter } from "next/router";
import type { Form } from "@/types/formsList/formsList";
import { useRouter } from "next/router";
import FormCardItem from "@/components/cardItem/FormCardItem";

function FormItems({ formsData }: { formsData: Form[] }) {
  const router = useRouter();
  const formNavigator = (formData: Form) => {
    let pathname: string;
    let query = {};
    switch (formData.__typename) {
      case "DailyReport":
        pathname = `/projects/${[formData?.workPackage?.id]}/locations/${[
          formData?.location?.id,
        ]}/reports/${[formData.id]}`;
        query = { pathOrigin: "forms" };
        router.push({
          pathname,
          query,
        });
        break;
      case "JobSafetyBriefing":
        pathname = `/jsb`;
        query = {
          locationId: [formData?.location?.id],
          jsbId: [formData?.id],
          pathOrigin: "forms",
        };
        router.push({
          pathname,
          query,
        });
        break;
      case "EnergyBasedObservation":
        pathname = `/ebo`;
        query = {
          eboId: [formData?.id],
        };
        router.push({
          pathname,
          query,
        });
        break;
      case "NatGridJobSafetyBriefing":
        pathname = `/jsb-share/natgrid/${[formData?.id]}`;
        router.push({
          pathname,
        });
        break;
      default:
        pathname = "";
        router.push({
          pathname,
        });
        break;
    }
  };

  return (
    <>
      {formsData.map(formData => (
        <FormCardItem
          formsData={formData}
          key={formData.id}
          onClick={() => formNavigator(formData)}
        />
      ))}
    </>
  );
}

export { FormItems };
