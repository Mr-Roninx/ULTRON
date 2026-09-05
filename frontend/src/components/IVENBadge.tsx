"use client";

import React from "react";
import { TrendingUp, AlertTriangle, ShieldAlert, Sparkles } from "lucide-react";

export type IVENBand = "STRONG" | "MODERATE" | "WEAK" | "NEGATIVE";

interface IVENBadgeProps {
  band?: IVENBand;
  valuePaise?: number;
  showExplanation?: boolean;
  size?: "sm" | "md" | "lg";
}

export function IVENBadge({
  band,
  valuePaise,
  showExplanation = false,
  size = "md",
}: IVENBadgeProps) {
  // Derive band from valuePaise if band not provided
  let effectiveBand: IVENBand = band || "WEAK";
  if (!band && typeof valuePaise === "number") {
    if (valuePaise >= 15000) effectiveBand = "STRONG";
    else if (valuePaise >= 5000) effectiveBand = "MODERATE";
    else if (valuePaise > 0) effectiveBand = "WEAK";
    else effectiveBand = "NEGATIVE";
  }

  const config = {
    STRONG: {
      label: "STRONG IVEN",
      range: "≥ ₹150",
      color: "text-emerald-400 bg-emerald-950/40 border-emerald-500/40 shadow-emerald-950/20",
      dot: "bg-emerald-400 animate-pulse",
      icon: TrendingUp,
      desc: "High economic conviction: net expected incremental recovery value exceeds ₹150.",
    },
    MODERATE: {
      label: "MODERATE IVEN",
      range: "₹50 - ₹149",
      color: "text-cyan-300 bg-cyan-950/40 border-cyan-500/40 shadow-cyan-950/20",
      dot: "bg-cyan-400",
      icon: Sparkles,
      desc: "Profitable recovery: incremental recovery exceeds operational and fatigue friction.",
    },
    WEAK: {
      label: "WEAK IVEN",
      range: "< ₹50",
      color: "text-amber-400 bg-amber-950/40 border-amber-500/40 shadow-amber-950/20",
      dot: "bg-amber-400",
      icon: AlertTriangle,
      desc: "Marginal opportunity: vulnerable to shadow price exclusion when capacity is tight.",
    },
    NEGATIVE: {
      label: "NEGATIVE IVEN",
      range: "≤ ₹0",
      color: "text-rose-400 bg-rose-950/40 border-rose-500/40 shadow-rose-950/20",
      dot: "bg-rose-500",
      icon: ShieldAlert,
      desc: "Value destructive: action costs exceed incremental recovery probability. Must ABSTAIN.",
    },
  }[effectiveBand];

  const sizeClasses = {
    sm: "px-2 py-0.5 text-[10px] gap-1",
    md: "px-2.5 py-1 text-xs gap-1.5",
    lg: "px-3 py-1.5 text-sm gap-2",
  }[size];

  const Icon = config.icon;
  const formattedValue = typeof valuePaise === "number" ? `₹${(valuePaise / 100).toFixed(2)}` : null;

  return (
    <div className="inline-flex flex-col gap-0.5">
      <div
        className={`inline-flex items-center font-mono font-medium rounded-full border shadow-sm transition-all ${config.color} ${sizeClasses}`}
        title={`${config.label} (${config.range}): ${config.desc} *Model-estimated`}
      >
        <span className={`w-1.5 h-1.5 rounded-full ${config.dot}`} />
        <Icon className={size === "sm" ? "w-3 h-3" : "w-3.5 h-3.5"} />
        <span>{config.label}</span>
        {formattedValue && (
          <span className="opacity-90 font-semibold pl-0.5">({formattedValue})</span>
        )}
      </div>
      {showExplanation && (
        <span className="text-[10px] text-zinc-400 font-sans pl-1">
          {config.range} • <em className="text-zinc-500">*Model-estimated</em>
        </span>
      )}
    </div>
  );
}
