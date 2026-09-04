"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";

export default function ProductAliasPage() {
  const router = useRouter();

  useEffect(() => {
    router.replace("/showcase");
  }, [router]);

  return (
    <div style={{ minHeight: "100vh", background: "#03060c", display: "flex", alignItems: "center", justifyContent: "center", color: "#94a3b8", fontFamily: "sans-serif" }}>
      <span>Redirecting to ULTRON Product Showcase...</span>
    </div>
  );
}
