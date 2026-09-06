import { Outlet } from "react-router-dom";

import Sidebar from "../components/layout/Sidebar.jsx";
import Header from "../components/layout/Header.jsx";

export default function MainLayout() {
  return (
    <div className="flex h-screen overflow-hidden bg-[#060a11] text-white">
      <Sidebar />
      <div className="flex min-w-0 flex-1 flex-col bg-[#0a0f18]">
        <Header />
        <main className="min-h-0 flex-1 overflow-y-auto px-8 py-7">
          <Outlet />
        </main>
      </div>
    </div>
  );
}
