import type { Metadata } from 'next';
import Link from 'next/link';
import { getAllLocations } from '@/lib/locations';
import { SITE_CONFIG } from '@/lib/seo';

export const metadata: Metadata = {
  title: 'Contractor Quote Verification by State | Local Pricing Data',
  description:
    'Get your contractor quote verified with state-specific pricing data. Independent analysis for homeowners across all 50 states.',
  alternates: {
    canonical: `${SITE_CONFIG.url}/locations`,
  },
};

export default function LocationsIndexPage() {
  const locations = getAllLocations();

  return (
    <div className="bg-white">
      {/* Hero */}
      <div className="bg-gradient-to-b from-primary-50 to-white">
        <div className="container mx-auto px-4 py-16 max-w-4xl text-center">
          <h1 className="text-4xl font-bold text-gray-900 mb-4">
            Contractor Quote Verification by State
          </h1>
          <p className="text-xl text-gray-600 max-w-2xl mx-auto">
            Get your quote analyzed with state-specific pricing data—not generic
            national averages. Select your state below.
          </p>
        </div>
      </div>

      {/* State Grid */}
      <div className="container mx-auto px-4 pb-20 max-w-5xl">
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
          {locations.map((location) => (
            <Link
              key={location.slug}
              href={`/locations/${location.slug}`}
              className="p-4 border border-gray-200 rounded-lg hover:border-primary-500 hover:shadow-md transition-all group"
            >
              <div className="flex items-center justify-between">
                <div>
                  <h2 className="text-lg font-semibold text-gray-900 group-hover:text-primary-600">
                    {location.title.split(' ')[0]}
                  </h2>
                  <p className="text-sm text-gray-500 mt-1">
                    {location.majorCities.slice(0, 2).join(', ')}
                    {location.majorCities.length > 2 && '...'}
                  </p>
                </div>
                <svg
                  className="w-5 h-5 text-gray-400 group-hover:text-primary-600 transition-colors"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M9 5l7 7-7 7"
                  />
                </svg>
              </div>
            </Link>
          ))}
        </div>
      </div>
    </div>
  );
}
