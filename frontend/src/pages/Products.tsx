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
import Pagination from "@mui/material/Pagination";
import Tabs from "@mui/material/Tabs";
import Tab from "@mui/material/Tab";
import EditRoundedIcon from "@mui/icons-material/EditRounded";
import DeleteOutlineRoundedIcon from "@mui/icons-material/DeleteOutlineRounded";
import AddRoundedIcon from "@mui/icons-material/AddRounded";
import { api, apiErrorMessage } from "../api/client";
import type { Category, Product } from "../types";
import { useAuth } from "../context/AuthContext";

export default function Products() {
  const { user } = useAuth();
  const isAdmin = user?.role === "admin";
  const [tab, setTab] = useState(0);

  const [products, setProducts] = useState<Product[]>([]);
  const [categories, setCategories] = useState<Category[]>([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [search, setSearch] = useState("");

  const [productDialog, setProductDialog] = useState(false);
  const [editingProduct, setEditingProduct] = useState<Product | null>(null);
  const [form, setForm] = useState({ name: "", sku: "", description: "", base_price: "", category_id: "" });

  const [categoryDialog, setCategoryDialog] = useState(false);
  const [categoryForm, setCategoryForm] = useState({ name: "", description: "" });

  const loadCategories = () => api.get("/categories", { params: { page_size: 100 } }).then((r) => setCategories(r.data.data.items));

  const loadProducts = () => {
    api.get("/products", { params: { page, page_size: 10, search: search || undefined } }).then((r) => {
      setProducts(r.data.data.items);
      setTotal(r.data.data.total_pages);
    });
  };

  useEffect(() => { loadCategories(); }, []);
  useEffect(() => { loadProducts(); }, [page, search]);

  const openCreateProduct = () => {
    setEditingProduct(null);
    setForm({ name: "", sku: "", description: "", base_price: "", category_id: "" });
    setProductDialog(true);
  };
  const openEditProduct = (p: Product) => {
    setEditingProduct(p);
    setForm({ name: p.name, sku: p.sku, description: p.description || "", base_price: String(p.base_price), category_id: p.category_id ? String(p.category_id) : "" });
    setProductDialog(true);
  };

  const saveProduct = async () => {
    const payload = {
      name: form.name,
      sku: form.sku,
      description: form.description || null,
      base_price: parseFloat(form.base_price),
      category_id: form.category_id ? parseInt(form.category_id) : null,
    };
    try {
      if (editingProduct) {
        await api.put(`/products/${editingProduct.id}`, payload);
      } else {
        await api.post("/products", payload);
      }
      setProductDialog(false);
      loadProducts();
    } catch (e) {
      alert(apiErrorMessage(e));
    }
  };

  const deleteProduct = async (id: number) => {
    if (!confirm("Delete this product?")) return;
    await api.delete(`/products/${id}`);
    loadProducts();
  };

  const saveCategory = async () => {
    try {
      await api.post("/categories", categoryForm);
      setCategoryDialog(false);
      setCategoryForm({ name: "", description: "" });
      loadCategories();
    } catch (e) {
      alert(apiErrorMessage(e));
    }
  };

  return (
    <AppLayout title="Products & Categories">
      <Tabs value={tab} onChange={(_, v) => setTab(v)} sx={{ mb: 3 }} textColor="secondary" indicatorColor="secondary">
        <Tab label="Products" />
        <Tab label="Categories" />
      </Tabs>

      {tab === 0 && (
        <Paper sx={{ p: 3, borderRadius: 3 }}>
          <Box sx={{ display: "flex", justifyContent: "space-between", mb: 2.5, gap: 2, flexWrap: "wrap" }}>
            <TextField placeholder="Search by name or SKU" value={search} onChange={(e) => { setSearch(e.target.value); setPage(1); }} sx={{ minWidth: 260 }} />
            {isAdmin && <Button startIcon={<AddRoundedIcon />} variant="contained" onClick={openCreateProduct}>Add product</Button>}
          </Box>
          <Table>
            <TableHead>
              <TableRow>
                <TableCell>Name</TableCell>
                <TableCell>SKU</TableCell>
                <TableCell>Category</TableCell>
                <TableCell align="right">Base Price</TableCell>
                <TableCell>Status</TableCell>
                {isAdmin && <TableCell align="right">Actions</TableCell>}
              </TableRow>
            </TableHead>
            <TableBody>
              {products.map((p) => (
                <TableRow key={p.id} hover>
                  <TableCell>{p.name}</TableCell>
                  <TableCell><Chip size="small" label={p.sku} variant="outlined" /></TableCell>
                  <TableCell>{p.category?.name || "—"}</TableCell>
                  <TableCell align="right">${Number(p.base_price).toFixed(2)}</TableCell>
                  <TableCell>
                    <Chip size="small" label={p.is_active ? "Active" : "Inactive"} color={p.is_active ? "success" : "default"} variant="outlined" />
                  </TableCell>
                  {isAdmin && (
                    <TableCell align="right">
                      <IconButton size="small" onClick={() => openEditProduct(p)}><EditRoundedIcon fontSize="small" /></IconButton>
                      <IconButton size="small" onClick={() => deleteProduct(p.id)}><DeleteOutlineRoundedIcon fontSize="small" /></IconButton>
                    </TableCell>
                  )}
                </TableRow>
              ))}
            </TableBody>
          </Table>
          <Box sx={{ display: "flex", justifyContent: "center", mt: 3 }}>
            <Pagination count={total} page={page} onChange={(_, v) => setPage(v)} color="secondary" />
          </Box>
        </Paper>
      )}

      {tab === 1 && (
        <Paper sx={{ p: 3, borderRadius: 3 }}>
          <Box sx={{ display: "flex", justifyContent: "flex-end", mb: 2.5 }}>
            {isAdmin && <Button startIcon={<AddRoundedIcon />} variant="contained" onClick={() => setCategoryDialog(true)}>Add category</Button>}
          </Box>
          <Table>
            <TableHead>
              <TableRow><TableCell>Name</TableCell><TableCell>Description</TableCell><TableCell>Status</TableCell></TableRow>
            </TableHead>
            <TableBody>
              {categories.map((c) => (
                <TableRow key={c.id} hover>
                  <TableCell>{c.name}</TableCell>
                  <TableCell>{c.description || "—"}</TableCell>
                  <TableCell><Chip size="small" label={c.is_active ? "Active" : "Inactive"} color={c.is_active ? "success" : "default"} variant="outlined" /></TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </Paper>
      )}

      <Dialog open={productDialog} onClose={() => setProductDialog(false)} fullWidth maxWidth="sm">
        <DialogTitle>{editingProduct ? "Edit product" : "New product"}</DialogTitle>
        <DialogContent sx={{ display: "flex", flexDirection: "column", gap: 2, pt: 1 }}>
          <TextField label="Name" value={form.name} onChange={(e) => setForm({ ...form, name: e.target.value })} fullWidth />
          <TextField label="SKU" value={form.sku} onChange={(e) => setForm({ ...form, sku: e.target.value })} fullWidth />
          <TextField label="Description" value={form.description} onChange={(e) => setForm({ ...form, description: e.target.value })} fullWidth multiline rows={2} />
          <TextField label="Base price" type="number" value={form.base_price} onChange={(e) => setForm({ ...form, base_price: e.target.value })} fullWidth />
          <TextField select label="Category" value={form.category_id} onChange={(e) => setForm({ ...form, category_id: e.target.value })} fullWidth>
            <MenuItem value="">None</MenuItem>
            {categories.map((c) => <MenuItem key={c.id} value={c.id}>{c.name}</MenuItem>)}
          </TextField>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setProductDialog(false)}>Cancel</Button>
          <Button variant="contained" onClick={saveProduct}>Save</Button>
        </DialogActions>
      </Dialog>

      <Dialog open={categoryDialog} onClose={() => setCategoryDialog(false)} fullWidth maxWidth="xs">
        <DialogTitle>New category</DialogTitle>
        <DialogContent sx={{ display: "flex", flexDirection: "column", gap: 2, pt: 1 }}>
          <TextField label="Name" value={categoryForm.name} onChange={(e) => setCategoryForm({ ...categoryForm, name: e.target.value })} fullWidth />
          <TextField label="Description" value={categoryForm.description} onChange={(e) => setCategoryForm({ ...categoryForm, description: e.target.value })} fullWidth multiline rows={2} />
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setCategoryDialog(false)}>Cancel</Button>
          <Button variant="contained" onClick={saveCategory}>Save</Button>
        </DialogActions>
      </Dialog>
    </AppLayout>
  );
}
