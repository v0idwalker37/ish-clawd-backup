'use client';

import Script from 'next/script';
import { useState, useEffect } from 'react';

/**
 * Plausible Analytics — privacy-friendly, cookieless, GDPR-compliant.
 *
 * Plausible doesn't use cookies and doesn't collect personal data, so it's
 * compliant out of the box. However, we still respect the user's cookie-consent
 * preference for the "analytics" category. If they explicitly opt out, we
 * don't load the script.
 *
 * Behaviour:
 *  - No consent cookie yet (first visit) → load Plausible (it's cookieless)
 *  - User accepted analytics → load Plausible
 *  - User rejected analytics → don't load
 *
 * The domain is configurable via NEXT_PUBLIC_PLAUSIBLE_DOMAIN (defaults to
 * "gougealert.com").
 */

const COOKIE_NAME = 'ug_cookie_consent';

interface ConsentPrefs {
  essential: true;
  analytics: boolean;
  marketing: boolean;
}

function readConsentCookie(): ConsentPrefs | null {
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

export default function PlausibleAnalytics() {
  const domain =
    process.env.NEXT_PUBLIC_PLAUSIBLE_DOMAIN || 'gougealert.com';

  const [shouldLoad, setShouldLoad] = useState(false);

  useEffect(() => {
    const check = () => {
      const prefs = readConsentCookie();
      // No cookie yet → user hasn't decided; Plausible is cookieless so load it
      // Explicit analytics=true → load
      // Explicit analytics=false → don't load
      setShouldLoad(prefs === null || prefs.analytics === true);
    };

    check();

    // Listen for consent changes from CookieConsent component
    const handler = (e: Event) => {
      const detail = (e as CustomEvent<ConsentPrefs>).detail;
      setShouldLoad(detail.analytics);
    };

    window.addEventListener('cookie-consent-update', handler);
    return () => window.removeEventListener('cookie-consent-update', handler);
  }, []);

  if (!shouldLoad) return null;

  return (
    <Script
      defer
      data-domain={domain}
      src="https://plausible.io/js/script.js"
      strategy="afterInteractive"
    />
  );
}
