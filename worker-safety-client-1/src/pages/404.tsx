import { useRouter } from "next/router";
import ErrorContainer from "@/components/shared/error/ErrorContainer";

export default function PageNotFound(): JSX.Element {
  const router = useRouter();
  const navigateToHomeScreen = () => router.push("/");
  return <ErrorContainer notFoundError onClick={navigateToHomeScreen} />;
}
