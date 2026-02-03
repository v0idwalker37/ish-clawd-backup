import { AlertTriangle, CheckCircle, AlertCircle, XCircle } from 'lucide-react';

interface LineItemAnalysis {
  item_name: string;
  quoted_price: number;
  fair_price_low: number;
  fair_price_high: number;
  assessment: 'fair' | 'slightly_high' | 'high' | 'gouging';
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
          bg: 'bg-success/10',
          border: 'border-success',
          text: 'text-success',
          icon: CheckCircle,
          label: 'Fair Price',
        };
      case 'slightly_high':
        return {
          bg: 'bg-warning/10',
          border: 'border-warning',
          text: 'text-warning',
          icon: AlertCircle,
          label: 'Slightly High',
        };
      case 'high':
        return {
          bg: 'bg-orange-100',
          border: 'border-orange-500',
          text: 'text-orange-700',
          icon: AlertTriangle,
          label: 'High',
        };
      case 'gouging':
        return {
          bg: 'bg-danger/10',
          border: 'border-danger',
          text: 'text-danger',
          icon: XCircle,
          label: 'Potential Gouge',
        };
      default:
        return {
          bg: 'bg-gray-100',
          border: 'border-gray-300',
          text: 'text-gray-700',
          icon: AlertCircle,
          label: 'Unknown',
        };
    }
  };

  const style = getAssessmentStyle(lineItem.assessment);
  const Icon = style.icon;
  const overpayment = lineItem.quoted_price - lineItem.fair_price_high;
  const percentOver = ((overpayment / lineItem.fair_price_high) * 100).toFixed(0);

  return (
    <div className={`card border-2 ${style.border}`}>
      <div className="flex justify-between items-start mb-4">
        <div className="flex-1">
          <h3 className="text-xl font-bold mb-1">{lineItem.item_name}</h3>
          <div className={`inline-flex items-center px-3 py-1 rounded-full text-sm font-semibold ${style.bg} ${style.text}`}>
            <Icon className="w-4 h-4 mr-1" />
            {style.label}
          </div>
        </div>
        <div className="text-right">
          <p className="text-sm text-gray-600 mb-1">Quoted Price</p>
          <p className="text-2xl font-bold">${lineItem.quoted_price.toLocaleString()}</p>
        </div>
      </div>

      <div className="grid md:grid-cols-3 gap-4 mb-4">
        <div>
          <p className="text-sm text-gray-600 mb-1">Fair Range (Low)</p>
          <p className="text-lg font-semibold text-success">
            ${lineItem.fair_price_low.toLocaleString()}
          </p>
        </div>
        <div>
          <p className="text-sm text-gray-600 mb-1">Fair Range (High)</p>
          <p className="text-lg font-semibold text-success">
            ${lineItem.fair_price_high.toLocaleString()}
          </p>
        </div>
        {overpayment > 0 && (
          <div>
            <p className="text-sm text-gray-600 mb-1">Potential Overpayment</p>
            <p className="text-lg font-semibold text-danger">
              ${overpayment.toLocaleString()} ({percentOver}%)
            </p>
          </div>
        )}
      </div>

      <div className="p-4 bg-gray-50 rounded-lg mb-4">
        <p className="text-sm font-semibold text-gray-700 mb-2">Analysis:</p>
        <p className="text-gray-700">{lineItem.explanation}</p>
      </div>

      {(lineItem.bls_rate || lineItem.material_cost) && (
        <div className="grid md:grid-cols-2 gap-4 text-sm">
          {lineItem.bls_rate && (
            <div className="flex justify-between p-3 bg-primary-50 rounded">
              <span className="text-gray-700">BLS Labor Rate:</span>
              <span className="font-semibold">${lineItem.bls_rate}/hr</span>
            </div>
          )}
          {lineItem.material_cost && (
            <div className="flex justify-between p-3 bg-primary-50 rounded">
              <span className="text-gray-700">Material Cost (est):</span>
              <span className="font-semibold">${lineItem.material_cost.toLocaleString()}</span>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
