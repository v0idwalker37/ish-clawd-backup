import Link from 'next/link';
import {
  CheckCircle,
  Shield,
  DollarSign,
  FileText,
  Upload,
  Search,
  Award,
  Lock,
  TrendingDown,
  AlertTriangle,
  BarChart3,
  MapPin,
  Download,
  Eye,
} from 'lucide-react';
import FaqAccordion from '@/components/FaqAccordion';

/* ------------------------------------------------------------------ */
/*  Static data (no client JS needed)                                 */
/* ------------------------------------------------------------------ */

const faqs = [
  {
    question: 'How accurate is the analysis?',
    answer:
      "We cross-reference multiple professional construction estimating databases — including government labor statistics updated quarterly and industry-standard material cost references — calibrated to your zip code. Our engine covers 9,000+ individual line items across 45+ project types. While every project is unique, our reports give you statistically-sound benchmarks backed by real industry pricing data.",
  },
  {
    question: 'What project types do you cover?',
    answer:
      "We cover 45+ project types including kitchen remodels, bathroom renovations, roofing, siding, decks, painting (interior & exterior), HVAC, plumbing, electrical, flooring, fencing, windows, doors, concrete/masonry, landscaping, and more. If we don't cover your project type yet, we'll let you know before you pay.",
  },
  {
    question: 'How long does it take to get my report?',
    answer:
      'Most reports are generated in under 60 seconds. You upload your quote or enter the details, our AI runs the analysis against professional cost databases for your region, and you get your full report immediately. No waiting for a human to review it.',
  },
  {
    question: 'Is my data private?',
    answer:
      'Absolutely. We encrypt all your data with AES-256 and NEVER sell it to contractors, lead generation companies, or anyone else. Unlike other "quote comparison" sites, we make money from you (the homeowner paying $19.99), not from selling your information. Your quotes and contact details stay completely private.',
  },
  {
    question: 'Can I get a refund?',
    answer:
      "100% money-back guarantee within 7 days, no questions asked. If the report doesn't help you, just email support@ungouge.ai and we'll issue a full refund.",
  },
  {
    question: 'Do you share my information with contractors?',
    answer:
      "NEVER. This is our core principle. We will never sell your data, share it with contractors, or operate as a lead generation service. Most 'free quote comparison' sites exist to sell your contact info to contractors who then hound you with calls. We're the opposite — we're on your side, not theirs.",
  },
  {
    question: 'What if my quote is actually fair?',
    answer:
      "Great — then you'll know! Not every quote is overpriced, and knowing yours is fair is just as valuable. Your report confirms the pricing is reasonable, gives you confidence to move forward, and still shows you exactly what each line item should cost so you understand what you're paying for.",
  },
];

/* ------------------------------------------------------------------ */
/*  Page (server component — zero client JS except FaqAccordion)       */
/* ------------------------------------------------------------------ */

export default function HomePageContent() {
  return (
    <div>
      {/* ============================================================ */}
      {/*  HERO                                                        */}
      {/* ============================================================ */}
      <section className="bg-gradient-to-br from-primary-700 via-primary-800 to-primary-900 text-white py-16 md:py-24 relative overflow-hidden">
        {/* subtle background pattern */}
        <div
          className="absolute inset-0 opacity-[0.04]"
          style={{
            backgroundImage:
              'url("data:image/svg+xml,%3Csvg width=\'60\' height=\'60\' viewBox=\'0 0 60 60\' xmlns=\'http://www.w3.org/2000/svg\'%3E%3Cg fill=\'none\' fill-rule=\'evenodd\'%3E%3Cg fill=\'%23ffffff\' fill-opacity=\'1\'%3E%3Cpath d=\'M36 34v-4h-2v4h-4v2h4v4h2v-4h4v-2h-4zm0-30V0h-2v4h-4v2h4v4h2V6h4V4h-4zM6 34v-4H4v4H0v2h4v4h2v-4h4v-2H6zM6 4V0H4v4H0v2h4v4h2V6h4V4H6z\'/%3E%3C/g%3E%3C/g%3E%3C/svg%3E")',
          }}
        />
        <div className="container mx-auto px-4 max-w-6xl relative">
          <div className="text-center max-w-4xl mx-auto">
            {/* Trust chip */}
            <div className="inline-block mb-6">
              <span className="bg-white/10 backdrop-blur text-white px-5 py-2 rounded-full text-sm font-semibold border border-white/20 inline-flex items-center gap-2">
                <Shield className="w-4 h-4" />
                Independent Quote Analysis · No Lead Generation · Ever
              </span>
            </div>

            <h1 className="text-4xl sm:text-5xl md:text-6xl lg:text-7xl font-extrabold mb-6 leading-[1.1] tracking-tight">
              Is Your Contractor&apos;s Quote{' '}
              <span className="text-primary-300">Fair?</span>
            </h1>

            <p className="text-lg sm:text-xl md:text-2xl mb-8 text-primary-100 max-w-2xl mx-auto leading-relaxed">
              Find out in 60&nbsp;seconds. Upload your quote and our AI compares every
              line item against 9,000+ professional cost data points for your
              zip&nbsp;code — so you know <em>exactly</em> what&apos;s fair before you sign.
            </p>

            {/* Primary CTA */}
            <div className="flex flex-col sm:flex-row gap-4 justify-center mb-8">
              <Link
                href="/analyze"
                className="btn-primary bg-white text-primary-700 hover:bg-gray-100 text-lg shadow-xl px-8 py-4 inline-flex items-center justify-center gap-2 font-bold"
              >
                Analyze My Quote
                <span aria-hidden="true">→</span>
              </Link>
              <Link
                href="#how-it-works"
                className="bg-transparent border-2 border-white/60 text-white hover:bg-white/10 text-lg px-8 py-4 rounded-lg font-semibold inline-flex items-center justify-center gap-2 transition-all duration-200 focus:outline-none focus:ring-4 focus:ring-white/30"
              >
                See How It Works
              </Link>
            </div>

            {/* Value prop bullets */}
            <p className="text-primary-200 text-base sm:text-lg mb-10">
              <strong className="text-white">$19.99 per report</strong>
              {' · '}Instant results{' · '}No subscriptions{' · '}
              <strong className="text-white">100% money-back guarantee</strong>
            </p>

            {/* Trust badges */}
            <div className="grid grid-cols-3 gap-6 max-w-2xl mx-auto">
              <div className="flex flex-col items-center gap-2">
                <div className="w-12 h-12 bg-white/10 backdrop-blur rounded-full flex items-center justify-center border border-white/20">
                  <Lock className="w-6 h-6 text-green-300" />
                </div>
                <span className="text-xs sm:text-sm font-semibold text-white">Bank-Grade Encryption</span>
                <span className="text-xs text-primary-200 hidden sm:block">AES-256 · Fort Knox safe</span>
              </div>
              <div className="flex flex-col items-center gap-2">
                <div className="w-12 h-12 bg-white/10 backdrop-blur rounded-full flex items-center justify-center border border-white/20">
                  <Shield className="w-6 h-6 text-red-300" />
                </div>
                <span className="text-xs sm:text-sm font-semibold text-white">Zero Lead Generation</span>
                <span className="text-xs text-primary-200 hidden sm:block">We NEVER sell your data</span>
              </div>
              <div className="flex flex-col items-center gap-2">
                <div className="w-12 h-12 bg-white/10 backdrop-blur rounded-full flex items-center justify-center border border-white/20">
                  <Award className="w-6 h-6 text-blue-300" />
                </div>
                <span className="text-xs sm:text-sm font-semibold text-white">Money-Back Guarantee</span>
                <span className="text-xs text-primary-200 hidden sm:block">100% refund · 7 days</span>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* ============================================================ */}
      {/*  STATS BAR                                                   */}
      {/* ============================================================ */}
      <section className="bg-gray-50 border-b border-gray-200 py-10">
        <div className="container mx-auto px-4 max-w-5xl">
          <div className="grid grid-cols-2 md:grid-cols-4 gap-6 md:gap-8 text-center">
            <div>
              <p className="text-3xl md:text-4xl font-extrabold text-primary-600">9,000+</p>
              <p className="text-sm text-gray-500 mt-1 font-medium">Cost Data Points</p>
            </div>
            <div>
              <p className="text-3xl md:text-4xl font-extrabold text-primary-600">2026</p>
              <p className="text-sm text-gray-500 mt-1 font-medium">Pricing Data</p>
            </div>
            <div>
              <p className="text-3xl md:text-4xl font-extrabold text-primary-600">45+</p>
              <p className="text-sm text-gray-500 mt-1 font-medium">Project Types</p>
            </div>
            <div>
              <p className="text-3xl md:text-4xl font-extrabold text-primary-600">640+</p>
              <p className="text-sm text-gray-500 mt-1 font-medium">Cities Covered</p>
            </div>
          </div>
        </div>
      </section>

      {/* ============================================================ */}
      {/*  ANTI-LEAD-GEN BANNER (key differentiator)                   */}
      {/* ============================================================ */}
      <section className="bg-primary-800 text-white py-5">
        <div className="container mx-auto px-4 max-w-4xl text-center">
          <p className="text-base sm:text-lg font-semibold inline-flex items-center justify-center gap-2 flex-wrap">
            <Shield className="w-5 h-5 text-primary-300 flex-shrink-0" />
            We make $19.99 when you pay us. That&apos;s it.
            <span className="text-primary-200 font-normal">
              No lead gen. No contractor kickbacks. We work for <em>you</em>.
            </span>
          </p>
        </div>
      </section>

      {/* ============================================================ */}
      {/*  HOW IT WORKS                                                */}
      {/* ============================================================ */}
      <section id="how-it-works" className="py-20 bg-white scroll-mt-20">
        <div className="container mx-auto px-4 max-w-6xl">
          <div className="text-center mb-16">
            <h2 className="text-3xl md:text-4xl font-bold mb-4">
              How It Works
            </h2>
            <p className="text-xl text-gray-600">
              Three steps. Under two minutes. Zero bull.
            </p>
          </div>

          <div className="grid md:grid-cols-3 gap-10 relative">
            {/* connector lines (desktop) */}
            <div className="hidden md:block absolute top-10 left-[calc(33.33%+10px)] right-[calc(33.33%+10px)] h-0.5 bg-gradient-to-r from-primary-300 via-primary-400 to-primary-300" />

            {/* Step 1 */}
            <div className="text-center relative">
              <div className="w-20 h-20 bg-gradient-to-br from-primary-500 to-primary-600 rounded-2xl flex items-center justify-center mx-auto mb-6 shadow-lg relative z-10">
                <Upload className="w-10 h-10 text-white" />
              </div>
              <h3 className="text-2xl font-bold mb-3">1. Drop In Your Quote</h3>
              <p className="text-gray-600 leading-relaxed">
                Upload your contractor&apos;s quote (PDF or photo), enter your zip code, and let our AI extract the details. Under 2&nbsp;minutes.
              </p>
            </div>

            {/* Step 2 */}
            <div className="text-center relative">
              <div className="w-20 h-20 bg-gradient-to-br from-primary-500 to-primary-600 rounded-2xl flex items-center justify-center mx-auto mb-6 shadow-lg relative z-10">
                <Search className="w-10 h-10 text-white" />
              </div>
              <h3 className="text-2xl font-bold mb-3">2. Get Instant Analysis</h3>
              <p className="text-gray-600 leading-relaxed">
                Our AI cross-references professional labor rates and material-cost databases
                calibrated to your region. Results in under 60&nbsp;seconds.
              </p>
            </div>

            {/* Step 3 */}
            <div className="text-center relative">
              <div className="w-20 h-20 bg-gradient-to-br from-primary-500 to-primary-600 rounded-2xl flex items-center justify-center mx-auto mb-6 shadow-lg relative z-10">
                <FileText className="w-10 h-10 text-white" />
              </div>
              <h3 className="text-2xl font-bold mb-3">3. Know Before You Pay</h3>
              <p className="text-gray-600 leading-relaxed">
                Get a detailed report with fair price ranges, potential red flags, and specific negotiation talking&nbsp;points.
              </p>
            </div>
          </div>

          <div className="text-center mt-14">
            <Link
              href="/analyze"
              className="btn-primary text-lg inline-flex items-center gap-2 px-8 py-4"
            >
              Start Your Analysis
              <CheckCircle className="w-5 h-5" />
            </Link>
          </div>
        </div>
      </section>

      {/* ============================================================ */}
      {/*  WHAT YOU GET (report features)                              */}
      {/* ============================================================ */}
      <section className="py-20 bg-white">
        <div className="container mx-auto px-4 max-w-6xl">
          <div className="text-center mb-14">
            <h2 className="text-3xl md:text-4xl font-bold mb-4">
              What&apos;s in Your $19.99 Report
            </h2>
            <p className="text-xl text-gray-600 max-w-2xl mx-auto">
              Everything you need to negotiate with confidence — or walk away knowing why.
            </p>
          </div>

          <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-6">
            {/* Feature 1 */}
            <div className="card border-2 border-gray-100 hover:border-primary-200 transition-colors">
              <div className="w-12 h-12 bg-primary-50 rounded-xl flex items-center justify-center mb-4">
                <BarChart3 className="w-6 h-6 text-primary-600" />
              </div>
              <h3 className="text-lg font-bold mb-2">Line-by-Line Breakdown</h3>
              <p className="text-gray-600 text-sm leading-relaxed">
                Every line item in your quote analyzed individually — labor, materials, and markup shown separately.
              </p>
            </div>

            {/* Feature 2 */}
            <div className="card border-2 border-gray-100 hover:border-primary-200 transition-colors">
              <div className="w-12 h-12 bg-primary-50 rounded-xl flex items-center justify-center mb-4">
                <MapPin className="w-6 h-6 text-primary-600" />
              </div>
              <h3 className="text-lg font-bold mb-2">Regional Price Comparison</h3>
              <p className="text-gray-600 text-sm leading-relaxed">
                Fair price ranges calibrated to your zip code using professional wage data and regional material costs.
              </p>
            </div>

            {/* Feature 3 */}
            <div className="card border-2 border-gray-100 hover:border-primary-200 transition-colors">
              <div className="w-12 h-12 bg-red-50 rounded-xl flex items-center justify-center mb-4">
                <AlertTriangle className="w-6 h-6 text-red-500" />
              </div>
              <h3 className="text-lg font-bold mb-2">Red Flag Detection</h3>
              <p className="text-gray-600 text-sm leading-relaxed">
                Suspicious charges, phantom line items, and common contractor tricks — flagged and explained.
              </p>
            </div>

            {/* Feature 4 */}
            <div className="card border-2 border-gray-100 hover:border-primary-200 transition-colors">
              <div className="w-12 h-12 bg-yellow-50 rounded-xl flex items-center justify-center mb-4">
                <Eye className="w-6 h-6 text-yellow-600" />
              </div>
              <h3 className="text-lg font-bold mb-2">Upsell Identification</h3>
              <p className="text-gray-600 text-sm leading-relaxed">
                We spot unnecessary add-ons and premium upgrades you didn&apos;t ask for hiding in your quote.
              </p>
            </div>

            {/* Feature 5 */}
            <div className="card border-2 border-gray-100 hover:border-primary-200 transition-colors">
              <div className="w-12 h-12 bg-green-50 rounded-xl flex items-center justify-center mb-4">
                <DollarSign className="w-6 h-6 text-green-600" />
              </div>
              <h3 className="text-lg font-bold mb-2">Fair Price Range</h3>
              <p className="text-gray-600 text-sm leading-relaxed">
                See exactly what your project should cost — low, average, and high range for your area.
              </p>
            </div>

            {/* Feature 6 */}
            <div className="card border-2 border-gray-100 hover:border-primary-200 transition-colors">
              <div className="w-12 h-12 bg-blue-50 rounded-xl flex items-center justify-center mb-4">
                <Download className="w-6 h-6 text-blue-600" />
              </div>
              <h3 className="text-lg font-bold mb-2">PDF Download</h3>
              <p className="text-gray-600 text-sm leading-relaxed">
                Download your full report as a professional PDF — take it to your contractor or keep it for your records.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* ============================================================ */}
      {/*  SIMPLE, HONEST PRICING                                      */}
      {/* ============================================================ */}
      <section className="py-20 bg-white">
        <div className="container mx-auto px-4 max-w-4xl">
          <div className="text-center mb-12">
            <h2 className="text-3xl md:text-4xl font-bold mb-4">
              Simple, Honest Pricing
            </h2>
            <p className="text-xl text-gray-600">
              No subscriptions. No hidden fees. No data selling. Ever.
            </p>
          </div>

          {/* Pricing card */}
          <div className="max-w-lg mx-auto">
            <div className="card border-2 border-primary-200 shadow-xl relative overflow-hidden">
              {/* Top accent */}
              <div className="absolute top-0 left-0 right-0 h-1 bg-gradient-to-r from-primary-500 to-primary-700" />

              <div className="text-center pt-4 pb-2">
                <p className="text-sm font-semibold text-primary-600 uppercase tracking-wide mb-2">
                  Per Report
                </p>
                <div className="flex items-baseline justify-center gap-1 mb-1">
                  <span className="text-5xl md:text-6xl font-extrabold text-gray-900">
                    $19
                  </span>
                  <span className="text-2xl font-bold text-gray-500">.99</span>
                </div>
                <p className="text-gray-500 text-sm">One-time payment. That&apos;s it.</p>
              </div>

              <div className="border-t border-gray-100 mt-4 pt-6 space-y-3">
                {[
                  'Line-by-line quote analysis',
                  'Regional price comparison for your zip code',
                  'Red flag & upsell detection',
                  'Fair price range for your area',
                  'Negotiation talking points',
                  'Downloadable PDF report',
                  '7-day money-back guarantee',
                ].map((item) => (
                  <div key={item} className="flex items-start gap-3">
                    <CheckCircle className="w-5 h-5 text-green-500 flex-shrink-0 mt-0.5" />
                    <span className="text-gray-700">{item}</span>
                  </div>
                ))}
              </div>

              <div className="mt-8">
                <Link
                  href="/analyze"
                  className="btn-primary w-full text-center text-lg py-4 block font-bold"
                >
                  Analyze My Quote →
                </Link>
              </div>
            </div>
          </div>

          {/* Industry stat */}
          <div className="text-center mt-10">
            <div className="inline-flex items-center gap-2 bg-primary-50 border border-primary-200 px-6 py-3 rounded-full">
              <TrendingDown className="w-5 h-5 text-primary-600" />
              <span className="font-semibold text-gray-900">
                Homeowners routinely overpay <span className="text-primary-700">20–40%</span> on contractor quotes — we help you find out if you&apos;re one of them.
              </span>
            </div>
          </div>
        </div>
      </section>

      {/* (Pricing section moved up — above trust badges) */}

      {/* ============================================================ */}
      {/*  FAQ                                                         */}
      {/* ============================================================ */}
      <section className="py-20 bg-white">
        <div className="container mx-auto px-4 max-w-4xl">
          <div className="text-center mb-12">
            <h2 className="text-3xl md:text-4xl font-bold mb-4">
              Frequently Asked Questions
            </h2>
            <p className="text-xl text-gray-600">
              Everything you need to know before you buy
            </p>
          </div>

          <FaqAccordion faqs={faqs} />

          <div className="text-center mt-8">
            <p className="text-gray-600">
              Still have questions?{' '}
              <a
                href="mailto:support@ungouge.ai"
                className="text-primary-600 hover:text-primary-700 font-semibold"
              >
                Email us
              </a>
              {' '}— we respond within a few hours.
            </p>
          </div>
        </div>
      </section>

      {/* ============================================================ */}
      {/*  FINAL CTA                                                   */}
      {/* ============================================================ */}
      <section className="py-20 bg-gradient-to-br from-primary-700 via-primary-800 to-primary-900 text-white">
        <div className="container mx-auto px-4 max-w-4xl text-center">
          <h2 className="text-3xl sm:text-4xl md:text-5xl font-extrabold mb-6 leading-tight">
            Don&apos;t Sign Until You Know It&apos;s Fair
          </h2>
          <p className="text-lg sm:text-xl md:text-2xl mb-10 text-primary-100 max-w-2xl mx-auto leading-relaxed">
            Homeowners routinely overpay 20–40% on contractor quotes. For{' '}
            <strong className="text-white">$19.99</strong>, find out exactly where
            you stand — in under 60&nbsp;seconds.
          </p>
          <Link
            href="/analyze"
            className="btn-primary bg-white text-primary-700 hover:bg-gray-100 text-lg shadow-xl inline-flex items-center gap-2 px-10 py-4 font-bold"
          >
            Analyze Your Quote Now
            <span aria-hidden="true">→</span>
          </Link>
          <p className="mt-6 text-primary-200 text-base">
            <strong className="text-white">$19.99</strong> · Instant results ·
            100% money-back guarantee
          </p>
        </div>
      </section>
    </div>
  );
}
