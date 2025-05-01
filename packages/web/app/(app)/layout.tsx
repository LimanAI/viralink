"use client";
import { LuChartNoAxesColumnIncreasing, LuSettings } from "react-icons/lu";

import Header from "./_components/Header";
import { useRouter, usePathname } from "next/navigation";

// Sidebar navigation items
const sidebarItems = [
  {
    id: "dashboard",
    label: "Dashboard",
    href: "/dashboard",
    icon: <LuChartNoAxesColumnIncreasing className="w-5 h-5" />,
    isAdmin: false,
  },
  {
    id: "admin",
    label: "Admin",
    href: "/admin",
    icon: <LuSettings className="w-5 h-5" />,
    isAdmin: true,
  },
];

export default function Layout({ children }: { children: React.ReactNode }) {
  const router = useRouter();

  return (
    <div className="min-h-screen flex flex-col">
      <Header isAdmin={usePathname() === "/admin"} className="border-b border-gray-200" />

      <div className="flex flex-1 overflow-hidden">
        {/* Sidebar */}
        <aside className="w-20 md:w-64 border-r border-gray-200 flex-shrink-0">
          <div className="p-2">
            <ul className="space-y-2">
              {sidebarItems.map((item) => (
                <li key={item.id}>
                  <button
                    onClick={() => router.push(item.href)}
                    className={`relative w-full flex items-center cursor-pointer ${
                      usePathname() === item.href ? "bg-primary/10 text-primary font-medium" : "hover:bg-gray-50"
                    } rounded-lg p-3 transition-colors group`}
                  >
                    <div className="flex items-center w-full">
                      <div
                        className={`${
                          usePathname() === item.href ? "text-primary" : "text-gray-500 group-hover:text-primary"
                        }`}
                      >
                        {item.icon}
                      </div>
                      <span className="ml-3 hidden md:block">{item.label}</span>
                      {item.isAdmin && (
                        <span className="ml-auto hidden md:flex px-2 py-0.5 text-xs rounded-full bg-red-100 text-red-600">
                          Admin
                        </span>
                      )}
                    </div>
                  </button>
                </li>
              ))}
            </ul>
          </div>
        </aside>

        <main className="flex-1 overflow-auto p-6 bg-base-200/90">{children}</main>
      </div>
    </div>
  );
}
