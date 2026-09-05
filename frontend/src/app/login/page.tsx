"use client";

import React, { useState, useEffect, useRef } from "react";
import { useRouter } from "next/navigation";
import { Shield, Mail, ArrowRight, ArrowLeft, Sparkles, RefreshCw, CheckCircle2 } from "lucide-react";
import { useAuth } from "../../lib/auth";

export default function LoginPage() {
  const router = useRouter();
  const { sendOtp, verifyOtp, loginAsDemo, token, loading: authLoading } = useAuth();

  const [step, setStep] = useState<"EMAIL" | "OTP">("EMAIL");
  const [email, setEmail] = useState("");
  const [otp, setOtp] = useState(["", "", "", "", "", ""]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [devOtpHint, setDevOtpHint] = useState<string | null>(null);
  const [sandboxNotice, setSandboxNotice] = useState<string | null>(null);
  const [resendCountdown, setResendCountdown] = useState(0);

  const otpInputsRef = useRef<(HTMLInputElement | null)[]>([]);

  // Auto-redirect to dashboard if session token already exists
  useEffect(() => {
    if (token && !authLoading) {
      router.replace("/dashboard");
    }
  }, [token, authLoading, router]);

  // Resend countdown timer
  useEffect(() => {
    if (resendCountdown > 0) {
      const timer = setTimeout(() => setResendCountdown(resendCountdown - 1), 1000);
      return () => clearTimeout(timer);
    }
  }, [resendCountdown]);

  // Step 1: Request OTP
  const handleSendOtp = async (e?: React.FormEvent) => {
    if (e) e.preventDefault();
    if (!email || !email.includes("@")) {
      setError("Please enter a valid work email address.");
      return;
    }

    setError(null);
    setLoading(true);
    const res = await sendOtp(email.trim());
    setLoading(false);

    if (res.success) {
      setStep("OTP");
      setResendCountdown(45);
      if (res.dev_otp) {
        setDevOtpHint(res.dev_otp);
      }
      if (res.delivered === false) {
        setSandboxNotice(res.message || "Email provider sandbox active (Resend test key delivers only to account owner). Your verification code is auto-filled below.");
        if (res.dev_otp) {
          setOtp(res.dev_otp.split(""));
        }
      } else {
        setSandboxNotice(null);
      }
      // Auto-focus first OTP input after state update
      setTimeout(() => {
        otpInputsRef.current[0]?.focus();
      }, 100);
    } else {
      setError(res.error || "Failed to send verification code. Please try again.");
    }
  };

  // Step 2: Handle OTP input changes & auto-focus next digit
  const handleOtpChange = (index: number, val: string) => {
    const char = val.slice(-1); // Take last typed char
    if (char && !/^[0-9]$/.test(char)) return;

    const newOtp = [...otp];
    newOtp[index] = char;
    setOtp(newOtp);
    setError(null);

    // Auto-focus next input
    if (char && index < 5) {
      otpInputsRef.current[index + 1]?.focus();
    }

    // If all 6 digits filled, auto-verify
    const fullCode = newOtp.join("");
    if (fullCode.length === 6) {
      handleVerifyCode(fullCode);
    }
  };

  const handleOtpKeyDown = (index: number, e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === "Backspace" && !otp[index] && index > 0) {
      otpInputsRef.current[index - 1]?.focus();
    }
  };

  const handleOtpPaste = (e: React.ClipboardEvent<HTMLInputElement>) => {
    e.preventDefault();
    const pasted = e.clipboardData.getData("text").replace(/\D/g, "").slice(0, 6);
    if (pasted) {
      const newOtp = pasted.split("");
      while (newOtp.length < 6) newOtp.push("");
      setOtp(newOtp);
      if (pasted.length === 6) {
        handleVerifyCode(pasted);
      } else {
        otpInputsRef.current[pasted.length]?.focus();
      }
    }
  };

  // Step 3: Verify Code & Authenticate
  const handleVerifyCode = async (overrideCode?: string) => {
    const codeToVerify = overrideCode || otp.join("");
    if (codeToVerify.length !== 6) {
      setError("Please enter the complete 6-digit code.");
      return;
    }

    setError(null);
    setLoading(true);
    const res = await verifyOtp(email.trim(), codeToVerify);
    setLoading(false);

    if (res.success) {
      router.replace("/dashboard");
    } else {
      setError(res.error || "Invalid or expired verification code.");
    }
  };

  // 1-Click Instant Demo Login
  const handleInstantDemoLogin = async () => {
    setError(null);
    setLoading(true);
    const res = await loginAsDemo();
    setLoading(false);

    if (res.success) {
      router.replace("/dashboard");
    } else {
      setError(res.error || "Demo login failed");
    }
  };

  return (
    <div style={{
      display: "flex",
      minHeight: "100vh",
      background: "#02042B",
      color: "#f8fafc",
      fontFamily: "var(--font-sans)",
      position: "relative",
      overflow: "hidden"
    }}>
      {/* Background Razorpay ambient electric glow effects */}
      <div style={{
        position: "absolute", top: "-10%", left: "15%", width: "550px", height: "550px",
        background: "radial-gradient(circle, rgba(12, 131, 255, 0.16) 0%, rgba(0,0,0,0) 70%)",
        borderRadius: "50%", pointerEvents: "none"
      }} />
      <div style={{
        position: "absolute", bottom: "-10%", right: "15%", width: "550px", height: "550px",
        background: "radial-gradient(circle, rgba(0, 208, 156, 0.12) 0%, rgba(0,0,0,0) 70%)",
        borderRadius: "50%", pointerEvents: "none"
      }} />

      {/* Main Container */}
      <div style={{
        display: "flex",
        flexDirection: "column",
        alignItems: "center",
        justifyContent: "center",
        width: "100%",
        padding: "40px 20px",
        zIndex: 10
      }}>
        {/* Razorpay Brand Header with Stylized Emblem */}
        <div style={{ display: "flex", alignItems: "center", gap: 12, marginBottom: 28 }}>
          <div style={{
            width: 42, height: 42, borderRadius: 8,
            background: "linear-gradient(135deg, #0C83FF 0%, #0052CC 100%)",
            display: "flex", alignItems: "center", justifyContent: "center",
            boxShadow: "0 4px 16px rgba(12, 131, 255, 0.4)",
            position: "relative", overflow: "hidden"
          }}>
            <div style={{
              position: "absolute", top: -4, right: -4, width: 16, height: 16,
              background: "#00D09C", transform: "rotate(45deg)", opacity: 0.9
            }} />
            <Shield size={22} color="#ffffff" style={{ position: "relative", zIndex: 2 }} />
          </div>
          <div>
            <div style={{
              fontSize: 22, fontWeight: 800, letterSpacing: "-0.5px", color: "#ffffff",
              display: "flex", alignItems: "center", gap: 8
            }}>
              <span>ULTRON</span>
              <span style={{
                fontSize: 10, fontWeight: 700, padding: "2px 6px", borderRadius: 4,
                background: "rgba(12, 131, 255, 0.25)", color: "#58A6FF", border: "1px solid rgba(12, 131, 255, 0.4)"
              }}>
                RAZORPAY
              </span>
            </div>
            <div style={{ fontSize: 11, color: "#8492A6", fontWeight: 500, letterSpacing: "0.2px" }}>
              Autonomous Revenue Recovery Engine
            </div>
          </div>
        </div>

        {/* Razorpay Styled Login Card */}
        <div style={{
          width: "100%",
          maxWidth: 430,
          background: "#080C34",
          border: "1px solid #1E2659",
          borderTop: "3px solid #0C83FF",
          borderRadius: 8,
          padding: "36px 32px",
          boxShadow: "0 25px 50px -12px rgba(0, 0, 0, 0.8), 0 0 1px 1px rgba(255, 255, 255, 0.05)"
        }}>
          {/* 1-Click Instant Demo Login Banner in Razorpay Electric Blue */}
          <button
            type="button"
            onClick={handleInstantDemoLogin}
            disabled={loading}
            style={{
              width: "100%", padding: "12px 16px", fontSize: 13, fontWeight: 700,
              marginBottom: 24, display: "flex", alignItems: "center", justifyContent: "center", gap: 10,
              border: "1px solid rgba(12, 131, 255, 0.4)",
              background: "linear-gradient(90deg, #0C83FF 0%, #0066FF 100%)",
              color: "#ffffff", cursor: "pointer", borderRadius: 6,
              boxShadow: "0 4px 14px rgba(12, 131, 255, 0.35)",
              transition: "all 0.2s ease"
            }}
          >
            <Sparkles size={16} color="#ffffff" />
            <span>⚡ 1-Click Instant Demo Login</span>
          </button>

          <div style={{ display: "flex", alignItems: "center", gap: 12, marginBottom: 24 }}>
            <div style={{ flex: 1, height: 1, background: "#1E2659" }} />
            <span style={{ fontSize: 11, color: "#8492A6", textTransform: "uppercase", letterSpacing: 0.5, fontWeight: 600 }}>
              {step === "EMAIL" ? "or sign in with email" : "verification code"}
            </span>
            <div style={{ flex: 1, height: 1, background: "#1E2659" }} />
          </div>

          {/* Error Banner */}
          {error && (
            <div style={{
              padding: "12px 16px", marginBottom: 20, borderRadius: 6,
              background: "rgba(244, 63, 94, 0.12)", border: "1px solid rgba(244, 63, 94, 0.3)",
              color: "#FB7185", fontSize: 13, lineHeight: 1.5
            }}>
              {error}
            </div>
          )}

          {/* STEP 1: Enter Email */}
          {step === "EMAIL" && (
            <form onSubmit={handleSendOtp} style={{ display: "flex", flexDirection: "column", gap: 18 }}>
              <div>
                <h2 style={{ fontSize: 19, fontWeight: 700, color: "#ffffff", marginBottom: 6 }}>
                  Sign in or Sign up
                </h2>
                <p style={{ fontSize: 13, color: "#8492A6", lineHeight: 1.5, margin: 0 }}>
                  Enter your email address. We'll send a 6-digit verification code to sign in or create your merchant account.
                </p>
              </div>

              <div>
                <label style={{ display: "block", fontSize: 12, fontWeight: 600, color: "#CBD5E1", marginBottom: 8 }}>
                  Work Email Address
                </label>
                <div style={{ position: "relative" }}>
                  <Mail size={16} style={{ position: "absolute", left: 14, top: "50%", transform: "translateY(-50%)", color: "#525D7E" }} />
                  <input
                    type="email"
                    required
                    autoFocus
                    placeholder="merchant@yourbrand.com"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    style={{
                      width: "100%", padding: "12px 14px 12px 42px",
                      background: "#0C1033",
                      border: "1px solid #1E2659",
                      borderRadius: 6, color: "#ffffff", fontSize: 14,
                      outline: "none", boxSizing: "border-box",
                      fontFamily: "var(--font-sans)",
                      transition: "border-color 0.15s ease, box-shadow 0.15s ease"
                    }}
                  />
                </div>
              </div>

              <button
                type="submit"
                disabled={loading || !email.trim()}
                style={{
                  width: "100%", padding: "12px 16px",
                  background: "linear-gradient(90deg, #0C83FF 0%, #0066FF 100%)",
                  color: "#ffffff", border: "none", borderRadius: 6,
                  fontSize: 14, fontWeight: 600, cursor: loading ? "wait" : "pointer",
                  display: "flex", alignItems: "center", justifyContent: "center", gap: 8,
                  boxShadow: "0 4px 14px rgba(12, 131, 255, 0.35)", marginTop: 4
                }}
              >
                {loading ? (
                  <>
                    <RefreshCw size={16} className="animate-spin" />
                    <span>Sending code…</span>
                  </>
                ) : (
                  <>
                    <span>Send Verification Code</span>
                    <ArrowRight size={16} />
                  </>
                )}
              </button>
            </form>
          )}

          {/* STEP 2: Enter OTP */}
          {step === "OTP" && (
            <div style={{ display: "flex", flexDirection: "column", gap: 20 }}>
              <div>
                <button
                  type="button"
                  onClick={() => setStep("EMAIL")}
                  style={{
                    background: "none", border: "none", color: "#8492A6", cursor: "pointer",
                    fontSize: 12, display: "flex", alignItems: "center", gap: 6, padding: 0, marginBottom: 12
                  }}
                >
                  <ArrowLeft size={14} />
                  <span>Change email</span>
                </button>
                <h2 style={{ fontSize: 19, fontWeight: 700, color: "#ffffff", marginBottom: 6 }}>
                  Enter verification code
                </h2>
                <p style={{ fontSize: 13, color: "#8492A6", lineHeight: 1.5, margin: 0 }}>
                  We sent a 6-digit code to <strong style={{ color: "#ffffff" }}>{email}</strong>
                </p>
              </div>

              {/* Sandbox Notice / Dev hint banner */}
              {sandboxNotice && (
                <div style={{
                  padding: "12px 14px", borderRadius: 6,
                  background: "rgba(255, 153, 0, 0.12)", border: "1px solid rgba(255, 153, 0, 0.35)",
                  color: "#FCD34D", fontSize: 12, lineHeight: 1.5
                }}>
                  <div style={{ fontWeight: 600, marginBottom: 2 }}>⚠️ Sandbox Notice</div>
                  <div style={{ color: "#FEF3C7" }}>{sandboxNotice}</div>
                  <div style={{ marginTop: 6, fontSize: 11, color: "#CBD5E1" }}>
                    Code: <strong style={{ color: "#ffffff", fontFamily: "var(--font-mono)", fontSize: 14 }}>{devOtpHint}</strong> (Auto-filled below for instant access)
                  </div>
                </div>
              )}

              {!sandboxNotice && devOtpHint && (
                <div style={{
                  padding: "10px 14px", borderRadius: 6,
                  background: "rgba(12, 131, 255, 0.12)", border: "1px dashed rgba(12, 131, 255, 0.4)",
                  color: "#93C5FD", fontSize: 12, display: "flex", alignItems: "center", justifyContent: "space-between"
                }}>
                  <span>Dev Sandbox Code: <strong>{devOtpHint}</strong></span>
                  <button
                    type="button"
                    onClick={() => {
                      const digits = devOtpHint.split("");
                      setOtp(digits);
                      handleVerifyCode(devOtpHint);
                    }}
                    style={{
                      background: "rgba(12, 131, 255, 0.25)", border: "none", borderRadius: 4,
                      color: "#ffffff", padding: "3px 8px", cursor: "pointer", fontSize: 11, fontWeight: 600
                    }}
                  >
                    Auto-fill & Submit
                  </button>
                </div>
              )}

              {/* 6 Digit Input Boxes */}
              <div style={{ display: "flex", gap: 8, justifyContent: "center" }}>
                {otp.map((digit, idx) => (
                  <input
                    key={idx}
                    ref={(el) => { otpInputsRef.current[idx] = el; }}
                    type="text"
                    inputMode="numeric"
                    maxLength={1}
                    value={digit}
                    onChange={(e) => handleOtpChange(idx, e.target.value)}
                    onKeyDown={(e) => handleOtpKeyDown(idx, e)}
                    onPaste={handleOtpPaste}
                    style={{
                      width: 48, height: 54, textAlign: "center",
                      fontSize: 22, fontWeight: 700, color: "#ffffff",
                      background: "#0C1033",
                      border: digit ? "2px solid #0C83FF" : "1px solid #1E2659",
                      borderRadius: 6, outline: "none",
                      boxShadow: digit ? "0 0 10px rgba(12, 131, 255, 0.3)" : "none",
                      transition: "all 0.15s ease",
                      fontFamily: "var(--font-mono)"
                    }}
                  />
                ))}
              </div>

              {/* Verify Button */}
              <button
                type="button"
                onClick={() => handleVerifyCode()}
                disabled={loading || otp.join("").length < 6}
                style={{
                  width: "100%", padding: "12px 16px",
                  background: otp.join("").length === 6
                    ? "linear-gradient(90deg, #0C83FF 0%, #0066FF 100%)"
                    : "rgba(12, 131, 255, 0.4)",
                  color: "#ffffff", border: "none", borderRadius: 6,
                  fontSize: 14, fontWeight: 600, cursor: loading ? "wait" : "pointer",
                  display: "flex", alignItems: "center", justifyContent: "center", gap: 8,
                  boxShadow: otp.join("").length === 6 ? "0 4px 14px rgba(12, 131, 255, 0.35)" : "none"
                }}
              >
                {loading ? (
                  <>
                    <RefreshCw size={16} className="animate-spin" />
                    <span>Verifying…</span>
                  </>
                ) : (
                  <>
                    <span>Verify & Enter Dashboard</span>
                    <CheckCircle2 size={16} />
                  </>
                )}
              </button>

              {/* Resend Link */}
              <div style={{ textAlign: "center", fontSize: 12, color: "#8492A6" }}>
                {resendCountdown > 0 ? (
                  <span>Resend code in <strong style={{ color: "#ffffff" }}>{resendCountdown}s</strong></span>
                ) : (
                  <button
                    type="button"
                    onClick={() => handleSendOtp()}
                    disabled={loading}
                    style={{
                      background: "none", border: "none", color: "#0C83FF",
                      cursor: "pointer", fontSize: 12, fontWeight: 600, padding: 0
                    }}
                  >
                    Didn't receive code? Resend OTP
                  </button>
                )}
              </div>
            </div>
          )}
        </div>

        {/* Footer info */}
        <div style={{ marginTop: 24, fontSize: 12, color: "#525D7E", textAlign: "center" }}>
          Razorpay Partner Control Plane • Autonomous Payment Recovery Engine • Test & Live Gateway
        </div>
      </div>
    </div>
  );
}
