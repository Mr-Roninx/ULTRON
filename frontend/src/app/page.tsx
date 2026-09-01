"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";
import { useAuth } from "../lib/auth";

export default function RootPage() {
  const { token, loading } = useAuth();
  const router = useRouter();

  useEffect(() => {
    if (!loading) {
      router.replace(token ? "/dashboard" : "/login");
    }
  }, [token, loading, router]);

  return (
    <div style={{
      display: "flex", alignItems: "center", justifyContent: "center",
      minHeight: "100vh", background: "var(--bg-base)",
    }}>
      <div style={{
        display: "flex", flexDirection: "column", alignItems: "center", gap: 16,
      }}>
        <div style={{
          width: 40, height: 40, border: "3px solid var(--electric-blue)",
          borderTopColor: "transparent", borderRadius: "50%",
          animation: "spin 0.7s linear infinite",
        }} />
        <span style={{ color: "var(--text-muted)", fontSize: 13 }}>Loading ULTRON…</span>
      </div>
      <style>{`@keyframes spin { to { transform: rotate(360deg); } }`}</style>
    </div>
  );
}
