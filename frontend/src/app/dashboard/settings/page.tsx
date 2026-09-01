"use client";

import React, { useState, useEffect } from "react";
import { useAuth, api } from "../../../lib/auth";
import {
  Building2, Shield, Zap, Power, CheckCircle2,
  Copy, Save, RefreshCw, AlertTriangle, Key, Users, Globe, Lock
} from "lucide-react";

export default function GeneralSettingsPage() {
  const { user, tenant, refresh } = useAuth();
  const [businessName, setBusinessName] = useState("");
  const [capacityLimit, setCapacityLimit] = useState(5);
  const [environment, setEnvironment] = useState<"test" | "live">("test");
  const [saving, setSaving] = useState(false);
  const [savedSuccess, setSavedSuccess] = useState(false);
  const [copiedId, setCopiedId] = useState(false);

  useEffect(() => {
    if (tenant) {
      setBusinessName(tenant.name || "");
      setCapacityLimit(tenant.capacity_limit || 5);
      setEnvironment((tenant.environment as "test" | "live") || "test");
    }
  }, [tenant]);

  const handleSave = async (e: React.FormEvent) => {
    e.preventDefault();
    setSaving(true);
    setSavedSuccess(false);

    try {
      await api("/v1/auth/tenant", {
        method: "PATCH",
        body: JSON.stringify({
          name: businessName,
          capacity_limit: capacityLimit,
          environment,
        }),
      });
      await refresh();
      setSavedSuccess(true);
      setTimeout(() => setSavedSuccess(false), 4000);
    } catch (err: any) {
      alert(`Failed to save settings: ${err.message}`);
    } finally {
      setSaving(false);
    }
  };

  const copyTenantId = () => {
    if (tenant?.id) {
      navigator.clipboard.writeText(tenant.id);
      setCopiedId(true);
      setTimeout(() => setCopiedId(false), 2000);
    }
  };

  return (
    <div className="animate-fade-in" style={{ display: "flex", flexDirection: "column", gap: 24, maxWidth: 880 }}>
      {/* Header */}
      <div>
        <h1 style={{ fontSize: 22, fontWeight: 700, marginBottom: 4 }}>General Settings</h1>
        <p style={{ fontSize: 13, color: "var(--text-muted)" }}>
          Manage your organization details, autonomous recovery limits, and environment modes.
        </p>
      </div>

      {savedSuccess && (
        <div style={{
          padding: "14px 18px", borderRadius: 10,
          background: "rgba(16,185,129,0.1)", border: "1px solid rgba(16,185,129,0.3)",
          display: "flex", alignItems: "center", gap: 10, color: "var(--emerald)", fontSize: 13, fontWeight: 500
        }}>
          <CheckCircle2 size={16} /> Organization and recovery settings updated successfully.
        </div>
      )}

      <form onSubmit={handleSave} style={{ display: "flex", flexDirection: "column", gap: 24 }}>
        {/* Organization Card */}
        <div className="card" style={{ padding: 24 }}>
          <div style={{ display: "flex", alignItems: "center", gap: 10, marginBottom: 20 }}>
            <div style={{ width: 32, height: 32, borderRadius: 8, background: "rgba(59,130,246,0.1)", display: "flex", alignItems: "center", justifyContent: "center", color: "var(--electric-blue)" }}>
              <Building2 size={16} />
            </div>
            <div>
              <h2 style={{ fontSize: 15, fontWeight: 600 }}>Organization Profile</h2>
              <p style={{ fontSize: 12, color: "var(--text-muted)" }}>Your merchant tenant identity across the ULTRON control plane.</p>
            </div>
          </div>

          <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 20 }}>
            <div>
              <label style={{ display: "block", fontSize: 12, fontWeight: 500, marginBottom: 6, color: "var(--text-secondary)" }}>
                Business / Merchant Name
              </label>
              <input
                type="text"
                className="input"
                value={businessName}
                onChange={(e) => setBusinessName(e.target.value)}
                placeholder="e.g. Acme Payments Corp"
                required
              />
            </div>

            <div>
              <label style={{ display: "block", fontSize: 12, fontWeight: 500, marginBottom: 6, color: "var(--text-secondary)" }}>
                Tenant Identifier (Isolated ID)
              </label>
              <div style={{ display: "flex", gap: 8 }}>
                <input
                  type="text"
                  className="input"
                  value={tenant?.id || "Loading…"}
                  readOnly
                  style={{ background: "var(--bg-base)", color: "var(--text-muted)", fontFamily: "monospace", fontSize: 12 }}
                />
                <button
                  type="button"
                  className="btn btn-ghost"
                  onClick={copyTenantId}
                  style={{ flexShrink: 0, padding: "0 12px", fontSize: 12 }}
                >
                  {copiedId ? <CheckCircle2 size={14} color="var(--emerald)" /> : <Copy size={14} />}
                </button>
              </div>
            </div>

            <div>
              <label style={{ display: "block", fontSize: 12, fontWeight: 500, marginBottom: 6, color: "var(--text-secondary)" }}>
                Base Currency
              </label>
              <input
                type="text"
                className="input"
                value="INR (₹) - Indian Rupee"
                readOnly
                style={{ background: "var(--bg-base)", color: "var(--text-muted)", fontSize: 12 }}
              />
            </div>

            <div>
              <label style={{ display: "block", fontSize: 12, fontWeight: 500, marginBottom: 6, color: "var(--text-secondary)" }}>
                Environment Mode
              </label>
              <select
                className="input"
                value={environment}
                onChange={(e) => setEnvironment(e.target.value as "test" | "live")}
              >
                <option value="test">Test Mode (Razorpay Sandbox)</option>
                <option value="live">Live Mode (Production Traffic)</option>
              </select>
            </div>
          </div>
        </div>

        {/* Autonomous Recovery Capacity Policy */}
        <div className="card" style={{ padding: 24 }}>
          <div style={{ display: "flex", alignItems: "center", gap: 10, marginBottom: 20 }}>
            <div style={{ width: 32, height: 32, borderRadius: 8, background: "rgba(139,92,246,0.1)", display: "flex", alignItems: "center", justifyContent: "center", color: "var(--violet)" }}>
              <Zap size={16} />
            </div>
            <div>
              <h2 style={{ fontSize: 15, fontWeight: 600 }}>Autonomous Recovery & Capacity Policy</h2>
              <p style={{ fontSize: 12, color: "var(--text-muted)" }}>Control scarce recovery link budget and contact fatigue thresholds.</p>
            </div>
          </div>

          <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 20 }}>
            <div>
              <label style={{ display: "block", fontSize: 12, fontWeight: 500, marginBottom: 6, color: "var(--text-secondary)" }}>
                Max Recovery Links per Batch (Capacity Limit)
              </label>
              <input
                type="number"
                min={1}
                max={50}
                className="input"
                value={capacityLimit}
                onChange={(e) => setCapacityLimit(parseInt(e.target.value, 10) || 5)}
              />
              <div style={{ fontSize: 11, color: "var(--text-muted)", marginTop: 4 }}>
                Enforces scarce allocation. Opportunities above this limit are ranked by shadow price and deferred.
              </div>
            </div>

            <div>
              <label style={{ display: "block", fontSize: 12, fontWeight: 500, marginBottom: 6, color: "var(--text-secondary)" }}>
                AI Decision Engine
              </label>
              <input
                type="text"
                className="input"
                value="NVIDIA Nemotron 30B (Zero Execution Authority)"
                readOnly
                style={{ background: "var(--bg-base)", color: "var(--text-muted)", fontSize: 12 }}
              />
              <div style={{ fontSize: 11, color: "var(--text-muted)", marginTop: 4 }}>
                Strict invariant: LLM only explains decisions and drafts communications; never controls money.
              </div>
            </div>
          </div>
        </div>

        {/* Security & Authentication Overview */}
        <div className="card" style={{ padding: 24 }}>
          <div style={{ display: "flex", alignItems: "center", gap: 10, marginBottom: 20 }}>
            <div style={{ width: 32, height: 32, borderRadius: 8, background: "rgba(16,185,129,0.1)", display: "flex", alignItems: "center", justifyContent: "center", color: "var(--emerald)" }}>
              <Shield size={16} />
            </div>
            <div>
              <h2 style={{ fontSize: 15, fontWeight: 600 }}>Security & Authentication</h2>
              <p style={{ fontSize: 12, color: "var(--text-muted)" }}>Current authenticated session details and cryptographic key storage.</p>
            </div>
          </div>

          <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 20 }}>
            <div style={{ padding: "14px 16px", borderRadius: 8, background: "var(--bg-surface)", border: "1px solid var(--border)" }}>
              <div style={{ fontSize: 11, color: "var(--text-muted)", marginBottom: 4 }}>Signed In As</div>
              <div style={{ fontSize: 14, fontWeight: 600 }}>{user?.email}</div>
              <div style={{ marginTop: 8, display: "flex", gap: 6 }}>
                <span className="badge badge-violet" style={{ fontSize: 10 }}>{user?.role || "Owner"}</span>
                <span className="badge badge-green" style={{ fontSize: 10 }}>Supabase Auth Sync</span>
              </div>
            </div>

            <div style={{ padding: "14px 16px", borderRadius: 8, background: "var(--bg-surface)", border: "1px solid var(--border)" }}>
              <div style={{ fontSize: 11, color: "var(--text-muted)", marginBottom: 4 }}>Credential Encryption</div>
              <div style={{ fontSize: 14, fontWeight: 600 }}>AES-256-GCM Envelope</div>
              <div style={{ fontSize: 12, color: "var(--text-secondary)", marginTop: 4 }}>
                Tenant API secrets and webhook keys are encrypted in-flight and at-rest with zero plaintext leakage.
              </div>
            </div>
          </div>
        </div>

        {/* Actions */}
        <div style={{ display: "flex", justifyContent: "flex-end", gap: 12, marginTop: 4 }}>
          <button
            type="submit"
            className="btn btn-primary"
            disabled={saving}
            style={{ padding: "10px 24px", fontSize: 13, gap: 8 }}
          >
            {saving ? <RefreshCw size={14} style={{ animation: "spin 1s linear infinite" }} /> : <Save size={14} />}
            {saving ? "Saving Changes…" : "Save Organization Settings"}
          </button>
        </div>
      </form>
    </div>
  );
}
