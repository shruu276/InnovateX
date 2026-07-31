"use client";

export default function NewsletterInput() {
  return (
    <form
      onSubmit={(e) => e.preventDefault()}
      className="flex flex-col sm:flex-row lg:flex-col xl:flex-row gap-2 mt-3"
      aria-label="Newsletter sign-up"
      noValidate
    >
      <label htmlFor="footer-email" className="sr-only">
        Email address
      </label>
      <input
        id="footer-email"
        type="email"
        autoComplete="email"
        placeholder="you@example.com"
        required
        className="flex-1 min-w-0 rounded-lg bg-white/5 border border-white/15 px-3.5 py-2 text-sm text-white placeholder-white/30 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-colors"
      />
      <button
        type="submit"
        className="shrink-0 rounded-lg bg-blue-600 hover:bg-blue-500 text-white text-sm font-semibold px-4 py-2 transition-colors focus-visible:outline-white"
      >
        Subscribe
      </button>
    </form>
  );
}
