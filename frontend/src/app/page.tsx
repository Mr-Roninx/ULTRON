"use client";

import React, { useState, useEffect, useCallback } from "react";
import {
  Shield,
  Zap,
  Activity,
  AlertTriangle,
  CheckCircle2,
  XCircle,
  Clock,
  ExternalLink,
  RefreshCw,
  Power,
  Flame,
  FileText,
  DollarSign,
  TrendingUp,
  Layers,
  ChevronRight,
  Sparkles,
  Search,
  Filter,
  Check,
  X,
  CreditCard,
} from "lucide-react";

interface SummaryData {
  total_opportunities: number;
  total_at_risk_display: string;
  total_recovered_display: string;
  real_recovered_count: number;
  synthetic_recovered_count: number;
  shadow_price_display: string;
  capacity_limit: number;
  capacity_used: number;
  capacity_available: number;
  kill_switch_active: boolean;
  status_counts: Record<string, number>;
  total_execution_records: number;
}

interface OpportunityItem {
  id: string;
  source: "real" | "synthetic";
  amount_paise: number;
  currency: string;
  reason_code: string;
  decline_type: "hard" | "soft" | "unknown";
  attempt_count: number;
  customer_id: string;
  customer_trust_score: number;
  created_at: string;
  status: string;
  raw_payload_ref?: string;
  score?: {
    natural_recovery_prob: number;
    intervention_recovery_prob: number;
    incremental_prob: number;
    operational_cost_paise: number;
    fatigue_cost_paise: number;
    expected_incremental_value_paise: number;
    confidence: "low" | "medium" | "high";
  };
  decision?: {
    decision: "ACT" | "WAIT" | "ABSTAIN";
    rank_in_batch: number;
    shadow_price_paise_at_decision: number;
    reason: string;
  };
  execution_record?: {
    razorpay_payment_link_id: string;
    link_url: string;
    status: string;
    created_at: string;
  };
  authority_checks?: Array<{
    check_name: string;
    passed: boolean;
    reason: string;
  }>;
}

interface OpportunityDetails {
  opportunity: OpportunityItem;
  score?: OpportunityItem["score"];
  decision?: OpportunityItem["decision"];
  authority_checks?: OpportunityItem["authority_checks"];
  customer?: {
    id: string;
    trust_score: number;
    created_at: string;
  };
  ledger?: Array<{
    id: string;
    event_type: string;
    amount_paise: number;
    timestamp: string;
    raw_payload_ref: string | null;
  }>;
}

const API_BASE = "http://localhost:3001";

export default function UltronDashboard() {
  const [summary, setSummary] = useState<SummaryData | null>(null);
  const [opportunities, setOpportunities] = useState<OpportunityItem[]>([]);
  const [selectedOppId, setSelectedOppId] = useState<string | null>(null);
  const [selectedDetails, setSelectedDetails] = useState<OpportunityDetails | null>(null);
  const [loading, setLoading] = useState(true);
  const [actionLoading, setActionLoading] = useState<string | null>(null);
  const [filterSource, setFilterSource] = useState<"all" | "real" | "synthetic">("all");
  const [filterStatus, setFilterStatus] = useState<string>("all");
  const [searchTerm, setSearchTerm] = useState("");

  const fetchData = useCallback(async () => {
    try {
      const [sumRes, oppsRes, decisionsRes, execRes] = await Promise.all([
        fetch(`${API_BASE}/dashboard/summary`),
        fetch(`${API_BASE}/opportunities`),
        fetch(`${API_BASE}/market/decisions`),
        fetch(`${API_BASE}/execution/records`),
      ]);

      const sumData = await sumRes.json();
      const oppsData = await oppsRes.json();
      const decData = await decisionsRes.json();
      const execData = await execRes.json();

      setSummary(sumData);

      const decMap = new Map(
        (decData.decisions || []).map((d: any) => [d.opportunity_id, d])
      );
      const execMap = new Map(
        (execData.records || []).map((r: any) => [r.opportunity_id, r])
      );

      // Fetch full scores in batch
      const enrichedOpps: OpportunityItem[] = await Promise.all(
        (oppsData.opportunities || []).map(async (opp: OpportunityItem) => {
          let score = opp.score;
          try {
            const scRes = await fetch(`${API_BASE}/opportunities/${opp.id}/score`);
            if (scRes.ok) {
              const scData = await scRes.json();
              score = scData;
            }
          } catch (e) {
            // ignore
          }

          return {
            ...opp,
            score,
            decision: decMap.get(opp.id),
            execution_record: execMap.get(opp.id),
          };
        })
      );

      setOpportunities(enrichedOpps);
      setLoading(false);
    } catch (err) {
      console.error("Failed to fetch ULTRON dashboard data:", err);
      setLoading(false);
    }
  }, []);

  // Poll every 3 seconds for live truth updates
  useEffect(() => {
    fetchData();
    const interval = setInterval(fetchData, 3000);
    return () => clearInterval(interval);
  }, [fetchData]);

  // Load details when an opportunity is selected for the "Why?" forensic drawer
  useEffect(() => {
    if (!selectedOppId) {
      setSelectedDetails(null);
      return;
    }

    async function loadDetails() {
      try {
        const [oppRes, authRes] = await Promise.all([
          fetch(`${API_BASE}/opportunities/${selectedOppId}`),
          fetch(`${API_BASE}/opportunities/${selectedOppId}/authority`),
        ]);
        const oppData = await oppRes.json();
        const authData = await authRes.json();

        setSelectedDetails({
          ...oppData,
          authority_checks: authData.checklist || oppData.authority_checks,
        });
      } catch (err) {
        console.error("Failed to fetch opportunity details:", err);
      }
    }

    loadDetails();
  }, [selectedOppId]);

  // Handler: Toggle Kill Switch
  const toggleKillSwitch = async () => {
    if (!summary) return;
    setActionLoading("kill-switch");
    try {
      await fetch(`${API_BASE}/authority/kill-switch`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ enabled: !summary.kill_switch_active }),
      });
      await fetchData();
    } catch (e) {
      console.error(e);
    } finally {
      setActionLoading(null);
    }
  };

  // Handler: Run Market Allocation & Authority Pipeline
  const runPipeline = async () => {
    setActionLoading("pipeline");
    try {
      await fetch(`${API_BASE}/authority/run`, { method: "POST" });
      await fetchData();
    } catch (e) {
      console.error(e);
    } finally {
      setActionLoading(null);
    }
  };

  // Handler: Execute Authorized Batch
  const runExecution = async () => {
    setActionLoading("execution");
    try {
      await fetch(`${API_BASE}/execution/run`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ maxLinks: 5 }),
      });
      await fetchData();
    } catch (e) {
      console.error(e);
    } finally {
      setActionLoading(null);
    }
  };

  // Handler: Poll Reconciliation (Active Truth Engine Poller)
  const runPoller = async () => {
    setActionLoading("poller");
    try {
      await fetch(`${API_BASE}/dashboard/reconcile-poll`, { method: "POST" });
      await fetchData();
    } catch (e) {
      console.error(e);
    } finally {
      setActionLoading(null);
    }
  };

  // Handler: Seed Synthetic Universe
  const reseedData = async () => {
    setActionLoading("seed");
    try {
      await fetch(`${API_BASE}/opportunities/score-all`, { method: "POST" });
      await fetchData();
    } catch (e) {
      console.error(e);
    } finally {
      setActionLoading(null);
    }
  };

  // Handler: Simulate Test Payment Webhook for an opportunity
  const simulatePayment = async (opp: OpportunityItem) => {
    setActionLoading(`pay-${opp.id}`);
    try {
      const plinkId = opp.execution_record?.razorpay_payment_link_id || `plink_test_${Date.now()}`;
      const payload = {
        entity: "event",
        account_id: "acc_ultron_sim",
        event: "payment_link.paid",
        contains: ["payment_link", "payment"],
        payload: {
          payment_link: {
            entity: {
              id: plinkId,
              reference_id: opp.id,
              amount: opp.amount_paise,
              amount_paid: opp.amount_paise,
              status: "paid",
            },
          },
          payment: {
            entity: {
              id: `pay_sim_${Date.now()}`,
              amount: opp.amount_paise,
              status: "captured",
            },
          },
        },
        created_at: Math.floor(Date.now() / 1000),
      };

      // Direct local simulation via isolated simulation webhook route
      await fetch(`${API_BASE}/internal/simulate-webhook`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "x-razorpay-signature": "simulated_test_signature", // In test mode or local
        },
        body: JSON.stringify(payload),
      });

      // Also directly update DB state for instant test feedback
      await fetch(`${API_BASE}/dashboard/reconcile-poll`, { method: "POST" });
      await fetchData();
    } catch (e) {
      console.error(e);
    } finally {
      setActionLoading(null);
    }
  };

  // Filter opportunities
  const filteredOpportunities = opportunities.filter((opp) => {
    if (filterSource !== "all" && opp.source !== filterSource) return false;
    if (filterStatus !== "all" && opp.status !== filterStatus) return false;
    if (searchTerm) {
      const term = searchTerm.toLowerCase();
      return (
        opp.id.toLowerCase().includes(term) ||
        opp.reason_code.toLowerCase().includes(term) ||
        opp.customer_id.toLowerCase().includes(term)
      );
    }
    return true;
  });

  const getStatusBadge = (status: string) => {
    switch (status) {
      case "recovered":
        return (
          <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-semibold bg-emerald-500/10 text-emerald-400 border border-emerald-500/30">
            <CheckCircle2 size={13} /> RECOVERED
          </span>
        );
      case "executing":
        return (
          <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-semibold bg-cyan-500/10 text-cyan-400 border border-cyan-500/30 animate-pulse">
            <Clock size={13} /> EXECUTING
          </span>
        );
      case "authorized":
      case "allocated":
        return (
          <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-semibold bg-blue-500/10 text-blue-400 border border-blue-500/30">
            <Shield size={13} /> AUTHORIZED
          </span>
        );
      case "blocked":
        return (
          <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-semibold bg-red-500/10 text-red-400 border border-red-500/30">
            <XCircle size={13} /> BLOCKED
          </span>
        );
      case "abstained":
        return (
          <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-semibold bg-slate-500/10 text-slate-400 border border-slate-500/30">
            <AlertTriangle size={13} /> ABSTAINED
          </span>
        );
      case "deferred":
        return (
          <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-semibold bg-amber-500/10 text-amber-400 border border-amber-500/30">
            <Clock size={13} /> WAIT (DEFERRED)
          </span>
        );
      default:
        return (
          <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-semibold bg-purple-500/10 text-purple-400 border border-purple-500/30">
            {status.toUpperCase()}
          </span>
        );
    }
  };

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 font-sans selection:bg-cyan-500/30 selection:text-cyan-200">
      {/* Top Background Glow */}
      <div className="fixed top-0 left-1/4 w-96 h-96 bg-cyan-600/10 rounded-full blur-3xl pointer-events-none -z-10" />
      <div className="fixed top-20 right-1/4 w-96 h-96 bg-purple-600/10 rounded-full blur-3xl pointer-events-none -z-10" />

      {/* Main Container */}
      <div className="max-w-7xl mx-auto px-4 py-8 flex flex-col gap-6">
        {/* Header Bar */}
        <header className="flex flex-col md:flex-row md:items-center justify-between gap-4 p-6 bg-slate-900/60 backdrop-blur-xl border border-slate-800/80 rounded-2xl shadow-2xl">
          <div className="flex items-center gap-3.5">
            <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-cyan-500 to-blue-600 flex items-center justify-center shadow-lg shadow-cyan-500/25">
              <Shield className="w-7 h-7 text-white" />
            </div>
            <div>
              <div className="flex items-center gap-2.5">
                <h1 className="text-2xl font-bold tracking-tight text-white flex items-center gap-2">
                  <span className="bg-clip-text text-transparent bg-gradient-to-r from-cyan-400 via-blue-400 to-indigo-400">
                    ULTRON
                  </span>
                </h1>
                <span className="px-2.5 py-0.5 text-xs font-semibold rounded-full bg-cyan-500/10 text-cyan-400 border border-cyan-500/20 font-mono">
                  Razorpay Test Mode
                </span>
              </div>
              <p className="text-xs text-slate-400 mt-0.5">
                Autonomous Economic Control Plane for Failed-Payment Recovery
              </p>
            </div>
          </div>

          {/* Global Action Toolbar */}
          <div className="flex flex-wrap items-center gap-2.5">
            {/* Kill Switch Toggle */}
            <button
              onClick={toggleKillSwitch}
              disabled={actionLoading === "kill-switch"}
              className={`px-3.5 py-2 rounded-xl font-medium text-xs transition-all flex items-center gap-2 border shadow-lg ${
                summary?.kill_switch_active
                  ? "bg-red-600 text-white border-red-500 shadow-red-500/30 animate-pulse"
                  : "bg-slate-800/80 hover:bg-slate-800 text-slate-300 border-slate-700 hover:border-slate-600"
              }`}
            >
              <Power size={14} className={summary?.kill_switch_active ? "text-white" : "text-slate-400"} />
              {summary?.kill_switch_active ? "KILL SWITCH ENGAGED" : "KILL SWITCH: OFF"}
            </button>

            {/* Run Market Allocation */}
            <button
              onClick={runPipeline}
              disabled={actionLoading === "pipeline"}
              className="px-3.5 py-2 rounded-xl font-medium text-xs transition-all flex items-center gap-2 bg-gradient-to-r from-cyan-600 to-blue-600 hover:from-cyan-500 hover:to-blue-500 text-white border border-cyan-400/30 shadow-lg shadow-cyan-500/20"
            >
              <TrendingUp size={14} />
              {actionLoading === "pipeline" ? "Allocating..." : "Run Market Allocation"}
            </button>

            {/* Execute Live Razorpay Links */}
            <button
              onClick={runExecution}
              disabled={actionLoading === "execution"}
              className="px-3.5 py-2 rounded-xl font-medium text-xs transition-all flex items-center gap-2 bg-gradient-to-r from-emerald-600 to-teal-600 hover:from-emerald-500 hover:to-teal-500 text-white border border-emerald-400/30 shadow-lg shadow-emerald-500/20"
            >
              <Zap size={14} />
              {actionLoading === "execution" ? "Generating..." : "Execute (Max 5)"}
            </button>

            {/* Poll Active Truth Poller */}
            <button
              onClick={runPoller}
              disabled={actionLoading === "poller"}
              title="Queries Razorpay directly as active fallback"
              className="px-3 py-2 rounded-xl font-medium text-xs transition-all flex items-center gap-2 bg-slate-800/80 hover:bg-slate-800 text-slate-300 border border-slate-700 hover:border-slate-600"
            >
              <RefreshCw size={13} className={actionLoading === "poller" ? "animate-spin" : ""} />
              Poll Poller
            </button>
          </div>
        </header>

        {/* Summary KPI Cards Grid */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-4">
          {/* Card 1: Total Opportunities */}
          <div className="p-5 bg-slate-900/40 backdrop-blur-md border border-slate-800/80 rounded-2xl flex flex-col justify-between">
            <div className="flex items-center justify-between text-slate-400 text-xs font-medium">
              <span>Total Opportunities</span>
              <Layers size={16} className="text-slate-400" />
            </div>
            <div className="mt-3">
              <span className="text-2xl font-bold text-white tracking-tight">
                {loading ? "--" : summary?.total_opportunities || 0}
              </span>
              <span className="text-xs text-slate-400 block mt-0.5">
                {summary?.status_counts.executing || 0} in-flight • {summary?.status_counts.blocked || 0} blocked
              </span>
            </div>
          </div>

          {/* Card 2: Total At Risk */}
          <div className="p-5 bg-slate-900/40 backdrop-blur-md border border-slate-800/80 rounded-2xl flex flex-col justify-between">
            <div className="flex items-center justify-between text-slate-400 text-xs font-medium">
              <span>Total At Risk</span>
              <DollarSign size={16} className="text-amber-400" />
            </div>
            <div className="mt-3">
              <span className="text-2xl font-bold text-amber-400 tracking-tight font-mono">
                {loading ? "--" : summary?.total_at_risk_display || "₹0.00"}
              </span>
              <span className="text-xs text-slate-400 block mt-0.5">
                Gross failed volume
              </span>
            </div>
          </div>

          {/* Card 3: Total Recovered (STRICTLY REAL ONLY) */}
          <div className="p-5 bg-gradient-to-b from-emerald-950/40 to-slate-900/40 backdrop-blur-md border border-emerald-500/30 rounded-2xl flex flex-col justify-between shadow-lg shadow-emerald-950/20">
            <div className="flex items-center justify-between text-emerald-400 text-xs font-medium">
              <span className="flex items-center gap-1">
                <Sparkles size={13} className="text-emerald-400" /> Total Recovered (Real)
              </span>
              <span className="px-1.5 py-0.5 text-[10px] uppercase tracking-wider font-bold rounded bg-emerald-500/20 text-emerald-300">
                Reconciled
              </span>
            </div>
            <div className="mt-3">
              <span className="text-2xl font-bold text-emerald-400 tracking-tight font-mono">
                {loading ? "--" : summary?.total_recovered_display || "₹0.00"}
              </span>
              <span className="text-xs text-slate-400 block mt-0.5">
                {summary?.real_recovered_count || 0} real settlements (0 synthetic)
              </span>
            </div>
          </div>

          {/* Card 4: Market Shadow Price */}
          <div className="p-5 bg-slate-900/40 backdrop-blur-md border border-slate-800/80 rounded-2xl flex flex-col justify-between">
            <div className="flex items-center justify-between text-slate-400 text-xs font-medium">
              <span>Shadow Price (Marginal)</span>
              <Flame size={16} className="text-cyan-400" />
            </div>
            <div className="mt-3">
              <span className="text-2xl font-bold text-cyan-400 tracking-tight font-mono">
                {loading ? "--" : summary?.shadow_price_display || "₹0.00"}
              </span>
              <span className="text-xs text-slate-400 block mt-0.5">
                Marginal cutoff value
              </span>
            </div>
          </div>

          {/* Card 5: Capacity Used */}
          <div className="p-5 bg-slate-900/40 backdrop-blur-md border border-slate-800/80 rounded-2xl flex flex-col justify-between">
            <div className="flex items-center justify-between text-slate-400 text-xs font-medium">
              <span>Capacity Cap</span>
              <Activity size={16} className="text-indigo-400" />
            </div>
            <div className="mt-3">
              <div className="flex items-baseline gap-1.5">
                <span className="text-2xl font-bold text-white tracking-tight font-mono">
                  {summary?.capacity_used || 0}
                </span>
                <span className="text-sm text-slate-400 font-mono">/ {summary?.capacity_limit || 5} links</span>
              </div>
              <div className="w-full bg-slate-800 h-1.5 rounded-full mt-2 overflow-hidden">
                <div
                  className="bg-cyan-500 h-full rounded-full transition-all duration-500"
                  style={{
                    width: `${Math.min(
                      100,
                      ((summary?.capacity_used || 0) / (summary?.capacity_limit || 5)) * 100
                    )}%`,
                  }}
                />
              </div>
            </div>
          </div>
        </div>

        {/* Opportunity Portfolio Section */}
        <section className="bg-slate-900/50 backdrop-blur-xl border border-slate-800/80 rounded-2xl overflow-hidden shadow-2xl flex flex-col">
          {/* Table Header Filter Bar */}
          <div className="p-5 border-b border-slate-800 flex flex-col md:flex-row md:items-center justify-between gap-4">
            <div>
              <h2 className="text-lg font-semibold text-white tracking-tight flex items-center gap-2">
                Recovery Opportunity Portfolio
                <span className="text-xs font-mono px-2 py-0.5 rounded bg-slate-800 text-slate-400">
                  {filteredOpportunities.length} opportunities
                </span>
              </h2>
              <p className="text-xs text-slate-400 mt-0.5">
                Sorted by Portfolio Incremental Value (IVEN) • Click any row for stored forensic "Why?" audit
              </p>
            </div>

            {/* Filters */}
            <div className="flex flex-wrap items-center gap-3">
              {/* Search input */}
              <div className="relative">
                <Search size={14} className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" />
                <input
                  type="text"
                  placeholder="Search ID, reason..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="pl-8 pr-3 py-1.5 rounded-xl bg-slate-950/80 border border-slate-800 text-xs text-slate-200 focus:outline-none focus:border-cyan-500 w-44"
                />
              </div>

              {/* Source Filter */}
              <div className="flex rounded-xl bg-slate-950/80 border border-slate-800 p-0.5 text-xs">
                {(["all", "real", "synthetic"] as const).map((src) => (
                  <button
                    key={src}
                    onClick={() => setFilterSource(src)}
                    className={`px-2.5 py-1 rounded-lg capitalize transition-all ${
                      filterSource === src
                        ? "bg-cyan-500/20 text-cyan-300 font-semibold"
                        : "text-slate-400 hover:text-slate-200"
                    }`}
                  >
                    {src}
                  </button>
                ))}
              </div>

              {/* Status Filter */}
              <select
                value={filterStatus}
                onChange={(e) => setFilterStatus(e.target.value)}
                className="px-2.5 py-1.5 rounded-xl bg-slate-950/80 border border-slate-800 text-xs text-slate-300 focus:outline-none focus:border-cyan-500"
              >
                <option value="all">All Statuses</option>
                <option value="recovered">Recovered</option>
                <option value="executing">Executing</option>
                <option value="authorized">Authorized</option>
                <option value="allocated">Allocated</option>
                <option value="deferred">Deferred (Wait)</option>
                <option value="blocked">Blocked</option>
                <option value="abstained">Abstained</option>
              </select>
            </div>
          </div>

          {/* Table Container */}
          <div className="overflow-x-auto">
            <table className="w-full text-left border-collapse">
              <thead>
                <tr className="border-b border-slate-800/80 bg-slate-950/40 text-[11px] uppercase tracking-wider text-slate-400 font-semibold">
                  <th className="py-3.5 px-4">Rank / ID</th>
                  <th className="py-3.5 px-3">Source</th>
                  <th className="py-3.5 px-3">Amount</th>
                  <th className="py-3.5 px-3">Decline Taxonomy</th>
                  <th className="py-3.5 px-3">Att.</th>
                  <th className="py-3.5 px-3">
                    <span className="flex items-center gap-1">
                      IVEN (₹) <span className="text-[9px] text-cyan-400/80 lowercase">(model-est.)</span>
                    </span>
                  </th>
                  <th className="py-3.5 px-3">Market Decision</th>
                  <th className="py-3.5 px-3">Current Status</th>
                  <th className="py-3.5 px-4 text-right">Action / Link</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800/60 text-xs">
                {filteredOpportunities.map((opp) => {
                  const ivenPaise = opp.score?.expected_incremental_value_paise || 0;
                  const isSelected = selectedOppId === opp.id;
                  const rank = opp.decision?.rank_in_batch || "-";

                  return (
                    <tr
                      key={opp.id}
                      onClick={() => setSelectedOppId(opp.id)}
                      className={`hover:bg-slate-800/40 cursor-pointer transition-colors ${
                        isSelected ? "bg-cyan-950/20 border-l-2 border-cyan-500" : ""
                      }`}
                    >
                      {/* ID & Rank */}
                      <td className="py-3.5 px-4 font-mono font-medium text-slate-200">
                        <div className="flex items-center gap-2">
                          <span className="text-slate-400 w-5">#{rank}</span>
                          <span className="truncate max-w-[180px] text-white" title={opp.id}>
                            {opp.id}
                          </span>
                        </div>
                      </td>

                      {/* Source */}
                      <td className="py-3.5 px-3">
                        <span
                          className={`px-2 py-0.5 rounded text-[10px] font-bold uppercase ${
                            opp.source === "real"
                              ? "bg-emerald-500/20 text-emerald-300 border border-emerald-500/30"
                              : "bg-purple-500/20 text-purple-300 border border-purple-500/30"
                          }`}
                        >
                          {opp.source}
                        </span>
                      </td>

                      {/* Amount */}
                      <td className="py-3.5 px-3 font-mono font-semibold text-slate-200">
                        ₹{(opp.amount_paise / 100).toLocaleString(undefined, { minimumFractionDigits: 2 })}
                      </td>

                      {/* Reason & Decline */}
                      <td className="py-3.5 px-3">
                        <div className="flex items-center gap-1.5">
                          <span
                            className={`w-2 h-2 rounded-full ${
                              opp.decline_type === "hard"
                                ? "bg-red-500"
                                : opp.decline_type === "soft"
                                ? "bg-amber-500"
                                : "bg-slate-500"
                            }`}
                          />
                          <span className="capitalize font-medium text-slate-300">
                            {opp.decline_type}
                          </span>
                          <span className="text-slate-400 text-[11px] truncate max-w-[130px]" title={opp.reason_code}>
                            ({opp.reason_code})
                          </span>
                        </div>
                      </td>

                      {/* Attempts */}
                      <td className="py-3.5 px-3 font-mono text-slate-300">
                        {opp.attempt_count}
                      </td>

                      {/* IVEN */}
                      <td className="py-3.5 px-3 font-mono font-semibold">
                        <span
                          className={
                            ivenPaise > 0
                              ? "text-cyan-400"
                              : ivenPaise === 0
                              ? "text-slate-400"
                              : "text-red-400"
                          }
                        >
                          ₹{(ivenPaise / 100).toLocaleString(undefined, { minimumFractionDigits: 2 })}
                        </span>
                      </td>

                      {/* Market Decision */}
                      <td className="py-3.5 px-3">
                        <span
                          className={`font-semibold font-mono text-xs ${
                            opp.decision?.decision === "ACT"
                              ? "text-emerald-400"
                              : opp.decision?.decision === "WAIT"
                              ? "text-amber-400"
                              : "text-slate-400"
                          }`}
                        >
                          {opp.decision?.decision || "PENDING"}
                        </span>
                      </td>

                      {/* Status */}
                      <td className="py-3.5 px-3">
                        {getStatusBadge(opp.status)}
                      </td>

                      {/* Action / Link */}
                      <td className="py-3.5 px-4 text-right" onClick={(e) => e.stopPropagation()}>
                        <div className="flex items-center justify-end gap-2">
                          {opp.execution_record?.link_url ? (
                            <a
                              href={opp.execution_record.link_url}
                              target="_blank"
                              rel="noreferrer"
                              className="px-2.5 py-1 rounded-lg bg-cyan-500/10 hover:bg-cyan-500/20 text-cyan-400 border border-cyan-500/30 text-xs flex items-center gap-1"
                            >
                              <ExternalLink size={12} /> Pay Link
                            </a>
                          ) : null}

                          {opp.status === "executing" ? (
                            <button
                              onClick={() => simulatePayment(opp)}
                              disabled={actionLoading === `pay-${opp.id}`}
                              className="px-2.5 py-1 rounded-lg bg-emerald-500/20 hover:bg-emerald-500/30 text-emerald-300 border border-emerald-500/40 text-xs flex items-center gap-1"
                            >
                              <CreditCard size={12} /> Simulate Pay
                            </button>
                          ) : null}

                          <button
                            onClick={() => setSelectedOppId(opp.id)}
                            className="p-1 rounded text-slate-400 hover:text-white"
                          >
                            <ChevronRight size={16} />
                          </button>
                        </div>
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        </section>

        {/* Slide-out "Why?" Forensic Audit Drawer */}
        {selectedDetails && (
          <div className="fixed inset-0 z-50 bg-black/70 backdrop-blur-sm flex justify-end animate-in fade-in duration-200">
            <div className="w-full max-w-2xl bg-slate-900 border-l border-slate-800 h-full overflow-y-auto p-6 flex flex-col gap-6 shadow-2xl">
              {/* Drawer Header */}
              <div className="flex items-center justify-between border-b border-slate-800 pb-4">
                <div className="flex items-center gap-3">
                  <div className="w-10 h-10 rounded-xl bg-cyan-500/10 border border-cyan-500/30 flex items-center justify-center">
                    <FileText className="w-5 h-5 text-cyan-400" />
                  </div>
                  <div>
                    <h3 className="text-lg font-bold text-white tracking-tight flex items-center gap-2">
                      Forensic "Why?" Audit Trail
                    </h3>
                    <p className="text-xs text-slate-400 font-mono">
                      Opportunity ID: {selectedDetails.opportunity.id}
                    </p>
                  </div>
                </div>

                <button
                  onClick={() => setSelectedOppId(null)}
                  className="p-2 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-300 transition-colors"
                >
                  <X size={18} />
                </button>
              </div>

              {/* Explanatory Banner */}
              <div className="p-3.5 rounded-xl bg-blue-950/40 border border-blue-500/30 text-xs text-blue-200 flex items-start gap-2.5">
                <Shield size={16} className="text-blue-400 shrink-0 mt-0.5" />
                <div>
                  <span className="font-semibold text-blue-300 block">Durable Stored Audit Trail:</span>
                  This forensic record is constructed strictly by reading immutable, stored database fields across the 6 pipeline stages. Zero explanations are generated fresh at view time.
                </div>
              </div>

              {/* Stage 1: Raw Ingestion Event */}
              <div className="p-4 rounded-xl bg-slate-950/60 border border-slate-800 flex flex-col gap-2.5">
                <div className="flex items-center justify-between text-xs font-semibold text-slate-300">
                  <span className="flex items-center gap-1.5">
                    <span className="w-5 h-5 rounded-full bg-slate-800 text-slate-300 flex items-center justify-center text-[10px]">1</span>
                    Raw Ingestion Event
                  </span>
                  <span className="text-slate-400 font-mono text-[11px]">
                    {selectedDetails.opportunity.created_at}
                  </span>
                </div>
                <div className="grid grid-cols-2 gap-2 text-xs font-mono">
                  <div className="p-2 rounded bg-slate-900 border border-slate-800/80">
                    <span className="text-slate-400 block text-[10px]">RAW REASON CODE</span>
                    <span className="text-white font-medium">{selectedDetails.opportunity.reason_code}</span>
                  </div>
                  <div className="p-2 rounded bg-slate-900 border border-slate-800/80">
                    <span className="text-slate-400 block text-[10px]">AMOUNT AT RISK</span>
                    <span className="text-amber-400 font-medium">
                      ₹{(selectedDetails.opportunity.amount_paise / 100).toLocaleString(undefined, { minimumFractionDigits: 2 })}
                    </span>
                  </div>
                </div>
                {selectedDetails.opportunity.raw_payload_ref && (
                  <div className="p-2 rounded bg-slate-900/80 border border-slate-800/60 text-[11px] font-mono text-slate-400 break-all">
                    {selectedDetails.opportunity.raw_payload_ref}
                  </div>
                )}
              </div>

              {/* Stage 2: Perception Normalization */}
              <div className="p-4 rounded-xl bg-slate-950/60 border border-slate-800 flex flex-col gap-2.5">
                <div className="flex items-center justify-between text-xs font-semibold text-slate-300">
                  <span className="flex items-center gap-1.5">
                    <span className="w-5 h-5 rounded-full bg-slate-800 text-slate-300 flex items-center justify-center text-[10px]">2</span>
                    Perception Normalization (Feature 2)
                  </span>
                </div>
                <div className="grid grid-cols-3 gap-2 text-xs font-mono">
                  <div className="p-2 rounded bg-slate-900 border border-slate-800/80">
                    <span className="text-slate-400 block text-[10px]">DECLINE TYPE</span>
                    <span className={`font-semibold capitalize ${
                      selectedDetails.opportunity.decline_type === "hard" ? "text-red-400" : "text-emerald-400"
                    }`}>
                      {selectedDetails.opportunity.decline_type}
                    </span>
                  </div>
                  <div className="p-2 rounded bg-slate-900 border border-slate-800/80">
                    <span className="text-slate-400 block text-[10px]">ATTEMPT COUNT</span>
                    <span className="text-white font-semibold">
                      {selectedDetails.opportunity.attempt_count}
                    </span>
                  </div>
                  <div className="p-2 rounded bg-slate-900 border border-slate-800/80">
                    <span className="text-slate-400 block text-[10px]">CUSTOMER TRUST</span>
                    <span className="text-cyan-400 font-semibold">
                      {selectedDetails.opportunity.customer_trust_score.toFixed(2)}
                    </span>
                  </div>
                </div>
              </div>

              {/* Stage 3: Economic Reasoning Breakdown */}
              <div className="p-4 rounded-xl bg-slate-950/60 border border-cyan-500/30 flex flex-col gap-2.5">
                <div className="flex items-center justify-between text-xs font-semibold text-cyan-300">
                  <span className="flex items-center gap-1.5">
                    <span className="w-5 h-5 rounded-full bg-cyan-500/20 text-cyan-300 flex items-center justify-center text-[10px]">3</span>
                    Economic Reasoning & Costs
                  </span>
                  <span className="px-2 py-0.5 rounded bg-cyan-500/20 text-cyan-300 text-[10px] uppercase font-bold tracking-wider">
                    Model-Estimated
                  </span>
                </div>
                <div className="grid grid-cols-2 sm:grid-cols-3 gap-2 text-xs font-mono">
                  <div className="p-2 rounded bg-slate-900 border border-slate-800">
                    <span className="text-slate-400 block text-[10px]">P(NATURAL)</span>
                    <span className="text-white">{(selectedDetails.score?.natural_recovery_prob || 0).toFixed(2)}</span>
                  </div>
                  <div className="p-2 rounded bg-slate-900 border border-slate-800">
                    <span className="text-slate-400 block text-[10px]">P(INTERVENTION)</span>
                    <span className="text-white">{(selectedDetails.score?.intervention_recovery_prob || 0).toFixed(2)}</span>
                  </div>
                  <div className="p-2 rounded bg-slate-900 border border-slate-800">
                    <span className="text-slate-400 block text-[10px]">INCREMENTAL PROB</span>
                    <span className="text-cyan-400 font-bold">{(selectedDetails.score?.incremental_prob || 0).toFixed(2)}</span>
                  </div>
                  <div className="p-2 rounded bg-slate-900 border border-slate-800">
                    <span className="text-slate-400 block text-[10px]">DELIVERY COST</span>
                    <span className="text-slate-300">₹{((selectedDetails.score?.operational_cost_paise || 400) / 100).toFixed(2)}</span>
                  </div>
                  <div className="p-2 rounded bg-slate-900 border border-slate-800">
                    <span className="text-slate-400 block text-[10px]">FATIGUE COST</span>
                    <span className="text-slate-300">₹{((selectedDetails.score?.fatigue_cost_paise || 0) / 100).toFixed(2)}</span>
                  </div>
                  <div className="p-2 rounded bg-slate-900 border border-slate-800">
                    <span className="text-slate-400 block text-[10px]">CONFIDENCE</span>
                    <span className="text-cyan-300 uppercase font-semibold">{selectedDetails.score?.confidence || "MEDIUM"}</span>
                  </div>
                </div>

                <div className="p-2.5 rounded-lg bg-cyan-950/30 border border-cyan-500/30 flex items-center justify-between text-xs font-mono">
                  <span className="text-slate-300">Expected Incremental Value (IVEN):</span>
                  <span className="text-sm font-bold text-cyan-400">
                    ₹{(((selectedDetails.score?.expected_incremental_value_paise || 0)) / 100).toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
                  </span>
                </div>
              </div>

              {/* Stage 4: Recovery Market Greedy Allocation */}
              <div className="p-4 rounded-xl bg-slate-950/60 border border-slate-800 flex flex-col gap-2.5">
                <div className="flex items-center justify-between text-xs font-semibold text-slate-300">
                  <span className="flex items-center gap-1.5">
                    <span className="w-5 h-5 rounded-full bg-slate-800 text-slate-300 flex items-center justify-center text-[10px]">4</span>
                    Recovery Market Allocation (Feature 4)
                  </span>
                  <span className={`font-mono text-xs font-bold px-2 py-0.5 rounded ${
                    selectedDetails.decision?.decision === "ACT"
                      ? "bg-emerald-500/20 text-emerald-300"
                      : "bg-amber-500/20 text-amber-300"
                  }`}>
                    Decision: {selectedDetails.decision?.decision || "PENDING"}
                  </span>
                </div>
                <div className="grid grid-cols-2 gap-2 text-xs font-mono">
                  <div className="p-2 rounded bg-slate-900 border border-slate-800/80">
                    <span className="text-slate-400 block text-[10px]">RANK IN BATCH</span>
                    <span className="text-white font-semibold">#{selectedDetails.decision?.rank_in_batch || "-"}</span>
                  </div>
                  <div className="p-2 rounded bg-slate-900 border border-slate-800/80">
                    <span className="text-slate-400 block text-[10px]">SHADOW PRICE AT RUN</span>
                    <span className="text-cyan-400 font-semibold">
                      ₹{(((selectedDetails.decision?.shadow_price_paise_at_decision || 0)) / 100).toLocaleString(undefined, { minimumFractionDigits: 2 })}
                    </span>
                  </div>
                </div>
                <div className="p-2.5 rounded bg-slate-900 border border-slate-800 text-xs text-slate-300 font-mono">
                  <span className="text-slate-400 block text-[10px]">ALLOCATION REASON:</span>
                  {selectedDetails.decision?.reason || "Pending portfolio allocation run"}
                </div>
              </div>

              {/* Stage 5: Action Authority Compliance Checklist */}
              <div className="p-4 rounded-xl bg-slate-950/60 border border-slate-800 flex flex-col gap-2.5">
                <div className="flex items-center justify-between text-xs font-semibold text-slate-300">
                  <span className="flex items-center gap-1.5">
                    <span className="w-5 h-5 rounded-full bg-slate-800 text-slate-300 flex items-center justify-center text-[10px]">5</span>
                    Action Authority Compliance Gate (Feature 5)
                  </span>
                  <span className="text-xs font-mono font-bold text-white">
                    {getStatusBadge(selectedDetails.opportunity.status)}
                  </span>
                </div>

                <div className="border border-slate-800 rounded-lg overflow-hidden divide-y divide-slate-800/80 text-xs">
                  {(selectedDetails.authority_checks || []).map((chk) => (
                    <div key={chk.check_name} className="p-2.5 flex items-start justify-between gap-3 bg-slate-900/60">
                      <div className="flex items-start gap-2">
                        {chk.passed ? (
                          <Check className="w-4 h-4 text-emerald-400 shrink-0 mt-0.5" />
                        ) : (
                          <X className="w-4 h-4 text-red-400 shrink-0 mt-0.5" />
                        )}
                        <div>
                          <span className="font-mono font-medium text-slate-200 block text-[11px]">
                            {chk.check_name}
                          </span>
                          <span className="text-[11px] text-slate-400">
                            {chk.reason}
                          </span>
                        </div>
                      </div>
                      <span
                        className={`text-[10px] font-bold uppercase font-mono px-1.5 py-0.5 rounded ${
                          chk.passed ? "bg-emerald-500/20 text-emerald-400" : "bg-red-500/20 text-red-400"
                        }`}
                      >
                        {chk.passed ? "Pass" : "Fail"}
                      </span>
                    </div>
                  ))}
                </div>
              </div>

              {/* Stage 6: Execution & Ledger Audit Timeline */}
              <div className="p-4 rounded-xl bg-slate-950/60 border border-slate-800 flex flex-col gap-2.5">
                <div className="flex items-center justify-between text-xs font-semibold text-slate-300">
                  <span className="flex items-center gap-1.5">
                    <span className="w-5 h-5 rounded-full bg-slate-800 text-slate-300 flex items-center justify-center text-[10px]">6</span>
                    Execution & Truth Engine Ledger (Feature 6 & 7)
                  </span>
                </div>

                {selectedDetails.opportunity.execution_record && (
                  <div className="p-3 rounded bg-slate-900 border border-slate-800 flex flex-col gap-2 text-xs font-mono">
                    <div className="flex items-center justify-between">
                      <span className="text-slate-400 text-[10px]">RAZORPAY PAYMENT LINK ID</span>
                      <span className="text-cyan-400 font-bold">{selectedDetails.opportunity.execution_record.razorpay_payment_link_id}</span>
                    </div>
                    <div className="flex items-center justify-between">
                      <span className="text-slate-400 text-[10px]">HOSTED CHECKOUT URL</span>
                      <a
                        href={selectedDetails.opportunity.execution_record.link_url}
                        target="_blank"
                        rel="noreferrer"
                        className="text-cyan-400 hover:underline flex items-center gap-1 text-[11px]"
                      >
                        {selectedDetails.opportunity.execution_record.link_url}
                        <ExternalLink size={12} />
                      </a>
                    </div>
                  </div>
                )}

                {/* Ledger entries timeline */}
                <div className="mt-1 flex flex-col gap-2">
                  <span className="text-[11px] font-semibold text-slate-400 uppercase tracking-wider">
                    Immutable Ledger Events:
                  </span>
                  {(selectedDetails.ledger || []).map((entry) => (
                    <div key={entry.id} className="p-2.5 rounded bg-slate-900/80 border border-slate-800 text-xs font-mono flex flex-col gap-1">
                      <div className="flex items-center justify-between">
                        <span className="font-bold text-cyan-300 uppercase text-[11px]">
                          {entry.event_type}
                        </span>
                        <span className="text-[10px] text-slate-400">
                          {entry.timestamp}
                        </span>
                      </div>
                      <div className="text-[11px] text-slate-400">
                        Amount: ₹{(entry.amount_paise / 100).toLocaleString(undefined, { minimumFractionDigits: 2 })}
                      </div>
                      {entry.raw_payload_ref && (
                        <div className="text-[10px] text-slate-400 break-all bg-slate-950 p-1.5 rounded">
                          {entry.raw_payload_ref}
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
