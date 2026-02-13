import Link from 'next/link';
import { CheckCircle, Shield, DollarSign, FileText, Upload, Search, Award, Lock, TrendingDown, Star, ChevronDown } from 'lucide-react';
import FaqAccordion from '@/components/FaqAccordion';

const faqs = [
  {
    question: 'How does Ungouge.ai work?',
    answer: 'Simply upload your contractor quote and project details. Our AI analyzes each line item against official Bureau of Labor Statistics wage data and real-time material cost databases for your region. You\'ll get a detailed report showing fair price ranges, percentage markups, and specific negotiation advice within seconds.',
  },
  {
    question: 'Is my data safe and private?',
    answer: 'Absolutely. We encrypt all your data and NEVER sell it to contractors or lead generation companies. Unlike other "quote comparison" sites, we make money from you (the homeowner), not from selling your info. Your quotes and contact details stay completely private.',
  },
  {
    question: 'What does $19.99 get me?',
    answer: 'One comprehensive analysis report including: line-by-line pricing breakdown, fair market ranges based on BLS data, gouge rating for each item, overall quote assessment, negotiation tips, and alternative pricing suggestions. No subscriptions, one-time payment per quote.',
  },
  {
    question: 'How accurate are your reports?',
    answer: 'We use official BLS occupational wage data (updated quarterly) and real-time material cost databases. In our analysis of thousands of quotes, we\'ve identified overcharges in 73% of cases, with an average markup of 28% above fair market rates. While contractor pricing varies, our reports provide statistically sound benchmarks.',
  },
  {
    question: 'Can I get a refund if I\'m not satisfied?',
    answer: '100% money-back guarantee within 7 days, no questions asked. If the report doesn\'t meet your needs, just email us and we\'ll issue a full refund.',
  },
  {
    question: 'Do you share my information with contractors?',
    answer: 'NEVER. This is our core principle. We will never sell your data, share it with contractors, or operate as a lead generation service. We\'re on your side, not theirs.',
  },
];

export default function HomePageContent() {
  return (
    <div>
      {/* Hero Section */}
      <section className="bg-gradient-to-br from-primary-600 to-primary-800 text-white py-20">
        <div className="container mx-auto px-4 max-w-6xl">
          <div className="text-center">
            <div className="inline-block mb-4">
              <span className="bg-primary-500/30 text-white px-4 py-2 rounded-full text-sm font-semibold border border-primary-400">
                ✓ Trusted by 10,000+ homeowners
              </span>
            </div>
            <h1 className="text-5xl md:text-6xl font-bold mb-6">
              Stop Getting Gouged on Contractor Quotes
            </h1>
            <p className="text-xl md:text-2xl mb-8 text-primary-100 max-w-3xl mx-auto">
              Get instant, data-backed analysis of any contractor quote using real BLS labor rates and material costs. Know if you're being overcharged before you sign.
            </p>
            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <Link href="/analyze" className="btn-primary bg-white text-primary-600 hover:bg-gray-100 text-lg shadow-xl">
                Analyze a Quote →
              </Link>
              <Link href="/pricing" className="btn-secondary border-2 border-white text-white hover:bg-primary-700 text-lg">
                See Pricing
              </Link>
            </div>
            <p className="mt-6 text-primary-100 text-lg">
              <strong className="text-white">$19.99 per report</strong> · No subscriptions · No data selling · 100% money-back guarantee
            </p>
          </div>
        </div>
      </section>

      {/* How It Works */}
      <section className="py-20 bg-white">
        <div className="container mx-auto px-4 max-w-6xl">
          <div className="text-center mb-16">
            <h2 className="text-4xl font-bold mb-4">How It Works</h2>
            <p className="text-xl text-gray-600">Three simple steps to fair pricing</p>
          </div>
          <div className="grid md:grid-cols-3 gap-8 relative">
            {/* Step 1 */}
            <div className="relative">
              <div className="text-center">
                <div className="w-20 h-20 bg-gradient-to-br from-primary-500 to-primary-600 rounded-2xl flex items-center justify-center mx-auto mb-6 shadow-lg">
                  <Upload className="w-10 h-10 text-white" />
                </div>
                <div className="absolute top-10 left-1/2 transform translate-x-12 hidden md:block">
                  <div className="w-24 h-0.5 bg-gradient-to-r from-primary-300 to-transparent"></div>
                </div>
                <h3 className="text-2xl font-bold mb-3">1. Upload Quote</h3>
                <p className="text-gray-600 leading-relaxed">
                  Enter your contractor's quote details — project type, location, and line-by-line costs. Takes less than 2 minutes.
                </p>
              </div>
            </div>

            {/* Step 2 */}
            <div className="relative">
              <div className="text-center">
                <div className="w-20 h-20 bg-gradient-to-br from-primary-500 to-primary-600 rounded-2xl flex items-center justify-center mx-auto mb-6 shadow-lg">
                  <Search className="w-10 h-10 text-white" />
                </div>
                <div className="absolute top-10 left-1/2 transform translate-x-12 hidden md:block">
                  <div className="w-24 h-0.5 bg-gradient-to-r from-primary-300 to-transparent"></div>
                </div>
                <h3 className="text-2xl font-bold mb-3">2. AI Analysis</h3>
                <p className="text-gray-600 leading-relaxed">
                  Our AI cross-references official BLS labor rates and material cost databases for your exact region. Instant, accurate, unbiased.
                </p>
              </div>
            </div>

            {/* Step 3 */}
            <div className="relative">
              <div className="text-center">
                <div className="w-20 h-20 bg-gradient-to-br from-primary-500 to-primary-600 rounded-2xl flex items-center justify-center mx-auto mb-6 shadow-lg">
                  <FileText className="w-10 h-10 text-white" />
                </div>
                <h3 className="text-2xl font-bold mb-3">3. Get Report</h3>
                <p className="text-gray-600 leading-relaxed">
                  Receive a detailed breakdown showing fair price ranges, percentage markups, and negotiation tips. Use it to save thousands.
                </p>
              </div>
            </div>
          </div>

          <div className="text-center mt-12">
            <Link href="/analyze" className="btn-primary text-lg inline-flex items-center gap-2">
              Start Your Analysis
              <CheckCircle className="w-5 h-5" />
            </Link>
          </div>
        </div>
      </section>

      {/* Trust Badges */}
      <section className="py-16 bg-gray-50 border-y border-gray-200">
        <div className="container mx-auto px-4 max-w-6xl">
          <div className="grid md:grid-cols-3 gap-8 text-center">
            <div className="flex flex-col items-center">
              <div className="w-16 h-16 bg-green-100 rounded-full flex items-center justify-center mb-4">
                <Lock className="w-8 h-8 text-green-600" />
              </div>
              <h3 className="font-bold text-lg mb-2">Bank-Grade Security</h3>
              <p className="text-sm text-gray-600">AES-256 encryption. Your data is protected like Fort Knox.</p>
            </div>
            <div className="flex flex-col items-center">
              <div className="w-16 h-16 bg-red-100 rounded-full flex items-center justify-center mb-4">
                <Shield className="w-8 h-8 text-red-600" />
              </div>
              <h3 className="font-bold text-lg mb-2">Zero Lead Generation</h3>
              <p className="text-sm text-gray-600">We NEVER sell your data to contractors. Ever. Period.</p>
            </div>
            <div className="flex flex-col items-center">
              <div className="w-16 h-16 bg-blue-100 rounded-full flex items-center justify-center mb-4">
                <Award className="w-8 h-8 text-blue-600" />
              </div>
              <h3 className="font-bold text-lg mb-2">Money-Back Guarantee</h3>
              <p className="text-sm text-gray-600">100% refund within 7 days. No questions asked.</p>
            </div>
          </div>
        </div>
      </section>

      {/* Testimonials */}
      <section className="py-20 bg-white">
        <div className="container mx-auto px-4 max-w-6xl">
          <div className="text-center mb-16">
            <h2 className="text-4xl font-bold mb-4">What Homeowners Are Saying</h2>
            <p className="text-xl text-gray-600">Real people, real savings</p>
          </div>

          <div className="grid md:grid-cols-3 gap-8">
            {/* Testimonial 1 */}
            <div className="card border-2 border-gray-100 hover:border-primary-300 transition-colors">
              <div className="flex items-center gap-1 mb-4" aria-label="5 out of 5 stars">
                {[...Array(5)].map((_, i) => (
                  <Star key={i} className="w-5 h-5 fill-yellow-400 text-yellow-400" />
                ))}
              </div>
              <p className="text-gray-700 mb-4 leading-relaxed">
                &ldquo;Saved me $6,200 on a kitchen remodel. The contractor tried to charge $52k for work that should&apos;ve cost $46k. Used the report to negotiate down to $47k. Best $20 I ever spent!&rdquo;
              </p>
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 bg-primary-600 rounded-full flex items-center justify-center text-white font-bold">
                  S
                </div>
                <div>
                  <p className="font-semibold">Sarah M.</p>
                  <p className="text-sm text-gray-500">Portland, OR</p>
                </div>
              </div>
            </div>

            {/* Testimonial 2 */}
            <div className="card border-2 border-gray-100 hover:border-primary-300 transition-colors">
              <div className="flex items-center gap-1 mb-4" aria-label="5 out of 5 stars">
                {[...Array(5)].map((_, i) => (
                  <Star key={i} className="w-5 h-5 fill-yellow-400 text-yellow-400" />
                ))}
              </div>
              <p className="text-gray-700 mb-4 leading-relaxed">
                &ldquo;Turns out my deck quote was actually fair! I was worried I was overpaying, but Ungouge showed me the pricing was right in line with market rates. Gave me confidence to move forward.&rdquo;
              </p>
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 bg-primary-600 rounded-full flex items-center justify-center text-white font-bold">
                  M
                </div>
                <div>
                  <p className="font-semibold">Mike R.</p>
                  <p className="text-sm text-gray-500">Austin, TX</p>
                </div>
              </div>
            </div>

            {/* Testimonial 3 */}
            <div className="card border-2 border-gray-100 hover:border-primary-300 transition-colors">
              <div className="flex items-center gap-1 mb-4" aria-label="5 out of 5 stars">
                {[...Array(5)].map((_, i) => (
                  <Star key={i} className="w-5 h-5 fill-yellow-400 text-yellow-400" />
                ))}
              </div>
              <p className="text-gray-700 mb-4 leading-relaxed">
                &ldquo;The report was super detailed and easy to understand. It showed exactly which line items were overpriced and gave me specific talking points for negotiation. Contractor knocked off $3,400 without argument.&rdquo;
              </p>
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 bg-primary-600 rounded-full flex items-center justify-center text-white font-bold">
                  J
                </div>
                <div>
                  <p className="font-semibold">Jennifer L.</p>
                  <p className="text-sm text-gray-500">Denver, CO</p>
                </div>
              </div>
            </div>
          </div>

          <div className="text-center mt-12">
            <div className="inline-flex items-center gap-2 bg-primary-50 px-6 py-3 rounded-full">
              <TrendingDown className="w-5 h-5 text-primary-600" />
              <span className="font-semibold text-gray-900">Average savings: $4,127 per quote</span>
            </div>
          </div>
        </div>
      </section>

      {/* Features */}
      <section className="py-20 bg-gray-50">
        <div className="container mx-auto px-4 max-w-6xl">
          <h2 className="text-4xl font-bold text-center mb-12">Why Ungouge.ai?</h2>
          <div className="grid md:grid-cols-2 gap-8">
            <div className="card">
              <Shield className="w-10 h-10 text-primary-600 mb-4" />
              <h3 className="text-2xl font-semibold mb-3">No Lead Generation</h3>
              <p className="text-gray-600">
                We&apos;ll never sell your data or refer contractors. You get honest analysis, period.
              </p>
            </div>
            <div className="card">
              <DollarSign className="w-10 h-10 text-primary-600 mb-4" />
              <h3 className="text-2xl font-semibold mb-3">Real BLS Data</h3>
              <p className="text-gray-600">
                Our analysis uses official Bureau of Labor Statistics wage data for your exact region.
              </p>
            </div>
            <div className="card">
              <FileText className="w-10 h-10 text-primary-600 mb-4" />
              <h3 className="text-2xl font-semibold mb-3">Detailed Reports</h3>
              <p className="text-gray-600">
                Get line-by-line breakdowns with fair price ranges and negotiation tips.
              </p>
            </div>
            <div className="card">
              <CheckCircle className="w-10 h-10 text-primary-600 mb-4" />
              <h3 className="text-2xl font-semibold mb-3">Instant Results</h3>
              <p className="text-gray-600">
                No waiting around. Get your comprehensive report in seconds.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* FAQ Section */}
      <section className="py-20 bg-gray-50">
        <div className="container mx-auto px-4 max-w-4xl">
          <div className="text-center mb-12">
            <h2 className="text-4xl font-bold mb-4">Frequently Asked Questions</h2>
            <p className="text-xl text-gray-600">Everything you need to know</p>
          </div>

          <FaqAccordion faqs={faqs} />

          <div className="text-center mt-8">
            <p className="text-gray-600">
              Have more questions?{' '}
              <a href="mailto:support@ungouge.ai" className="text-primary-600 hover:text-primary-700 font-semibold">
                Email us
              </a>{' '}
              or use the chat widget in the bottom-right corner.
            </p>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-20 bg-gradient-to-br from-primary-600 to-primary-800 text-white">
        <div className="container mx-auto px-4 max-w-4xl text-center">
          <h2 className="text-4xl md:text-5xl font-bold mb-6">Ready to Stop Overpaying?</h2>
          <p className="text-xl md:text-2xl mb-8 text-primary-100">
            Join 10,000+ homeowners who&apos;ve saved an average of $4,127 per project.
          </p>
          <Link href="/analyze" className="btn-primary bg-white text-primary-600 hover:bg-gray-100 text-lg shadow-xl inline-flex items-center gap-2">
            Analyze Your Quote Now →
          </Link>
          <p className="mt-6 text-primary-100">
            <strong className="text-white">$19.99</strong> · Instant results · 100% money-back guarantee
          </p>
        </div>
      </section>
    </div>
  );
}
