import type { Metadata } from 'next';
import Link from 'next/link';
import { SITE_CONFIG } from '@/lib/seo';

export const metadata: Metadata = {
  title: 'Frequently Asked Questions | GougeAlert',
  description:
    'Common questions about GougeAlert contractor quote verification: How it works, pricing, accuracy, privacy, and more.',
  alternates: {
    canonical: `${SITE_CONFIG.url}/faq`,
  },
};

const faqs = [
  {
    category: 'How It Works',
    questions: [
      {
        q: 'How does GougeAlert verify my contractor quote?',
        a: `We analyze your quote line-by-line against real market data:
        
• **Material pricing:** We compare quoted material costs against retail pricing and verify markup percentages (20-40% is fair; 100%+ is excessive)
• **Labor rates:** We check labor charges against regional averages for each trade (electrician, plumber, carpenter, etc.)
• **Project scope:** We verify the work scope matches industry standards and identify missing or inflated line items
• **Location factors:** We adjust for your specific region (NYC costs ≠ Mississippi costs)

Our analysis is powered by RSMeans cost data, Craftsman National Estimator, and real-time market research.`,
      },
      {
        q: 'What if I only have a total-only quote (no itemization)?',
        a: `We can still help! For total-only quotes, we:

• Compare the total against typical market ranges for your project type and size
• Provide educational cost breakdowns (what materials/labor typically cost)
• Identify if the total is fair, high, or suspiciously low
• Recommend asking for itemization if you want to proceed

However, **itemized quotes give much better analysis**—we can catch specific overcharges line-by-line.`,
      },
      {
        q: 'How accurate is your analysis?',
        a: `Our current accuracy is **65-75%** (verified against real market data). We're continuously improving by:

• Adding more cost database sources
• Refining regional adjustments
• Learning from submitted quotes

**What we catch well:** Material markups, labor rate inflation, obvious padding  
**What's harder:** Specialized work, custom materials, regional micro-variations

We always show our confidence level and explain our reasoning—you make the final call.`,
      },
      {
        q: 'How long does analysis take?',
        a: `**24 hours or less.** Most reports are ready within 12 hours.

You'll get an email when your report is ready. No need to check back—we'll notify you.`,
      },
    ],
  },
  {
    category: 'Pricing & Payment',
    questions: [
      {
        q: 'How much does it cost?',
        a: `**$19.99 per quote analysis.**

One-time payment. No subscription. No hidden fees.

We occasionally offer promo codes (like LAUNCH2026 and BETATESTER) for early adopters.`,
      },
      {
        q: 'Do you offer refunds?',
        a: `**Yes, if our analysis doesn't help you.**

If you're unsatisfied with the report quality or it doesn't provide useful insights, email us at human@gougealert.com within 7 days and we'll refund you—no questions asked.

We stand behind our work.`,
      },
      {
        q: 'Can I get multiple quotes analyzed?',
        a: `**Yes!** Each quote is $19.99.

Many customers submit 2-3 competing quotes to see which is fairest. We'll analyze each one independently.`,
      },
      {
        q: 'What payment methods do you accept?',
        a: `We accept all major credit cards, debit cards, and Apple Pay via Stripe.

Your payment information is processed securely—we never see or store your card details.`,
      },
    ],
  },
  {
    category: 'Privacy & Data',
    questions: [
      {
        q: 'What do you do with my data?',
        a: `**Nothing.** We NEVER sell your data. Ever.

Here's exactly what happens to your information:

✅ **We use it to:** Analyze your quote and generate your report  
✅ **We store it to:** Let you access your report later  
❌ **We DON'T:** Sell it, share it with contractors, use it for lead generation, or give it to third parties

**This is our core differentiator.** Lead-gen sites (HomeAdvisor, Thumbtack, Angie's List) sell your info to 3-5 contractors who call/email you relentlessly. We don't.

Read our full [Privacy Policy](/privacy).`,
      },
      {
        q: 'Do you share my quote with contractors?',
        a: `**No.** We never contact contractors or share your information with them.

We're not a referral service. We're an independent analysis tool. Your quote stays private.`,
      },
      {
        q: 'Can I delete my data?',
        a: `**Yes.** Email human@gougealert.com and we'll delete your account and all associated data within 48 hours.

You can also download your data before deletion if you want a copy.`,
      },
    ],
  },
  {
    category: 'Reports',
    questions: [
      {
        q: 'What\'s included in the report?',
        a: `Every report includes:

📊 **Overall Assessment**  
Fair / High / Suspiciously Low with confidence score

📝 **Line-by-Line Analysis** (for itemized quotes)  
Each item rated: Fair / Slightly High / High / Red Flag

💰 **Cost Breakdown**  
Material costs, labor rates, markup analysis

🚩 **Red Flags Identified**  
Vague descriptions, excessive markups, missing permits, etc.

🎯 **Recommendations**  
Negotiate these items / Get competing bid / Proceed / Walk away

📈 **Market Comparison**  
How your quote compares to typical pricing for your region

All delivered as a clean, branded PDF you can save or share.`,
      },
      {
        q: 'Can I share my report with my contractor?',
        a: `**Absolutely!** The report is yours to use however you want.

Many customers use it to negotiate:  
*"Your material markup on cabinets is 180%. Industry standard is 20-40%. Can we adjust that?"*

The report gives you specific talking points backed by data.`,
      },
      {
        q: 'What if the analysis says my quote is fair but I still feel uncertain?',
        a: `Trust your gut. Our analysis is data-driven, but you know your situation best.

**If you're still uncertain:**
- Get 1-2 competing quotes for comparison
- Ask the contractor to clarify specific line items
- Check contractor reviews/references (we verify *pricing*, not *quality*)

Our report is one input to your decision—not the only input.`,
      },
    ],
  },
  {
    category: 'Technical',
    questions: [
      {
        q: 'What file formats can I upload?',
        a: `We accept:
• PDF
• Images (JPG, PNG, HEIC)
• Screenshots
• Scanned documents
• Email forwards (copy-paste the quote text)

**Tip:** The clearer the quote, the better our analysis. Blurry photos or handwritten quotes are harder to parse.`,
      },
      {
        q: 'Do you work with contractors outside the US?',
        a: `**Currently US-only.** Our cost data is US-specific.

We're planning to expand to Canada and UK in 2026. Sign up for our newsletter to be notified.`,
      },
      {
        q: 'What if my contractor used non-standard terminology?',
        a: `Our AI is trained to understand construction jargon and variations.

If we can't parse something, we'll flag it in the report and explain what we need clarified. You can then ask your contractor for clarification.`,
      },
    ],
  },
  {
    category: 'Getting Started',
    questions: [
      {
        q: 'Do I need to create an account?',
        a: `**Yes.** This lets you:
• Access your reports anytime
• Submit multiple quotes
• Track your analysis history

Sign-up takes 30 seconds (email + password). No credit card required until you're ready to pay for analysis.`,
      },
      {
        q: 'What if I don\'t have a quote yet?',
        a: `Check out our **free cost guides** to get a sense of fair pricing before you even request quotes:

• [State-by-state pricing](/locations)
• [Project cost breakdowns](/blog)
• [How to read contractor quotes](/blog/how-to-read-contractor-quote)

Then when you get quotes, you'll already have context for what's reasonable.`,
      },
      {
        q: 'Can I try it for free?',
        a: `We offer **promo codes** for early adopters. Current active codes:

• **LAUNCH2026** - Free analysis (limited time)
• **BETATESTER** - Free analysis for beta testers

Enter the code at checkout. If it's expired, email human@gougealert.com—we'll hook you up.`,
      },
    ],
  },
  {
    category: 'Still Have Questions?',
    questions: [
      {
        q: 'How do I contact support?',
        a: `**Email:** human@gougealert.com  
**Response time:** Usually within 24 hours (often faster)

We're a small team, but we read every email and respond personally—no bots, no canned responses.

You can also use the chat widget on any page (powered by Zedd, our AI assistant, but escalates to humans for complex issues).`,
      },
    ],
  },
];

export default function FAQPage() {
  return (
    <div className="bg-white">
      {/* Header */}
      <div className="bg-gradient-to-b from-primary-50 to-white">
        <div className="container mx-auto px-4 py-16 max-w-4xl">
          <h1 className="text-4xl font-bold text-gray-900 mb-4 text-center">
            Frequently Asked Questions
          </h1>
          <p className="text-xl text-gray-600 text-center max-w-2xl mx-auto">
            Everything you need to know about GougeAlert contractor quote
            verification.
          </p>
        </div>
      </div>

      {/* FAQ Sections */}
      <div className="container mx-auto px-4 pb-20 max-w-4xl">
        {faqs.map((section, sectionIdx) => (
          <div key={sectionIdx} className="mb-16">
            <h2 className="text-2xl font-bold text-gray-900 mb-6 pb-2 border-b-2 border-primary-500">
              {section.category}
            </h2>
            <div className="space-y-8">
              {section.questions.map((item, qIdx) => (
                <div key={qIdx}>
                  <h3 className="text-lg font-semibold text-gray-900 mb-3">
                    {item.q}
                  </h3>
                  <div className="text-gray-700 leading-relaxed whitespace-pre-line">
                    {item.a}
                  </div>
                </div>
              ))}
            </div>
          </div>
        ))}

        {/* CTA */}
        <div className="mt-16 p-8 bg-primary-50 rounded-2xl text-center">
          <h3 className="text-2xl font-semibold text-gray-900 mb-2">
            Ready to verify your quote?
          </h3>
          <p className="text-gray-600 mb-6">
            Upload your contractor quote and get an independent analysis in 24
            hours.
          </p>
          <Link
            href="/analyze"
            className="inline-block bg-primary-600 text-white font-semibold px-8 py-3 rounded-lg hover:bg-primary-700 transition-colors"
          >
            Get Started — $19.99
          </Link>
        </div>
      </div>
    </div>
  );
}
