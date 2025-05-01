"use client";

import { usePathname } from "next/navigation";
import { PiTelegramLogo } from "react-icons/pi";

const tabItems = [
  {
    id: "admin",
    label: "TG Accounts Setup",
    href: "/admin",
    icon: <PiTelegramLogo className="w-5 h-5" />,
  },
];

export default function AdminLayout({ children }: { children: React.ReactNode }) {
  return (
    <div>
      <div>
        <h1 className="text-2xl font-bold">Admin Dashboard</h1>
        <p className="text-base-content/60">Manage your ViraLink AI platform settings</p>
      </div>

      <div className="navbar bg-base-300/50 rounded-md my-6 p-1 min-h-0">
        {tabItems.map((item) => (
          <a
            key={item.id}
            href={item.href}
            className={`btn btn-ghost  m-0 ${usePathname().startsWith(item.href) ? "btn-active bg-base-100" : ""}`}
          >
            {item.icon} {item.label}
          </a>
        ))}
      </div>

      <div>{children}</div>
    </div>
  );
}
