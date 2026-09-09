import React from "react";
import { NavLink, useLocation } from "react-router-dom";
import Drawer from "@mui/material/Drawer";
import Box from "@mui/material/Box";
import List from "@mui/material/List";
import ListItemButton from "@mui/material/ListItemButton";
import ListItemIcon from "@mui/material/ListItemIcon";
import ListItemText from "@mui/material/ListItemText";
import Typography from "@mui/material/Typography";
import Divider from "@mui/material/Divider";
import DashboardRoundedIcon from "@mui/icons-material/DashboardRounded";
import Inventory2RoundedIcon from "@mui/icons-material/Inventory2Rounded";
import GroupRoundedIcon from "@mui/icons-material/GroupRounded";
import RuleRoundedIcon from "@mui/icons-material/RuleRounded";
import LocalOfferRoundedIcon from "@mui/icons-material/LocalOfferRounded";
import CalculateRoundedIcon from "@mui/icons-material/CalculateRounded";
import ScienceRoundedIcon from "@mui/icons-material/ScienceRounded";
import HistoryRoundedIcon from "@mui/icons-material/HistoryRounded";
import BoltRoundedIcon from "@mui/icons-material/BoltRounded";
import GroupsRoundedIcon from "@mui/icons-material/GroupsRounded";

export const DRAWER_WIDTH = 248;

const items = [
  { label: "Dashboard", path: "/", icon: <DashboardRoundedIcon fontSize="small" /> },
  { label: "Products", path: "/products", icon: <Inventory2RoundedIcon fontSize="small" /> },
  { label: "Customers", path: "/customers", icon: <GroupRoundedIcon fontSize="small" /> },
  { label: "Pricing Rules", path: "/rules", icon: <RuleRoundedIcon fontSize="small" /> },
  { label: "Promotions", path: "/promotions", icon: <LocalOfferRoundedIcon fontSize="small" /> },
  { label: "Pricing Preview", path: "/preview", icon: <CalculateRoundedIcon fontSize="small" /> },
  { label: "Rule Testing", path: "/testing", icon: <ScienceRoundedIcon fontSize="small" /> },
  { label: "Pricing History", path: "/history", icon: <HistoryRoundedIcon fontSize="small" /> },
  { label: "Users", path: "/users", icon: <GroupsRoundedIcon fontSize="small" /> },
];

export default function Sidebar() {
  const location = useLocation();

  return (
    <Drawer
      variant="permanent"
      sx={{
        width: DRAWER_WIDTH,
        flexShrink: 0,
        "& .MuiDrawer-paper": { width: DRAWER_WIDTH, boxSizing: "border-box" },
      }}
    >
      <Box sx={{ display: "flex", alignItems: "center", gap: 1.2, px: 2.5, py: 3 }}>
        <Box
          sx={{
            width: 34,
            height: 34,
            borderRadius: "9px",
            display: "grid",
            placeItems: "center",
            backgroundImage: "linear-gradient(135deg, #9C6EF5, #6D28D9)",
          }}
        >
          <BoltRoundedIcon sx={{ fontSize: 20, color: "#0D0A18" }} />
        </Box>
        <Box>
          <Typography variant="subtitle1" sx={{ fontWeight: 700, lineHeight: 1.1 }}>
            Pricelogic
          </Typography>
          <Typography variant="caption" color="text.secondary">
            Rules Engine
          </Typography>
        </Box>
      </Box>
      <Divider />
      <List sx={{ px: 1.5, py: 2 }}>
        {items.map((item) => {
          const active = location.pathname === item.path;
          return (
            <ListItemButton
              key={item.path}
              component={NavLink}
              to={item.path}
              selected={active}
              sx={{
                borderRadius: 2,
                mb: 0.5,
                color: active ? "#F3F0FF" : "text.secondary",
                "&.Mui-selected": {
                  backgroundColor: "rgba(139,92,246,0.16)",
                  borderLeft: "2px solid #8B5CF6",
                },
                "&.Mui-selected:hover": { backgroundColor: "rgba(139,92,246,0.22)" },
              }}
            >
              <ListItemIcon sx={{ minWidth: 34, color: active ? "#B594FA" : "inherit" }}>{item.icon}</ListItemIcon>
              <ListItemText primaryTypographyProps={{ fontSize: "0.875rem", fontWeight: active ? 600 : 500 }}>
                {item.label}
              </ListItemText>
            </ListItemButton>
          );
        })}
      </List>
    </Drawer>
  );
}
