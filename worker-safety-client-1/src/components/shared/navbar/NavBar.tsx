import type { ReactNode } from "react";
import UrbintLogo from "../urbintLogo/UrbintLogo";

export interface NavBarProps {
  title: string;
  leftContent?: ReactNode;
  rightContent?: ReactNode;
}

export default function NavBar({
  title,
  leftContent,
  rightContent,
}: NavBarProps): JSX.Element {
  return (
    <header
      className="flex items-center h-12 py-2 px-5 bg-brand-urbint-60 shadow-20 text-white w-full"
      data-testid="navbar"
    >
      <UrbintLogo className="text-white" />
      <div
        className="pl-2 text-sm font-semibold uppercase"
        data-testid="navbar-title"
      >
        {title}
      </div>
      {leftContent && <div className="ml-10">{leftContent}</div>}
      <div className="ml-auto" data-testid="navbar-rightContent">
        {rightContent}
      </div>
    </header>
  );
}
