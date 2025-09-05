import type { MultiOption } from "../multiOptionWrapper/MultiOptionWrapper";

function removeDuplicateOptionsByName(options: MultiOption[]) {
  const uniqueNamesSet = new Set();
  return options
    .reduce((uniqueOptions: MultiOption[], option) => {
      if (option.name && !uniqueNamesSet.has(option.name)) {
        uniqueNamesSet.add(option.name);
        uniqueOptions.push(option);
      }
      return uniqueOptions;
    }, [])
    .sort((a, b) => a.name.localeCompare(b.name));
}

export { removeDuplicateOptionsByName };
