import React from "react";
import Box from "@mui/material/Box";
import Toolbar from "@mui/material/Toolbar";
import Sidebar from "./Sidebar";
import Topbar from "./Topbar";

export default function AppLayout({ title, children }: { title: string; children: React.ReactNode }) {
  return (
    <Box sx={{ display: "flex" }}>
      <Sidebar />
      <Box component="main" sx={{ flexGrow: 1, minHeight: "100vh" }}>
        <Topbar title={title} />
        <Toolbar />
        <Box sx={{ p: { xs: 2, md: 4 }, maxWidth: 1400, mx: "auto" }}>{children}</Box>
      </Box>
    </Box>
  );
}
