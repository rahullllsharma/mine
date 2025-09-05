import { useRouter } from "next/router";
import ErrorContainer from "@/components/shared/error/ErrorContainer";

const ErrorPage = () => {
  const router = useRouter();
  return (
    <ErrorContainer
      authenticationError
      onClick={() => {
        router.push("/");
      }}
    />
  );
};

export default ErrorPage;
