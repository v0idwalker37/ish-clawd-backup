import { AlertTriangle, CheckCircle, AlertCircle, XCircle, Zap } from 'lucide-react';

interface LineItemAnalysis {
  item_name: string;
  quoted_price: number;
  fair_price_low: number;
  fair_price_high: number;
  assessment: 'fair' | 'slightly_high' | 'high' | 'gouging' | 'suspiciously_low' | 'unknown';
  explanation: string;
  bls_rate?: number;
  material_cost?: number;
}

interface ReportCardProps {
  lineItem: LineItemAnalysis;
}

export default function ReportCard({ lineItem }: ReportCardProps) {
  const getAssessmentStyle = (assessment: string) => {
    switch (assessment) {
      case 'fair':
        return {
          bg: 'bg-emerald-50',
          border: 'border-emerald-400',
          text: 'text-emerald-700',
          icon: CheckCircle,
          label: '✅ Fair Price',
          barColor: 'bg-emerald-500',
        };
      case 'slightly_high':
        return {
          bg: 'bg-amber-50',
          border: 'border-amber-400',
          text: 'text-amber-700',
          icon: AlertCircle,
          label: '⚠️ Slightly High',
          barColor: 'bg-amber-500',
        };
      case 'high':
        return {
          bg: 'bg-orange-50',
          border: 'border-orange-500',
          text: 'text-orange-700',
          icon: AlertTriangle,
          label: '🔶 High',
          barColor: 'bg-orange-500',
        };
      case 'gouging':
        return {
          bg: 'bg-red-50',
          border: 'border-red-500',
          text: 'text-red-700',
          icon: XCircle,
          label: '🚨 Possible Gouge',
          barColor: 'bg-red-600',
        };
      case 'suspiciously_low':
        return {
          bg: 'bg-blue-50',
          border: 'border-blue-400',
          text: 'text-blue-700',
          icon: Zap,
          label: '⚡ Suspiciously Low',
          barColor: 'bg-blue-500',
        };
      default:
        return {
          bg: 'bg-gray-50',
          border: 'border-gray-300',
          text: 'text-gray-700',
          icon: AlertCircle,
          label: '❓ Unknown',
          barColor: 'bg-gray-400',
        };
    }
  };

  const style = getAssessmentStyle(lineItem.assessment);
  const Icon = style.icon;
  const overpayment = lineItem.quoted_price - lineItem.fair_price_high;
  const percentOver = lineItem.fair_price_high > 0
    ? ((overpayment / lineItem.fair_price_high) * 100).toFixed(0)
    : '0';

  // Mini bar visualization
  const maxVal = Math.max(lineItem.quoted_price, lineItem.fair_price_high) * 1.2;
  const quotedWidth = maxVal > 0 ? (lineItem.quoted_price / maxVal) * 100 : 0;
  const fairHighWidth = maxVal > 0 ? (lineItem.fair_price_high / maxVal) * 100 : 0;
  const fairLowWidth = maxVal > 0 ? (lineItem.fair_price_low / maxVal) * 100 : 0;

  return (
    <div className={`card border-2 ${style.border} shadow-sm hover:shadow-md transition-shadow`}>
      <div className="flex justify-between items-start mb-4">
        <div className="flex-1">
          <h3 className="text-xl font-bold mb-2">{lineItem.item_name}</h3>
          <div className={`inline-flex items-center px-3 py-1.5 rounded-full text-sm font-bold ${style.bg} ${style.text}`}>
            <Icon className="w-4 h-4 mr-1.5" />
            {style.label}
          </div>
        </div>
        <div className="text-right">
          <p className="text-xs text-gray-500 uppercase tracking-wide mb-1">Quoted</p>
          <p className="text-2xl font-bold">${lineItem.quoted_price.toLocaleString()}</p>
        </div>
      </div>

      {/* Mini price comparison bar */}
      <div className="mb-4 p-3 bg-gray-50 rounded-lg">
        <div className="space-y-2">
          <div className="flex items-center gap-3">
            <span className="text-xs text-gray-500 w-16 text-right">Quoted</span>
            <div className="flex-1 h-4 bg-gray-100 rounded-full overflow-hidden">
              <div className={`h-full rounded-full ${style.barColor}`} style={{ width: `${quotedWidth}%` }} />
            </div>
            <span className="text-xs font-semibold w-24 text-right">${lineItem.quoted_price.toLocaleString()}</span>
          </div>
          <div className="flex items-center gap-3">
            <span className="text-xs text-gray-500 w-16 text-right">Fair</span>
            <div className="flex-1 h-4 bg-gray-100 rounded-full overflow-hidden relative">
              <div className="h-full rounded-full bg-emerald-300" style={{ width: `${fairHighWidth}%` }} />
              <div className="absolute top-0 h-full rounded-full bg-emerald-500" style={{ width: `${fairLowWidth}%` }} />
            </div>
            <span className="text-xs font-semibold w-24 text-right text-emerald-700">
              ${lineItem.fair_price_low.toLocaleString()} – ${lineItem.fair_price_high.toLocaleString()}
            </span>
          </div>
        </div>
      </div>

      {/* Overpayment callout */}
      {overpayment > 0 && (
        <div className="mb-4 p-3 bg-red-50 border border-red-200 rounded-lg flex items-center justify-between">
          <span className="text-sm font-semibold text-red-800">Potential Overpayment</span>
          <span className="text-lg font-bold text-red-700">
            ${overpayment.toLocaleString()} ({percentOver}% over)
          </span>
        </div>
      )}

      {/* Explanation */}
      <div className="p-4 bg-gray-50 rounded-lg">
        <p className="text-sm font-semibold text-gray-700 mb-2">💡 Analysis:</p>
        <p className="text-gray-700 leading-relaxed">{lineItem.explanation}</p>
      </div>
    </div>
  );
}
