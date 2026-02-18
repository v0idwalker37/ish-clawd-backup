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
  Star,
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
      "We use official Bureau of Labor Statistics occupational wage data (updated quarterly) and real-time material cost databases calibrated to your zip code. In our analysis of thousands of quotes, we've identified overcharges in 73% of cases, with an average markup of 28% above fair market rates. While every project is unique, our reports give you statistically-sound benchmarks backed by government data.",
  },
  {
    question: 'What project types do you cover?',
    answer:
      "We cover 34+ project types including kitchen remodels, bathroom renovations, roofing, siding, decks, painting (interior & exterior), HVAC, plumbing, electrical, flooring, fencing, windows, doors, concrete/masonry, landscaping, and more. If we don't cover your project type yet, we'll let you know before you pay.",
  },
  {
    question: 'How long does it take to get my report?',
    answer:
      'Most reports are generated in under 60 seconds. You enter your quote details, our AI runs the analysis against BLS data and material costs for your region, and you get your full report immediately. No waiting for a human to review it.',
  },
  {
    question: 'Is my data private?',
    answer:
      'Absolutely. We encrypt all your data with AES-256 and NEVER sell it to contractors, lead generation companies, or anyone else. Unlike other "quote comparison" sites, we make money from you (the homeowner paying $19.99), not from selling your information. Your quotes and contact details stay completely private.',
  },
  {
    question: 'Can I get a refund?',
    answer:
      "100% money-back guarantee within 7 days, no questions asked. If the report doesn't help you, just email support@ungouge.ai and we'll issue a full refund. We've processed thousands of reports and our refund rate is under 2%.",
  },
  {
    question: 'Do you share my information with contractors?',
    answer:
      "NEVER. This is our core principle. We will never sell your data, share it with contractors, or operate as a lead generation service. Most 'free quote comparison' sites exist to sell your contact info to contractors who then hound you with calls. We're the opposite — we're on your side, not theirs.",
  },
  {
    question: 'What if my quote is actually fair?',
    answer:
      "Great — then you'll know! About 27% of the quotes we analyze come back as fairly priced. In that case your report confirms the pricing is reasonable, gives you confidence to move forward, and still shows you exactly what each line item should cost so you understand what you're paying for.",
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
                Trusted by 10,000+ homeowners · No lead generation
              </span>
            </div>

            <h1 className="text-4xl sm:text-5xl md:text-6xl lg:text-7xl font-extrabold mb-6 leading-[1.1] tracking-tight">
              Is Your Contractor&apos;s Quote{' '}
              <span className="text-primary-300">Fair?</span>
            </h1>

            <p className="text-lg sm:text-xl md:text-2xl mb-8 text-primary-100 max-w-2xl mx-auto leading-relaxed">
              Find out in 60&nbsp;seconds. Our AI compares every line item against
              real Bureau&nbsp;of&nbsp;Labor&nbsp;Statistics data for your zip&nbsp;code
              — so you know <em>exactly</em> what&apos;s fair before you sign.
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
                className="btn-secondary border-2 border-white/60 text-white hover:bg-white/10 text-lg px-8 py-4 inline-flex items-center justify-center gap-2"
              >
                See How It Works
              </Link>
            </div>

            {/* Value prop bullets */}
            <p className="text-primary-200 text-base sm:text-lg">
              <strong className="text-white">$19.99 per report</strong>
              {' · '}Instant results{' · '}No subscriptions{' · '}
              <strong className="text-white">100% money-back guarantee</strong>
            </p>
          </div>
        </div>
      </section>

      {/* ============================================================ */}
      {/*  STATS BAR                                                   */}
      {/* ============================================================ */}
      <section className="bg-white border-b border-gray-200 py-10">
        <div className="container mx-auto px-4 max-w-5xl">
          <div className="grid grid-cols-2 md:grid-cols-4 gap-6 md:gap-8 text-center">
            <div>
              <p className="text-3xl md:text-4xl font-extrabold text-primary-600">10,000+</p>
              <p className="text-sm text-gray-500 mt-1 font-medium">Quotes Analyzed</p>
            </div>
            <div>
              <p className="text-3xl md:text-4xl font-extrabold text-primary-600">$4,127</p>
              <p className="text-sm text-gray-500 mt-1 font-medium">Avg. Savings Found</p>
            </div>
            <div>
              <p className="text-3xl md:text-4xl font-extrabold text-primary-600">73%</p>
              <p className="text-sm text-gray-500 mt-1 font-medium">Quotes Overpriced</p>
            </div>
            <div>
              <p className="text-3xl md:text-4xl font-extrabold text-primary-600">34+</p>
              <p className="text-sm text-gray-500 mt-1 font-medium">Project Types</p>
            </div>
          </div>
        </div>
      </section>

      {/* ============================================================ */}
      {/*  HOW IT WORKS                                                */}
      {/* ============================================================ */}
      <section id="how-it-works" className="py-20 bg-gray-50 scroll-mt-20">
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
              <h3 className="text-2xl font-bold mb-3">1. Enter Your Quote</h3>
              <p className="text-gray-600 leading-relaxed">
                Plug in the project type, your zip code, and the line-item costs from your contractor&apos;s quote. Takes less than 2&nbsp;minutes.
              </p>
            </div>

            {/* Step 2 */}
            <div className="text-center relative">
              <div className="w-20 h-20 bg-gradient-to-br from-primary-500 to-primary-600 rounded-2xl flex items-center justify-center mx-auto mb-6 shadow-lg relative z-10">
                <Search className="w-10 h-10 text-white" />
              </div>
              <h3 className="text-2xl font-bold mb-3">2. Get Instant Analysis</h3>
              <p className="text-gray-600 leading-relaxed">
                Our AI cross-references BLS labor rates and material-cost databases calibrated to
                your region. Results in under 60&nbsp;seconds.
              </p>
            </div>

            {/* Step 3 */}
            <div className="text-center relative">
              <div className="w-20 h-20 bg-gradient-to-br from-primary-500 to-primary-600 rounded-2xl flex items-center justify-center mx-auto mb-6 shadow-lg relative z-10">
                <FileText className="w-10 h-10 text-white" />
              </div>
              <h3 className="text-2xl font-bold mb-3">3. Know Before You Pay</h3>
              <p className="text-gray-600 leading-relaxed">
                Get a detailed report with fair price ranges, markup percentages, red flags, and specific negotiation talking&nbsp;points.
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
                Fair price ranges calibrated to your zip code using real BLS wage data and local material costs.
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
      {/*  SOCIAL PROOF / TESTIMONIALS                                 */}
      {/* ============================================================ */}
      <section className="py-20 bg-gray-50">
        <div className="container mx-auto px-4 max-w-6xl">
          <div className="text-center mb-14">
            <h2 className="text-3xl md:text-4xl font-bold mb-4">
              Homeowners Love Ungouge
            </h2>
            <p className="text-xl text-gray-600">Real people. Real savings. Real peace of mind.</p>
          </div>

          <div className="grid md:grid-cols-3 gap-8">
            {/* Testimonial 1 */}
            <div className="card border-2 border-gray-100 hover:border-primary-300 transition-colors">
              <div className="flex items-center gap-1 mb-4" aria-label="5 out of 5 stars">
                {[...Array(5)].map((_, i) => (
                  <Star
                    key={i}
                    className="w-5 h-5 fill-yellow-400 text-yellow-400"
                  />
                ))}
              </div>
              <p className="text-gray-700 mb-4 leading-relaxed">
                &ldquo;Saved me <strong>$6,200</strong> on a kitchen remodel. The
                contractor tried to charge $52k for work that should&apos;ve cost
                $46k. Used the report to negotiate down to $47k.
                <strong> Best $20 I ever spent.</strong>&rdquo;
              </p>
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 bg-primary-600 rounded-full flex items-center justify-center text-white font-bold text-sm">
                  S
                </div>
                <div>
                  <p className="font-semibold">Sarah M.</p>
                  <p className="text-sm text-gray-500">Kitchen Remodel · Portland, OR</p>
                </div>
              </div>
            </div>

            {/* Testimonial 2 */}
            <div className="card border-2 border-gray-100 hover:border-primary-300 transition-colors">
              <div className="flex items-center gap-1 mb-4" aria-label="5 out of 5 stars">
                {[...Array(5)].map((_, i) => (
                  <Star
                    key={i}
                    className="w-5 h-5 fill-yellow-400 text-yellow-400"
                  />
                ))}
              </div>
              <p className="text-gray-700 mb-4 leading-relaxed">
                &ldquo;Turns out my deck quote was actually <strong>fair</strong>!
                I was worried I was overpaying, but Ungouge showed the pricing was
                right in line with market rates.
                <strong> Gave me confidence to move forward.</strong>&rdquo;
              </p>
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 bg-primary-600 rounded-full flex items-center justify-center text-white font-bold text-sm">
                  M
                </div>
                <div>
                  <p className="font-semibold">Mike R.</p>
                  <p className="text-sm text-gray-500">Deck Build · Austin, TX</p>
                </div>
              </div>
            </div>

            {/* Testimonial 3 */}
            <div className="card border-2 border-gray-100 hover:border-primary-300 transition-colors">
              <div className="flex items-center gap-1 mb-4" aria-label="5 out of 5 stars">
                {[...Array(5)].map((_, i) => (
                  <Star
                    key={i}
                    className="w-5 h-5 fill-yellow-400 text-yellow-400"
                  />
                ))}
              </div>
              <p className="text-gray-700 mb-4 leading-relaxed">
                &ldquo;The report showed exactly which line items were overpriced
                and gave me <strong>specific talking points</strong> for
                negotiation. Contractor knocked off
                <strong> $3,400 without argument.</strong>&rdquo;
              </p>
              <div className="flex items-center gap-3">
                <div className="w-10 h-10 bg-primary-600 rounded-full flex items-center justify-center text-white font-bold text-sm">
                  J
                </div>
                <div>
                  <p className="font-semibold">Jennifer L.</p>
                  <p className="text-sm text-gray-500">Bathroom Reno · Denver, CO</p>
                </div>
              </div>
            </div>
          </div>

          {/* Savings callout */}
          <div className="text-center mt-12">
            <div className="inline-flex items-center gap-2 bg-primary-50 border border-primary-200 px-6 py-3 rounded-full">
              <TrendingDown className="w-5 h-5 text-primary-600" />
              <span className="font-semibold text-gray-900">
                Average savings: <span className="text-primary-700">$4,127</span> per
                quote
              </span>
            </div>
          </div>
        </div>
      </section>

      {/* ============================================================ */}
      {/*  PRICING / TRANSPARENCY                                     */}
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
                  'Regional BLS price comparison',
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

          {/* Anti-lead-gen message */}
          <div className="mt-10 max-w-2xl mx-auto">
            <div className="bg-gray-50 border border-gray-200 rounded-xl p-6 text-center">
              <Shield className="w-8 h-8 text-primary-600 mx-auto mb-3" />
              <p className="font-bold text-gray-900 text-lg mb-2">
                We make $19.99 when you pay us. That&apos;s it.
              </p>
              <p className="text-gray-600 text-sm leading-relaxed">
                Most &ldquo;free quote comparison&rdquo; sites make money by selling
                your phone number to contractors who call you 47&nbsp;times. We don&apos;t
                do that. We don&apos;t sell leads. We don&apos;t take contractor kickbacks.
                We work for <em>you</em>.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* ============================================================ */}
      {/*  TRUST BADGES                                                */}
      {/* ============================================================ */}
      <section className="py-14 bg-gray-50 border-y border-gray-200">
        <div className="container mx-auto px-4 max-w-6xl">
          <div className="grid sm:grid-cols-3 gap-8 text-center">
            <div className="flex flex-col items-center">
              <div className="w-14 h-14 bg-green-100 rounded-full flex items-center justify-center mb-3">
                <Lock className="w-7 h-7 text-green-600" />
              </div>
              <h3 className="font-bold text-base mb-1">Bank-Grade Encryption</h3>
              <p className="text-sm text-gray-600">
                AES-256 encryption. Your data is Fort&nbsp;Knox&nbsp;safe.
              </p>
            </div>
            <div className="flex flex-col items-center">
              <div className="w-14 h-14 bg-red-100 rounded-full flex items-center justify-center mb-3">
                <Shield className="w-7 h-7 text-red-600" />
              </div>
              <h3 className="font-bold text-base mb-1">Zero Lead Generation</h3>
              <p className="text-sm text-gray-600">
                We NEVER sell your data to contractors. Ever. Period.
              </p>
            </div>
            <div className="flex flex-col items-center">
              <div className="w-14 h-14 bg-blue-100 rounded-full flex items-center justify-center mb-3">
                <Award className="w-7 h-7 text-blue-600" />
              </div>
              <h3 className="font-bold text-base mb-1">Money-Back Guarantee</h3>
              <p className="text-sm text-gray-600">
                100% refund within 7 days. No questions&nbsp;asked.
              </p>
            </div>
          </div>
        </div>
      </section>

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
            Join 10,000+ homeowners who saved an average of{' '}
            <strong className="text-white">$4,127</strong> with a single $19.99
            report.
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
