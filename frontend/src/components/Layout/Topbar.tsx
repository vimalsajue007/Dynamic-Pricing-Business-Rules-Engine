import React from "react";
import AppBar from "@mui/material/AppBar";
import Toolbar from "@mui/material/Toolbar";
import Box from "@mui/material/Box";
import Typography from "@mui/material/Typography";
import Avatar from "@mui/material/Avatar";
import Chip from "@mui/material/Chip";
import IconButton from "@mui/material/IconButton";
import Menu from "@mui/material/Menu";
import MenuItem from "@mui/material/MenuItem";
import LogoutRoundedIcon from "@mui/icons-material/LogoutRounded";
import { DRAWER_WIDTH } from "./Sidebar";
import { useAuth } from "../../context/AuthContext";
import { useNavigate } from "react-router-dom";

export default function Topbar({ title }: { title: string }) {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const [anchor, setAnchor] = React.useState<null | HTMLElement>(null);

  const initials = (user?.full_name || "?")
    .split(" ")
    .map((p) => p[0])
    .slice(0, 2)
    .join("")
    .toUpperCase();

  return (
    <AppBar position="fixed" sx={{ width: `calc(100% - ${DRAWER_WIDTH}px)`, ml: `${DRAWER_WIDTH}px` }} elevation={0}>
      <Toolbar sx={{ justifyContent: "space-between" }}>
        <Typography variant="h6" sx={{ fontSize: "1.05rem" }}>
          {title}
        </Typography>
        <Box sx={{ display: "flex", alignItems: "center", gap: 1.5 }}>
          {user && (
            <Chip
              size="small"
              label={user.role === "admin" ? "Administrator" : "User"}
              sx={{
                backgroundColor: user.role === "admin" ? "rgba(139,92,246,0.18)" : "rgba(255,255,255,0.06)",
                color: user.role === "admin" ? "#C4B5FD" : "text.secondary",
              }}
            />
          )}
          <IconButton onClick={(e) => setAnchor(e.currentTarget)} size="small">
            <Avatar sx={{ width: 32, height: 32, fontSize: "0.8rem", bgcolor: "#6D28D9" }}>{initials}</Avatar>
          </IconButton>
          <Menu anchorEl={anchor} open={!!anchor} onClose={() => setAnchor(null)}>
            <Box sx={{ px: 2, py: 1 }}>
              <Typography variant="body2" fontWeight={600}>{user?.full_name}</Typography>
              <Typography variant="caption" color="text.secondary">{user?.email}</Typography>
            </Box>
            <MenuItem
              onClick={() => {
                logout();
                navigate("/login");
              }}
            >
              <LogoutRoundedIcon fontSize="small" sx={{ mr: 1 }} /> Sign out
            </MenuItem>
          </Menu>
        </Box>
      </Toolbar>
    </AppBar>
  );
}
