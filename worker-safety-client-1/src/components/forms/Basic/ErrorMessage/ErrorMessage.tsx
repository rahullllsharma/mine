import type { FormField } from "@/utils/formField";
import type { Errors } from "io-ts";
import classnames from "classnames";
import { isLeft } from "fp-ts/Either";
import { failure } from "io-ts/PathReporter";

type ErrorMessageProps<V> = {
  className?: string;
  field: FormField<Errors, string, V>;
};

function ErrorMessage<V>({ className, field }: ErrorMessageProps<V>) {
  const { val } = field;
  return (
    <>
      {isLeft(val) &&
        failure(val.left).map(message => (
          <span
            key={message}
            className={classnames(
              "text-sm mt-1 text-system-error-40",
              className
            )}
          >
            {message}
          </span>
        ))}
    </>
  );
}

export { ErrorMessage };
