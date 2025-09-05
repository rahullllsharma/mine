import type { ButtonSize } from "../ButtonSize";
import ButtonLarge from "../large/ButtonLarge";
import ButtonRegular from "../regular/ButtonRegular";
import ButtonSmall from "../small/ButtonSmall";

// eslint-disable-next-line @typescript-eslint/explicit-module-boundary-types
export const getButtonBySize = (size?: ButtonSize) => {
  let Button = ButtonRegular;
  if (size === "lg") {
    Button = ButtonLarge;
  } else if (size === "sm") {
    Button = ButtonSmall;
  }

  return Button;
};
