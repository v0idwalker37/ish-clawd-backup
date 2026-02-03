import Link from 'next/link';
import { Shield, Lock } from 'lucide-react';

export default function Footer() {
  const currentYear = new Date().getFullYear();

  return (
    <footer className="bg-gray-900 text-gray-300">
      <div className="container mx-auto px-4 py-12 max-w-6xl">
        {/* Data Privacy Badge - Prominent */}
        <div className="bg-gradient-to-r from-primary-900/30 to-primary-800/30 border-2 border-primary-700/50 rounded-xl p-6 mb-10">
          <div className="flex flex-col md:flex-row items-center justify-center gap-4 text-center md:text-left">
            <div className="flex items-center gap-3">
              <div className="w-12 h-12 bg-primary-600 rounded-full flex items-center justify-center flex-shrink-0">
                <Shield className="w-6 h-6 text-white" />
              </div>
              <div>
                <p className="text-white font-bold text-lg">We NEVER Sell Your Data</p>
                <p className="text-primary-200 text-sm">No lead generation. No contractor referrals. Zero data selling.</p>
              </div>
            </div>
            <div className="flex items-center gap-2 px-4 py-2 bg-green-900/30 border border-green-700/50 rounded-lg">
              <Lock className="w-4 h-4 text-green-400" />
              <span className="text-green-200 text-sm font-semibold">Your privacy guaranteed</span>
            </div>
          </div>
        </div>

        <div className="grid md:grid-cols-4 gap-8 mb-8">
          {/* Brand */}
          <div>
            <div className="flex items-center mb-4">
              <div className="text-2xl font-bold text-white">
                Ungouge<span className="text-primary-400">.ai</span>
              </div>
            </div>
            <p className="text-sm text-gray-400 mb-4">
              Fair contractor quote analysis powered by real BLS data. Built to protect homeowners, not profit from their information.
            </p>
            <a 
              href="mailto:support@ungouge.ai" 
              className="text-sm text-primary-400 hover:text-primary-300 transition-colors"
            >
              support@ungouge.ai
            </a>
          </div>

          {/* Product */}
          <div>
            <h3 className="font-semibold text-white mb-4">Product</h3>
            <ul className="space-y-2 text-sm">
              <li>
                <Link href="/analyze" className="hover:text-white transition-colors">
                  Analyze Quote
                </Link>
              </li>
              <li>
                <Link href="/pricing" className="hover:text-white transition-colors">
                  Pricing
                </Link>
              </li>
              <li>
                <Link href="/about" className="hover:text-white transition-colors">
                  How It Works
                </Link>
              </li>
              <li>
                <Link href="/dashboard" className="hover:text-white transition-colors">
                  Dashboard
                </Link>
              </li>
            </ul>
          </div>

          {/* Legal */}
          <div>
            <h3 className="font-semibold text-white mb-4">Legal & Support</h3>
            <ul className="space-y-2 text-sm">
              <li>
                <Link href="/privacy" className="hover:text-white transition-colors flex items-center gap-2">
                  <Shield className="w-3 h-3" />
                  Privacy Policy
                </Link>
              </li>
              <li>
                <Link href="/terms" className="hover:text-white transition-colors">
                  Terms of Service
                </Link>
              </li>
              <li>
                <Link href="/about" className="hover:text-white transition-colors">
                  About Us
                </Link>
              </li>
              <li>
                <a href="mailto:support@ungouge.ai" className="hover:text-white transition-colors">
                  Contact Support
                </a>
              </li>
            </ul>
          </div>

          {/* Trust Badges */}
          <div>
            <h3 className="font-semibold text-white mb-4">Our Guarantee</h3>
            <div className="space-y-3">
              <div className="flex items-start text-sm">
                <Shield className="w-4 h-4 mr-2 text-green-400 flex-shrink-0 mt-0.5" />
                <span>Zero lead generation</span>
              </div>
              <div className="flex items-start text-sm">
                <Shield className="w-4 h-4 mr-2 text-green-400 flex-shrink-0 mt-0.5" />
                <span>Never sell your data</span>
              </div>
              <div className="flex items-start text-sm">
                <Shield className="w-4 h-4 mr-2 text-green-400 flex-shrink-0 mt-0.5" />
                <span>No contractor kickbacks</span>
              </div>
              <div className="flex items-start text-sm">
                <Shield className="w-4 h-4 mr-2 text-green-400 flex-shrink-0 mt-0.5" />
                <span>100% refund guarantee</span>
              </div>
            </div>
          </div>
        </div>

        {/* Bottom Bar */}
        <div className="border-t border-gray-800 pt-8">
          <div className="flex flex-col md:flex-row items-center justify-between gap-4">
            <p className="text-sm text-gray-400">
              © {currentYear} Ungouge.ai. All rights reserved. Built to protect homeowners.
            </p>
            <div className="flex items-center gap-4 text-sm text-gray-400">
              <Link href="/privacy" className="hover:text-white transition-colors">
                Privacy
              </Link>
              <span>•</span>
              <Link href="/terms" className="hover:text-white transition-colors">
                Terms
              </Link>
              <span>•</span>
              <a href="mailto:support@ungouge.ai" className="hover:text-white transition-colors">
                Support
              </a>
            </div>
          </div>
        </div>
      </div>
    </footer>
  );
}
