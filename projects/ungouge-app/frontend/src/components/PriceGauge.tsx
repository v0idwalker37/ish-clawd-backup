'use client';

interface PriceGaugeProps {
  quotedPrice: number;
  fairLow: number;
  fairHigh: number;
}

export default function PriceGauge({ quotedPrice, fairLow, fairHigh }: PriceGaugeProps) {
  // Calculate the position and status
  const maxPrice = Math.max(quotedPrice, fairHigh * 1.5);
  const quotedPercent = (quotedPrice / maxPrice) * 100;
  const fairLowPercent = (fairLow / maxPrice) * 100;
  const fairHighPercent = (fairHigh / maxPrice) * 100;

  let status: 'fair' | 'slightly_high' | 'high' | 'gouging';
  let statusColor: string;
  let statusText: string;

  if (quotedPrice <= fairHigh) {
    status = 'fair';
    statusColor = 'bg-success';
    statusText = 'Fair Price';
  } else if (quotedPrice <= fairHigh * 1.15) {
    status = 'slightly_high';
    statusColor = 'bg-warning';
    statusText = 'Slightly High';
  } else if (quotedPrice <= fairHigh * 1.35) {
    status = 'high';
    statusColor = 'bg-orange-500';
    statusText = 'High Price';
  } else {
    status = 'gouging';
    statusColor = 'bg-danger';
    statusText = 'Potential Gouge';
  }

  return (
    <div className="py-6">
      <h3 className="text-lg font-semibold mb-4 text-center">Price Assessment</h3>
      
      {/* Gauge */}
      <div className="relative h-12 bg-gray-200 rounded-full overflow-hidden mb-4">
        {/* Fair range zone */}
        <div
          className="absolute h-full bg-success/30"
          style={{
            left: `${fairLowPercent}%`,
            width: `${fairHighPercent - fairLowPercent}%`,
          }}
        />
        
        {/* Warning zone */}
        <div
          className="absolute h-full bg-warning/20"
          style={{
            left: `${fairHighPercent}%`,
            width: `${Math.min(15, 100 - fairHighPercent)}%`,
          }}
        />
        
        {/* Danger zone */}
        <div
          className="absolute h-full bg-danger/20"
          style={{
            left: `${Math.min(fairHighPercent + 15, 100)}%`,
            width: `${Math.max(0, 100 - fairHighPercent - 15)}%`,
          }}
        />

        {/* Quoted price marker */}
        <div
          className="absolute top-0 bottom-0 w-1 bg-gray-900 z-10"
          style={{ left: `${quotedPercent}%` }}
        >
          <div className="absolute -top-8 left-1/2 -translate-x-1/2 whitespace-nowrap">
            <div className="bg-gray-900 text-white text-xs font-semibold px-2 py-1 rounded">
              Your Quote
            </div>
          </div>
        </div>
      </div>

      {/* Labels */}
      <div className="relative h-8">
        <div
          className="absolute text-xs text-gray-600"
          style={{ left: `${fairLowPercent}%`, transform: 'translateX(-50%)' }}
        >
          <div className="font-semibold">${fairLow.toLocaleString()}</div>
          <div>Fair Low</div>
        </div>
        <div
          className="absolute text-xs text-gray-600"
          style={{ left: `${fairHighPercent}%`, transform: 'translateX(-50%)' }}
        >
          <div className="font-semibold">${fairHigh.toLocaleString()}</div>
          <div>Fair High</div>
        </div>
      </div>

      {/* Status */}
      <div className={`mt-6 p-4 rounded-lg text-white text-center ${statusColor}`}>
        <p className="text-2xl font-bold">{statusText}</p>
        {status !== 'fair' && (
          <p className="text-sm mt-1 opacity-90">
            ${(quotedPrice - fairHigh).toLocaleString()} over fair market value
          </p>
        )}
      </div>
    </div>
  );
}
