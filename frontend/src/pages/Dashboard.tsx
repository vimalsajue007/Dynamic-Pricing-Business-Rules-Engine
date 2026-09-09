import React, { useEffect, useState } from "react";
import Grid from "@mui/material/Grid";
import Paper from "@mui/material/Paper";
import Box from "@mui/material/Box";
import Typography from "@mui/material/Typography";
import Skeleton from "@mui/material/Skeleton";
import { Line } from "react-chartjs-2";
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Tooltip,
  Filler,
} from "chart.js";
import AppLayout from "../components/Layout/AppLayout";
import { api } from "../api/client";
import type { DashboardSummary } from "../types";
import Inventory2RoundedIcon from "@mui/icons-material/Inventory2Rounded";
import RuleRoundedIcon from "@mui/icons-material/RuleRounded";
import LocalOfferRoundedIcon from "@mui/icons-material/LocalOfferRounded";
import PaidRoundedIcon from "@mui/icons-material/PaidRounded";
import CalculateRoundedIcon from "@mui/icons-material/CalculateRounded";

ChartJS.register(CategoryScale, LinearScale, PointElement, LineElement, Tooltip, Filler);

function StatCard({ label, value, icon }: { label: string; value: string | number; icon: React.ReactNode }) {
  return (
    <Paper sx={{ p: 2.5, borderRadius: 3, height: "100%" }}>
      <Box sx={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start" }}>
        <Box>
          <Typography variant="body2" color="text.secondary">{label}</Typography>
          <Typography variant="h4" sx={{ mt: 0.5 }}>{value}</Typography>
        </Box>
        <Box
          sx={{
            width: 40, height: 40, borderRadius: "10px", display: "grid", placeItems: "center",
            backgroundColor: "rgba(139,92,246,0.14)", color: "#B594FA",
          }}
        >
          {icon}
        </Box>
      </Box>
    </Paper>
  );
}

export default function Dashboard() {
  const [data, setData] = useState<DashboardSummary | null>(null);

  useEffect(() => {
    api.get("/dashboard/summary").then((res) => setData(res.data.data));
  }, []);

  return (
    <AppLayout title="Dashboard">
      {!data ? (
        <Grid container spacing={2.5}>
          {[1, 2, 3, 4, 5].map((i) => (
            <Grid item xs={12} sm={6} md={4} lg={2.4} key={i}>
              <Skeleton variant="rounded" height={110} sx={{ borderRadius: 3 }} />
            </Grid>
          ))}
        </Grid>
      ) : (
        <>
          <Grid container spacing={2.5} sx={{ mb: 3 }}>
            <Grid item xs={12} sm={6} md={4} lg={2.4}>
              <StatCard label="Total Products" value={data.total_products} icon={<Inventory2RoundedIcon />} />
            </Grid>
            <Grid item xs={12} sm={6} md={4} lg={2.4}>
              <StatCard label="Active Pricing Rules" value={data.active_pricing_rules} icon={<RuleRoundedIcon />} />
            </Grid>
            <Grid item xs={12} sm={6} md={4} lg={2.4}>
              <StatCard label="Active Promotions" value={data.active_promotions} icon={<LocalOfferRoundedIcon />} />
            </Grid>
            <Grid item xs={12} sm={6} md={4} lg={2.4}>
              <StatCard label="Total Discounts Given" value={`$${data.total_discounts_given.toFixed(2)}`} icon={<PaidRoundedIcon />} />
            </Grid>
            <Grid item xs={12} sm={6} md={4} lg={2.4}>
              <StatCard label="Calculations Run" value={data.pricing_calculation_count} icon={<CalculateRoundedIcon />} />
            </Grid>
          </Grid>

          <Grid container spacing={2.5}>
            <Grid item xs={12} md={8}>
              <Paper sx={{ p: 3, borderRadius: 3 }}>
                <Typography variant="subtitle1" sx={{ mb: 2 }}>Pricing activity, last 14 days</Typography>
                <Box sx={{ height: 280 }}>
                  <Line
                    data={{
                      labels: data.pricing_activity_trend.map((t) => t.date.slice(5)),
                      datasets: [
                        {
                          label: "Calculations",
                          data: data.pricing_activity_trend.map((t) => t.count),
                          borderColor: "#9C6EF5",
                          backgroundColor: "rgba(139,92,246,0.18)",
                          fill: true,
                          tension: 0.35,
                          pointRadius: 0,
                        },
                      ],
                    }}
                    options={{
                      responsive: true,
                      maintainAspectRatio: false,
                      plugins: { legend: { display: false } },
                      scales: {
                        x: { grid: { color: "#2A2246" }, ticks: { color: "#A99FCB" } },
                        y: { grid: { color: "#2A2246" }, ticks: { color: "#A99FCB" }, beginAtZero: true },
                      },
                    }}
                  />
                </Box>
              </Paper>
            </Grid>
            <Grid item xs={12} md={4}>
              <Paper sx={{ p: 3, borderRadius: 3, height: "100%" }}>
                <Typography variant="subtitle1" sx={{ mb: 2 }}>Most applied rules</Typography>
                {data.most_applied_rules.length === 0 ? (
                  <Typography variant="body2" color="text.secondary">No rules have fired yet.</Typography>
                ) : (
                  data.most_applied_rules.map((r, i) => (
                    <Box key={i} sx={{ display: "flex", justifyContent: "space-between", py: 1, borderBottom: i < data.most_applied_rules.length - 1 ? "1px solid #2A2246" : "none" }}>
                      <Typography variant="body2">{r.rule_name}</Typography>
                      <Typography variant="body2" color="secondary" fontWeight={600}>{r.times_applied}×</Typography>
                    </Box>
                  ))
                )}
              </Paper>
            </Grid>
          </Grid>
        </>
      )}
    </AppLayout>
  );
}
