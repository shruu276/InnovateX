"use client";

import { useState, useEffect, useCallback } from "react";
import Link from "next/link";
import { Menu, X, Moon, Sun, Zap } from "lucide-react";

const NAV_LINKS = [
  { label: "Features",     href: "#features"      },
  { label: "How It Works", href: "#ai"             },
  { label: "Pricing",      href: "#pricing"        },
  { label: "Use Cases",    href: "#testimonials"   },
  { label: "Blog",         href: "/blog"           },
] as const;

export default function Navbar() {
  const [scrolled,     setScrolled]     = useState(false);
  const [mobileOpen,   setMobileOpen]   = useState(false);
  const [darkMode,     setDarkMode]     = useState(false);
  const [activeSection, setActiveSection] = useState("");

  /* ── scroll state ── */
  useEffect(() => {
    const onScroll = () => setScrolled(window.scrollY > 12);
    window.addEventListener("scroll", onScroll, { passive: true });
    return () => window.removeEventListener("scroll", onScroll);
  }, []);

  /* ── active section highlight ── */
  useEffect(() => {
    const ids = NAV_LINKS.map((l) => l.href.replace("#", "")).filter((h) => h.startsWith("f") || h.startsWith("a") || h.startsWith("t"));
    const observer = new IntersectionObserver(
      (entries) => {
        const visible = entries.find((e) => e.isIntersecting);
        if (visible) setActiveSection(visible.target.id);
      },
      { rootMargin: "-40% 0px -50% 0px" }
    );
    ids.forEach((id) => {
      const el = document.getElementById(id);
      if (el) observer.observe(el);
    });
    return () => observer.disconnect();
  }, []);

  /* ── dark mode ── */
  useEffect(() => {
    const stored = localStorage.getItem("theme");
    const prefersDark = window.matchMedia("(prefers-color-scheme: dark)").matches;
    const enabled = stored === "dark" || (!stored && prefersDark);
    setDarkMode(enabled);
    document.documentElement.classList.toggle("dark", enabled);
  }, []);

  const toggleDark = useCallback(() => {
    setDarkMode((prev) => {
      const next = !prev;
      document.documentElement.classList.toggle("dark", next);
      localStorage.setItem("theme", next ? "dark" : "light");
      return next;
    });
  }, []);

  /* ── lock body scroll when mobile menu open ── */
  useEffect(() => {
    document.body.style.overflow = mobileOpen ? "hidden" : "";
    return () => { document.body.style.overflow = ""; };
  }, [mobileOpen]);

  const isActive = (href: string) =>
    href.startsWith("#") && activeSection === href.replace("#", "");

  return (
    <>
      <header
        role="banner"
        className={`fixed inset-x-0 top-0 z-50 transition-all duration-300 ${
          scrolled
            ? "bg-white/90 dark:bg-[#0D0F14]/90 backdrop-blur-md shadow-sm border-b border-gray-200/60 dark:border-white/10"
            : "bg-transparent"
        }`}
      >
        <div className="mx-auto max-w-6xl px-4 sm:px-6 lg:px-8">
          <div className="flex h-16 items-center justify-between">

            {/* ── Logo ── */}
            <Link
              href="/"
              className="flex items-center gap-2 group focus-visible:outline-none"
              aria-label="InnovateX AI home"
            >
              <span className="flex h-8 w-8 items-center justify-center rounded-lg bg-gradient-to-br from-blue-500 to-purple-600 shadow-md group-hover:shadow-blue-500/30 transition-shadow">
                <Zap className="h-4 w-4 text-white" aria-hidden="true" />
              </span>
              <span
                className={`text-base font-extrabold tracking-tight transition-colors ${
                  scrolled ? "text-gray-900 dark:text-white" : "text-white"
                }`}
              >
                InnovateX{" "}
                <span className="gradient-text">AI</span>
              </span>
            </Link>

            {/* ── Desktop nav links ── */}
            <nav aria-label="Main navigation" className="hidden lg:flex items-center gap-1">
              {NAV_LINKS.map(({ label, href }) => (
                <a
                  key={label}
                  href={href}
                  className={`relative px-3 py-1.5 text-sm font-medium rounded-md transition-colors ${
                    isActive(href)
                      ? "text-blue-500 dark:text-blue-400"
                      : scrolled
                      ? "text-gray-600 dark:text-gray-300 hover:text-gray-900 dark:hover:text-white"
                      : "text-white/80 hover:text-white"
                  }`}
                >
                  {label}
                  {isActive(href) && (
                    <span
                      aria-hidden="true"
                      className="absolute bottom-0 left-3 right-3 h-0.5 rounded-full bg-blue-500"
                    />
                  )}
                </a>
              ))}
            </nav>

            {/* ── Right controls ── */}
            <div className="flex items-center gap-2">
              {/* Dark mode toggle */}
              <button
                onClick={toggleDark}
                aria-label={darkMode ? "Switch to light mode" : "Switch to dark mode"}
                className={`hidden sm:flex h-9 w-9 items-center justify-center rounded-lg transition-colors ${
                  scrolled
                    ? "text-gray-500 dark:text-gray-400 hover:bg-gray-100 dark:hover:bg-white/10"
                    : "text-white/70 hover:text-white hover:bg-white/10"
                }`}
              >
                {darkMode ? (
                  <Sun className="h-4 w-4" aria-hidden="true" />
                ) : (
                  <Moon className="h-4 w-4" aria-hidden="true" />
                )}
              </button>

              {/* Sign in */}
              <Link
                href="/login"
                className={`hidden sm:inline-flex items-center px-3 py-1.5 text-sm font-medium rounded-lg transition-colors ${
                  scrolled
                    ? "text-gray-600 dark:text-gray-300 hover:text-gray-900 dark:hover:text-white"
                    : "text-white/80 hover:text-white"
                }`}
              >
                Sign In
              </Link>

              {/* Get started CTA */}
              <Link
                href="/register"
                className="inline-flex items-center gap-1.5 rounded-lg bg-blue-600 hover:bg-blue-500 active:bg-blue-700 text-white px-4 py-2 text-sm font-semibold transition-colors shadow-sm shadow-blue-500/20"
              >
                Get Started
                <svg className="h-3.5 w-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2.5} aria-hidden="true">
                  <path strokeLinecap="round" strokeLinejoin="round" d="M13.5 4.5L21 12m0 0l-7.5 7.5M21 12H3" />
                </svg>
              </Link>

              {/* Mobile hamburger */}
              <button
                onClick={() => setMobileOpen((o) => !o)}
                aria-label={mobileOpen ? "Close menu" : "Open menu"}
                aria-expanded={mobileOpen}
                aria-controls="mobile-menu"
                className={`lg:hidden flex h-9 w-9 items-center justify-center rounded-lg transition-colors ${
                  scrolled
                    ? "text-gray-600 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-white/10"
                    : "text-white hover:bg-white/10"
                }`}
              >
                {mobileOpen ? (
                  <X className="h-5 w-5" aria-hidden="true" />
                ) : (
                  <Menu className="h-5 w-5" aria-hidden="true" />
                )}
              </button>
            </div>
          </div>
        </div>
      </header>

      {/* ── Mobile drawer ── */}
      <div
        id="mobile-menu"
        role="dialog"
        aria-modal="true"
        aria-label="Mobile navigation"
        className={`fixed inset-0 z-40 lg:hidden transition-opacity duration-200 ${
          mobileOpen ? "opacity-100 pointer-events-auto" : "opacity-0 pointer-events-none"
        }`}
      >
        {/* Backdrop */}
        <div
          aria-hidden="true"
          onClick={() => setMobileOpen(false)}
          className="absolute inset-0 bg-black/50 backdrop-blur-sm"
        />

        {/* Panel */}
        <nav
          className={`absolute right-0 top-0 h-full w-72 bg-white dark:bg-[#0D0F14] border-l border-gray-200 dark:border-white/10 flex flex-col transition-transform duration-300 ${
            mobileOpen ? "translate-x-0" : "translate-x-full"
          }`}
        >
          {/* Panel header */}
          <div className="flex items-center justify-between px-5 py-4 border-b border-gray-100 dark:border-white/10">
            <span className="font-extrabold text-gray-900 dark:text-white">
              InnovateX <span className="gradient-text">AI</span>
            </span>
            <button
              onClick={() => setMobileOpen(false)}
              aria-label="Close menu"
              className="h-8 w-8 flex items-center justify-center rounded-md text-gray-500 hover:bg-gray-100 dark:hover:bg-white/10"
            >
              <X className="h-4 w-4" aria-hidden="true" />
            </button>
          </div>

          {/* Links */}
          <ul className="flex flex-col px-3 py-4 gap-1 flex-1">
            {NAV_LINKS.map(({ label, href }) => (
              <li key={label}>
                <a
                  href={href}
                  onClick={() => setMobileOpen(false)}
                  className={`flex items-center px-3 py-2.5 rounded-lg text-sm font-medium transition-colors ${
                    isActive(href)
                      ? "bg-blue-50 dark:bg-blue-500/10 text-blue-600 dark:text-blue-400"
                      : "text-gray-700 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-white/5"
                  }`}
                >
                  {label}
                </a>
              </li>
            ))}
          </ul>

          {/* Mobile footer */}
          <div className="px-5 py-5 border-t border-gray-100 dark:border-white/10 flex flex-col gap-3">
            <button
              onClick={toggleDark}
              className="flex items-center gap-2 text-sm font-medium text-gray-600 dark:text-gray-300 hover:text-gray-900 dark:hover:text-white transition-colors"
            >
              {darkMode ? <Sun className="h-4 w-4" /> : <Moon className="h-4 w-4" />}
              {darkMode ? "Light Mode" : "Dark Mode"}
            </button>
            <Link
              href="/login"
              onClick={() => setMobileOpen(false)}
              className="w-full rounded-lg border border-gray-200 dark:border-white/20 px-4 py-2.5 text-center text-sm font-medium text-gray-700 dark:text-gray-200 hover:bg-gray-50 dark:hover:bg-white/5 transition-colors"
            >
              Sign In
            </Link>
            <Link
              href="/register"
              onClick={() => setMobileOpen(false)}
              className="w-full rounded-lg bg-blue-600 hover:bg-blue-500 text-white px-4 py-2.5 text-center text-sm font-semibold transition-colors"
            >
              Get Started Free
            </Link>
          </div>
        </nav>
      </div>
    </>
  );
}
