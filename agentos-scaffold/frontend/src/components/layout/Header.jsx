import { useLocation } from "react-router-dom";

const sectionNames = {
  "/dashboard": "Dashboard",
  "/workspace": "AI Workspace",
  "/analytics": "Analytics",
  "/reports": "Reports",
};

export default function Header() {
  const { pathname } = useLocation();
  const sectionName = sectionNames[pathname] ?? "AgentOS";

  return (
    <header className="flex h-15 shrink-0 items-center border-b border-white/[0.07] px-8">
      <span className="text-sm font-medium tracking-wide text-white/65">
        {sectionName}
      </span>
    </header>
  );
}
