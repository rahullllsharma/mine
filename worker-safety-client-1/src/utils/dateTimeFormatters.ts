export const formatDateTime = (dateTimeString: string): string => {
  try {
    const date = new Date(dateTimeString);
    if (isNaN(date.getTime())) return dateTimeString;
    const formattedDate = date.toLocaleDateString();
    const timePart = date.toLocaleTimeString("en-US", {
      hour: "numeric",
      minute: "2-digit",
      hour12: true,
    });

    return `${formattedDate}, ${timePart}`;
  } catch (error) {
    return dateTimeString;
  }
};

export const formatDateOnly = (dateTimeString: string): string => {
  try {
    const date = new Date(dateTimeString);
    if (isNaN(date.getTime())) return dateTimeString;
    return date.toLocaleDateString();
  } catch (error) {
    return dateTimeString;
  }
};

export const formatTimeOnly = (timeString: string): string => {
  try {
    const [hoursStr, minutesStr] = timeString.split(":");
    const hours = Number(hoursStr);
    const minutes = Number(minutesStr);
    if (
      isNaN(hours) ||
      isNaN(minutes) ||
      hours < 0 ||
      hours > 23 ||
      minutes < 0 ||
      minutes > 59
    ) {
      return timeString;
    }
    const date = new Date();
    date.setHours(hours, minutes, 0, 0);
    return date.toLocaleTimeString("en-US", {
      hour: "numeric",
      minute: "2-digit",
      hour12: true,
    });
  } catch (error) {
    return timeString;
  }
};
