import { twMerge } from "tailwind-merge";

import Logo from "@/components/Logo";
import UserMenu from "@/components/UserMenu";

export default function Header({ isAdmin, className }: { isAdmin: boolean; className?: string }) {
  return (
    <header className={twMerge("px-4 py-3", className)}>
      {isAdmin && <div className="absolute left-0 top-0 w-full h-1 bg-error"></div>}
      <div className="container mx-auto flex justify-between items-center">
        <Logo url="/dashboard" />
        <UserMenu />
      </div>
    </header>
  );
}
