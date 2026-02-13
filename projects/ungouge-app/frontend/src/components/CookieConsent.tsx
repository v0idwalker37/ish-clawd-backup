'use client';

import { useState, useEffect, useCallback, useRef } from 'react';

// ---------------------------------------------------------------------------
// Types
// ---------------------------------------------------------------------------

export interface CookieConsentPreferences {
  essential: true; // always on
  analytics: boolean;
  marketing: boolean;
}

type ConsentState = 'undecided' | 'decided';

const COOKIE_NAME = 'ug_cookie_consent';
const COOKIE_MAX_AGE_SECONDS = 365 * 24 * 60 * 60; // ~12 months

// ---------------------------------------------------------------------------
// Cookie helpers (vanilla – no dependencies)
// ---------------------------------------------------------------------------

function parseCookie(): CookieConsentPreferences | null {
  if (typeof document === 'undefined') return null;
  const match = document.cookie
    .split('; ')
    .find((row) => row.startsWith(`${COOKIE_NAME}=`));
  if (!match) return null;
  try {
    return JSON.parse(decodeURIComponent(match.split('=')[1]));
  } catch {
    return null;
  }
}

function writeCookie(prefs: CookieConsentPreferences) {
  const value = encodeURIComponent(JSON.stringify(prefs));
  document.cookie = `${COOKIE_NAME}=${value}; path=/; max-age=${COOKIE_MAX_AGE_SECONDS}; SameSite=Lax`;
}

// ---------------------------------------------------------------------------
// Global event bus so the Footer "Cookie Settings" link can re-open the banner
// ---------------------------------------------------------------------------

type Listener = () => void;
const listeners = new Set<Listener>();

export function openCookieSettings() {
  listeners.forEach((fn) => fn());
}

function useOnOpenCookieSettings(callback: Listener) {
  const ref = useRef(callback);
  ref.current = callback;

  useEffect(() => {
    const wrapped = () => ref.current();
    listeners.add(wrapped);
    return () => {
      listeners.delete(wrapped);
    };
  }, []);
}

// ---------------------------------------------------------------------------
// Component
// ---------------------------------------------------------------------------

export default function CookieConsent() {
  const [visible, setVisible] = useState(false);
  const [showCustomize, setShowCustomize] = useState(false);
  const [prefs, setPrefs] = useState<CookieConsentPreferences>({
    essential: true,
    analytics: false,
    marketing: false,
  });
  const bannerRef = useRef<HTMLDivElement>(null);

  // On mount: decide whether to show the banner
  useEffect(() => {
    const stored = parseCookie();
    if (!stored) {
      setVisible(true);
    } else {
      setPrefs(stored);
    }
  }, []);

  // Allow external re-open (e.g. footer link)
  useOnOpenCookieSettings(() => {
    const stored = parseCookie();
    if (stored) setPrefs(stored);
    setShowCustomize(true);
    setVisible(true);
    // Move focus into the banner for accessibility
    requestAnimationFrame(() => bannerRef.current?.focus());
  });

  // ------ actions ------

  const save = useCallback(
    (overridePrefs?: CookieConsentPreferences) => {
      const final = overridePrefs ?? prefs;
      writeCookie(final);
      setPrefs(final);
      setVisible(false);
      setShowCustomize(false);

      // Dispatch a custom event so analytics/marketing scripts can react
      window.dispatchEvent(
        new CustomEvent('cookie-consent-update', { detail: final }),
      );
    },
    [prefs],
  );

  const acceptAll = useCallback(() => {
    save({ essential: true, analytics: true, marketing: true });
  }, [save]);

  const rejectNonEssential = useCallback(() => {
    save({ essential: true, analytics: false, marketing: false });
  }, [save]);

  // ------ render ------

  if (!visible) return null;

  return (
    <div
      ref={bannerRef}
      role="dialog"
      aria-label="Cookie consent"
      aria-modal="false"
      tabIndex={-1}
      className="fixed bottom-0 inset-x-0 z-[9999] pointer-events-none"
    >
      <div className="pointer-events-auto mx-auto max-w-4xl px-4 pb-4">
        <div className="rounded-xl border border-gray-200 bg-white shadow-2xl p-5 sm:p-6">
          {/* Header row */}
          <div className="flex items-start gap-3 mb-3">
            {/* Cookie icon */}
            <span className="text-2xl flex-shrink-0" aria-hidden="true">
              🍪
            </span>
            <div className="flex-1 min-w-0">
              <h2 className="text-base font-semibold text-gray-900 leading-tight">
                We value your privacy
              </h2>
              <p className="text-sm text-gray-600 mt-1 leading-relaxed">
                We use cookies to improve your experience. Essential cookies keep
                the site working. Analytics and marketing cookies are optional —
                you're in control.
              </p>
            </div>
          </div>

          {/* Customise panel (toggle) */}
          {showCustomize && (
            <div className="mb-4 border border-gray-100 rounded-lg bg-gray-50 p-4 space-y-3">
              {/* Essential */}
              <label className="flex items-center justify-between">
                <div>
                  <span className="text-sm font-medium text-gray-900">
                    Essential
                  </span>
                  <p className="text-xs text-gray-500">
                    Required for the site to function. Always active.
                  </p>
                </div>
                <input
                  type="checkbox"
                  checked
                  disabled
                  aria-label="Essential cookies (always enabled)"
                  className="h-5 w-5 rounded border-gray-300 text-blue-600 cursor-not-allowed opacity-60"
                />
              </label>

              {/* Analytics */}
              <label className="flex items-center justify-between cursor-pointer">
                <div>
                  <span className="text-sm font-medium text-gray-900">
                    Analytics
                  </span>
                  <p className="text-xs text-gray-500">
                    Help us understand how visitors use the site.
                  </p>
                </div>
                <input
                  type="checkbox"
                  checked={prefs.analytics}
                  onChange={(e) =>
                    setPrefs((p) => ({ ...p, analytics: e.target.checked }))
                  }
                  aria-label="Analytics cookies"
                  className="h-5 w-5 rounded border-gray-300 text-blue-600 cursor-pointer accent-[#2563EB]"
                />
              </label>

              {/* Marketing */}
              <label className="flex items-center justify-between cursor-pointer">
                <div>
                  <span className="text-sm font-medium text-gray-900">
                    Marketing
                  </span>
                  <p className="text-xs text-gray-500">
                    Used for personalised ads and campaign measurement.
                  </p>
                </div>
                <input
                  type="checkbox"
                  checked={prefs.marketing}
                  onChange={(e) =>
                    setPrefs((p) => ({ ...p, marketing: e.target.checked }))
                  }
                  aria-label="Marketing cookies"
                  className="h-5 w-5 rounded border-gray-300 text-blue-600 cursor-pointer accent-[#2563EB]"
                />
              </label>
            </div>
          )}

          {/* Buttons */}
          <div className="flex flex-col sm:flex-row items-stretch sm:items-center gap-2 sm:gap-3">
            {!showCustomize ? (
              <button
                onClick={() => setShowCustomize(true)}
                className="order-3 sm:order-1 text-sm font-medium text-gray-600 hover:text-gray-900 underline underline-offset-2 transition-colors px-1 py-1.5 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-blue-500 focus-visible:ring-offset-2 rounded"
                aria-label="Customise cookie preferences"
              >
                Customise
              </button>
            ) : (
              <button
                onClick={() => save()}
                className="order-3 sm:order-1 text-sm font-semibold rounded-lg border border-[#2563EB] text-[#2563EB] hover:bg-blue-50 px-5 py-2.5 transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-blue-500 focus-visible:ring-offset-2"
                aria-label="Save cookie preferences"
              >
                Save Preferences
              </button>
            )}

            <button
              onClick={rejectNonEssential}
              className="order-2 text-sm font-semibold rounded-lg border border-gray-300 text-gray-700 hover:bg-gray-50 px-5 py-2.5 transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-blue-500 focus-visible:ring-offset-2"
              aria-label="Reject non-essential cookies"
            >
              Reject Non-Essential
            </button>

            <button
              onClick={acceptAll}
              className="order-1 sm:order-3 text-sm font-semibold rounded-lg bg-[#2563EB] text-white hover:bg-blue-700 px-5 py-2.5 transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-blue-500 focus-visible:ring-offset-2"
              aria-label="Accept all cookies"
            >
              Accept All
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
