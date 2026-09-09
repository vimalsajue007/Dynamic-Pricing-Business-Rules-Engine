import React from "react";
import { Routes, Route } from "react-router-dom";
import Login from "./pages/Login";
import Register from "./pages/Register";
import Dashboard from "./pages/Dashboard";
import Products from "./pages/Products";
import Customers from "./pages/Customers";
import PricingRules from "./pages/PricingRules";
import Promotions from "./pages/Promotions";
import PricingPreview from "./pages/PricingPreview";
import RuleTesting from "./pages/RuleTesting";
import PricingHistory from "./pages/PricingHistory";
import ProtectedRoute from "./components/ProtectedRoute";
import Users from "./pages/Users";

export default function App() {
  return (
    <Routes>
      <Route path="/login" element={<Login />} />
      <Route path="/register" element={<Register />} />
      <Route path="/" element={<ProtectedRoute><Dashboard /></ProtectedRoute>} />
      <Route path="/products" element={<ProtectedRoute><Products /></ProtectedRoute>} />
      <Route path="/customers" element={<ProtectedRoute><Customers /></ProtectedRoute>} />
      <Route path="/rules" element={<ProtectedRoute><PricingRules /></ProtectedRoute>} />
      <Route path="/promotions" element={<ProtectedRoute><Promotions /></ProtectedRoute>} />
      <Route path="/preview" element={<ProtectedRoute><PricingPreview /></ProtectedRoute>} />
      <Route path="/testing" element={<ProtectedRoute><RuleTesting /></ProtectedRoute>} />
      <Route path="/history" element={<ProtectedRoute><PricingHistory /></ProtectedRoute>} />
      <Route path="/users" element={<ProtectedRoute adminOnly><Users /></ProtectedRoute>} />
    </Routes>
  );
}
