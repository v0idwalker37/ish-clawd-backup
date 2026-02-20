import type { Metadata } from 'next';
import Link from 'next/link';
import { Check, X } from 'lucide-react';

export const metadata: Metadata = {
  title: 'Pricing — $9.99 Per Quote Analysis',
  description:
    '$9.99 per contractor quote analysis. No subscriptions, no hidden fees, no lead generation. Get a full BLS-backed pricing report with 100% money-back guarantee.',
  alternates: {
    canonical: 'https://ungouge.ai/pricing',
  },
  openGraph: {
    title: 'Simple, Honest Pricing — UnGouge.ai',
    description:
      '$9.99 per quote. Full line-item analysis against BLS data. No subscriptions. 100% money-back guarantee.',
    url: 'https://ungouge.ai/pricing',
  },
};

export default function PricingPage() {
  return (
    <div className="py-12 bg-gray-50">
      <div className="container mx-auto px-4 max-w-6xl">
        <div className="text-center mb-12">
          <h1 className="text-4xl font-bold mb-4">Simple, Honest Pricing</h1>
          <p className="text-xl text-gray-600">
            One price, no subscriptions, no hidden fees.
          </p>
        </div>

        <div className="grid md:grid-cols-3 gap-8 mb-12">
          {/* Single Report */}
          <div className="card border-2 border-gray-200">
            <div className="text-center mb-6">
              <h3 className="text-2xl font-bold mb-2">Single Report</h3>
              <div className="text-5xl font-bold text-primary-600 mb-2">$9.99</div>
              <div className="text-lg text-gray-500 line-through mb-1">$19.99</div>
              <p className="text-sm text-primary-600 font-semibold mb-2">Early Adopter Pricing</p>
              <p className="text-gray-600">Per quote analysis</p>
            </div>
            <ul className="space-y-3 mb-6">
              <li className="flex items-start">
                <Check className="w-5 h-5 text-success mr-2 flex-shrink-0 mt-0.5" />
                <span>Complete line-item analysis</span>
              </li>
              <li className="flex items-start">
                <Check className="w-5 h-5 text-success mr-2 flex-shrink-0 mt-0.5" />
                <span>BLS labor rate verification</span>
              </li>
              <li className="flex items-start">
                <Check className="w-5 h-5 text-success mr-2 flex-shrink-0 mt-0.5" />
                <span>Regional material cost data</span>
              </li>
              <li className="flex items-start">
                <Check className="w-5 h-5 text-success mr-2 flex-shrink-0 mt-0.5" />
                <span>Instant PDF report</span>
              </li>
              <li className="flex items-start">
                <Check className="w-5 h-5 text-success mr-2 flex-shrink-0 mt-0.5" />
                <span>Negotiation tips</span>
              </li>
            </ul>
            <Link href="/analyze" className="btn-primary w-full text-center block">
              Get Started
            </Link>
          </div>

          {/* Bundle - Featured */}
          <div className="card border-4 border-primary-600 relative transform md:scale-105">
            <div className="absolute -top-4 left-1/2 -translate-x-1/2 bg-primary-600 text-white px-4 py-1 rounded-full text-sm font-semibold">
              Best Value
            </div>
            <div className="text-center mb-6">
              <h3 className="text-2xl font-bold mb-2">3-Report Bundle</h3>
              <div className="text-5xl font-bold text-primary-600 mb-2">$49.99</div>
              <p className="text-gray-600">Save $10 · $16.66 per report</p>
            </div>
            <ul className="space-y-3 mb-6">
              <li className="flex items-start">
                <Check className="w-5 h-5 text-success mr-2 flex-shrink-0 mt-0.5" />
                <span>Everything in Single Report</span>
              </li>
              <li className="flex items-start">
                <Check className="w-5 h-5 text-success mr-2 flex-shrink-0 mt-0.5" />
                <span>Compare multiple quotes</span>
              </li>
              <li className="flex items-start">
                <Check className="w-5 h-5 text-success mr-2 flex-shrink-0 mt-0.5" />
                <span>Track different projects</span>
              </li>
              <li className="flex items-start">
                <Check className="w-5 h-5 text-success mr-2 flex-shrink-0 mt-0.5" />
                <span>Reports never expire</span>
              </li>
              <li className="flex items-start">
                <Check className="w-5 h-5 text-success mr-2 flex-shrink-0 mt-0.5" />
                <span>Priority support</span>
              </li>
            </ul>
            <Link href="/analyze?bundle=3" className="btn-primary w-full text-center block">
              Get Bundle
            </Link>
          </div>

          {/* Enterprise */}
          <div className="card border-2 border-gray-200">
            <div className="text-center mb-6">
              <h3 className="text-2xl font-bold mb-2">Enterprise</h3>
              <div className="text-5xl font-bold text-primary-600 mb-2">Custom</div>
              <p className="text-gray-600">For property managers</p>
            </div>
            <ul className="space-y-3 mb-6">
              <li className="flex items-start">
                <Check className="w-5 h-5 text-success mr-2 flex-shrink-0 mt-0.5" />
                <span>Unlimited reports</span>
              </li>
              <li className="flex items-start">
                <Check className="w-5 h-5 text-success mr-2 flex-shrink-0 mt-0.5" />
                <span>API access</span>
              </li>
              <li className="flex items-start">
                <Check className="w-5 h-5 text-success mr-2 flex-shrink-0 mt-0.5" />
                <span>Team accounts</span>
              </li>
              <li className="flex items-start">
                <Check className="w-5 h-5 text-success mr-2 flex-shrink-0 mt-0.5" />
                <span>Custom integrations</span>
              </li>
              <li className="flex items-start">
                <Check className="w-5 h-5 text-success mr-2 flex-shrink-0 mt-0.5" />
                <span>Dedicated support</span>
              </li>
            </ul>
            <a href="mailto:enterprise@ungouge.ai" className="btn-secondary w-full text-center block">
              Contact Sales
            </a>
          </div>
        </div>

        {/* What You're NOT Paying For */}
        <div className="card bg-primary-50 border-2 border-primary-200">
          <h2 className="text-2xl font-bold mb-6 text-center">What You're NOT Paying For</h2>
          <div className="grid md:grid-cols-2 gap-4">
            <div className="flex items-start">
              <X className="w-5 h-5 text-danger mr-2 flex-shrink-0 mt-0.5" />
              <span><strong>No subscriptions</strong> — Pay only when you need a report</span>
            </div>
            <div className="flex items-start">
              <X className="w-5 h-5 text-danger mr-2 flex-shrink-0 mt-0.5" />
              <span><strong>No contractor referrals</strong> — We don't sell your information</span>
            </div>
            <div className="flex items-start">
              <X className="w-5 h-5 text-danger mr-2 flex-shrink-0 mt-0.5" />
              <span><strong>No lead generation</strong> — Your data stays private</span>
            </div>
            <div className="flex items-start">
              <X className="w-5 h-5 text-danger mr-2 flex-shrink-0 mt-0.5" />
              <span><strong>No upsells</strong> — The price you see is what you pay</span>
            </div>
          </div>
        </div>

        {/* FAQ */}
        <div className="mt-12">
          <h2 className="text-3xl font-bold text-center mb-8">Frequently Asked Questions</h2>
          <div className="space-y-6">
            <div className="card">
              <h3 className="text-xl font-semibold mb-2">How accurate are your reports?</h3>
              <p className="text-gray-700">
                Our analysis is based on official BLS wage data and real-time material cost databases. While regional variations exist, our data represents industry-standard fair pricing for your area.
              </p>
            </div>
            <div className="card">
              <h3 className="text-xl font-semibold mb-2">Can I use this to negotiate?</h3>
              <p className="text-gray-700">
                Absolutely! That's exactly what it's for. Our reports provide specific data points you can reference when discussing pricing with contractors.
              </p>
            </div>
            <div className="card">
              <h3 className="text-xl font-semibold mb-2">What if my quote is actually fair?</h3>
              <p className="text-gray-700">
                Great! Then you'll have peace of mind knowing you're getting a fair deal. Many contractors charge fairly—we help you identify which ones.
              </p>
            </div>
            <div className="card">
              <h3 className="text-xl font-semibold mb-2">Do reports expire?</h3>
              <p className="text-gray-700">
                No. Once you purchase a report, you have lifetime access to it. However, market rates change, so we recommend getting fresh analysis for quotes older than 6 months.
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
