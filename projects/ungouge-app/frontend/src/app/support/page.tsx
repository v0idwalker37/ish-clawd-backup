import type { Metadata } from 'next';
import {
  MessageCircle,
  Mail,
  Users,
  Clock,
  ChevronDown,
  Zap,
  Shield,
  FileText,
  CreditCard,
  HelpCircle,
  Bot,
} from 'lucide-react';
import Link from 'next/link';
import SupportPageClient from './SupportPageClient';

export const metadata: Metadata = {
  title: 'Support — Get Help with Your Quote Analysis | UnGouge.ai',
  description:
    'Get instant help from our AI support assistant or reach our human team. FAQs, chat support, and direct email — we\'re real people building real tools.',
  alternates: {
    canonical: 'https://ungouge.ai/support',
  },
};

const faqCategories = [
  {
    title: 'Getting Started',
    icon: FileText,
    faqs: [
      {
        q: 'How does UnGouge.ai work?',
        a: 'Upload your contractor quote (PDF, photo, or manual entry), and our AI analyzes every line item against current market data for your specific location. We use real-time pricing research to compare what you\'re being charged against what similar work actually costs in your area. You get a detailed report showing fair price ranges, potential overcharges, and negotiation recommendations.',
      },
      {
        q: 'What types of quotes can you analyze?',
        a: 'We support any home improvement or renovation quote — kitchen remodels, bathroom renovations, roofing, HVAC, plumbing, electrical, painting, flooring, deck construction, and more. If a contractor gave you a quote with line items and prices, we can analyze it.',
      },
      {
        q: 'How accurate are the fair price ranges?',
        a: 'Our AI researches current market rates using real-time data for your specific location. Fair ranges reflect actual costs reported by contractors, material suppliers, and industry databases in your area. As with any estimate, actual prices can vary based on project specifics, contractor experience, and material choices — but our ranges give you a strong baseline for negotiation.',
      },
      {
        q: 'Do I need to create an account?',
        a: 'Yes — a free account lets you save your reports, access them anytime, and download PDFs. We don\'t sell your data or send you contractor referrals. Your account exists purely so you can access your reports.',
      },
    ],
  },
  {
    title: 'Pricing & Payments',
    icon: CreditCard,
    faqs: [
      {
        q: 'How much does an analysis cost?',
        a: 'Each quote analysis is a one-time payment of $19.99. No subscriptions, no hidden fees. You get the full report with line-by-line analysis, fair price ranges, and a downloadable PDF.',
      },
      {
        q: 'What payment methods do you accept?',
        a: 'We accept all major credit cards, debit cards, and Apple Pay / Google Pay through our secure payment partner, Stripe. We never see or store your card details.',
      },
      {
        q: 'Can I get a refund?',
        a: 'If our AI made a clear error in your analysis (e.g., wrong location, misread line items), contact us and we\'ll either re-run your analysis at no charge or issue a full refund. We stand behind the quality of our reports.',
      },
      {
        q: 'Do you have promo codes?',
        a: 'We occasionally offer promotional codes through our newsletter and launch campaigns. Enter your code on the Quote Details page (Step 2) before submitting for payment.',
      },
    ],
  },
  {
    title: 'Understanding Your Report',
    icon: HelpCircle,
    faqs: [
      {
        q: 'What does "Possible Gouge" mean?',
        a: 'This flag means a line item is priced significantly above the fair market range for your area — typically 35%+ over what similar work costs. It doesn\'t necessarily mean the contractor is dishonest; it could reflect premium materials, specialized expertise, or market conditions. But it\'s a strong signal to ask questions and get competing quotes for that specific item.',
      },
      {
        q: 'What does "Suspiciously Low" mean?',
        a: 'A price flagged as suspiciously low may indicate bundled costs that will appear later as change orders, use of unlicensed subcontractors, lower-quality materials, or a bid-winning tactic. It\'s worth asking the contractor for a detailed breakdown of what\'s included at that price.',
      },
      {
        q: 'Should I fire my contractor based on this report?',
        a: 'No — this report is a negotiation tool, not a verdict. Most contractors price fairly on most items. Use the report to have an informed conversation: "I noticed the window installation seems high compared to market rates — can you help me understand what\'s included?" That approach gets better results than accusation.',
      },
      {
        q: 'Why do some items show $0?',
        a: 'A $0 line item usually means the cost is bundled into another item. For example, a contractor might include demolition costs in the overall kitchen remodel price rather than breaking it out separately. Our AI accounts for this in the analysis.',
      },
    ],
  },
  {
    title: 'Privacy & Security',
    icon: Shield,
    faqs: [
      {
        q: 'Do you sell my data to contractors?',
        a: 'Absolutely not. We will never sell your data, share your quote details with contractors, or send you contractor referrals. Our only revenue is the $19.99 analysis fee. Your trust is our business model.',
      },
      {
        q: 'Is my contractor quote data secure?',
        a: 'Yes. Your data is encrypted in transit (TLS) and at rest. We use Google Cloud infrastructure with enterprise-grade security. Your uploaded files are processed for analysis and stored securely for your future access only.',
      },
      {
        q: 'Can my contractor see my report?',
        a: 'No. Your report is private to your account. You can choose to share it (via PDF download), but we never make reports visible to anyone else.',
      },
    ],
  },
];

export default function SupportPage() {
  return (
    <div className="py-12 bg-gray-50">
      <div className="container mx-auto px-4 max-w-5xl">
        {/* Hero */}
        <div className="text-center mb-12">
          <h1 className="text-4xl font-bold text-gray-900 mb-4">
            How Can We Help?
          </h1>
          <p className="text-xl text-gray-600 max-w-2xl mx-auto">
            Get answers instantly from our AI assistant, browse FAQs, or reach out to a real human. We&apos;re here either way.
          </p>
        </div>

        {/* Support Channels — 2 cards */}
        <div className="grid md:grid-cols-2 gap-6 mb-16">
          {/* AI Assistant */}
          <div className="bg-white rounded-2xl border border-gray-200 p-8 shadow-sm hover:shadow-md transition-shadow">
            <div className="flex items-center gap-4 mb-4">
              <div className="w-14 h-14 bg-primary-100 rounded-xl flex items-center justify-center">
                <Zap className="w-7 h-7 text-primary-600" />
              </div>
              <div>
                <h2 className="text-xl font-bold text-gray-900">Ask Scout</h2>
                <p className="text-sm text-gray-500">AI Support Assistant</p>
              </div>
            </div>
            <p className="text-gray-600 mb-4">
              Scout can answer most questions instantly — how to read your report, what assessments mean, account issues, payment questions, and more. Available 24/7.
            </p>
            <div className="flex items-center gap-2 text-sm text-emerald-600 font-medium mb-6">
              <Clock className="w-4 h-4" />
              Typical response: Instant
            </div>
            <SupportPageClient />
          </div>

          {/* Human Support */}
          <div className="bg-white rounded-2xl border border-gray-200 p-8 shadow-sm hover:shadow-md transition-shadow">
            <div className="flex items-center gap-4 mb-4">
              <div className="w-14 h-14 bg-amber-100 rounded-xl flex items-center justify-center">
                <Users className="w-7 h-7 text-amber-600" />
              </div>
              <div>
                <h2 className="text-xl font-bold text-gray-900">Talk to a Human</h2>
                <p className="text-sm text-gray-500">Real people, real answers</p>
              </div>
            </div>
            <p className="text-gray-600 mb-4">
              For complex issues, refund requests, or when you just want to talk to a person — we get it. We&apos;re a small team and we read every email personally.
            </p>
            <div className="flex items-center gap-2 text-sm text-amber-600 font-medium mb-6">
              <Clock className="w-4 h-4" />
              Typical response: Within 24 hours (business days)
            </div>
            <div className="space-y-4">
              <a
                href="mailto:human@ungouge.ai"
                className="flex items-center gap-3 w-full px-5 py-3.5 bg-amber-50 border border-amber-200 rounded-xl text-amber-800 font-semibold hover:bg-amber-100 transition-colors"
              >
                <Mail className="w-5 h-5" />
                human@ungouge.ai
              </a>
              <p className="text-xs text-gray-500">
                Yes, that&apos;s a real email that goes to a real person. We&apos;re not hiding behind a chatbot — we&apos;re just honest that a human response takes longer than an AI one.
              </p>
            </div>

            <div className="mt-6 pt-6 border-t border-gray-100">
              <p className="text-sm text-gray-500 mb-3">For general inquiries:</p>
              <a
                href="mailto:support@ungouge.ai"
                className="flex items-center gap-3 w-full px-5 py-3 bg-gray-50 border border-gray-200 rounded-xl text-gray-700 font-medium hover:bg-gray-100 transition-colors"
              >
                <Mail className="w-5 h-5 text-gray-400" />
                support@ungouge.ai
              </a>
            </div>
          </div>
        </div>

        {/* Who We Are callout */}
        <div className="bg-white rounded-2xl border border-gray-200 p-8 mb-16 shadow-sm">
          <div className="flex items-start gap-4">
            <div className="w-12 h-12 bg-emerald-100 rounded-xl flex items-center justify-center flex-shrink-0">
              <Users className="w-6 h-6 text-emerald-600" />
            </div>
            <div>
              <h3 className="text-lg font-bold text-gray-900 mb-2">We&apos;re Real People</h3>
              <p className="text-gray-600 leading-relaxed">
                UnGouge.ai is built by a small team who believes homeowners deserve pricing transparency. We use AI because it lets us deliver better analysis faster — not because we&apos;re trying to replace human judgment. When you email <strong>human@ungouge.ai</strong>, you&apos;re reaching the people who built this product and care about getting it right. We may be slower than Scout, but we&apos;re listening.
              </p>
            </div>
          </div>
        </div>

        {/* FAQs */}
        <div className="mb-16">
          <h2 className="text-3xl font-bold text-gray-900 text-center mb-2">
            Frequently Asked Questions
          </h2>
          <p className="text-gray-600 text-center mb-10">
            Can&apos;t find your answer? Ask Scout or email us.
          </p>

          <div className="space-y-8">
            {faqCategories.map((category) => {
              const Icon = category.icon;
              return (
                <div key={category.title}>
                  <div className="flex items-center gap-3 mb-4">
                    <Icon className="w-5 h-5 text-primary-600" />
                    <h3 className="text-xl font-bold text-gray-900">{category.title}</h3>
                  </div>
                  <div className="space-y-3">
                    {category.faqs.map((faq) => (
                      <details
                        key={faq.q}
                        className="group bg-white rounded-xl border border-gray-200 overflow-hidden"
                      >
                        <summary className="flex items-center justify-between px-6 py-4 cursor-pointer hover:bg-gray-50 transition-colors list-none">
                          <span className="font-medium text-gray-900 pr-4">{faq.q}</span>
                          <ChevronDown className="w-5 h-5 text-gray-400 flex-shrink-0 group-open:rotate-180 transition-transform" />
                        </summary>
                        <div className="px-6 pb-5 text-gray-600 leading-relaxed border-t border-gray-100 pt-4">
                          {faq.a}
                        </div>
                      </details>
                    ))}
                  </div>
                </div>
              );
            })}
          </div>
        </div>

        {/* Bottom CTA */}
        <div className="text-center bg-primary-50 rounded-2xl p-8 border border-primary-100">
          <h3 className="text-2xl font-bold text-gray-900 mb-3">Still have questions?</h3>
          <p className="text-gray-600 mb-6 max-w-xl mx-auto">
            Scout has answers to most questions — try asking before you go.
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <Link href="/analyze" className="btn-primary">
              Analyze a Quote
            </Link>
            <SupportPageClient variant="secondary" />
          </div>
        </div>
      </div>
    </div>
  );
}
