import parsePhoneNumber from "libphonenumber-js";
import { isValidPhoneNumberFormat } from "@/components/templatesComponents/customisedForm.utils";

const formatTextToPhone = (str: string) => {
  if (str.length <= 3) {
    return str;
  }

  const phoneNumber = parsePhoneNumber(str, "US");

  if (phoneNumber && isValidPhoneNumberFormat(phoneNumber.formatNational())) {
    return phoneNumber.formatNational();
  }

  const digitsOnly = str.replace(/\D/g, "");

  if (digitsOnly.length >= 10) {
    const areaCode = digitsOnly.slice(0, 3);
    const prefix = digitsOnly.slice(3, 6);
    const lineNumber = digitsOnly.slice(6, 10);
    return `(${areaCode}) ${prefix}-${lineNumber}`;
  }

  return str;
};

export default formatTextToPhone;
