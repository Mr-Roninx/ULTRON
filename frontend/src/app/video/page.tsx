"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";

export default function VideoAliasPage() {
  const router = useRouter();

  useEffect(() => {
    router.replace("/pitch/video");
  }, [router]);

  return (
    <div style={{ minHeight: "100vh", background: "#03060c", display: "flex", alignItems: "center", justifyContent: "center", color: "#94a3b8", fontFamily: "sans-serif" }}>
      <span>Redirecting to ULTRON 5-Minute Motion Presentation...</span>
    </div>
  );
}
