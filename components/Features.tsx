import { type LucideIcon, Bot, MessageSquare, TrendingUp, BarChart3, ShieldCheck, Puzzle, Rocket, Clock, Globe, BookOpen } from "lucide-react";

// ─── Types ────────────────────────────────────────────────────────────────────
interface Feature {
  icon: LucideIcon;
  iconBg: string;
  iconColor: string;
  title: string;
  description: string;
  badge?: string;
  badgeColor?: string;
  href: string;
}

// ─── Feature data ─────────────────────────────────────────────────────────────
const PRIMARY_FEATURES: Feature[] = [
  {
    icon: Bot,
    iconBg:    "bg-blue-500/10",
    iconColor: "text-blue-500 dark:text-blue-400",
    title:       "AI Project Matching",
    description: "ML-powered compatibility scoring connects you with ideal collaborators, co-investigators, and industry partners across all sectors automatically.",
    badge:      "AI-Powered",
    badgeColor: "bg-blue-50 dark:bg-blue-500/10 text-blue-600 dark:text-blue-400 border-blue-200 dark:border-blue-500/20",
    href: "#ai",
  },
  {
    icon: MessageSquare,
    iconBg:    "bg-purple-500/10",
    iconColor: "text-purple-500 dark:text-purple-400",
    title:       "Real-Time Collaboration",
    description: "Integrated chat, HD video calls, shared whiteboards, and live document co-editing — everything your cross-sector team needs in one workspace.",
    href: "#features",
  },
  {
    icon: TrendingUp,
    iconBg:    "bg-green-500/10",
    iconColor: "text-green-600 dark:text-green-400",
    title:       "Smart Funding Discovery",
    description: "Our AI continuously scans 10,000+ active grants, fellowships, and investment opportunities and ranks them by alignment with your project goals.",
    badge:      "New",
    badgeColor: "bg-green-50 dark:bg-green-500/10 text-green-600 dark:text-green-400 border-green-200 dark:border-green-500/20",
    href: "#features",
  },
  {
    icon: BarChart3,
    iconBg:    "bg-orange-500/10",
    iconColor: "text-orange-500 dark:text-orange-400",
    title:       "Innovation Score",
    description: "A composite real-time metric across project health, team engagement, milestone velocity, and sector diversity — gamified to keep teams motivated.",
    href: "#features",
  },
  {
    icon: ShieldCheck,
    iconBg:    "bg-slate-500/10",
    iconColor: "text-slate-600 dark:text-slate-400",
    title:       "Enterprise Security",
    description: "SOC 2 Type II certified. GDPR, HIPAA, and FERPA compliant. End-to-end encrypted workspaces with granular role-based access control.",
    href: "#features",
  },
  {
    icon: Puzzle,
    iconBg:    "bg-indigo-500/10",
    iconColor: "text-indigo-500 dark:text-indigo-400",
    title:       "40+ Integrations",
    description: "Native connections to GitHub, Jira, Slack, Google Workspace, Notion, Zoom, and more — sync your existing tools without friction.",
    href: "#features",
  },
];

const SECONDARY_FEATURES = [
  { icon: Rocket, title: "Fast Onboarding",     description: "Full workspace setup in under 3 minutes." },
  { icon: Clock,  title: "24/7 AI Availability", description: "The AI assistant never sleeps, always ready." },
  { icon: Globe,  title: "Multi-Region",         description: "Data residency in 8 global AWS regions."    },
  { icon: BookOpen, title: "Rich Templates",     description: "200+ project and proposal templates."        },
] as const;

// ─── Sub-components ───────────────────────────────────────────────────────────
function SectionHeader() {
  return (
    <div className="text-center mb-14">
      <span className="inline-block rounded-full bg-purple-50 dark:bg-purple-500/10 border border-purple-200 dark:border-purple-500/20 px-4 py-1 text-xs font-semibold uppercase tracking-widest text-purple-600 dark:text-purple-400 mb-4">
        ✦ Platform Features
      </span>
      <h2 className="text-3xl sm:text-4xl font-extrabold text-gray-900 dark:text-white mb-3">
        Everything you need to{" "}
        <span className="gradient-text">innovate at scale</span>
      </h2>
      <p className="text-base text-gray-500 dark:text-gray-400 max-w-xl mx-auto leading-relaxed">
        One platform. All sectors. Infinite possibilities. Built by researchers and engineers who understand how real innovation happens.
      </p>
    </div>
  );
}

function FeatureCard({ feature }: { feature: Feature }) {
  const Icon = feature.icon;
  return (
    <div className="feature-card group relative flex flex-col gap-4 rounded-2xl border border-gray-200 dark:border-white/10 bg-white dark:bg-white/[0.02] p-6 hover:bg-gray-50/50 dark:hover:bg-white/[0.04]">
      {/* Icon */}
      <div
        className={`flex h-11 w-11 shrink-0 items-center justify-center rounded-xl ${feature.iconBg}`}
        aria-hidden="true"
      >
        <Icon className={`h-5 w-5 ${feature.iconColor}`} strokeWidth={1.75} />
      </div>

      {/* Title + badge */}
      <div className="flex items-start justify-between gap-2">
        <h3 className="text-base font-semibold text-gray-900 dark:text-white leading-snug">
          {feature.title}
        </h3>
        {feature.badge && (
          <span
            className={`shrink-0 rounded-full border px-2 py-0.5 text-[10px] font-semibold ${feature.badgeColor}`}
          >
            {feature.badge}
          </span>
        )}
      </div>

      {/* Description */}
      <p className="text-sm text-gray-500 dark:text-gray-400 leading-relaxed flex-1">
        {feature.description}
      </p>

      {/* Learn more link */}
      <a
        href={feature.href}
        className="inline-flex items-center gap-1 text-xs font-semibold text-blue-600 dark:text-blue-400 opacity-0 group-hover:opacity-100 transition-opacity focus-visible:opacity-100"
        aria-label={`Learn more about ${feature.title}`}
      >
        Learn more
        <svg className="h-3.5 w-3.5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2.5} aria-hidden="true">
          <path strokeLinecap="round" strokeLinejoin="round" d="M13.5 4.5L21 12m0 0l-7.5 7.5M21 12H3" />
        </svg>
      </a>
    </div>
  );
}

function SecondaryFeatureBar() {
  return (
    <div className="mt-10 grid grid-cols-2 sm:grid-cols-4 gap-4">
      {SECONDARY_FEATURES.map(({ icon: Icon, title, description }) => (
        <div
          key={title}
          className="flex items-start gap-3 rounded-xl bg-gray-50 dark:bg-white/[0.03] border border-gray-100 dark:border-white/10 px-4 py-4"
        >
          <div className="mt-0.5 flex h-7 w-7 shrink-0 items-center justify-center rounded-lg bg-white dark:bg-white/10 border border-gray-200 dark:border-white/10">
            <Icon className="h-3.5 w-3.5 text-gray-500 dark:text-gray-400" strokeWidth={1.75} aria-hidden="true" />
          </div>
          <div>
            <p className="text-xs font-semibold text-gray-800 dark:text-gray-200">{title}</p>
            <p className="text-xs text-gray-500 dark:text-gray-500 leading-tight mt-0.5">
              {description}
            </p>
          </div>
        </div>
      ))}
    </div>
  );
}

// ─── Section ──────────────────────────────────────────────────────────────────
export default function Features() {
  return (
    <section
      id="features"
      aria-labelledby="features-heading"
      className="py-24 bg-white dark:bg-[#0D0F14]"
    >
      <div className="mx-auto max-w-6xl px-4 sm:px-6 lg:px-8">
        <SectionHeader />

        {/* Primary 3×2 card grid */}
        <div
          role="list"
          aria-labelledby="features-heading"
          className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-5"
        >
          {PRIMARY_FEATURES.map((feature) => (
            <div key={feature.title} role="listitem">
              <FeatureCard feature={feature} />
            </div>
          ))}
        </div>

        {/* Secondary feature bar */}
        <SecondaryFeatureBar />

        {/* Bottom comparison note */}
        <p className="mt-10 text-center text-xs text-gray-400 dark:text-gray-600">
          ✦ Unlike generic project management tools, InnovateX AI is purpose-built for research, innovation, and cross-sector collaboration.
        </p>
      </div>
    </section>
  );
}
