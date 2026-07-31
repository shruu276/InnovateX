"use client";

import { useEffect } from "react";

// ── Watson Orchestrate agent configuration ────────────────────────────────────
// Values sourced directly from the embed snippet provided by IBM watsonx Orchestrate.
const WXO_CONFIG = {
  orchestrationID:    "62a9ab916d48467e8e363bdc980298b9_b9f2f905-584b-40c6-a3b7-a9fd8e724e7b",
  hostURL:            "https://au-syd.watson-orchestrate.cloud.ibm.com",
  rootElementID:      "root",
  deploymentPlatform: "ibmcloud",
  crn:                "crn:v1:bluemix:public:watsonx-orchestrate:au-syd:a/62a9ab916d48467e8e363bdc980298b9:b9f2f905-584b-40c6-a3b7-a9fd8e724e7b::",
  chatOptions: {
    agentId: "5524b461-0454-4f13-ab6d-ae2bc0087708",
  },
} as const;

// Extend window so TypeScript knows about the globals injected by the loader.
declare global {
  interface Window {
    wxOConfiguration?: typeof WXO_CONFIG;
    wxoLoader?: { init: () => void };
  }
}

/**
 * WatsonAgent
 *
 * Injects the IBM watsonx Orchestrate chat widget into the page.
 *
 * How it works:
 *   1. Writes `window.wxOConfiguration` — the loader reads this on init.
 *   2. Appends the remote `wxoLoader.js` script to `<head>`.
 *   3. Calls `wxoLoader.init()` once the script fires its `load` event.
 *
 * Rendered once inside the root layout so the widget persists across all
 * route navigations without re-mounting.
 *
 * Cleanup: the script tag and window property are removed on unmount so
 * hot-reload in development doesn't stack duplicate widgets.
 */
export default function WatsonAgent() {
  useEffect(() => {
    // Guard: skip if already initialised (e.g. HMR double-invoke in dev)
    if (document.getElementById("wxo-loader-script")) return;

    // 1. Publish configuration before the loader script runs
    window.wxOConfiguration = WXO_CONFIG;

    // 2. Build and append the loader <script>
    const loaderURL = `${WXO_CONFIG.hostURL}/wxochat/wxoLoader.js?embed=true`;
    const script = document.createElement("script");
    script.id = "wxo-loader-script";
    script.src = loaderURL;
    script.async = true;

    script.addEventListener("load", () => {
      window.wxoLoader?.init();
    });

    script.addEventListener("error", () => {
      console.warn(
        "[WatsonAgent] Failed to load wxoLoader.js — chat widget unavailable."
      );
    });

    document.head.appendChild(script);

    // 3. Cleanup on unmount (development HMR / strict-mode double effect)
    return () => {
      document.getElementById("wxo-loader-script")?.remove();
      delete window.wxOConfiguration;
    };
  }, []); // run once on mount

  // This component renders no visible DOM — the widget iframe is injected
  // by the loader script itself into the body.
  return null;
}
