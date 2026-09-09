import React, { useState } from "react";
import Box from "@mui/material/Box";
import Paper from "@mui/material/Paper";
import Typography from "@mui/material/Typography";
import TextField from "@mui/material/TextField";
import Button from "@mui/material/Button";
import Alert from "@mui/material/Alert";
import Link from "@mui/material/Link";
import BoltRoundedIcon from "@mui/icons-material/BoltRounded";
import { Link as RouterLink, useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import { apiErrorMessage } from "../api/client";

export default function Login() {
  const { login } = useAuth();
  const navigate = useNavigate();
  const [email, setEmail] = useState("admin@example.com");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const onSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");
    setLoading(true);
    try {
      await login(email, password);
      navigate("/");
    } catch (err) {
      setError(apiErrorMessage(err));
    } finally {
      setLoading(false);
    }
  };

  return (
    <Box
      sx={{
        minHeight: "100vh",
        display: "grid",
        placeItems: "center",
        backgroundImage: "radial-gradient(circle at 30% 20%, rgba(139,92,246,0.16), transparent 45%)",
      }}
    >
      <Paper sx={{ width: 400, p: 4, borderRadius: 3 }}>
        <Box sx={{ display: "flex", alignItems: "center", gap: 1.2, mb: 3 }}>
          <Box
            sx={{
              width: 36, height: 36, borderRadius: "10px", display: "grid", placeItems: "center",
              backgroundImage: "linear-gradient(135deg, #9C6EF5, #6D28D9)",
            }}
          >
            <BoltRoundedIcon sx={{ color: "#0D0A18" }} />
          </Box>
          <Box>
            <Typography variant="h6" sx={{ lineHeight: 1.1 }}>Pricelogic</Typography>
            <Typography variant="caption" color="text.secondary">Dynamic Pricing Engine</Typography>
          </Box>
        </Box>

        <Typography variant="h5" sx={{ mb: 0.5 }}>Welcome back</Typography>
        <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
          Sign in to manage products, rules and promotions.
        </Typography>

        {error && <Alert severity="error" sx={{ mb: 2 }}>{error}</Alert>}

        <form onSubmit={onSubmit}>
          <TextField label="Email" type="email" fullWidth sx={{ mb: 2 }} value={email} onChange={(e) => setEmail(e.target.value)} required />
          <TextField label="Password" type="password" fullWidth sx={{ mb: 3 }} value={password} onChange={(e) => setPassword(e.target.value)} required />
          <Button type="submit" fullWidth variant="contained" size="large" disabled={loading}>
            {loading ? "Signing in..." : "Sign in"}
          </Button>
        </form>

        <Typography variant="body2" sx={{ mt: 3, textAlign: "center" }} color="text.secondary">
          No account?{" "}
          <Link component={RouterLink} to="/register" color="secondary">
            Create one
          </Link>
        </Typography>
      </Paper>
    </Box>
  );
}
