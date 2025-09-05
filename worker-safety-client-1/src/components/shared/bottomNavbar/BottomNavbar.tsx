import type { ReactNode } from "react";

export interface BottomNavBarProps {
  content: ReactNode;
}

export default function BottomNavbar({
  content,
}: BottomNavBarProps): JSX.Element {
  return (
    <header
      className="flex items-center z-10 h-16 bg-white fixed bottom-0 w-full border-t border-[#E9E9E9] shadow-20"
      data-testid="bottom-navbar"
    >
      {content}
    </header>
  );
}
