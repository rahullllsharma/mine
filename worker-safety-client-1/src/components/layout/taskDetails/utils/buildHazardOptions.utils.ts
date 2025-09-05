/** Extracts and returns an object with the prefix and index task */
function buildHazardOptions(controlFormPrefix?: `${string}.${number}`) {
  if (!controlFormPrefix?.includes(".")) {
    return undefined;
  }

  const [prefix, index] = controlFormPrefix.split(".");
  return {
    prefix,
    taskIndex: +index,
  };
}

export { buildHazardOptions };
