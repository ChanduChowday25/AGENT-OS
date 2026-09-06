import { Routes, Route } from "react-router-dom";

import MainLayout from "./layouts/MainLayout.jsx";
import Intro from "./pages/Intro.jsx";
import Dashboard from "./pages/Dashboard.jsx";
import Workspace from "./pages/Workspace.jsx";
import Analytics from "./pages/Analytics.jsx";
import Reports from "./pages/Reports.jsx";

export default function App() {
  return (
    <Routes>
      <Route path="/" element={<Intro />} />
      <Route element={<MainLayout />}>
        <Route path="/dashboard" element={<Dashboard />} />
        <Route path="/workspace" element={<Workspace />} />
        <Route path="/analytics" element={<Analytics />} />
        <Route path="/reports" element={<Reports />} />
      </Route>
    </Routes>
  );
}
