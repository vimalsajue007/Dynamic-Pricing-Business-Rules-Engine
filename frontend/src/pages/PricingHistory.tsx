import React, { useEffect, useState } from "react";
import AppLayout from "../components/Layout/AppLayout";
import Paper from "@mui/material/Paper";
import Table from "@mui/material/Table";
import TableHead from "@mui/material/TableHead";
import TableRow from "@mui/material/TableRow";
import TableCell from "@mui/material/TableCell";
import TableBody from "@mui/material/TableBody";
import Chip from "@mui/material/Chip";
import Box from "@mui/material/Box";
import Pagination from "@mui/material/Pagination";
import { api } from "../api/client";
import type { PricingHistoryItem } from "../types";

export default function PricingHistory() {
  const [items, setItems] = useState<PricingHistoryItem[]>([]);
  const [page, setPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);

  useEffect(() => {
    api.get("/pricing/history", { params: { page, page_size: 15 } }).then((r) => {
      setItems(r.data.data.items);
      setTotalPages(r.data.data.total_pages);
    });
  }, [page]);

  return (
    <AppLayout title="Pricing History">
      <Paper sx={{ p: 3, borderRadius: 3 }}>
        <Table>
          <TableHead>
            <TableRow>
              <TableCell>When</TableCell><TableCell>Product</TableCell><TableCell>Promo</TableCell>
              <TableCell align="right">Original</TableCell><TableCell align="right">Discount</TableCell>
              <TableCell align="right">Tax</TableCell><TableCell align="right">Final</TableCell>
            </TableRow>
          </TableHead>
          <TableBody>
            {items.map((h) => (
              <TableRow key={h.id} hover>
                <TableCell>{new Date(h.calculation_time).toLocaleString()}</TableCell>
                <TableCell>#{h.product_id}</TableCell>
                <TableCell>{h.promo_code ? <Chip size="small" label={h.promo_code} /> : "—"}</TableCell>
                <TableCell align="right">${Number(h.original_price).toFixed(2)}</TableCell>
                <TableCell align="right" sx={{ color: "#34D399" }}>-${Number(h.discount_amount).toFixed(2)}</TableCell>
                <TableCell align="right">${Number(h.tax_amount).toFixed(2)}</TableCell>
                <TableCell align="right"><strong>${Number(h.final_price).toFixed(2)}</strong></TableCell>
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
