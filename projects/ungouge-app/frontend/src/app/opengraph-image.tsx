import { ImageResponse } from 'next/og';

export const runtime = 'edge';

export const alt = 'UnGouge.ai — Independent Contractor Quote Verification';
export const size = { width: 1200, height: 630 };
export const contentType = 'image/png';

export default async function Image() {
  return new ImageResponse(
    (
      <div
        style={{
          background: 'linear-gradient(135deg, #2563eb 0%, #1d4ed8 100%)',
          width: '100%',
          height: '100%',
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'center',
          justifyContent: 'center',
          padding: '60px',
        }}
      >
        {/* Logo / brand area */}
        <div
          style={{
            display: 'flex',
            alignItems: 'center',
            marginBottom: '30px',
          }}
        >
          <div
            style={{
              width: '60px',
              height: '60px',
              borderRadius: '12px',
              background: 'rgba(255,255,255,0.2)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              marginRight: '16px',
              fontSize: '32px',
            }}
          >
            🛡️
          </div>
          <span
            style={{
              fontSize: '36px',
              fontWeight: 700,
              color: 'white',
              letterSpacing: '-0.5px',
            }}
          >
            UnGouge.ai
          </span>
        </div>

        {/* Headline */}
        <div
          style={{
            fontSize: '56px',
            fontWeight: 800,
            color: 'white',
            textAlign: 'center',
            lineHeight: 1.15,
            maxWidth: '900px',
            marginBottom: '24px',
          }}
        >
          Stop Getting Gouged on Contractor Quotes
        </div>

        {/* Subline */}
        <div
          style={{
            fontSize: '24px',
            color: 'rgba(255,255,255,0.85)',
            textAlign: 'center',
            maxWidth: '700px',
            lineHeight: 1.4,
            marginBottom: '40px',
          }}
        >
          Instant, BLS-backed price verification for homeowners. No lead gen. No contractor kickbacks.
        </div>

        {/* Stats bar */}
        <div
          style={{
            display: 'flex',
            gap: '40px',
            background: 'rgba(255,255,255,0.15)',
            borderRadius: '16px',
            padding: '20px 40px',
          }}
        >
          <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
            <span style={{ fontSize: '28px', fontWeight: 700, color: 'white' }}>$4,127</span>
            <span style={{ fontSize: '14px', color: 'rgba(255,255,255,0.7)' }}>Avg. Savings</span>
          </div>
          <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
            <span style={{ fontSize: '28px', fontWeight: 700, color: 'white' }}>10,000+</span>
            <span style={{ fontSize: '14px', color: 'rgba(255,255,255,0.7)' }}>Homeowners</span>
          </div>
          <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
            <span style={{ fontSize: '28px', fontWeight: 700, color: 'white' }}>$19.99</span>
            <span style={{ fontSize: '14px', color: 'rgba(255,255,255,0.7)' }}>Per Report</span>
          </div>
        </div>
      </div>
    ),
    { ...size }
  );
}
