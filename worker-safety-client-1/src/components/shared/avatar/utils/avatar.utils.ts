export const getUserInitials = (name = ""): string => {
  const splittedName = name.split(" ");

  if (splittedName.length > 1) {
    const [firstName, ...restNames] = splittedName;
    const [lastName] = restNames.splice(-1);

    return (firstName[0] + lastName?.[0] ?? "").toUpperCase();
  }

  // When it receives name initials instead of full name
  // Will be unnecessary in the future eventually
  return name.replace(/\W/g, "").substring(0, 2).toUpperCase();
};
