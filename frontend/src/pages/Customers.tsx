import React, { useEffect, useState } from "react";
import AppLayout from "../components/Layout/AppLayout";
import Box from "@mui/material/Box";
import Paper from "@mui/material/Paper";
import Table from "@mui/material/Table";
import TableHead from "@mui/material/TableHead";
import TableRow from "@mui/material/TableRow";
import TableCell from "@mui/material/TableCell";
import TableBody from "@mui/material/TableBody";
import TextField from "@mui/material/TextField";
import Button from "@mui/material/Button";
import Chip from "@mui/material/Chip";
import MenuItem from "@mui/material/MenuItem";
import Pagination from "@mui/material/Pagination";
import Dialog from "@mui/material/Dialog";
import DialogTitle from "@mui/material/DialogTitle";
import DialogContent from "@mui/material/DialogContent";
import DialogActions from "@mui/material/DialogActions";
import AddRoundedIcon from "@mui/icons-material/AddRounded";
import { api, apiErrorMessage } from "../api/client";
import type { Customer, CustomerType } from "../types";
import { useAuth } from "../context/AuthContext";

const TYPES: CustomerType[] = ["Regular", "Premium", "Business", "Wholesale"];

export default function Customers() {
  const { user } = useAuth();
  const isAdmin = user?.role === "admin";
  const [customers, setCustomers] = useState<Customer[]>([]);
  const [page, setPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [search, setSearch] = useState("");
  const [typeFilter, setTypeFilter] = useState("");
  const [dialog, setDialog] = useState(false);
  const [form, setForm] = useState({ name: "", email: "", customer_type: "Regular", location: "", category: "" });

  const load = () => {
    api
      .get("/customers", { params: { page, page_size: 10, search: search || undefined, customer_type: typeFilter || undefined } })
      .then((r) => { setCustomers(r.data.data.items); setTotalPages(r.data.data.total_pages); });
  };

  useEffect(() => { load(); }, [page, search, typeFilter]);

  const save = async () => {
    try {
      await api.post("/customers", form);
      setDialog(false);
      setForm({ name: "", email: "", customer_type: "Regular", location: "", category: "" });
      load();
    } catch (e) {
      alert(apiErrorMessage(e));
    }
  };

  return (
    <AppLayout title="Customers">
      <Paper sx={{ p: 3, borderRadius: 3 }}>
        <Box sx={{ display: "flex", justifyContent: "space-between", mb: 2.5, gap: 2, flexWrap: "wrap" }}>
          <Box sx={{ display: "flex", gap: 2 }}>
            <TextField placeholder="Search name or email" value={search} onChange={(e) => { setSearch(e.target.value); setPage(1); }} sx={{ minWidth: 240 }} />
            <TextField select label="Type" value={typeFilter} onChange={(e) => { setTypeFilter(e.target.value); setPage(1); }} sx={{ minWidth: 160 }}>
              <MenuItem value="">All types</MenuItem>
              {TYPES.map((t) => <MenuItem key={t} value={t}>{t}</MenuItem>)}
            </TextField>
          </Box>
          {isAdmin && <Button startIcon={<AddRoundedIcon />} variant="contained" onClick={() => setDialog(true)}>Add customer</Button>}
        </Box>
        <Table>
          <TableHead>
            <TableRow>
              <TableCell>Name</TableCell><TableCell>Email</TableCell><TableCell>Type</TableCell><TableCell>Location</TableCell><TableCell>Status</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {customers.map((c) => (
              <TableRow key={c.id} hover>
                <TableCell>{c.name}</TableCell>
                <TableCell>{c.email}</TableCell>
                <TableCell><Chip size="small" label={c.customer_type} sx={{ backgroundColor: "rgba(139,92,246,0.14)", color: "#C4B5FD" }} /></TableCell>
                <TableCell>{c.location || "—"}</TableCell>
                <TableCell><Chip size="small" label={c.is_active ? "Active" : "Inactive"} color={c.is_active ? "success" : "default"} variant="outlined" /></TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
        <Box sx={{ display: "flex", justifyContent: "center", mt: 3 }}>
          <Pagination count={totalPages} page={page} onChange={(_, v) => setPage(v)} color="secondary" />
        </Box>
      </Paper>

      <Dialog open={dialog} onClose={() => setDialog(false)} fullWidth maxWidth="sm">
        <DialogTitle>New customer</DialogTitle>
        <DialogContent sx={{ display: "flex", flexDirection: "column", gap: 2, pt: 1 }}>
          <TextField label="Name" value={form.name} onChange={(e) => setForm({ ...form, name: e.target.value })} fullWidth />
          <TextField label="Email" value={form.email} onChange={(e) => setForm({ ...form, email: e.target.value })} fullWidth />
          <TextField select label="Customer type" value={form.customer_type} onChange={(e) => setForm({ ...form, customer_type: e.target.value })} fullWidth>
            {TYPES.map((t) => <MenuItem key={t} value={t}>{t}</MenuItem>)}
          </TextField>
          <TextField label="Location" value={form.location} onChange={(e) => setForm({ ...form, location: e.target.value })} fullWidth />
          <TextField label="Category" value={form.category} onChange={(e) => setForm({ ...form, category: e.target.value })} fullWidth />
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setDialog(false)}>Cancel</Button>
          <Button variant="contained" onClick={save}>Save</Button>
        </DialogActions>
      </Dialog>
    </AppLayout>
  );
}
