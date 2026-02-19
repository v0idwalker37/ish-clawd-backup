'use client';

interface PriceGaugeProps {
  quotedPrice: number;
  fairLow: number;
  fairHigh: number;
}

export default function PriceGauge({ quotedPrice, fairLow, fairHigh }: PriceGaugeProps) {
  const maxPrice = Math.max(quotedPrice, fairHigh * 1.5);
  const quotedPercent = (quotedPrice / maxPrice) * 100;
  const fairLowPercent = (fairLow / maxPrice) * 100;
  const fairHighPercent = (fairHigh / maxPrice) * 100;

  let statusColor: string;
  let statusText: string;
  let statusSubtext: string | null = null;

  if (quotedPrice <= fairHigh) {
    statusColor = 'bg-emerald-500';
    statusText = '✅ Fair Price';
  } else if (quotedPrice <= fairHigh * 1.15) {
    statusColor = 'bg-amber-500';
    statusText = '⚠️ Slightly High';
    statusSubtext = `$${(quotedPrice - fairHigh).toLocaleString()} over fair market value`;
  } else if (quotedPrice <= fairHigh * 1.35) {
    statusColor = 'bg-orange-600';
    statusText = '🔶 High Price';
    statusSubtext = `$${(quotedPrice - fairHigh).toLocaleString()} over fair market value`;
  } else {
    statusColor = 'bg-red-600';
    statusText = '🚨 Possible Gouge';
    statusSubtext = `$${(quotedPrice - fairHigh).toLocaleString()} over fair market value`;
  }

  return (
    <div className="py-6">
      <h3 className="text-lg font-semibold mb-4 text-center">Price Assessment</h3>

      {/* Gauge */}
      <div className="relative h-14 bg-gray-100 rounded-full overflow-hidden mb-4 shadow-inner">
        {/* Fair range zone — vivid green */}
        <div
          className="absolute h-full bg-emerald-400"
          style={{
            left: `${fairLowPercent}%`,
            width: `${fairHighPercent - fairLowPercent}%`,
          }}
        />

        {/* Warning zone — vivid amber */}
        <div
          className="absolute h-full bg-amber-400"
          style={{
            left: `${fairHighPercent}%`,
            width: `${Math.min(15, 100 - fairHighPercent)}%`,
          }}
        />

        {/* Danger zone — vivid red */}
        <div
          className="absolute h-full bg-red-500"
          style={{
            left: `${Math.min(fairHighPercent + 15, 100)}%`,
            width: `${Math.max(0, 100 - fairHighPercent - 15)}%`,
          }}
        />

        {/* Quoted price marker */}
        <div
          className="absolute top-0 bottom-0 w-1.5 bg-gray-900 z-10 rounded-full shadow-lg"
          style={{ left: `${Math.min(quotedPercent, 98)}%` }}
        >
          <div className="absolute -top-9 left-1/2 -translate-x-1/2 whitespace-nowrap">
            <div className="bg-gray-900 text-white text-xs font-bold px-3 py-1.5 rounded-lg shadow-md">
              Your Quote: ${quotedPrice.toLocaleString()}
            </div>
          </div>
        </div>
      </div>

      {/* Labels */}
      <div className="relative h-10 mt-2">
        <div
          className="absolute text-xs text-gray-600"
          style={{ left: `${fairLowPercent}%`, transform: 'translateX(-50%)' }}
        >
          <div className="font-bold text-emerald-700">${fairLow.toLocaleString()}</div>
          <div className="text-gray-500">Fair Low</div>
        </div>
        <div
          className="absolute text-xs text-gray-600"
          style={{ left: `${fairHighPercent}%`, transform: 'translateX(-50%)' }}
        >
          <div className="font-bold text-emerald-700">${fairHigh.toLocaleString()}</div>
          <div className="text-gray-500">Fair High</div>
        </div>
      </div>

      {/* Status */}
      <div className={`mt-4 p-4 rounded-xl text-white text-center ${statusColor} shadow-lg`}>
        <p className="text-2xl font-bold">{statusText}</p>
        {statusSubtext && (
          <p className="text-sm mt-1 opacity-90">{statusSubtext}</p>
        )}
      </div>
    </div>
  );
}
