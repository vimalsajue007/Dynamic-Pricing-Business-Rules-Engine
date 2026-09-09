import React, { useEffect, useState } from "react";
import AppLayout from "../components/Layout/AppLayout";
import Paper from "@mui/material/Paper";
import Table from "@mui/material/Table";
import TableHead from "@mui/material/TableHead";
import TableRow from "@mui/material/TableRow";
import TableCell from "@mui/material/TableCell";
import TableBody from "@mui/material/TableBody";
import Chip from "@mui/material/Chip";
import Switch from "@mui/material/Switch";
import Box from "@mui/material/Box";
import TextField from "@mui/material/TextField";
import Pagination from "@mui/material/Pagination";
import Alert from "@mui/material/Alert";
import Select from "@mui/material/Select";
import MenuItem from "@mui/material/MenuItem";
import { api, apiErrorMessage } from "../api/client";
import { useAuth } from "../context/AuthContext";
import type { User } from "../types";

export default function Users() {
  const { user: currentUser } = useAuth();
  const [users, setUsers] = useState<User[]>([]);
  const [page, setPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [search, setSearch] = useState("");
  const [error, setError] = useState("");

  const load = () => {
    api.get("/users", { params: { page, page_size: 10, search: search || undefined } })
      .then((r) => {
        setUsers(r.data.data.items);
        setTotalPages(r.data.data.total_pages);
        setError("");
      })
      .catch((e) => setError(apiErrorMessage(e)));
  };

  useEffect(() => { load(); }, [page, search]);

  const toggleStatus = async (u: User) => {
    if (u.id === currentUser?.id) {
      alert("You can't deactivate your own account.");
      return;
    }
    try {
      await api.patch(`/users/${u.id}/status`, { is_active: !u.is_active });
      load();
    } catch (e) {
      alert(apiErrorMessage(e));
    }
  };

  const changeRole = async (u: User, newRole: string) => {
    if (u.id === currentUser?.id) {
      alert("You can't change your own role.");
      return;
    }
    try {
      await api.patch(`/users/${u.id}/role`, { role: newRole });
      load();
    } catch (e) {
      alert(apiErrorMessage(e));
    }
  };

  return (
    <AppLayout title="Users">
      <Paper sx={{ p: 3, borderRadius: 3 }}>
        <Box sx={{ mb: 2.5 }}>
          <TextField
            placeholder="Search by name or email"
            value={search}
            onChange={(e) => { setSearch(e.target.value); setPage(1); }}
            sx={{ minWidth: 260 }}
          />
        </Box>
        {error && <Alert severity="error" sx={{ mb: 2 }}>{error}</Alert>}
        <Table>
          <TableHead>
            <TableRow>
              <TableCell>Name</TableCell>
              <TableCell>Email</TableCell>
              <TableCell>Role</TableCell>
              <TableCell>Status</TableCell>
              <TableCell align="right">Active</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {users.map((u) => (
              <TableRow key={u.id} hover>
                <TableCell>{u.full_name}</TableCell>
                <TableCell>{u.email}</TableCell>
                <TableCell>
                  <Select
                    size="small"
                    value={u.role}
                    onChange={(e) => changeRole(u, e.target.value)}
                    disabled={u.id === currentUser?.id}
                    sx={{
                      minWidth: 160,
                      "& .MuiSelect-select": {
                        color: u.role === "admin" ? "#C4B5FD" : "text.secondary",
                        fontWeight: 600,
                      },
                    }}
                  >
                    <MenuItem value="user">User</MenuItem>
                    <MenuItem value="admin">Administrator</MenuItem>
                  </Select>
                </TableCell>
                <TableCell>
                  <Chip size="small" label={u.is_active ? "Active" : "Deactivated"} color={u.is_active ? "success" : "default"} variant="outlined" />
                </TableCell>
                <TableCell align="right">
                  <Switch checked={u.is_active} onChange={() => toggleStatus(u)} disabled={u.id === currentUser?.id} />
                </TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
        <Box sx={{ display: "flex", justifyContent: "center", mt: 3 }}>
          <Pagination count={totalPages} page={page} onChange={(_, v) => setPage(v)} color="secondary" />
        </Box>
      </Paper>
    </AppLayout>
  );
}