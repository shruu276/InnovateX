import Navbar from "@/components/Navbar";
import Hero from "@/components/Hero";
import Features from "@/components/Features";
import Footer from "@/components/Footer";

// ─── Social-proof stats ───────────────────────────────────────────────────────
const STATS = [
  { value: "12,000+", label: "Active Users" },
  { value: "3,400+",  label: "Projects Launched" },
  { value: "$48M+",   label: "Funding Facilitated" },
  { value: "92%",     label: "Project Success Rate" },
] as const;

// ─── Partner logos (text-based placeholder) ──────────────────────────────────
const PARTNERS = [
  "MIT", "Stanford", "Microsoft", "NASA",
  "Y Combinator", "UN", "EU Commission", "Google",
] as const;

// ─── Testimonials ────────────────────────────────────────────────────────────
const TESTIMONIALS = [
  {
    quote:
      "InnovateX AI helped us secure a $2M NSF grant in 60 days. The AI matched us with the perfect research partners instantly.",
    name: "Dr. Maya Patel",
    role: "Professor, MIT · Biotech Lab",
    initials: "MP",
    featured: true,
  },
  {
    quote:
      "We scaled from idea to pilot with 3 universities, 2 startups, and a government agency — coordinated entirely on InnovateX.",
    name: "James Okafor",
    role: "CEO, ClimateGrid · Y Combinator W23",
    initials: "JO",
    featured: false,
  },
  {
    quote:
      "The AI assistant alone saves our policy team 15 hours per week on research synthesis and report writing.",
    name: "Sarah Müller",
    role: "Innovation Director · EU Commission",
    initials: "SM",
    featured: false,
  },
] as const;

// ─── AI capabilities tab data ─────────────────────────────────────────────────
const AI_CAPABILITIES = [
  {
    icon: "🤖",
    title: "AI Project Assistant",
    description: "Ask anything about your project in natural language.",
    preview: [
      { role: "user",  text: "Analyse my climate-tech problem statement and suggest 3 collaborators." },
      { role: "ai",    text: 'Based on your focus on urban carbon capture, I recommend: Dr. Sarah Chen (MIT Energy Lab), GreenGrid Startups (Berlin), and the EPA Innovation Office. Shall I draft introduction emails?' },
    ],
  },
  {
    icon: "🎯",
    title: "Smart Matching Engine",
    description: "Find ideal collaborators using ML compatibility scoring.",
    preview: [
      { role: "user",  text: "Find researchers with expertise in CRISPR gene-editing for my biotech project." },
      { role: "ai",    text: "Found 14 matches. Top result: Dr. Lena Park (96% match) — Stanford Genomics, 3 prior cross-sector projects, active grant seeker." },
    ],
  },
  {
    icon: "📈",
    title: "Predictive Analytics",
    description: "Forecast project success, timelines, and funding chances.",
    preview: [
      { role: "user",  text: "What is the likelihood of my project receiving NSF funding this cycle?" },
      { role: "ai",    text: "Probability: 74% based on your team profile, research alignment with NSF priorities, and 12 comparable funded projects. I suggest strengthening the broader-impact statement." },
    ],
  },
  {
    icon: "📝",
    title: "Auto Documentation",
    description: "AI generates reports, summaries, and grant narratives.",
    preview: [
      { role: "user",  text: "Generate an executive summary for our Q2 project milestone report." },
      { role: "ai",    text: "Draft ready: 'In Q2, Team InnovateCarbonX achieved 3 of 4 milestones, onboarded 2 industry partners (valued at $340K), and published 1 peer-reviewed paper. On track for Phase 2 funding.'" },
    ],
  },
  {
    icon: "💡",
    title: "Funding Discovery",
    description: "AI scans 10,000+ grants and matches your project.",
    preview: [
      { role: "user",  text: "Show me active grants for renewable energy storage under $500K." },
      { role: "ai",    text: "Found 23 matching opportunities. Top match: DOE ARPA-E OPEN 2025 — $450K, deadline Aug 15. Your project has an 81% alignment score. Want me to start the application?" },
    ],
  },
] as const;

// ─── Page component ───────────────────────────────────────────────────────────
export default function LandingPage() {
  return (
    <>
      <Navbar />
      <main>
        {/* ── Hero ── */}
        <Hero />

        {/* ── Social-proof / Stats strip ── */}
        <section
          id="stats"
          aria-label="Platform statistics and partner logos"
          className="border-y border-gray-200 dark:border-white/10 bg-white dark:bg-[#0D0F14] py-12"
        >
          <div className="mx-auto max-w-6xl px-4 sm:px-6 lg:px-8">
            {/* Partners marquee */}
            <p className="text-center text-xs font-semibold uppercase tracking-widest text-gray-400 mb-6">
              Trusted by teams at leading institutions &amp; companies
            </p>
            <div className="overflow-hidden mb-10">
              <div className="marquee-track select-none">
                {[...PARTNERS, ...PARTNERS].map((name, i) => (
                  <span
                    key={i}
                    className="mx-10 text-sm font-bold text-gray-300 dark:text-gray-600 whitespace-nowrap"
                  >
                    {name}
                  </span>
                ))}
              </div>
            </div>

            {/* Stats counters */}
            <div className="grid grid-cols-2 sm:grid-cols-4 gap-6">
              {STATS.map(({ value, label }) => (
                <div key={label} className="text-center">
                  <p className="text-3xl sm:text-4xl font-extrabold gradient-text tabular-nums">
                    {value}
                  </p>
                  <p className="mt-1 text-sm text-gray-500 dark:text-gray-400">
                    {label}
                  </p>
                </div>
              ))}
            </div>
          </div>
        </section>

        {/* ── Features ── */}
        <Features />

        {/* ── AI Capabilities ── */}
        <section
          id="ai"
          aria-labelledby="ai-heading"
          className="bg-[#0D0F14] py-24"
        >
          <div className="mx-auto max-w-6xl px-4 sm:px-6 lg:px-8">
            <div className="text-center mb-14">
              <span className="inline-block rounded-full bg-purple-500/10 border border-purple-500/20 px-4 py-1 text-xs font-semibold uppercase tracking-widest text-purple-400 mb-4">
                AI Capabilities
              </span>
              <h2
                id="ai-heading"
                className="text-3xl sm:text-4xl font-extrabold text-white"
              >
                Intelligence built into{" "}
                <span className="gradient-text">every workflow</span>
              </h2>
              <p className="mt-3 text-gray-400 max-w-xl mx-auto text-base">
                Five purpose-built AI engines that understand research, innovation, and cross-sector collaboration.
              </p>
            </div>

            {/* Tabs + preview */}
            <div className="flex flex-col lg:flex-row gap-6 items-start">
              {/* Tab list */}
              <div className="flex flex-row lg:flex-col gap-2 w-full lg:w-72 overflow-x-auto lg:overflow-visible pb-2 lg:pb-0 shrink-0">
                {AI_CAPABILITIES.map((cap, i) => (
                  <div
                    key={cap.title}
                    className={`flex-shrink-0 rounded-xl border px-4 py-3 cursor-pointer transition-all duration-200 ${
                      i === 0
                        ? "bg-blue-500/10 border-blue-500/40"
                        : "bg-white/[0.03] border-white/10 hover:bg-white/[0.06]"
                    }`}
                  >
                    <p className={`text-sm font-semibold ${i === 0 ? "text-blue-300" : "text-gray-300"}`}>
                      {cap.icon} {cap.title}
                    </p>
                    <p className="text-xs text-gray-500 mt-0.5 hidden lg:block">
                      {cap.description}
                    </p>
                  </div>
                ))}
              </div>

              {/* Preview panel — shows first capability as static demo */}
              <div className="flex-1 rounded-2xl border border-white/10 bg-white/[0.03] p-5 backdrop-blur-sm min-h-[280px] flex flex-col gap-3">
                <p className="text-xs text-gray-500 font-medium uppercase tracking-widest mb-1">
                  Live Preview — AI Project Assistant
                </p>
                {AI_CAPABILITIES[0].preview.map((msg, i) => (
                  <div
                    key={i}
                    className={`rounded-xl px-4 py-3 text-sm ${
                      msg.role === "user"
                        ? "bg-white/[0.06] border border-white/10 text-gray-300 self-end max-w-[90%]"
                        : "bg-blue-500/10 border border-blue-500/20 text-blue-200 self-start max-w-[95%]"
                    }`}
                  >
                    {msg.role === "ai" && (
                      <span className="font-semibold text-blue-400 mr-1">🤖 AI:</span>
                    )}
                    {msg.text}
                  </div>
                ))}
                <div className="mt-auto flex gap-2">
                  <div className="flex-1 rounded-lg bg-white/[0.05] border border-white/10 px-4 py-2 text-xs text-gray-500">
                    Ask InnovateX AI anything…
                  </div>
                  <button className="rounded-lg bg-blue-600 hover:bg-blue-500 text-white px-4 py-2 text-xs font-semibold transition-colors">
                    Send ↑
                  </button>
                </div>
              </div>
            </div>
          </div>
        </section>

        {/* ── Testimonials ── */}
        <section
          id="testimonials"
          aria-labelledby="testimonials-heading"
          className="bg-gray-50 dark:bg-[#0D0F14]/60 py-24"
        >
          <div className="mx-auto max-w-6xl px-4 sm:px-6 lg:px-8">
            <div className="text-center mb-14">
              <span className="inline-flex items-center gap-1 rounded-full bg-yellow-50 dark:bg-yellow-500/10 border border-yellow-200 dark:border-yellow-500/20 px-4 py-1 text-xs font-semibold text-yellow-600 dark:text-yellow-400 mb-4">
                ★★★★★ 4.9 / 5 from 800+ reviews
              </span>
              <h2
                id="testimonials-heading"
                className="text-3xl sm:text-4xl font-extrabold text-gray-900 dark:text-white"
              >
                Loved by researchers,{" "}
                <span className="gradient-text">startups &amp; governments</span>
              </h2>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              {TESTIMONIALS.map(({ quote, name, role, initials, featured }) => (
                <figure
                  key={name}
                  className={`relative flex flex-col justify-between rounded-2xl border p-6 transition-all duration-200 ${
                    featured
                      ? "border-blue-400/40 bg-white dark:bg-white/[0.04] shadow-xl shadow-blue-500/10"
                      : "border-gray-200 dark:border-white/10 bg-white dark:bg-white/[0.02] hover:border-blue-300 dark:hover:border-blue-500/40"
                  }`}
                >
                  <span className="text-3xl font-serif leading-none text-blue-400 mb-3 block">
                    &ldquo;
                  </span>
                  <blockquote className="text-sm text-gray-600 dark:text-gray-300 leading-relaxed flex-1">
                    {quote}
                  </blockquote>
                  <figcaption className="flex items-center gap-3 mt-5 pt-5 border-t border-gray-100 dark:border-white/10">
                    <div className="w-9 h-9 rounded-full bg-gradient-to-br from-blue-500 to-purple-600 flex items-center justify-center text-white text-xs font-bold shrink-0">
                      {initials}
                    </div>
                    <div>
                      <p className="text-sm font-semibold text-gray-900 dark:text-white">
                        {name}
                      </p>
                      <p className="text-xs text-gray-500 dark:text-gray-400">
                        {role}
                      </p>
                    </div>
                  </figcaption>
                </figure>
              ))}
            </div>
          </div>
        </section>

        {/* ── CTA banner ── */}
        <section
          id="cta"
          aria-labelledby="cta-heading"
          className="py-24 bg-[#0D0F14]"
        >
          <div className="mx-auto max-w-4xl px-4 sm:px-6 lg:px-8">
            <div className="relative overflow-hidden rounded-3xl bg-cta-gradient p-12 text-center">
              {/* Subtle SVG grid overlay */}
              <div
                aria-hidden="true"
                className="pointer-events-none absolute inset-0 hero-grid opacity-30"
              />
              <span className="inline-block rounded-full bg-white/10 border border-white/20 px-4 py-1 text-xs font-semibold text-white/80 uppercase tracking-widest mb-6">
                🚀 Join 12,000+ innovators today
              </span>
              <h2
                id="cta-heading"
                className="text-3xl sm:text-5xl font-extrabold text-white mb-4 leading-tight"
              >
                Ready to Build the Future?
              </h2>
              <p className="text-white/70 text-base sm:text-lg mb-8 max-w-md mx-auto">
                Start your free workspace today. No credit card required. Set up in under 3&nbsp;minutes.
              </p>
              <div className="flex flex-col sm:flex-row gap-3 justify-center">
                <a
                  href="/register"
                  className="inline-flex items-center justify-center gap-2 rounded-xl bg-white text-[#1E3A6E] font-bold px-7 py-3.5 text-sm hover:bg-gray-100 transition-colors focus-visible:outline-white"
                >
                  Start for Free
                  <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2.5}>
                    <path strokeLinecap="round" strokeLinejoin="round" d="M13.5 4.5L21 12m0 0l-7.5 7.5M21 12H3" />
                  </svg>
                </a>
                <a
                  href="/demo"
                  className="inline-flex items-center justify-center rounded-xl border border-white/30 bg-white/10 text-white font-semibold px-7 py-3.5 text-sm hover:bg-white/20 transition-colors"
                >
                  Request a Demo
                </a>
              </div>
              <div className="mt-8 flex flex-wrap justify-center gap-x-6 gap-y-2 text-xs text-white/40">
                <span>SOC 2 Certified</span>
                <span>GDPR Compliant</span>
                <span>99.99% Uptime</span>
                <span>Cancel Anytime</span>
              </div>
            </div>
          </div>
        </section>
      </main>

      <Footer />
    </>
  );
}
