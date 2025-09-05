import type { ReactNode } from "react";
import React from "react";
import style from "../createTemplateStyle.module.scss";

const FormComponentWrapper = ({ children }: { children: ReactNode }) => {
  return (
    <div className={style.previewComponentParent__formComponentParent}>
      {children}
    </div>
  );
};

export default FormComponentWrapper;
