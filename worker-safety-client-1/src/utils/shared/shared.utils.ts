/**
 * Remove __typename from the mutation result.
 *
 * @description
 * As a way to store the result in state and to reuse it, we need to remove the `__typename` properties from the
 * mutation result before storing it in the state.
 */
export function stripTypename<T>(input: T): T {
  const result = Array.isArray(input) ? [] : {};

  for (const prop in input) {
    const cachedProp = input[prop];

    if (prop === "__typename") {
      // skip the value and continue iterating the object/array
      continue;
    }

    // eslint-disable-next-line
    // @ts-ignore
    result[prop] =
      typeof cachedProp === "object" && cachedProp !== null
        ? stripTypename(cachedProp)
        : cachedProp;
  }

  return result as T;
}

export function appendToFilename(filename: string, suffix: string): string {
  const dotIndex = filename.lastIndexOf(".");
  if (dotIndex === -1) {
    return filename + suffix;
  }
  return `${filename.substring(0, dotIndex)}${suffix}${filename.substring(
    dotIndex
  )}`;
}
