"use client";

import React, { useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { Shield, Eye, EyeOff, CheckCircle2, AlertCircle } from "lucide-react";
import { useAuth } from "../../lib/auth";

function PasswordStrengthBar({ password }: { password: string }) {
  const checks = [
    { label: "8+ characters", ok: password.length >= 8 },
    { label: "Uppercase letter", ok: /[A-Z]/.test(password) },
    { label: "Number", ok: /[0-9]/.test(password) },
  ];
  const score = checks.filter((c) => c.ok).length;
  const colors = ["var(--rose)", "var(--amber)", "var(--emerald)"];
  const labels = ["Weak", "Fair", "Strong"];

  if (!password) return null;

  return (
    <div style={{ marginTop: 8 }}>
      <div style={{ display: "flex", gap: 4, marginBottom: 8 }}>
        {[0, 1, 2].map((i) => (
          <div key={i} style={{
            flex: 1, height: 3, borderRadius: 2,
            background: i < score ? colors[score - 1] : "var(--border)",
            transition: "background 0.3s",
          }} />
        ))}
      </div>
      <div style={{ display: "flex", gap: 12 }}>
        {checks.map(({ label, ok }) => (
          <span key={label} style={{ display: "flex", alignItems: "center", gap: 4, fontSize: 11, color: ok ? "var(--emerald)" : "var(--text-muted)" }}>
            {ok ? <CheckCircle2 size={10} /> : <AlertCircle size={10} />}
            {label}
          </span>
        ))}
      </div>
    </div>
  );
}

export default function SignupPage() {
  const router = useRouter();
  const { signup } = useAuth();
  const [form, setForm] = useState({ email: "", business_name: "", password: "" });
  const [showPassword, setShowPassword] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setLoading(true);
    const result = await signup(form.email, form.business_name, form.password);
    setLoading(false);
    if (result.success) {
      router.push("/dashboard");
    } else {
      setError(result.error || "Signup failed");
    }
  };

  const set = (field: string) => (e: React.ChangeEvent<HTMLInputElement>) =>
    setForm((f) => ({ ...f, [field]: e.target.value }));

  return (
    <div style={{ display: "flex", minHeight: "100vh", background: "var(--gradient-bg)" }}>
      {/* ── Left Panel ── */}
      <div style={{
        flex: "0 0 45%",
        display: "flex",
        flexDirection: "column",
        alignItems: "center",
        justifyContent: "center",
        padding: "60px",
        background: "linear-gradient(135deg, #060b18 0%, #0a0520 50%, #060b18 100%)",
        position: "relative",
        overflow: "hidden",
      }}>
        <div style={{
          position: "absolute", inset: 0,
          backgroundImage: "radial-gradient(circle at 1px 1px, rgba(59,130,246,0.07) 1px, transparent 0)",
          backgroundSize: "40px 40px",
        }} />
        <div style={{
          position: "absolute", width: 400, height: 400, borderRadius: "50%",
          background: "radial-gradient(circle, rgba(139,92,246,0.12) 0%, transparent 70%)",
          top: "10%", right: "5%",
        }} />

        <div style={{ position: "relative", textAlign: "center", maxWidth: 400 }}>
          <div style={{
            display: "inline-flex", alignItems: "center", justifyContent: "center",
            width: 64, height: 64, borderRadius: 18,
            background: "linear-gradient(135deg, rgba(59,130,246,0.2), rgba(139,92,246,0.2))",
            border: "1px solid rgba(139,92,246,0.3)",
            marginBottom: 20,
          }}>
            <Shield size={30} color="var(--violet)" />
          </div>
          <h1 style={{ fontSize: 36, fontWeight: 800, letterSpacing: "-0.5px", marginBottom: 12 }}>
            <span className="gradient-text">ULTRON</span>
          </h1>
          <p style={{ fontSize: 15, color: "var(--text-secondary)", marginBottom: 40, lineHeight: 1.6 }}>
            Set up your merchant account in under<br />2 minutes and start recovering failed payments.
          </p>

          <div style={{ display: "flex", flexDirection: "column", gap: 16, textAlign: "left" }}>
            {[
              { num: "1", title: "Create your account", desc: "Set up your merchant profile" },
              { num: "2", title: "Connect Razorpay", desc: "Paste your test mode API keys" },
              { num: "3", title: "Go live", desc: "ULTRON starts recovering payments automatically" },
            ].map(({ num, title, desc }) => (
              <div key={num} style={{ display: "flex", gap: 14, alignItems: "flex-start" }}>
                <div style={{
                  width: 28, height: 28, borderRadius: "50%", flexShrink: 0,
                  background: "var(--gradient-brand)",
                  display: "flex", alignItems: "center", justifyContent: "center",
                  fontSize: 12, fontWeight: 700, color: "white",
                }}>
                  {num}
                </div>
                <div>
                  <div style={{ fontSize: 13, fontWeight: 600, marginBottom: 2 }}>{title}</div>
                  <div style={{ fontSize: 12, color: "var(--text-muted)" }}>{desc}</div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* ── Right Panel: Signup Form ── */}
      <div style={{
        flex: 1,
        display: "flex",
        flexDirection: "column",
        alignItems: "center",
        justifyContent: "center",
        padding: "60px 40px",
        background: "var(--bg-card)",
      }}>
        <div className="animate-fade-in" style={{ width: "100%", maxWidth: 400 }}>
          <div style={{ marginBottom: 32 }}>
            <div style={{ display: "flex", alignItems: "center", gap: 8, marginBottom: 20 }}>
              <Shield size={18} color="var(--violet)" />
              <span style={{ fontSize: 13, fontWeight: 600, color: "var(--violet)" }}>ULTRON</span>
            </div>
            <h2 style={{ fontSize: 26, fontWeight: 700, marginBottom: 8 }}>Create your account</h2>
            <p style={{ fontSize: 14, color: "var(--text-secondary)" }}>
              Get autonomous failed-payment recovery running today
            </p>
          </div>

          {error && (
            <div style={{
              padding: "12px 16px", marginBottom: 20, borderRadius: 8,
              background: "rgba(244,63,94,0.1)", border: "1px solid rgba(244,63,94,0.3)",
              color: "var(--rose)", fontSize: 13,
            }}>
              {error}
            </div>
          )}

          <form onSubmit={handleSubmit} style={{ display: "flex", flexDirection: "column", gap: 16 }}>
            <div>
              <label style={{ display: "block", fontSize: 13, fontWeight: 500, marginBottom: 6, color: "var(--text-secondary)" }}>
                Business email
              </label>
              <input
                id="signup-email"
                type="email"
                className="input"
                placeholder="you@company.com"
                value={form.email}
                onChange={set("email")}
                required
                autoComplete="email"
              />
            </div>

            <div>
              <label style={{ display: "block", fontSize: 13, fontWeight: 500, marginBottom: 6, color: "var(--text-secondary)" }}>
                Business name
              </label>
              <input
                id="signup-business-name"
                type="text"
                className="input"
                placeholder="Acme Technologies"
                value={form.business_name}
                onChange={set("business_name")}
                required
                autoComplete="organization"
              />
            </div>

            <div>
              <label style={{ display: "block", fontSize: 13, fontWeight: 500, marginBottom: 6, color: "var(--text-secondary)" }}>
                Password
              </label>
              <div style={{ position: "relative" }}>
                <input
                  id="signup-password"
                  type={showPassword ? "text" : "password"}
                  className="input"
                  placeholder="Create a strong password"
                  value={form.password}
                  onChange={set("password")}
                  required
                  autoComplete="new-password"
                  style={{ paddingRight: 44 }}
                />
                <button
                  type="button"
                  onClick={() => setShowPassword(!showPassword)}
                  style={{
                    position: "absolute", right: 12, top: "50%", transform: "translateY(-50%)",
                    background: "none", border: "none", cursor: "pointer", color: "var(--text-muted)", padding: 2,
                  }}
                  aria-label={showPassword ? "Hide" : "Show"}
                >
                  {showPassword ? <EyeOff size={16} /> : <Eye size={16} />}
                </button>
              </div>
              <PasswordStrengthBar password={form.password} />
            </div>

            <button
              id="signup-submit"
              type="submit"
              className="btn btn-primary"
              disabled={loading}
              style={{ width: "100%", padding: "12px", fontSize: 15, marginTop: 4 }}
            >
              {loading ? (
                <span style={{ display: "flex", alignItems: "center", gap: 8 }}>
                  <span style={{ width: 16, height: 16, border: "2px solid white", borderTopColor: "transparent", borderRadius: "50%", animation: "spin 0.7s linear infinite" }} />
                  Creating account…
                </span>
              ) : "Create merchant account →"}
            </button>
          </form>

          <div style={{ marginTop: 24, textAlign: "center" }}>
            <p style={{ fontSize: 13, color: "var(--text-secondary)" }}>
              Already have an account?{" "}
              <Link href="/login" style={{ color: "var(--electric-blue)", fontWeight: 600, textDecoration: "none" }}>
                Sign in
              </Link>
            </p>
          </div>

          <div style={{ marginTop: 24, paddingTop: 20, borderTop: "1px solid var(--border)" }}>
            <p style={{ fontSize: 11, color: "var(--text-muted)", textAlign: "center", lineHeight: 1.6 }}>
              ULTRON operates in <strong style={{ color: "var(--amber)" }}>Razorpay Test Mode</strong>.<br />
              No real money is charged during testing.
            </p>
          </div>
        </div>
      </div>

      <style>{`@keyframes spin { to { transform: rotate(360deg); } }`}</style>
    </div>
  );
}
