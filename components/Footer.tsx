import Link from "next/link";
import { Zap, Linkedin, Github, Twitter, Youtube } from "lucide-react";
import NewsletterInput from "@/components/NewsletterInput";

// ─── Data ─────────────────────────────────────────────────────────────────────
const FOOTER_LINKS = [
  {
    heading: "Product",
    links: [
      { label: "Features",      href: "#features"      },
      { label: "Pricing",       href: "/pricing"       },
      { label: "Changelog",     href: "/changelog"     },
      { label: "Roadmap",       href: "/roadmap"       },
      { label: "Status",        href: "/status"        },
      { label: "Security",      href: "/security"      },
    ],
  },
  {
    heading: "Resources",
    links: [
      { label: "Documentation", href: "/docs"          },
      { label: "API Reference", href: "/docs/api"      },
      { label: "Blog",          href: "/blog"          },
      { label: "Case Studies",  href: "/case-studies"  },
      { label: "Community",     href: "/community"     },
      { label: "Webinars",      href: "/webinars"      },
    ],
  },
  {
    heading: "Company",
    links: [
      { label: "About",         href: "/about"         },
      { label: "Careers",       href: "/careers",      },
      { label: "Press Kit",     href: "/press"         },
      { label: "Partners",      href: "/partners"      },
      { label: "Contact",       href: "/contact"       },
      { label: "Investors",     href: "/investors"     },
    ],
  },
] as const;

const SOCIAL_LINKS = [
  { icon: Linkedin, label: "LinkedIn",  href: "https://linkedin.com"  },
  { icon: Twitter,  label: "X / Twitter", href: "https://twitter.com" },
  { icon: Github,   label: "GitHub",    href: "https://github.com"    },
  { icon: Youtube,  label: "YouTube",   href: "https://youtube.com"   },
] as const;

const TRUST_BADGES = [
  "SOC 2 Type II",
  "GDPR Compliant",
  "HIPAA Ready",
  "ISO 27001",
] as const;

// ─── Footer ───────────────────────────────────────────────────────────────────
export default function Footer() {
  return (
    <footer
      role="contentinfo"
      className="bg-[#0D0F14] border-t border-white/10"
    >
      <div className="mx-auto max-w-6xl px-4 sm:px-6 lg:px-8">

        {/* ── Trust badges strip ── */}
        <div className="flex flex-wrap justify-center gap-x-8 gap-y-2 py-5 border-b border-white/10">
          {TRUST_BADGES.map((badge) => (
            <span
              key={badge}
              className="text-[11px] font-semibold text-white/25 uppercase tracking-widest"
            >
              ✓ {badge}
            </span>
          ))}
        </div>

        {/* ── Main grid ── */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-[1.4fr_repeat(3,1fr)_1.4fr] gap-10 py-14">

          {/* Column 1 — Brand */}
          <div className="flex flex-col gap-4">
            {/* Logo */}
            <Link href="/" className="flex items-center gap-2 group w-fit" aria-label="InnovateX AI home">
              <span className="flex h-8 w-8 items-center justify-center rounded-lg bg-gradient-to-br from-blue-500 to-purple-600">
                <Zap className="h-4 w-4 text-white" aria-hidden="true" />
              </span>
              <span className="text-sm font-extrabold text-white tracking-tight">
                InnovateX <span className="gradient-text">AI</span>
              </span>
            </Link>

            {/* Tagline */}
            <p className="text-sm text-white/40 leading-relaxed max-w-[220px]">
              Bridging Academia, Industry, Government &amp; Startups through AI-powered collaboration.
            </p>

            {/* Social links */}
            <div className="flex items-center gap-2 mt-1" aria-label="Social media links">
              {SOCIAL_LINKS.map(({ icon: Icon, label, href }) => (
                <a
                  key={label}
                  href={href}
                  target="_blank"
                  rel="noopener noreferrer"
                  aria-label={label}
                  className="flex h-8 w-8 items-center justify-center rounded-lg bg-white/5 border border-white/10 text-white/40 hover:text-white hover:bg-white/10 hover:border-white/20 transition-colors"
                >
                  <Icon className="h-3.5 w-3.5" aria-hidden="true" />
                </a>
              ))}
            </div>
          </div>

          {/* Columns 2–4 — Nav links */}
          {FOOTER_LINKS.map(({ heading, links }) => (
            <nav key={heading} aria-labelledby={`footer-nav-${heading.toLowerCase()}`}>
              <h3
                id={`footer-nav-${heading.toLowerCase()}`}
                className="text-xs font-bold uppercase tracking-widest text-white mb-4"
              >
                {heading}
              </h3>
              <ul className="flex flex-col gap-2.5">
                {links.map(({ label, href }) => (
                  <li key={label}>
                    <Link
                      href={href}
                      className="text-sm text-white/40 hover:text-white/80 transition-colors"
                    >
                      {label}
                    </Link>
                  </li>
                ))}
              </ul>
            </nav>
          ))}

          {/* Column 5 — Newsletter */}
          <div>
            <h3 className="text-xs font-bold uppercase tracking-widest text-white mb-1">
              Stay in the loop
            </h3>
            <p className="text-sm text-white/40 leading-relaxed mb-1">
              Product updates, AI insights, and innovation news — monthly, no spam.
            </p>
            <NewsletterInput />
            <p className="mt-2 text-[11px] text-white/20">
              By subscribing you agree to our{" "}
              <Link href="/privacy" className="underline underline-offset-2 hover:text-white/40 transition-colors">
                Privacy Policy
              </Link>
              .
            </p>
          </div>
        </div>

        {/* ── Bottom bar ── */}
        <div className="flex flex-col sm:flex-row items-center justify-between gap-4 py-6 border-t border-white/10">
          {/* Copyright */}
          <p className="text-xs text-white/25 order-2 sm:order-1">
            © {new Date().getFullYear()} InnovateX AI, Inc. All rights reserved.
          </p>

          {/* Legal links */}
          <nav
            aria-label="Legal links"
            className="flex flex-wrap items-center justify-center gap-x-5 gap-y-1 order-1 sm:order-2"
          >
            {[
              { label: "Privacy Policy", href: "/privacy" },
              { label: "Terms of Service", href: "/terms" },
              { label: "Cookie Settings", href: "/cookies" },
              { label: "Accessibility",   href: "/accessibility" },
            ].map(({ label, href }) => (
              <Link
                key={label}
                href={href}
                className="text-xs text-white/25 hover:text-white/50 transition-colors"
              >
                {label}
              </Link>
            ))}
          </nav>
        </div>
      </div>
    </footer>
  );
}
