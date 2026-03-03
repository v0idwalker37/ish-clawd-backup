import { ImageResponse } from 'next/og';

export const runtime = 'edge';

export const alt = 'GougeAlert — Stop overpaying for home improvements — Know Before You Sign';
export const size = { width: 1200, height: 630 };
export const contentType = 'image/png';

export default async function Image() {
  return new ImageResponse(
    (
      <div
        style={{
          background: 'linear-gradient(135deg, #1e3a5f 0%, #1a2e4a 50%, #0f1d30 100%)',
          width: '100%',
          height: '100%',
          display: 'flex',
          flexDirection: 'column',
          alignItems: 'flex-start',
          justifyContent: 'center',
          padding: '80px',
          position: 'relative',
        }}
      >
        {/* Logo + brand + tagline at top */}
        <div
          style={{
            display: 'flex',
            alignItems: 'center',
            marginBottom: '16px',
          }}
        >
          {/* Shield logo */}
          <div
            style={{
              width: '72px',
              height: '72px',
              borderRadius: '16px',
              background: 'rgba(16,185,129,0.15)',
              border: '3px solid #10b981',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              marginRight: '20px',
            }}
          >
            <svg
              width="42"
              height="42"
              viewBox="0 0 24 24"
              fill="none"
              xmlns="http://www.w3.org/2000/svg"
            >
              <path
                d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"
                stroke="#10b981"
                strokeWidth="2.5"
                strokeLinecap="round"
                strokeLinejoin="round"
              />
            </svg>
          </div>
          
          {/* Brand name + tagline */}
          <div style={{ display: 'flex', flexDirection: 'column' }}>
            <span
              style={{
                fontSize: '48px',
                fontWeight: 800,
                color: '#10b981',
                letterSpacing: '-1px',
                lineHeight: 1,
              }}
            >
              GougeAlert
            </span>
            <span
              style={{
                fontSize: '20px',
                color: 'rgba(255,255,255,0.7)',
                marginTop: '6px',
                letterSpacing: '0.5px',
              }}
            >
              Know Before You Sign
            </span>
          </div>
        </div>

        {/* Main headline with accent */}
        <div
          style={{
            fontSize: '68px',
            fontWeight: 800,
            lineHeight: 1.1,
            marginTop: '40px',
            marginBottom: '28px',
            maxWidth: '1000px',
            display: 'flex',
            flexDirection: 'column',
          }}
        >
          <span style={{ color: 'white' }}>Stop overpaying for</span>
          <span style={{ color: '#10b981' }}>home improvements</span>
        </div>

        {/* Subheadline */}
        <div
          style={{
            fontSize: '24px',
            color: 'rgba(255,255,255,0.75)',
            maxWidth: '850px',
            lineHeight: 1.4,
            marginBottom: '20px',
          }}
        >
          Data-driven quote verification · $9.99 per report · 0% lead generation
        </div>
      </div>
    ),
    { ...size }
  );
}
