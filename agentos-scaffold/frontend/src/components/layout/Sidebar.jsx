import { NavLink } from "react-router-dom";
import {
  BarChart3,
  FileText,
  LayoutDashboard,
  Sparkles,
} from "lucide-react";

const links = [
  { to: "/dashboard", label: "Dashboard", icon: LayoutDashboard },
  { to: "/workspace", label: "AI Workspace", icon: Sparkles },
  { to: "/analytics", label: "Analytics", icon: BarChart3 },
  { to: "/reports", label: "Reports", icon: FileText },
];

export default function Sidebar() {
  return (
    <aside className="flex w-60 shrink-0 flex-col border-r border-white/[0.07] bg-[#080d16] px-4 py-5">
      <div className="mb-10 flex items-center gap-3 px-2">
        <div className="flex h-8 w-8 items-center justify-center rounded-lg border border-cyan-300/20 bg-cyan-300/[0.08] text-cyan-200 shadow-[0_0_18px_rgba(103,232,249,0.08)]">
          <Sparkles size={16} strokeWidth={1.8} />
        </div>
        <span className="text-[15px] font-semibold tracking-[0.18em] text-white/90">
          AgentOS
        </span>
      </div>
      <nav className="flex flex-col gap-1.5" aria-label="Primary navigation">
        {links.map((link) => (
          <NavLink
            key={link.to}
            to={link.to}
            className={({ isActive }) =>
              [
                "group flex items-center gap-3 rounded-lg border px-3 py-2.5 text-sm transition-all duration-200",
                isActive
                  ? "border-cyan-300/20 bg-white/[0.055] text-white shadow-[0_0_24px_rgba(45,212,191,0.07)]"
                  : "border-transparent text-white/45 hover:border-white/[0.06] hover:bg-white/[0.03] hover:text-white/80",
              ].join(" ")
            }
          >
            {({ isActive }) => (
              <>
                <link.icon
                  size={17}
                  strokeWidth={isActive ? 1.8 : 1.6}
                  className={
                    isActive
                      ? "text-cyan-200"
                      : "text-white/35 transition-colors duration-200 group-hover:text-white/65"
                  }
                />
                <span>{link.label}</span>
              </>
            )}
          </NavLink>
        ))}
      </nav>
    </aside>
  );
}
