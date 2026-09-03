"use client";

import React, { useState, useEffect } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { Shield, Eye, EyeOff, Zap, TrendingUp, Lock, Sparkles } from "lucide-react";
import { useAuth } from "../../lib/auth";

export default function LoginPage() {
  const router = useRouter();
  const { login, loginAsDemo, token, loading: authLoading } = useAuth();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [showPassword, setShowPassword] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Auto-redirect to dashboard if session token already exists
  useEffect(() => {
    if (token && !authLoading) {
      router.replace("/dashboard");
    }
  }, [token, authLoading, router]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setLoading(true);
    const result = await login(email, password);
    setLoading(false);
    if (result.success) {
      router.push("/dashboard");
    } else {
      setError(result.error || "Login failed");
    }
  };

  const handleDemoLogin = async () => {
    setError(null);
    setLoading(true);
    const result = await loginAsDemo();
    setLoading(false);
    if (result.success) {
      router.push("/dashboard");
    } else {
      setError(result.error || "Demo login failed");
    }
  };

  const handlePrefillDemo = () => {
    setEmail("demo@ultron.app");
    setPassword("Ultron@2026");
  };

  return (
    <div style={{ display: "flex", minHeight: "100vh", background: "var(--gradient-bg)" }}>
      {/* ── Left Panel: Brand ── */}
      <div
        style={{
          flex: "0 0 55%",
          display: "flex",
          flexDirection: "column",
          alignItems: "center",
          justifyContent: "center",
          padding: "60px",
          background: "linear-gradient(135deg, #060b18 0%, #0a0520 50%, #060b18 100%)",
          position: "relative",
          overflow: "hidden",
        }}
      >
        {/* Animated grid background */}
        <div style={{
          position: "absolute", inset: 0,
          backgroundImage: "radial-gradient(circle at 1px 1px, rgba(59,130,246,0.08) 1px, transparent 0)",
          backgroundSize: "40px 40px",
        }} />

        {/* Glow orbs */}
        <div style={{
          position: "absolute", width: 400, height: 400, borderRadius: "50%",
          background: "radial-gradient(circle, rgba(59,130,246,0.12) 0%, transparent 70%)",
          top: "20%", left: "10%",
        }} />
        <div style={{
          position: "absolute", width: 300, height: 300, borderRadius: "50%",
          background: "radial-gradient(circle, rgba(139,92,246,0.10) 0%, transparent 70%)",
          bottom: "20%", right: "15%",
        }} />

        {/* Content */}
        <div style={{ position: "relative", textAlign: "center", maxWidth: 440 }}>
          {/* Logo */}
          <div style={{
            display: "inline-flex", alignItems: "center", justifyContent: "center",
            width: 72, height: 72, borderRadius: 20,
            background: "linear-gradient(135deg, rgba(59,130,246,0.2), rgba(139,92,246,0.2))",
            border: "1px solid rgba(59,130,246,0.3)",
            marginBottom: 24,
            boxShadow: "0 0 30px rgba(59,130,246,0.2)",
          }}>
            <Shield size={36} color="#3b82f6" />
          </div>

          <h1 style={{ fontSize: 42, fontWeight: 800, letterSpacing: "-1px", marginBottom: 12 }}>
            <span className="gradient-text">ULTRON</span>
          </h1>
          <p style={{ fontSize: 16, color: "var(--text-secondary)", marginBottom: 48, lineHeight: 1.6 }}>
            Autonomous economic control plane for<br />failed-payment recovery on Razorpay
          </p>

          {/* Stats card */}
          <div className="glass animate-float" style={{
            borderRadius: 16, padding: "24px 32px",
            border: "1px solid rgba(59,130,246,0.2)",
            boxShadow: "0 0 40px rgba(59,130,246,0.1)",
          }}>
            <p style={{ fontSize: 11, color: "var(--text-muted)", textTransform: "uppercase", letterSpacing: "1px", marginBottom: 16 }}>
              Platform Recovery Stats (model-estimated)
            </p>
            <div style={{ display: "flex", gap: 32, justifyContent: "center" }}>
              <div>
                <div style={{ display: "flex", alignItems: "center", gap: 6, marginBottom: 4 }}>
                  <TrendingUp size={14} color="var(--emerald)" />
                  <span style={{ fontSize: 26, fontWeight: 800, color: "var(--text-primary)" }}>₹2.4Cr</span>
                </div>
                <p style={{ fontSize: 11, color: "var(--text-muted)" }}>Recovered this month</p>
              </div>
              <div style={{ width: 1, background: "var(--border)" }} />
              <div>
                <div style={{ display: "flex", alignItems: "center", gap: 6, marginBottom: 4 }}>
                  <Zap size={14} color="var(--electric-blue)" />
                  <span style={{ fontSize: 26, fontWeight: 800, color: "var(--text-primary)" }}>94.3%</span>
                </div>
                <p style={{ fontSize: 11, color: "var(--text-muted)" }}>Recovery rate</p>
              </div>
            </div>
          </div>

          {/* Features */}
          <div style={{ marginTop: 40, display: "flex", flexDirection: "column", gap: 12, textAlign: "left" }}>
            {[
              { icon: "🧮", text: "Incremental IVEN scoring — not raw probability" },
              { icon: "🏛️", text: "Portfolio-level allocation with shadow price" },
              { icon: "🛡️", text: "2-stage compliance gate before any execution" },
            ].map(({ icon, text }) => (
              <div key={text} style={{ display: "flex", alignItems: "center", gap: 12 }}>
                <span style={{ fontSize: 18 }}>{icon}</span>
                <span style={{ fontSize: 13, color: "var(--text-secondary)" }}>{text}</span>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* ── Right Panel: Login Form ── */}
      <div style={{
        flex: 1,
        display: "flex",
        flexDirection: "column",
        alignItems: "center",
        justifyContent: "center",
        padding: "60px 40px",
        background: "var(--bg-card)",
      }}>
        <div className="animate-fade-in" style={{ width: "100%", maxWidth: 380 }}>
          {/* Header */}
          <div style={{ marginBottom: 36 }}>
            <div style={{ display: "flex", alignItems: "center", gap: 8, marginBottom: 20 }}>
              <Shield size={20} color="var(--electric-blue)" />
              <span style={{ fontSize: 13, fontWeight: 600, color: "var(--electric-blue)" }}>ULTRON</span>
            </div>
            <h2 style={{ fontSize: 26, fontWeight: 700, marginBottom: 8 }}>Welcome back</h2>
            <p style={{ fontSize: 14, color: "var(--text-secondary)" }}>
              Sign in to your merchant control plane
            </p>
          </div>

          {/* Error */}
          {error && (
            <div style={{
              padding: "12px 16px", marginBottom: 20, borderRadius: 8,
              background: "rgba(244,63,94,0.1)", border: "1px solid rgba(244,63,94,0.3)",
              color: "var(--rose)", fontSize: 13,
            }}>
              {error}
            </div>
          )}

          {/* 1-Click Demo Access Button */}
          <button
            type="button"
            onClick={handleDemoLogin}
            disabled={loading}
            className="btn btn-secondary"
            style={{
              width: "100%", padding: "12px 16px", fontSize: 14, fontWeight: 700,
              marginBottom: 20, display: "flex", alignItems: "center", justifyContent: "center", gap: 10,
              border: "1px solid rgba(59,130,246,0.4)", background: "linear-gradient(135deg, rgba(59,130,246,0.12), rgba(139,92,246,0.12))",
              color: "#60a5fa", cursor: "pointer", borderRadius: 8,
              boxShadow: "0 2px 10px rgba(59,130,246,0.15)",
              transition: "all 0.2s ease"
            }}
          >
            <Sparkles size={16} color="#60a5fa" />
            <span>🚀 1-Click Instant Demo Login</span>
          </button>

          <div style={{ display: "flex", alignItems: "center", gap: 12, marginBottom: 20 }}>
            <div style={{ flex: 1, height: 1, background: "var(--border)" }} />
            <span style={{ fontSize: 11, color: "var(--text-muted)", textTransform: "uppercase", letterSpacing: 0.5 }}>or sign in with password</span>
            <div style={{ flex: 1, height: 1, background: "var(--border)" }} />
          </div>

          {/* Form */}
          <form onSubmit={handleSubmit} style={{ display: "flex", flexDirection: "column", gap: 16 }}>
            <div>
              <label style={{ display: "block", fontSize: 13, fontWeight: 500, marginBottom: 6, color: "var(--text-secondary)" }}>
                Email address
              </label>
              <input
                id="login-email"
                type="email"
                className="input"
                placeholder="merchant@company.com"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                required
                autoComplete="email"
              />
            </div>

            <div>
              <label style={{ display: "block", fontSize: 13, fontWeight: 500, marginBottom: 6, color: "var(--text-secondary)" }}>
                Password
              </label>
              <div style={{ position: "relative" }}>
                <input
                  id="login-password"
                  type={showPassword ? "text" : "password"}
                  className="input"
                  placeholder="••••••••"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  required
                  autoComplete="current-password"
                  style={{ paddingRight: 44 }}
                />
                <button
                  type="button"
                  onClick={() => setShowPassword(!showPassword)}
                  style={{
                    position: "absolute", right: 12, top: "50%", transform: "translateY(-50%)",
                    background: "none", border: "none", cursor: "pointer", color: "var(--text-muted)",
                    padding: 2,
                  }}
                  aria-label={showPassword ? "Hide password" : "Show password"}
                >
                  {showPassword ? <EyeOff size={16} /> : <Eye size={16} />}
                </button>
              </div>
            </div>

            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", fontSize: 12, marginTop: -4 }}>
              <span style={{ color: "var(--text-muted)" }}>Demo: <code style={{ color: "var(--text-secondary)" }}>demo@ultron.app</code></span>
              <button
                type="button"
                onClick={handlePrefillDemo}
                style={{
                  background: "none", border: "none", color: "var(--electric-blue)",
                  cursor: "pointer", fontSize: 12, fontWeight: 600, padding: 0
                }}
              >
                Auto-fill credentials
              </button>
            </div>

            <button
              id="login-submit"
              type="submit"
              className="btn btn-primary"
              disabled={loading}
              style={{ width: "100%", padding: "12px", fontSize: 15, marginTop: 4 }}
            >
              {loading ? (
                <span style={{ display: "flex", alignItems: "center", gap: 8 }}>
                  <span style={{ width: 16, height: 16, border: "2px solid white", borderTopColor: "transparent", borderRadius: "50%", animation: "spin 0.7s linear infinite" }} />
                  Signing in…
                </span>
              ) : (
                <>
                  <Lock size={15} />
                  Sign in
                </>
              )}
            </button>
          </form>

          {/* Footer */}
          <div style={{ marginTop: 28, textAlign: "center" }}>
            <p style={{ fontSize: 13, color: "var(--text-secondary)" }}>
              New to ULTRON?{" "}
              <Link href="/signup" style={{ color: "var(--electric-blue)", fontWeight: 600, textDecoration: "none" }}>
                Create account
              </Link>
            </p>
          </div>

          <div style={{ marginTop: 32, paddingTop: 24, borderTop: "1px solid var(--border)" }}>
            <p style={{ fontSize: 11, color: "var(--text-muted)", textAlign: "center", lineHeight: 1.6 }}>
              ULTRON operates in <strong style={{ color: "var(--amber)" }}>Razorpay Test Mode</strong> only.<br />
              All recovery statistics are <strong>model-estimated</strong>, not measured fact.
            </p>
          </div>
        </div>
      </div>

      <style>{`
        @keyframes spin { to { transform: rotate(360deg); } }
        @media (max-width: 768px) {
          .auth-left { display: none !important; }
        }
      `}</style>
    </div>
  );
}
