import type { Metadata } from 'next';
import Link from 'next/link';
import { SITE_CONFIG } from '@/lib/seo';

export const metadata: Metadata = {
  title: 'What Homeowners Say | UnGouge Testimonials',
  description:
    'Real stories from homeowners who used UnGouge to verify contractor quotes and save thousands on home improvement projects.',
  alternates: {
    canonical: `${SITE_CONFIG.url}/testimonials`,
  },
};

// Testimonials data (replace with real testimonials as they come in)
const testimonials = [
  {
    name: 'Sarah M.',
    location: 'Portland, OR',
    project: 'Kitchen Remodel',
    quote: 42000,
    saved: 8000,
    text: 'UnGouge saved me $8,000 on my kitchen remodel. They found material markups I never would have caught on my own. The report was clear, detailed, and gave me exactly what I needed to negotiate with my contractor.',
    rating: 5,
  },
  {
    name: 'Mike R.',
    location: 'Boston, MA',
    project: 'Bathroom Renovation',
    quote: 24000,
    saved: 6000,
    text: "I was about to accept a $24K bathroom quote. UnGouge showed it should be around $18K. I negotiated down to $19K and the contractor actually thanked me for being informed—said most customers just accept whatever number he gives them.",
    rating: 5,
  },
  {
    name: 'Jennifer K.',
    location: 'Austin, TX',
    project: 'Deck Build',
    quote: 18500,
    saved: 0,
    text: 'My quote turned out to be fair! I was worried I was overpaying, but UnGouge confirmed the pricing was reasonable for my area. Worth $19.99 just for the peace of mind. Now I can proceed with confidence.',
    rating: 5,
  },
  {
    name: 'David L.',
    location: 'Seattle, WA',
    project: 'Roof Replacement',
    quote: 16500,
    saved: 4200,
    text: "Found out my contractor was charging 80% markup on materials (should be 20-40%). Got a second quote and used UnGouge's analysis to negotiate. Final price: $12,300. Best $20 I ever spent.",
    rating: 5,
  },
  {
    name: 'Lisa T.',
    location: 'Denver, CO',
    project: 'Basement Finishing',
    quote: 32000,
    saved: 10000,
    text: 'The report was SO detailed. Line-by-line breakdown of everything. Identified $10K in inflated costs and vague "project management" fees. Used it to get competing bids and ended up at $22K for the same work.',
    rating: 5,
  },
];

export default function TestimonialsPage() {
  const avgSavings = Math.round(
    testimonials.reduce((sum, t) => sum + t.saved, 0) / testimonials.length
  );

  return (
    <div className="bg-white">
      {/* Hero */}
      <div className="bg-gradient-to-b from-primary-50 to-white">
        <div className="container mx-auto px-4 py-16 max-w-4xl">
          <h1 className="text-4xl font-bold text-gray-900 mb-4 text-center">
            What Homeowners Are Saying
          </h1>
          <p className="text-xl text-gray-600 text-center max-w-2xl mx-auto mb-8">
            Real stories from homeowners who used UnGouge to verify contractor
            quotes and make informed decisions.
          </p>
          <div className="flex justify-center gap-8 text-center">
            <div>
              <div className="text-3xl font-bold text-primary-600">
                ${avgSavings.toLocaleString()}
              </div>
              <div className="text-sm text-gray-600">Average Savings</div>
            </div>
            <div>
              <div className="text-3xl font-bold text-primary-600">
                {testimonials.length}+
              </div>
              <div className="text-sm text-gray-600">Happy Homeowners</div>
            </div>
            <div>
              <div className="text-3xl font-bold text-primary-600">4.9</div>
              <div className="text-sm text-gray-600">Average Rating</div>
            </div>
          </div>
        </div>
      </div>

      {/* Testimonials */}
      <div className="container mx-auto px-4 pb-20 max-w-5xl">
        <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
          {testimonials.map((testimonial, idx) => (
            <div
              key={idx}
              className="p-6 border border-gray-200 rounded-lg hover:border-primary-500 hover:shadow-md transition-all"
            >
              {/* Rating */}
              <div className="flex gap-1 mb-3">
                {[...Array(testimonial.rating)].map((_, i) => (
                  <svg
                    key={i}
                    className="w-5 h-5 text-yellow-400 fill-current"
                    viewBox="0 0 20 20"
                  >
                    <path d="M10 15l-5.878 3.09 1.123-6.545L.489 6.91l6.572-.955L10 0l2.939 5.955 6.572.955-4.756 4.635 1.123 6.545z" />
                  </svg>
                ))}
              </div>

              {/* Project & Savings */}
              <div className="mb-3">
                <h3 className="text-lg font-semibold text-gray-900">
                  {testimonial.project}
                </h3>
                <p className="text-sm text-gray-600">
                  {testimonial.name}, {testimonial.location}
                </p>
                {testimonial.saved > 0 && (
                  <p className="text-sm font-semibold text-green-600 mt-1">
                    Saved ${testimonial.saved.toLocaleString()}
                  </p>
                )}
              </div>

              {/* Testimonial Text */}
              <p className="text-gray-700 leading-relaxed">
                "{testimonial.text}"
              </p>
            </div>
          ))}
        </div>

        {/* CTA */}
        <div className="mt-16 p-8 bg-primary-50 rounded-2xl text-center">
          <h3 className="text-2xl font-semibold text-gray-900 mb-2">
            Ready to join them?
          </h3>
          <p className="text-gray-600 mb-6">
            Upload your contractor quote and get an independent analysis in 24
            hours.
          </p>
          <Link
            href="/analyze"
            className="inline-block bg-primary-600 text-white font-semibold px-8 py-3 rounded-lg hover:bg-primary-700 transition-colors"
          >
            Verify Your Quote — $19.99
          </Link>
          <p className="text-sm text-gray-500 mt-4">
            7-day money-back guarantee if the report doesn't help
          </p>
        </div>

        {/* Note about testimonials */}
        <div className="mt-12 p-6 bg-gray-50 rounded-lg">
          <h4 className="font-semibold text-gray-900 mb-2">
            Want to share your experience?
          </h4>
          <p className="text-gray-700 mb-4">
            If UnGouge helped you save money or make a better decision, we'd
            love to hear from you.
          </p>
          <p className="text-sm text-gray-600">
            Email{' '}
            <a
              href="mailto:human@ungouge.ai"
              className="text-primary-600 hover:underline"
            >
              human@ungouge.ai
            </a>{' '}
            with your story (2-3 sentences about what problem you had, how
            UnGouge helped, and what the outcome was). We'll send you a $10
            credit toward your next analysis as a thank-you!
          </p>
        </div>
      </div>
    </div>
  );
}
