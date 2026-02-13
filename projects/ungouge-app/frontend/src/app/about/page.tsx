import type { Metadata } from 'next';
import { Shield, Target, Heart } from 'lucide-react';

export const metadata: Metadata = {
  title: 'About Us — Our Mission to End Contractor Overcharging',
  description:
    'UnGouge.ai was built to protect homeowners from contractor overcharges. Learn about our mission, our data-driven approach using BLS labor rates, and our zero lead-gen promise.',
  alternates: {
    canonical: 'https://ungouge.ai/about',
  },
  openGraph: {
    title: 'About UnGouge.ai — Protecting Homeowners from Overcharges',
    description:
      'We bring transparency to home renovation pricing. No lead gen, no contractor kickbacks — just honest, BLS-backed quote analysis.',
    url: 'https://ungouge.ai/about',
  },
};

export default function AboutPage() {
  return (
    <div className="py-12 bg-gray-50">
      <div className="container mx-auto px-4 max-w-4xl">
        <div className="card mb-8">
          <h1 className="text-4xl font-bold mb-6">About Ungouge.ai</h1>
          <p className="text-xl text-gray-600 mb-6">
            We're on a mission to bring transparency to home renovation pricing.
          </p>
          <p className="text-gray-700 mb-4">
            Every year, homeowners overpay billions of dollars on contractor work—not because contractors are all dishonest, but because information asymmetry makes it impossible to know what's fair.
          </p>
          <p className="text-gray-700 mb-4">
            Ungouge.ai levels the playing field by giving you instant access to the same data contractors use: real Bureau of Labor Statistics wage rates and regional material costs.
          </p>
        </div>

        <div className="grid md:grid-cols-3 gap-6 mb-8">
          <div className="card text-center">
            <Shield className="w-12 h-12 text-primary-600 mx-auto mb-4" />
            <h3 className="text-xl font-semibold mb-3">No Lead Generation</h3>
            <p className="text-gray-600">
              We'll never sell your data, spam you with contractor referrals, or monetize your trust.
            </p>
          </div>
          <div className="card text-center">
            <Target className="w-12 h-12 text-primary-600 mx-auto mb-4" />
            <h3 className="text-xl font-semibold mb-3">Data-Driven</h3>
            <p className="text-gray-600">
              Our analysis is built on official BLS data and real material cost databases—no guesswork.
            </p>
          </div>
          <div className="card text-center">
            <Heart className="w-12 h-12 text-primary-600 mx-auto mb-4" />
            <h3 className="text-xl font-semibold mb-3">Homeowner First</h3>
            <p className="text-gray-600">
              We're here to protect you, not extract more value from you. One fair price per report.
            </p>
          </div>
        </div>

        <div className="card">
          <h2 className="text-2xl font-bold mb-4">Our Approach</h2>
          <div className="space-y-4 text-gray-700">
            <p>
              <strong>Real BLS Data:</strong> We use official Bureau of Labor Statistics wage data, which tracks hourly rates for every construction trade across different metropolitan areas. This is the same data professional estimators use.
            </p>
            <p>
              <strong>Regional Material Costs:</strong> Material prices vary significantly by region and season. Our database tracks current market rates for common construction materials.
            </p>
            <p>
              <strong>Fair Markup Analysis:</strong> We account for reasonable contractor overhead, insurance, and profit margins—typically 20-35%. We're not trying to squeeze contractors; we're identifying price gouging.
            </p>
            <p>
              <strong>AI-Enhanced Analysis:</strong> Our AI reviews each line item, cross-references industry standards, and provides context on what's typical for your project type and location.
            </p>
          </div>
        </div>

        <div className="card mt-8">
          <h2 className="text-2xl font-bold mb-4">What We're NOT</h2>
          <ul className="space-y-3 text-gray-700">
            <li className="flex items-start">
              <span className="text-danger mr-2">✗</span>
              <span>We're not a contractor referral service. We don't take kickbacks.</span>
            </li>
            <li className="flex items-start">
              <span className="text-danger mr-2">✗</span>
              <span>We're not a lead generation platform. Your information stays private.</span>
            </li>
            <li className="flex items-start">
              <span className="text-danger mr-2">✗</span>
              <span>We're not here to replace professional estimates—just to verify them.</span>
            </li>
            <li className="flex items-start">
              <span className="text-danger mr-2">✗</span>
              <span>We're not anti-contractor. Fair contractors benefit from informed customers.</span>
            </li>
          </ul>
        </div>
      </div>
    </div>
  );
}
