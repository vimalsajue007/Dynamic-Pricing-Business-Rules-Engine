import React, { useEffect, useState } from "react";
import AppLayout from "../components/Layout/AppLayout";
import Grid from "@mui/material/Grid";
import Paper from "@mui/material/Paper";
import Box from "@mui/material/Box";
import TextField from "@mui/material/TextField";
import MenuItem from "@mui/material/MenuItem";
import Button from "@mui/material/Button";
import Typography from "@mui/material/Typography";
import Chip from "@mui/material/Chip";
import Alert from "@mui/material/Alert";
import Divider from "@mui/material/Divider";
import { api, apiErrorMessage } from "../api/client";
import type { Product, Customer, RuleTestResult } from "../types";

export default function RuleTesting() {
  const [products, setProducts] = useState<Product[]>([]);
  const [customers, setCustomers] = useState<Customer[]>([]);
  const [productId, setProductId] = useState("");
  const [customerId, setCustomerId] = useState("");
  const [quantity, setQuantity] = useState(1);
  const [location, setLocation] = useState("");
  const [promoCode, setPromoCode] = useState("");
  const [result, setResult] = useState<RuleTestResult | null>(null);
  const [error, setError] = useState("");

  useEffect(() => {
    api.get("/products", { params: { page_size: 100, is_active: true } }).then((r) => setProducts(r.data.data.items));
    api.get("/customers", { params: { page_size: 100 } }).then((r) => setCustomers(r.data.data.items));
  }, []);

  const runTest = async () => {
    setError(""); setResult(null);
    try {
      const { data } = await api.post("/pricing/test", {
        product_id: parseInt(productId),
        customer_id: customerId ? parseInt(customerId) : null,
        quantity,
        location: location || null,
        promo_code: promoCode || null,
      });
      setResult(data.data);
    } catch (e) {
      setError(apiErrorMessage(e));
    }
  };

  return (
    <AppLayout title="Rule Testing">
      <Grid container spacing={3}>
        <Grid item xs={12} md={5}>
          <Paper sx={{ p: 3, borderRadius: 3 }}>
            <Typography variant="subtitle1" sx={{ mb: 1 }}>Sample input</Typography>
            <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
              Dry-run a calculation to see exactly which rules match before making them live. Nothing here is saved to pricing history.
            </Typography>
            <Box sx={{ display: "flex", flexDirection: "column", gap: 2 }}>
              <TextField select label="Product" value={productId} onChange={(e) => setProductId(e.target.value)} fullWidth required>
                {products.map((p) => <MenuItem key={p.id} value={p.id}>{p.name}</MenuItem>)}
              </TextField>
              <TextField select label="Customer (optional)" value={customerId} onChange={(e) => setCustomerId(e.target.value)} fullWidth>
                <MenuItem value="">Walk-in / guest</MenuItem>
                {customers.map((c) => <MenuItem key={c.id} value={c.id}>{c.name} ({c.customer_type})</MenuItem>)}
              </TextField>
              <TextField label="Quantity" type="number" value={quantity} onChange={(e) => setQuantity(parseInt(e.target.value) || 1)} fullWidth />
              <TextField label="Location (optional)" value={location} onChange={(e) => setLocation(e.target.value)} fullWidth />
              <TextField label="Promo code (optional)" value={promoCode} onChange={(e) => setPromoCode(e.target.value.toUpperCase())} fullWidth />
              <Button variant="contained" size="large" onClick={runTest} disabled={!productId}>Run test</Button>
              {error && <Alert severity="error">{error}</Alert>}
            </Box>
          </Paper>
        </Grid>

        <Grid item xs={12} md={7}>
          <Paper sx={{ p: 3, borderRadius: 3, minHeight: 400 }}>
            {!result ? (
              <Typography variant="body2" color="text.secondary">Run a test to see matched and non-matched rules with the calculated price.</Typography>
            ) : (
              <Box>
                <Typography variant="subtitle1" sx={{ mb: 1.5 }}>Matched rules</Typography>
                {result.matched_rules.length === 0 ? (
                  <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>No rules matched.</Typography>
                ) : (
                  result.matched_rules.map((r, i) => (
                    <Box key={i} sx={{ display: "flex", justifyContent: "space-between", mb: 1 }}>
                      <Chip size="small" color="success" variant="outlined" label={r.rule_name} />
                      <Typography variant="body2">
                        {r.action_type.replace("_", " ")}: {r.discount_amount > 0 ? `-$${r.discount_amount.toFixed(2)}` : `+$${r.surcharge_amount.toFixed(2)}`}
                      </Typography>
                    </Box>
                  ))
                )}

                <Typography variant="subtitle1" sx={{ mt: 3, mb: 1.5 }}>Non-matched rules</Typography>
                {result.non_matched_rules.length === 0 ? (
                  <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>All active rules matched.</Typography>
                ) : (
                  result.non_matched_rules.map((r, i) => (
                    <Box key={i} sx={{ display: "flex", justifyContent: "space-between", mb: 1 }}>
                      <Chip size="small" variant="outlined" label={r.rule_name} />
                      <Typography variant="body2" color="text.secondary">{r.reason}</Typography>
                    </Box>
                  ))
                )}

                <Divider sx={{ my: 2 }} />
                <Box sx={{ display: "flex", justifyContent: "space-between", alignItems: "baseline" }}>
                  <Typography variant="subtitle1">Final calculated price</Typography>
                  <Typography variant="h4" color="secondary">${result.pricing.final_price.toFixed(2)}</Typography>
                </Box>
              </Box>
            )}
          </Paper>
        </Grid>
      </Grid>
    </AppLayout>
  );
}
