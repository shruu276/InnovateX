"use client";

import { useEffect, useRef, useState } from "react";
import Link from "next/link";
import { ArrowRight, Play, Star, Users, Zap } from "lucide-react";

const SECTOR_BADGES = [
  { icon: "🎓", label: "Academia"   },
  { icon: "🏭", label: "Industry"   },
  { icon: "🏛",  label: "Government" },
  { icon: "🚀", label: "Startups"   },
] as const;

const ANNOUNCEMENT_TEXTS = [
  "Now powered by GPT-4o",
  "New: AI Funding Discovery",
  "1,000+ projects funded",
] as const;

// ─── Lightweight animated mock dashboard rendered with DOM ───────────────────
function DashboardPreview() {
  return (
    <div
      className="animate-float rounded-2xl border border-white/15 bg-white/5 backdrop-blur-sm overflow-hidden shadow-2xl shadow-blue-500/10"
      aria-hidden="true"
    >
      {/* Window chrome */}
      <div className="flex items-center gap-1.5 px-4 py-3 border-b border-white/10 bg-white/5">
        <span className="h-2.5 w-2.5 rounded-full bg-red-400/70" />
        <span className="h-2.5 w-2.5 rounded-full bg-yellow-400/70" />
        <span className="h-2.5 w-2.5 rounded-full bg-green-400/70" />
        <span className="ml-3 text-[10px] text-white/30 font-mono">
          innovatex.ai/dashboard
        </span>
      </div>

      <div className="p-4 flex flex-col gap-3">
        {/* Top metric row */}
        <div className="grid grid-cols-3 gap-2">
          {[
            { label: "Active Projects", value: "24", delta: "+3" },
            { label: "Team Members",    value: "87", delta: "+12" },
            { label: "Inno. Score",     value: "94", delta: "+5" },
          ].map(({ label, value, delta }) => (
            <div key={label} className="rounded-xl bg-white/[0.06] border border-white/10 px-3 py-2">
              <p className="text-[9px] text-white/40 leading-none mb-1">{label}</p>
              <div className="flex items-end gap-1">
                <p className="text-base font-extrabold text-white leading-none">{value}</p>
                <p className="text-[9px] text-green-400 mb-0.5">{delta}</p>
              </div>
            </div>
          ))}
        </div>

        {/* AI suggestion card */}
        <div className="rounded-xl bg-blue-500/10 border border-blue-500/20 p-3">
          <div className="flex items-center gap-2 mb-1.5">
            <Zap className="h-3 w-3 text-blue-400" />
            <p className="text-[10px] font-semibold text-blue-300">AI Recommendation</p>
          </div>
          <p className="text-[10px] text-blue-200/80 leading-relaxed">
            3 researchers match your climate-tech project. 2 active NSF grants aligned. Deadline in 14 days.
          </p>
        </div>

        {/* Kanban strip */}
        <div className="grid grid-cols-3 gap-2">
          {[
            { col: "To Do",      color: "bg-gray-500/20 text-gray-400",  n: 4 },
            { col: "In Progress",color: "bg-blue-500/20 text-blue-400",  n: 7 },
            { col: "Done",       color: "bg-green-500/20 text-green-400",n: 12 },
          ].map(({ col, color, n }) => (
            <div key={col} className="rounded-lg border border-white/10 bg-white/[0.03] p-2">
              <p className={`text-[9px] font-semibold rounded px-1.5 py-0.5 inline-block mb-1.5 ${color}`}>
                {col}
              </p>
              <div className="flex flex-col gap-1">
                {Array.from({ length: Math.min(n, 3) }).map((_, i) => (
                  <div key={i} className="h-2 rounded-full bg-white/10" style={{ width: `${60 + i * 15}%` }} />
                ))}
              </div>
              <p className="text-[9px] text-white/30 mt-1">{n} tasks</p>
            </div>
          ))}
        </div>

        {/* Team avatars */}
        <div className="flex items-center justify-between">
          <div className="flex -space-x-1.5">
            {["MP", "JO", "SM", "LK", "+8"].map((initials, i) => (
              <div
                key={i}
                className="h-6 w-6 rounded-full border-2 border-[#0D0F14] flex items-center justify-center text-[8px] font-bold text-white"
                style={{ background: `hsl(${210 + i * 30}, 70%, 45%)` }}
              >
                {initials}
              </div>
            ))}
          </div>
          <span className="text-[9px] text-white/30">Active now</span>
        </div>
      </div>
    </div>
  );
}

// ─── Animated announcement pill ─────────────────────────────────────────────
function AnnouncementPill() {
  const [index, setIndex] = useState(0);
  const [fade,  setFade]  = useState(true);

  useEffect(() => {
    const id = setInterval(() => {
      setFade(false);
      setTimeout(() => {
        setIndex((i) => (i + 1) % ANNOUNCEMENT_TEXTS.length);
        setFade(true);
      }, 300);
    }, 3500);
    return () => clearInterval(id);
  }, []);

  return (
    <div className="inline-flex items-center gap-2 rounded-full border border-purple-500/30 bg-purple-500/10 px-4 py-1.5 text-xs font-semibold text-purple-300">
      <span className="relative flex h-2 w-2">
        <span className="absolute inline-flex h-full w-full animate-ping rounded-full bg-purple-400 opacity-75" />
        <span className="relative inline-flex h-2 w-2 rounded-full bg-purple-500" />
      </span>
      <span
        className="transition-opacity duration-300"
        style={{ opacity: fade ? 1 : 0 }}
      >
        {ANNOUNCEMENT_TEXTS[index]}
      </span>
    </div>
  );
}

// ─── Video modal ─────────────────────────────────────────────────────────────
function VideoModal({ open, onClose }: { open: boolean; onClose: () => void }) {
  const ref = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (!open) return;
    const handler = (e: KeyboardEvent) => e.key === "Escape" && onClose();
    window.addEventListener("keydown", handler);
    return () => window.removeEventListener("keydown", handler);
  }, [open, onClose]);

  if (!open) return null;

  return (
    <div
      role="dialog"
      aria-modal="true"
      aria-label="Product demo video"
      className="fixed inset-0 z-50 flex items-center justify-center p-4"
    >
      <div
        aria-hidden="true"
        onClick={onClose}
        className="absolute inset-0 bg-black/80 backdrop-blur-sm"
      />
      <div
        ref={ref}
        className="relative w-full max-w-3xl rounded-2xl overflow-hidden border border-white/10 shadow-2xl bg-[#0D0F14]"
      >
        <button
          onClick={onClose}
          aria-label="Close video"
          className="absolute top-3 right-3 z-10 flex h-8 w-8 items-center justify-center rounded-full bg-white/10 text-white hover:bg-white/20 transition-colors"
        >
          <span aria-hidden="true" className="text-base font-bold leading-none">&times;</span>
        </button>
        {/* Placeholder video area */}
        <div className="aspect-video flex items-center justify-center bg-gradient-to-br from-[#1E3A6E] to-[#3B1F7C]">
          <div className="text-center">
            <div className="mx-auto mb-4 flex h-16 w-16 items-center justify-center rounded-full bg-white/10 border border-white/20">
              <Play className="h-7 w-7 text-white ml-1" aria-hidden="true" />
            </div>
            <p className="text-white/60 text-sm">InnovateX AI Product Demo</p>
            <p className="text-white/30 text-xs mt-1">2 min walkthrough</p>
          </div>
        </div>
      </div>
    </div>
  );
}

// ─── Hero ────────────────────────────────────────────────────────────────────
export default function Hero() {
  const [videoOpen, setVideoOpen] = useState(false);

  return (
    <>
      <VideoModal open={videoOpen} onClose={() => setVideoOpen(false)} />

      <section
        id="hero"
        aria-labelledby="hero-heading"
        className="relative min-h-screen flex items-center overflow-hidden bg-[#0D0F14] pt-16"
      >
        {/* Background layers */}
        <div aria-hidden="true" className="pointer-events-none absolute inset-0">
          {/* Radial glows */}
          <div className="absolute top-0 right-[15%] h-[500px] w-[500px] rounded-full bg-blue-600/10 blur-[120px]" />
          <div className="absolute bottom-[10%] left-[5%] h-[400px] w-[400px] rounded-full bg-purple-700/10 blur-[100px]" />
          {/* Grid overlay */}
          <div className="absolute inset-0 hero-grid opacity-100" />
        </div>

        <div className="relative mx-auto max-w-6xl px-4 sm:px-6 lg:px-8 py-20 lg:py-0">
          <div className="grid grid-cols-1 lg:grid-cols-[1.1fr_0.9fr] gap-12 lg:gap-16 items-center">

            {/* ── Left: text column ── */}
            <div className="flex flex-col items-start gap-6">
              {/* Announcement pill */}
              <AnnouncementPill />

              {/* H1 */}
              <h1
                id="hero-heading"
                className="text-4xl sm:text-5xl lg:text-6xl font-extrabold text-white leading-[1.1] tracking-tight"
              >
                Where Ideas Meet{" "}
                <span className="gradient-text">Intelligence.</span>
                <br className="hidden sm:block" />
                {" "}Build the Future{" "}
                <span className="text-white/90">Together.</span>
              </h1>

              {/* Subheadline */}
              <p className="text-base sm:text-lg text-white/60 max-w-[480px] leading-relaxed">
                InnovateX AI bridges <strong className="text-white/80 font-semibold">academia</strong>,{" "}
                <strong className="text-white/80 font-semibold">industry</strong>,{" "}
                <strong className="text-white/80 font-semibold">government</strong>, and{" "}
                <strong className="text-white/80 font-semibold">startups</strong> through an AI-powered
                platform designed for real-world impact.
              </p>

              {/* CTA row */}
              <div className="flex flex-col sm:flex-row items-start sm:items-center gap-3">
                <Link
                  href="/register"
                  className="inline-flex items-center gap-2 rounded-xl bg-blue-600 hover:bg-blue-500 active:bg-blue-700 text-white font-bold px-6 py-3.5 text-sm transition-colors shadow-lg shadow-blue-500/25 focus-visible:outline-white"
                >
                  Start for Free
                  <ArrowRight className="h-4 w-4" aria-hidden="true" />
                </Link>

                <button
                  onClick={() => setVideoOpen(true)}
                  className="inline-flex items-center gap-2.5 rounded-xl border border-white/20 bg-white/5 hover:bg-white/10 text-white font-semibold px-5 py-3.5 text-sm transition-colors focus-visible:outline-white"
                >
                  <span className="flex h-6 w-6 items-center justify-center rounded-full bg-white/15 border border-white/20">
                    <Play className="h-3 w-3 fill-current ml-0.5" aria-hidden="true" />
                  </span>
                  Watch Demo
                  <span className="text-white/40 text-xs font-normal">2 min</span>
                </button>
              </div>

              {/* Social proof micro-strip */}
              <div className="flex flex-col sm:flex-row sm:items-center gap-3 text-xs text-white/40 pt-2">
                {/* Avatars */}
                <div className="flex -space-x-1.5" aria-hidden="true">
                  {["#3B82D4", "#7C5CD8", "#06b6d4", "#10b981", "#f59e0b"].map((bg, i) => (
                    <div
                      key={i}
                      className="h-7 w-7 rounded-full border-2 border-[#0D0F14]"
                      style={{ background: bg }}
                    />
                  ))}
                </div>
                {/* Rating */}
                <div className="flex items-center gap-1.5">
                  <div className="flex" aria-label="5 stars">
                    {Array.from({ length: 5 }).map((_, i) => (
                      <Star key={i} className="h-3 w-3 fill-yellow-400 text-yellow-400" aria-hidden="true" />
                    ))}
                  </div>
                  <span>4.9 / 5</span>
                </div>
                <span aria-label="12,000 or more active users">
                  <Users className="inline h-3 w-3 mr-1" aria-hidden="true" />
                  12,000+ innovators
                </span>
                <span className="hidden sm:inline">No credit card required</span>
              </div>
            </div>

            {/* ── Right: dashboard visual ── */}
            <div className="hidden lg:block">
              <DashboardPreview />
            </div>
          </div>

          {/* ── Sector badges — bottom strip ── */}
          <div
            className="mt-16 lg:mt-20 flex flex-wrap justify-center gap-3"
            aria-label="Platform sectors"
          >
            {SECTOR_BADGES.map(({ icon, label }) => (
              <span
                key={label}
                className="inline-flex items-center gap-2 rounded-full border border-white/15 bg-white/5 px-4 py-1.5 text-xs font-medium text-white/60 backdrop-blur-sm"
              >
                <span aria-hidden="true">{icon}</span>
                {label}
              </span>
            ))}
          </div>
        </div>

        {/* Scroll indicator */}
        <div
          aria-hidden="true"
          className="absolute bottom-8 left-1/2 -translate-x-1/2 flex flex-col items-center gap-1 opacity-40"
        >
          <span className="text-[10px] uppercase tracking-widest text-white/50">Scroll</span>
          <div className="h-8 w-5 rounded-full border border-white/20 flex justify-center pt-1.5">
            <div className="h-2 w-1 rounded-full bg-white/40 animate-bounce" />
          </div>
        </div>
      </section>
    </>
  );
}
