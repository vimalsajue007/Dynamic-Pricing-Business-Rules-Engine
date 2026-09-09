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
import Dialog from "@mui/material/Dialog";
import DialogTitle from "@mui/material/DialogTitle";
import DialogContent from "@mui/material/DialogContent";
import DialogActions from "@mui/material/DialogActions";
import AddRoundedIcon from "@mui/icons-material/AddRounded";
import { api, apiErrorMessage } from "../api/client";
import type { Promotion } from "../types";
import { useAuth } from "../context/AuthContext";

export default function Promotions() {
  const { user } = useAuth();
  const isAdmin = user?.role === "admin";
  const [promos, setPromos] = useState<Promotion[]>([]);
  const [dialog, setDialog] = useState(false);
  const [form, setForm] = useState({
    code: "", description: "", discount_type: "percent", discount_value: "", minimum_purchase: "0",
    maximum_discount: "", start_date: "", expiry_date: "", usage_limit: "",
  });

  const load = () => api.get("/promotions", { params: { page_size: 50 } }).then((r) => setPromos(r.data.data.items));
  useEffect(() => { load(); }, []);

  const save = async () => {
    try {
      await api.post("/promotions", {
        code: form.code,
        description: form.description || null,
        discount_type: form.discount_type,
        discount_value: parseFloat(form.discount_value),
        minimum_purchase: parseFloat(form.minimum_purchase || "0"),
        maximum_discount: form.maximum_discount ? parseFloat(form.maximum_discount) : null,
        start_date: form.start_date || null,
        expiry_date: form.expiry_date || null,
        usage_limit: form.usage_limit ? parseInt(form.usage_limit) : null,
      });
      setDialog(false);
      load();
    } catch (e) {
      alert(apiErrorMessage(e));
    }
  };

  return (
    <AppLayout title="Promotional Codes">
      <Paper sx={{ p: 3, borderRadius: 3 }}>
        <Box sx={{ display: "flex", justifyContent: "flex-end", mb: 2.5 }}>
          {isAdmin && <Button startIcon={<AddRoundedIcon />} variant="contained" onClick={() => setDialog(true)}>New promotion</Button>}
        </Box>
        <Table>
          <TableHead>
            <TableRow>
              <TableCell>Code</TableCell><TableCell>Discount</TableCell><TableCell>Min purchase</TableCell>
              <TableCell>Max discount</TableCell><TableCell>Usage</TableCell><TableCell>Valid window</TableCell><TableCell>Status</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {promos.map((p) => (
              <TableRow key={p.id} hover>
                <TableCell><Chip size="small" label={p.code} sx={{ backgroundColor: "rgba(139,92,246,0.14)", color: "#C4B5FD", fontWeight: 700 }} /></TableCell>
                <TableCell>{p.discount_value}{p.discount_type === "percent" ? "%" : "$"}</TableCell>
                <TableCell>${p.minimum_purchase}</TableCell>
                <TableCell>{p.maximum_discount != null ? `$${p.maximum_discount}` : "—"}</TableCell>
                <TableCell>{p.usage_count}{p.usage_limit ? ` / ${p.usage_limit}` : ""}</TableCell>
                <TableCell>
                  {p.start_date ? new Date(p.start_date).toLocaleDateString() : "—"} → {p.expiry_date ? new Date(p.expiry_date).toLocaleDateString() : "—"}
                </TableCell>
                <TableCell><Chip size="small" label={p.is_active ? "Active" : "Inactive"} color={p.is_active ? "success" : "default"} variant="outlined" /></TableCell>
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </Paper>

      <Dialog open={dialog} onClose={() => setDialog(false)} fullWidth maxWidth="sm">
        <DialogTitle>New promotion</DialogTitle>
        <DialogContent sx={{ display: "flex", flexDirection: "column", gap: 2, pt: 1 }}>
          <TextField label="Code" value={form.code} onChange={(e) => setForm({ ...form, code: e.target.value.toUpperCase() })} fullWidth />
          <TextField label="Description" value={form.description} onChange={(e) => setForm({ ...form, description: e.target.value })} fullWidth />
          <Box sx={{ display: "flex", gap: 2 }}>
            <TextField select label="Type" value={form.discount_type} onChange={(e) => setForm({ ...form, discount_type: e.target.value })} sx={{ width: 160 }}>
              <MenuItem value="percent">Percent</MenuItem>
              <MenuItem value="flat">Flat amount</MenuItem>
            </TextField>
            <TextField label="Discount value" type="number" value={form.discount_value} onChange={(e) => setForm({ ...form, discount_value: e.target.value })} fullWidth />
          </Box>
          <Box sx={{ display: "flex", gap: 2 }}>
            <TextField label="Minimum purchase" type="number" value={form.minimum_purchase} onChange={(e) => setForm({ ...form, minimum_purchase: e.target.value })} fullWidth />
            <TextField label="Maximum discount" type="number" value={form.maximum_discount} onChange={(e) => setForm({ ...form, maximum_discount: e.target.value })} fullWidth />
          </Box>
          <Box sx={{ display: "flex", gap: 2 }}>
            <TextField label="Start date" type="date" InputLabelProps={{ shrink: true }} value={form.start_date} onChange={(e) => setForm({ ...form, start_date: e.target.value })} fullWidth />
            <TextField label="Expiry date" type="date" InputLabelProps={{ shrink: true }} value={form.expiry_date} onChange={(e) => setForm({ ...form, expiry_date: e.target.value })} fullWidth />
          </Box>
          <TextField label="Usage limit (optional)" type="number" value={form.usage_limit} onChange={(e) => setForm({ ...form, usage_limit: e.target.value })} fullWidth />
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setDialog(false)}>Cancel</Button>
          <Button variant="contained" onClick={save}>Save</Button>
        </DialogActions>
      </Dialog>
    </AppLayout>
  );
}
