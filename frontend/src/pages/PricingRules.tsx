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
import IconButton from "@mui/material/IconButton";
import Dialog from "@mui/material/Dialog";
import DialogTitle from "@mui/material/DialogTitle";
import DialogContent from "@mui/material/DialogContent";
import DialogActions from "@mui/material/DialogActions";
import MenuItem from "@mui/material/MenuItem";
import Switch from "@mui/material/Switch";
import FormControlLabel from "@mui/material/FormControlLabel";
import Divider from "@mui/material/Divider";
import Typography from "@mui/material/Typography";
import EditRoundedIcon from "@mui/icons-material/EditRounded";
import DeleteOutlineRoundedIcon from "@mui/icons-material/DeleteOutlineRounded";
import AddRoundedIcon from "@mui/icons-material/AddRounded";
import CloseRoundedIcon from "@mui/icons-material/CloseRounded";
import { api, apiErrorMessage } from "../api/client";
import type { PricingRule, RuleCondition, RuleAction } from "../types";
import { useAuth } from "../context/AuthContext";

const FIELDS = ["customer_type", "quantity", "location", "category", "product", "order_total", "date"];
const OPERATORS = ["equals", "not_equals", "greater_than", "greater_or_equal", "less_than", "less_or_equal", "in"];
const ACTION_TYPES = ["percent_discount", "flat_discount", "surcharge_percent", "surcharge_flat", "fixed_price"];

const emptyCondition: RuleCondition = { field: "customer_type", operator: "equals", value: "" };
const emptyAction: RuleAction = { action_type: "percent_discount", value: 0, max_amount: null };

export default function PricingRules() {
  const { user } = useAuth();
  const isAdmin = user?.role === "admin";
  const [rules, setRules] = useState<PricingRule[]>([]);
  const [dialog, setDialog] = useState(false);
  const [editing, setEditing] = useState<PricingRule | null>(null);

  const [name, setName] = useState("");
  const [description, setDescription] = useState("");
  const [priority, setPriority] = useState(100);
  const [logic, setLogic] = useState<"AND" | "OR">("AND");
  const [isExclusive, setIsExclusive] = useState(false);
  const [isStackable, setIsStackable] = useState(true);
  const [conditions, setConditions] = useState<RuleCondition[]>([{ ...emptyCondition }]);
  const [actions, setActions] = useState<RuleAction[]>([{ ...emptyAction }]);

  const load = () => api.get("/pricing-rules", { params: { page_size: 50 } }).then((r) => setRules(r.data.data.items));
  useEffect(() => { load(); }, []);

  const openCreate = () => {
    setEditing(null);
    setName(""); setDescription(""); setPriority(100); setLogic("AND");
    setIsExclusive(false); setIsStackable(true);
    setConditions([{ ...emptyCondition }]);
    setActions([{ ...emptyAction }]);
    setDialog(true);
  };

  const openEdit = (r: PricingRule) => {
    setEditing(r);
    setName(r.name); setDescription(r.description || ""); setPriority(r.priority); setLogic(r.condition_logic);
    setIsExclusive(r.is_exclusive); setIsStackable(r.is_stackable);
    setConditions(r.conditions.length ? r.conditions.map(({ id, ...c }) => c) : [{ ...emptyCondition }]);
    setActions(r.actions.map(({ id, ...a }) => a));
    setDialog(true);
  };

  const save = async () => {
    const payload = {
      name, description: description || null, priority,
      condition_logic: logic, is_exclusive: isExclusive, is_stackable: isStackable,
      conditions: conditions.filter((c) => c.value !== ""),
      actions,
    };
    try {
      if (editing) await api.put(`/pricing-rules/${editing.id}`, payload);
      else await api.post("/pricing-rules", payload);
      setDialog(false);
      load();
    } catch (e) {
      alert(apiErrorMessage(e));
    }
  };

  const remove = async (id: number) => {
    if (!confirm("Delete this pricing rule?")) return;
    await api.delete(`/pricing-rules/${id}`);
    load();
  };

  return (
    <AppLayout title="Pricing Rules">
      <Paper sx={{ p: 3, borderRadius: 3 }}>
        <Box sx={{ display: "flex", justifyContent: "space-between", mb: 2.5 }}>
          <Typography variant="body2" color="text.secondary">
            Rules run in ascending priority order. Exclusive rules stop evaluation once matched; non-stackable rules apply only if nothing else already fired.
          </Typography>
          {isAdmin && <Button startIcon={<AddRoundedIcon />} variant="contained" onClick={openCreate} sx={{ flexShrink: 0, ml: 2 }}>New rule</Button>}
        </Box>
        <Table>
          <TableHead>
            <TableRow>
              <TableCell>Priority</TableCell><TableCell>Name</TableCell><TableCell>Conditions</TableCell>
              <TableCell>Actions</TableCell><TableCell>Flags</TableCell><TableCell>Status</TableCell>
              {isAdmin && <TableCell align="right">Manage</TableCell>}
            </TableRow>
          </TableHead>
          <TableBody>
            {rules.map((r) => (
              <TableRow key={r.id} hover>
                <TableCell><Chip size="small" label={r.priority} variant="outlined" /></TableCell>
                <TableCell>
                  <Typography variant="body2" fontWeight={600}>{r.name}</Typography>
                  {r.description && <Typography variant="caption" color="text.secondary">{r.description}</Typography>}
                </TableCell>
                <TableCell>
                  {r.conditions.length === 0 ? "Always" : `${r.conditions.length} (${r.condition_logic})`}
                </TableCell>
                <TableCell>
                  {r.actions.map((a, i) => (
                    <div key={i}>{a.action_type.replace("_", " ")}: {a.value}{a.action_type.includes("percent") ? "%" : ""}</div>
                  ))}
                </TableCell>
                <TableCell>
                  {r.is_exclusive && <Chip size="small" label="Exclusive" sx={{ mr: 0.5, mb: 0.5 }} />}
                  {!r.is_stackable && <Chip size="small" label="No stack" sx={{ mb: 0.5 }} />}
                </TableCell>
                <TableCell><Chip size="small" label={r.is_active ? "Active" : "Inactive"} color={r.is_active ? "success" : "default"} variant="outlined" /></TableCell>
                {isAdmin && (
                  <TableCell align="right">
                    <IconButton size="small" onClick={() => openEdit(r)}><EditRoundedIcon fontSize="small" /></IconButton>
                    <IconButton size="small" onClick={() => remove(r.id)}><DeleteOutlineRoundedIcon fontSize="small" /></IconButton>
                  </TableCell>
                )}
              </TableRow>
            ))}
          </TableBody>
        </Table>
      </Paper>

      <Dialog open={dialog} onClose={() => setDialog(false)} fullWidth maxWidth="md">
        <DialogTitle>{editing ? "Edit pricing rule" : "New pricing rule"}</DialogTitle>
        <DialogContent sx={{ display: "flex", flexDirection: "column", gap: 2.5, pt: 1 }}>
          <Box sx={{ display: "flex", gap: 2 }}>
            <TextField label="Rule name" value={name} onChange={(e) => setName(e.target.value)} fullWidth />
            <TextField label="Priority" type="number" value={priority} onChange={(e) => setPriority(parseInt(e.target.value) || 0)} sx={{ width: 140 }} />
          </Box>
          <TextField label="Description" value={description} onChange={(e) => setDescription(e.target.value)} fullWidth multiline rows={2} />

          <Box sx={{ display: "flex", gap: 3, alignItems: "center" }}>
            <TextField select label="Match logic" value={logic} onChange={(e) => setLogic(e.target.value as "AND" | "OR")} sx={{ width: 160 }}>
              <MenuItem value="AND">Match ALL (AND)</MenuItem>
              <MenuItem value="OR">Match ANY (OR)</MenuItem>
            </TextField>
            <FormControlLabel control={<Switch checked={isStackable} onChange={(e) => setIsStackable(e.target.checked)} />} label="Stackable" />
            <FormControlLabel control={<Switch checked={isExclusive} onChange={(e) => setIsExclusive(e.target.checked)} />} label="Exclusive (stop further rules)" />
          </Box>

          <Divider />
          <Typography variant="subtitle2">Conditions</Typography>
          {conditions.map((c, i) => (
            <Box key={i} sx={{ display: "flex", gap: 1.5, alignItems: "center" }}>
              <TextField select label="Field" value={c.field} onChange={(e) => setConditions(conditions.map((x, idx) => idx === i ? { ...x, field: e.target.value as any } : x))} sx={{ width: 170 }}>
                {FIELDS.map((f) => <MenuItem key={f} value={f}>{f.replace("_", " ")}</MenuItem>)}
              </TextField>
              <TextField select label="Operator" value={c.operator} onChange={(e) => setConditions(conditions.map((x, idx) => idx === i ? { ...x, operator: e.target.value as any } : x))} sx={{ width: 190 }}>
                {OPERATORS.map((o) => <MenuItem key={o} value={o}>{o.replace("_", " ")}</MenuItem>)}
              </TextField>
              <TextField label="Value" value={c.value} onChange={(e) => setConditions(conditions.map((x, idx) => idx === i ? { ...x, value: e.target.value } : x))} fullWidth placeholder="e.g. Premium, 10, Electronics" />
              <IconButton size="small" onClick={() => setConditions(conditions.filter((_, idx) => idx !== i))}><CloseRoundedIcon fontSize="small" /></IconButton>
            </Box>
          ))}
          <Button size="small" startIcon={<AddRoundedIcon />} onClick={() => setConditions([...conditions, { ...emptyCondition }])} sx={{ alignSelf: "flex-start" }}>
            Add condition
          </Button>

          <Divider />
          <Typography variant="subtitle2">Actions (at least one required)</Typography>
          {actions.map((a, i) => (
            <Box key={i} sx={{ display: "flex", gap: 1.5, alignItems: "center" }}>
              <TextField select label="Action type" value={a.action_type} onChange={(e) => setActions(actions.map((x, idx) => idx === i ? { ...x, action_type: e.target.value as any } : x))} sx={{ width: 200 }}>
                {ACTION_TYPES.map((t) => <MenuItem key={t} value={t}>{t.replace("_", " ")}</MenuItem>)}
              </TextField>
              <TextField label="Value" type="number" value={a.value} onChange={(e) => setActions(actions.map((x, idx) => idx === i ? { ...x, value: parseFloat(e.target.value) || 0 } : x))} sx={{ width: 140 }} />
              <TextField label="Max amount (optional)" type="number" value={a.max_amount ?? ""} onChange={(e) => setActions(actions.map((x, idx) => idx === i ? { ...x, max_amount: e.target.value ? parseFloat(e.target.value) : null } : x))} fullWidth />
              {actions.length > 1 && <IconButton size="small" onClick={() => setActions(actions.filter((_, idx) => idx !== i))}><CloseRoundedIcon fontSize="small" /></IconButton>}
            </Box>
          ))}
          <Button size="small" startIcon={<AddRoundedIcon />} onClick={() => setActions([...actions, { ...emptyAction }])} sx={{ alignSelf: "flex-start" }}>
            Add action
          </Button>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setDialog(false)}>Cancel</Button>
          <Button variant="contained" onClick={save}>Save rule</Button>
        </DialogActions>
      </Dialog>
    </AppLayout>
  );
}
