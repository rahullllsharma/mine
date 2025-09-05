// Format date for input fields based on type
export const formatDateForInput = (
  date: Date,
  type: string,
  ignoreTime = false
): string => {
  // Format date string to ISO format which works well with date inputs
  const year = date.getFullYear();
  const month = String(date.getMonth() + 1).padStart(2, "0");
  const day = String(date.getDate()).padStart(2, "0");
  const todayDate = `${year}-${month}-${day}`;

  // Get current time in the proper format
  let timeNow: string;
  if (ignoreTime) {
    timeNow = "00:00"; // Set time to 00:00 when ignoreTime is true
  } else {
    const hours = String(date.getHours()).padStart(2, "0");
    const minutes = String(date.getMinutes()).padStart(2, "0");
    timeNow = `${hours}:${minutes}`;
  }

  if (type === "date_time") {
    return `${todayDate}T${timeNow}`;
  } else if (type === "date_only") {
    return todayDate;
  } else {
    return timeNow; // for time_only
  }
};

export const formatDateTimeLocal = (date?: Date | string | null) => {
  if (!date) return undefined;

  const dateObj = new Date(date);

  // Check if date is valid before trying to format it
  if (isNaN(dateObj.getTime())) {
    return undefined;
  }

  return dateObj.toISOString().slice(0, 16); // 'YYYY-MM-DDTHH:mm'
};

// Helper function to check only if the date has changed irrespective of time
interface DateValue {
  value?: string;
  from?: string;
  to?: string;
}

export const hasDateChanged = (
  oldValue: DateValue | null,
  newValue: DateValue | null
): boolean => {
  if (!oldValue || !newValue) return true;

  const extractDatePortion = (dateStr?: string): string | null => {
    if (!dateStr) return null;
    const date = new Date(dateStr);
    return `${date.getFullYear()}-${date.getMonth()}-${date.getDate()}`;
  };

  if ("from" in newValue && "from" in oldValue) {
    const oldFrom = extractDatePortion(oldValue.from);
    const newFrom = extractDatePortion(newValue.from);
    if (oldFrom !== newFrom) return true;
  }

  if ("to" in newValue && "to" in oldValue) {
    const oldTo = extractDatePortion(oldValue.to);
    const newTo = extractDatePortion(newValue.to);
    if (oldTo !== newTo) return true;
  }

  if ("value" in newValue && "value" in oldValue) {
    const oldDateValue = extractDatePortion(oldValue.value);
    const newDateValue = extractDatePortion(newValue.value);
    if (oldDateValue !== newDateValue) return true;
  }

  return false;
};

export const formatLocal = (d: string, t: string) => {
  const parseTime = (timeStr: string): string => {
    const match = timeStr.match(/(\d+):(\d+)\s*(AM|PM)/i);
    if (!match) {
      return timeStr;
    }

    let hours = parseInt(match[1], 10);
    const minutes = match[2];
    const period = match[3].toUpperCase();

    if (period === "PM" && hours !== 12) {
      hours += 12;
    } else if (period === "AM" && hours === 12) {
      hours = 0;
    }

    return `${hours.toString().padStart(2, "0")}:${minutes}`;
  };

  const time24Hour = parseTime(t);
  const local = new Date(`${d}T${time24Hour}Z`);

  return new Intl.DateTimeFormat(undefined, {
    month: "long",
    day: "numeric",
    year: "numeric",
    hour: "numeric",
    minute: "2-digit",
    hour12: true,
  }).format(local);
};

export const createAutoPopulatedDate = (
  startDate?: string | string[],
  selectedType?: string
): Date => {
  if (startDate) {
    // startDate is the workPackage date taken from route params
    const workPackageDate = new Date(
      startDate.toString().replace(/[-:]/g, "/")
    );

    if (selectedType === "date_time") {
      const now = new Date();
      return new Date(
        workPackageDate.getFullYear(),
        workPackageDate.getMonth(),
        workPackageDate.getDate(),
        now.getHours(),
        now.getMinutes(),
        now.getSeconds()
      );
    } else {
      return workPackageDate;
    }
  } else {
    return new Date();
  }
};

export const createAutoPopulatedValue = (
  date: Date,
  dateType: string,
  selectedType: string
): { value?: string; from?: string; to?: string } => {
  const ignoreTime = selectedType === "date_only";

  if (dateType === "date_range") {
    return {
      from: formatDateForInput(date, selectedType, ignoreTime),
      to: formatDateForInput(date, selectedType, ignoreTime),
    };
  } else {
    return {
      value: formatDateForInput(date, selectedType, ignoreTime),
    };
  }
};
