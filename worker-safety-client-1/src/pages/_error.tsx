import type { NextPageContext } from "next";
import ErrorContainer from "@/components/shared/error/ErrorContainer";

interface ErrorComponentProps {
  statusCode?: number;
}

function ErrorComponent({ statusCode }: ErrorComponentProps): JSX.Element {
  if (statusCode) console.log(`Error - Status code: ${statusCode}`);
  return <ErrorContainer />;
}

// Although this isn't being fully used for now, leaving it here to support the ongoing investigation (having errors with contextual messages)
// in the meanwhile, it will trigger a simple log when we get a server error
ErrorComponent.getInitialProps = ({ res, err }: NextPageContext) => {
  const statusCode = res?.statusCode ?? err?.statusCode ?? 404;
  return { statusCode };
};

export default ErrorComponent;
