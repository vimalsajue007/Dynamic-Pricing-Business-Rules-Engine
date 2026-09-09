import React, { useState } from "react";
import Box from "@mui/material/Box";
import Paper from "@mui/material/Paper";
import Typography from "@mui/material/Typography";
import TextField from "@mui/material/TextField";
import Button from "@mui/material/Button";
import Alert from "@mui/material/Alert";
import Link from "@mui/material/Link";
import { Link as RouterLink, useNavigate } from "react-router-dom";
import { useAuth } from "../context/AuthContext";
import { apiErrorMessage } from "../api/client";

export default function Register() {
  const { register } = useAuth();
  const navigate = useNavigate();
  const [fullName, setFullName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const onSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");
    setLoading(true);
    try {
      await register(fullName, email, password);
      navigate("/");
    } catch (err) {
      setError(apiErrorMessage(err));
    } finally {
      setLoading(false);
    }
  };

  return (
    <Box sx={{ minHeight: "100vh", display: "grid", placeItems: "center" }}>
      <Paper sx={{ width: 400, p: 4, borderRadius: 3 }}>
        <Typography variant="h5" sx={{ mb: 0.5 }}>Create your account</Typography>
        <Typography variant="body2" color="text.secondary" sx={{ mb: 3 }}>
          The first registered account becomes an administrator automatically.
        </Typography>
        {error && <Alert severity="error" sx={{ mb: 2 }}>{error}</Alert>}
        <form onSubmit={onSubmit}>
          <TextField label="Full name" fullWidth sx={{ mb: 2 }} value={fullName} onChange={(e) => setFullName(e.target.value)} required />
          <TextField label="Email" type="email" fullWidth sx={{ mb: 2 }} value={email} onChange={(e) => setEmail(e.target.value)} required />
          <TextField label="Password" type="password" helperText="At least 8 characters" fullWidth sx={{ mb: 3 }} value={password} onChange={(e) => setPassword(e.target.value)} required />
          <Button type="submit" fullWidth variant="contained" size="large" disabled={loading}>
            {loading ? "Creating..." : "Create account"}
          </Button>
        </form>
        <Typography variant="body2" sx={{ mt: 3, textAlign: "center" }} color="text.secondary">
          Already have an account?{" "}
          <Link component={RouterLink} to="/login" color="secondary">Sign in</Link>
        </Typography>
      </Paper>
    </Box>
  );
}
