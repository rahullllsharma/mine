/* eslint-disable @next/next/no-img-element */

import Link from "@/components/shared/link/Link";
import ButtonPrimary from "../button/primary/ButtonPrimary";

export type ErrorProps = {
  notFoundError?: boolean;
  authenticationError?: boolean;
  onClick?: () => void;
};

// Assuming scenario where we have only two kinds of error pages (404 and 500). Once we can have errors with contextual messages, the title will be updated to receive dynamic values
const defaultTitle = "Issue detected.";
const notFoundErrorTitle = "404: Page not found";
const authenticationErrorTitle = "Authentication Error.";
const defaultDescription =
  "Unfortunately, it's on our end. Our team of expert engineers is working to resolve this issue as soon as possible. For updates, contact ";
const notFoundErrorDescription =
  "It looks like the page you were trying to reach could not be found. If you believe that you've reached this page in error, contact ";

export default function ErrorContainer({
  notFoundError,
  authenticationError,
  onClick,
}: ErrorProps): JSX.Element {
  const title = notFoundError
    ? notFoundErrorTitle
    : authenticationError
    ? authenticationErrorTitle
    : defaultTitle;

  const description = notFoundError
    ? notFoundErrorDescription
    : defaultDescription;

  return (
    <div className="w-full h-full flex inset-0 md:place-content-center md:place-items-center overflow-auto text-neutral-shade-primary">
      <div className="flex flex-col max-w-[700px] gap-y-6 md:flex-row md:gap-x-14 md:p-0 p-8 ">
        <div className="w-full md:w-1/2">
          <img
            src="/assets/UrbintWordmarkSmall.svg"
            alt="Urbint"
            width="120px"
            height="33px"
          />
          <img
            src="/assets/ErrorCrackCones.png"
            alt="ErrorImage"
            className="w-full px-8 md:px-0"
            width="321px"
            height="222px"
          />
        </div>
        <div className="w-full md:w-1/2">
          <h1 className="text-3xl">{title}</h1>
          <div className="my-6">
            <span>{description}</span>
            <div className="inline-flex">
              <Link
                href="mailto:support@urbint.com"
                label="support@urbint.com"
              />
              .
            </div>
          </div>
          <p>
            Sincerely,
            <br />
            the Urbint team.
          </p>
          {(notFoundError || authenticationError) && (
            <ButtonPrimary
              className="mt-6"
              label="Go to home screen"
              onClick={onClick}
            />
          )}
        </div>
      </div>
    </div>
  );
}
