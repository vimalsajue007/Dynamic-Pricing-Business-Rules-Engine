import React, { useEffect, useState } from "react";
import AppLayout from "../components/Layout/AppLayout";
import Grid from "@mui/material/Grid";
import Paper from "@mui/material/Paper";
import Box from "@mui/material/Box";
import TextField from "@mui/material/TextField";
import MenuItem from "@mui/material/MenuItem";
import Button from "@mui/material/Button";
import Typography from "@mui/material/Typography";
import Divider from "@mui/material/Divider";
import Chip from "@mui/material/Chip";
import Alert from "@mui/material/Alert";
import { api, apiErrorMessage } from "../api/client";
import type { Product, Customer, PricingResult } from "../types";

export default function PricingPreview() {
  const [products, setProducts] = useState<Product[]>([]);
  const [customers, setCustomers] = useState<Customer[]>([]);
  const [productId, setProductId] = useState("");
  const [customerId, setCustomerId] = useState("");
  const [quantity, setQuantity] = useState(1);
  const [location, setLocation] = useState("");
  const [promoCode, setPromoCode] = useState("");
  const [result, setResult] = useState<PricingResult | null>(null);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    api.get("/products", { params: { page_size: 100, is_active: true } }).then((r) => setProducts(r.data.data.items));
    api.get("/customers", { params: { page_size: 100 } }).then((r) => setCustomers(r.data.data.items));
  }, []);

  const calculate = async () => {
    setError(""); setResult(null); setLoading(true);
    try {
      const { data } = await api.post("/pricing/preview", {
        product_id: parseInt(productId),
        customer_id: customerId ? parseInt(customerId) : null,
        quantity,
        location: location || null,
        promo_code: promoCode || null,
      });
      setResult(data.data);
    } catch (e) {
      setError(apiErrorMessage(e));
    } finally {
      setLoading(false);
    }
  };

  return (
    <AppLayout title="Pricing Preview">
      <Grid container spacing={3}>
        <Grid item xs={12} md={5}>
          <Paper sx={{ p: 3, borderRadius: 3 }}>
            <Typography variant="subtitle1" sx={{ mb: 2 }}>Inputs</Typography>
            <Box sx={{ display: "flex", flexDirection: "column", gap: 2 }}>
              <TextField select label="Product" value={productId} onChange={(e) => setProductId(e.target.value)} fullWidth required>
                {products.map((p) => <MenuItem key={p.id} value={p.id}>{p.name} — ${Number(p.base_price).toFixed(2)}</MenuItem>)}
              </TextField>
              <TextField select label="Customer (optional)" value={customerId} onChange={(e) => setCustomerId(e.target.value)} fullWidth>
                <MenuItem value="">Walk-in / guest</MenuItem>
                {customers.map((c) => <MenuItem key={c.id} value={c.id}>{c.name} ({c.customer_type})</MenuItem>)}
              </TextField>
              <TextField label="Quantity" type="number" value={quantity} onChange={(e) => setQuantity(parseInt(e.target.value) || 1)} fullWidth />
              <TextField label="Location (optional)" value={location} onChange={(e) => setLocation(e.target.value)} fullWidth />
              <TextField label="Promo code (optional)" value={promoCode} onChange={(e) => setPromoCode(e.target.value.toUpperCase())} fullWidth />
              <Button variant="contained" size="large" onClick={calculate} disabled={!productId || loading}>
                {loading ? "Calculating..." : "Calculate price"}
              </Button>
              {error && <Alert severity="error">{error}</Alert>}
            </Box>
          </Paper>
        </Grid>

        <Grid item xs={12} md={7}>
          <Paper sx={{ p: 3, borderRadius: 3, minHeight: 400 }}>
            <Typography variant="subtitle1" sx={{ mb: 2 }}>Result</Typography>
            {!result ? (
              <Typography variant="body2" color="text.secondary">Fill in the inputs and calculate to see the full price breakdown.</Typography>
            ) : (
              <Box>
                <Box sx={{ display: "flex", justifyContent: "space-between", mb: 1 }}>
                  <Typography variant="body2" color="text.secondary">Base price × quantity</Typography>
                  <Typography variant="body2">${result.subtotal.toFixed(2)}</Typography>
                </Box>

                {result.applied_rules.map((r, i) => (
                  <Box key={i} sx={{ display: "flex", justifyContent: "space-between", mb: 1 }}>
                    <Typography variant="body2" color="text.secondary">
                      Rule: {r.rule_name} {!r.stacked && <Chip size="small" label="exclusive" sx={{ ml: 1 }} />}
                    </Typography>
                    <Typography variant="body2" color={r.discount_amount > 0 ? "success.main" : "warning.main"}>
                      {r.discount_amount > 0 ? `- $${r.discount_amount.toFixed(2)}` : `+ $${r.surcharge_amount.toFixed(2)}`}
                    </Typography>
                  </Box>
                ))}

                {result.promotion && (
                  <Box sx={{ display: "flex", justifyContent: "space-between", mb: 1 }}>
                    <Typography variant="body2" color="text.secondary">
                      Promo {result.promotion.code} {!result.promotion.valid && `(${result.promotion.message})`}
                    </Typography>
                    <Typography variant="body2" color="success.main">
                      {result.promotion.valid ? `- $${result.promotion_discount.toFixed(2)}` : "not applied"}
                    </Typography>
                  </Box>
                )}

                <Box sx={{ display: "flex", justifyContent: "space-between", mb: 1 }}>
                  <Typography variant="body2" color="text.secondary">Taxable amount</Typography>
                  <Typography variant="body2">${result.taxable_amount.toFixed(2)}</Typography>
                </Box>
                <Box sx={{ display: "flex", justifyContent: "space-between", mb: 2 }}>
                  <Typography variant="body2" color="text.secondary">Tax ({result.tax_rate_percent}%)</Typography>
                  <Typography variant="body2">${result.tax_amount.toFixed(2)}</Typography>
                </Box>

                <Divider sx={{ mb: 2 }} />
                <Box sx={{ display: "flex", justifyContent: "space-between", alignItems: "baseline" }}>
                  <Typography variant="subtitle1">Final price</Typography>
                  <Typography variant="h4" color="secondary">${result.final_price.toFixed(2)}</Typography>
                </Box>
              </Box>
            )}
          </Paper>
        </Grid>
      </Grid>
    </AppLayout>
  );
}
