import type { Metadata } from 'next';
import { Shield, Lock, Eye, Database, UserX, FileText } from 'lucide-react';

export const metadata: Metadata = {
  title: 'Privacy Policy',
  description:
    'UnGouge.ai privacy policy. We never sell your data to contractors or lead generation companies. Your quotes and contact details stay completely private.',
  alternates: {
    canonical: 'https://ungouge.ai/privacy',
  },
};

export default function PrivacyPage() {
  return (
    <div className="py-12 bg-white">
      <div className="container mx-auto px-4 max-w-4xl">
        {/* Hero */}
        <div className="text-center mb-12">
          <div className="w-16 h-16 bg-primary-100 rounded-full flex items-center justify-center mx-auto mb-4">
            <Shield className="w-8 h-8 text-primary-600" />
          </div>
          <h1 className="text-4xl font-bold text-gray-900 mb-4">Privacy Policy</h1>
          <p className="text-xl text-gray-600">
            We protect your data because that's literally our entire mission
          </p>
          <p className="text-sm text-gray-500 mt-2">Last updated: February 13, 2026</p>
        </div>

        {/* Core Promise */}
        <div className="bg-primary-50 border-2 border-primary-600 rounded-xl p-6 mb-12">
          <h2 className="text-2xl font-bold text-gray-900 mb-4 flex items-center gap-2">
            <UserX className="w-6 h-6 text-primary-600" />
            Our Core Promise: No Lead Generation. Ever.
          </h2>
          <p className="text-gray-700 leading-relaxed mb-4">
            Unlike other "contractor quote" websites that exist solely to harvest your information and sell it to contractors, <strong>Ungouge.ai will NEVER sell, share, or monetize your personal data</strong>. We make money only from you, by providing honest analysis. Not from contractors paying for your contact information.
          </p>
          <p className="text-gray-700 leading-relaxed font-semibold">
            We will NEVER share your quotes, project details, or contact information with contractors, lead generation companies, or marketing firms. This is fundamental to who we are.
          </p>
        </div>

        {/* Content Sections */}
        <div className="space-y-8">
          <section>
            <div className="flex items-start gap-3 mb-4">
              <Database className="w-6 h-6 text-primary-600 flex-shrink-0 mt-1" />
              <div>
                <h2 className="text-2xl font-bold text-gray-900 mb-3">What Information We Collect</h2>
                <div className="space-y-3 text-gray-700">
                  <p><strong>Account Information:</strong> When you create an account, we collect your name, email address, and encrypted password. We never store passwords in plain text.</p>
                  
                  <p><strong>Quote Data:</strong> When you submit a contractor quote for analysis, we collect the project details, line items, costs, contractor name, and location. This data is necessary to perform our analysis.</p>
                  
                  <p><strong>Payment Information:</strong> We use Stripe for payment processing. We never see or store your full credit card numbers. Stripe maintains PCI DSS compliance on our behalf.</p>
                  
                  <p><strong>Usage Data:</strong> We collect basic analytics about how you use our service (pages visited, features used) to improve our product. This is aggregated and anonymized.</p>
                  
                  <p><strong>What We DON'T Collect:</strong> We don't use tracking pixels, we don't sell data to advertisers, we don't install third-party analytics beyond essential infrastructure monitoring.</p>
                </div>
              </div>
            </div>
          </section>

          <section>
            <div className="flex items-start gap-3 mb-4">
              <Lock className="w-6 h-6 text-primary-600 flex-shrink-0 mt-1" />
              <div>
                <h2 className="text-2xl font-bold text-gray-900 mb-3">How We Use Your Information</h2>
                <div className="space-y-3 text-gray-700">
                  <p>We use your information exclusively for:</p>
                  <ul className="list-disc list-inside space-y-2 ml-4">
                    <li><strong>Providing our service:</strong> Analyzing your quotes using BLS data and material cost databases</li>
                    <li><strong>Account management:</strong> Maintaining your account, sending transactional emails (receipts, report notifications)</li>
                    <li><strong>Customer support:</strong> Responding to your questions and helping you understand your reports</li>
                    <li><strong>Service improvement:</strong> Understanding how people use our service to make it better (always anonymized)</li>
                    <li><strong>Legal compliance:</strong> Meeting legal obligations like tax reporting</li>
                  </ul>
                  
                  <p className="font-semibold mt-4">We will NEVER use your information for:</p>
                  <ul className="list-disc list-inside space-y-2 ml-4">
                    <li>Selling to contractors or lead generation companies</li>
                    <li>Sharing with third-party marketing platforms</li>
                    <li>Building advertising profiles</li>
                    <li>Sending spam or promotional content from third parties</li>
                  </ul>
                </div>
              </div>
            </div>
          </section>

          <section>
            <div className="flex items-start gap-3 mb-4">
              <Shield className="w-6 h-6 text-primary-600 flex-shrink-0 mt-1" />
              <div>
                <h2 className="text-2xl font-bold text-gray-900 mb-3">Data Security</h2>
                <div className="space-y-3 text-gray-700">
                  <p>We take security seriously:</p>
                  <ul className="list-disc list-inside space-y-2 ml-4">
                    <li><strong>Encryption in transit:</strong> All data is transmitted using TLS 1.3 encryption</li>
                    <li><strong>Encryption at rest:</strong> Your data is encrypted using AES-256 encryption in our databases</li>
                    <li><strong>Access controls:</strong> Only essential personnel have access to production systems, with full audit logging</li>
                    <li><strong>Regular security audits:</strong> We conduct quarterly security reviews and penetration testing</li>
                    <li><strong>Secure infrastructure:</strong> We host on AWS with enterprise-grade security controls</li>
                    <li><strong>Password security:</strong> All passwords are hashed using bcrypt with work factor 12</li>
                  </ul>
                </div>
              </div>
            </div>
          </section>

          <section>
            <div className="flex items-start gap-3 mb-4">
              <Eye className="w-6 h-6 text-primary-600 flex-shrink-0 mt-1" />
              <div>
                <h2 className="text-2xl font-bold text-gray-900 mb-3">Data Sharing & Third Parties</h2>
                <div className="space-y-3 text-gray-700">
                  <p>We share your data with a minimal number of trusted service providers, and ONLY to the extent necessary to provide our service:</p>
                  
                  <p><strong>Service providers we use:</strong></p>
                  <ul className="list-disc list-inside space-y-2 ml-4">
                    <li><strong>Stripe:</strong> Payment processing (they never share your credit card details with us)</li>
                    <li><strong>AWS:</strong> Hosting and infrastructure (data stored in US-East region)</li>
                    <li><strong>SendGrid:</strong> Transactional emails only (receipts, password resets, report notifications)</li>
                  </ul>
                  
                  <p className="font-semibold mt-4">We will NEVER share your data with:</p>
                  <ul className="list-disc list-inside space-y-2 ml-4">
                    <li>Contractors or contractor networks</li>
                    <li>Lead generation or lead aggregation companies</li>
                    <li>Marketing platforms or advertising networks</li>
                    <li>Data brokers</li>
                    <li>Any party that would use it for purposes other than providing our core service</li>
                  </ul>
                  
                  <p className="mt-4"><strong>Legal requirements:</strong> We may disclose information if required by law (e.g., valid subpoena), but we will notify you first unless legally prohibited.</p>
                </div>
              </div>
            </div>
          </section>

          <section>
            <div className="flex items-start gap-3 mb-4">
              <FileText className="w-6 h-6 text-primary-600 flex-shrink-0 mt-1" />
              <div>
                <h2 className="text-2xl font-bold text-gray-900 mb-3">Your Rights & Data Control</h2>
                <div className="space-y-3 text-gray-700">
                  <p>You have complete control over your data:</p>
                  <ul className="list-disc list-inside space-y-2 ml-4">
                    <li><strong>Access:</strong> You can view all your data in your account dashboard at any time</li>
                    <li><strong>Download:</strong> You can export all your quotes and reports as PDF or JSON</li>
                    <li><strong>Correction:</strong> You can edit your account information and quote details anytime</li>
                    <li><strong>Deletion:</strong> You can delete your account and all associated data from your settings page. We'll permanently delete everything within 30 days</li>
                    <li><strong>Portability:</strong> You can download your data in machine-readable formats</li>
                    <li><strong>Opt-out:</strong> You can opt out of any non-essential emails (we'll still send transactional emails like receipts)</li>
                  </ul>
                  
                  <p className="mt-4">To exercise any of these rights, email us at <a href="mailto:legal@ungouge.ai" className="text-primary-600 hover:underline font-semibold">legal@ungouge.ai</a> or use your account settings.</p>
                </div>
              </div>
            </div>
          </section>

          <section>
            <h2 className="text-2xl font-bold text-gray-900 mb-3">Data Retention</h2>
            <div className="space-y-3 text-gray-700">
              <p>We retain your data only as long as necessary:</p>
              <ul className="list-disc list-inside space-y-2 ml-4">
                <li><strong>Active accounts:</strong> We keep your data while your account is active</li>
                <li><strong>Deleted accounts:</strong> Data is permanently deleted within 30 days of account deletion</li>
                <li><strong>Legal retention:</strong> Some data (invoices, payment records) must be kept for 7 years for tax purposes, but is encrypted and access-restricted</li>
              </ul>
            </div>
          </section>

          <section>
            <h2 className="text-2xl font-bold text-gray-900 mb-3">Cookies & Tracking</h2>
            <div className="space-y-3 text-gray-700">
              <p>We use minimal cookies:</p>
              <ul className="list-disc list-inside space-y-2 ml-4">
                <li><strong>Essential cookies:</strong> Authentication session cookies (required for login)</li>
                <li><strong>Analytics:</strong> Basic, anonymized page view analytics to understand usage patterns</li>
                <li><strong>What we DON'T use:</strong> No advertising cookies, no cross-site tracking, no third-party marketing pixels</li>
              </ul>
            </div>
          </section>

          <section>
            <h2 className="text-2xl font-bold text-gray-900 mb-3">Children's Privacy</h2>
            <p className="text-gray-700">
              Our service is not intended for anyone under 18. We do not knowingly collect information from children. If you believe we've accidentally collected data from a child, please contact us immediately at <a href="mailto:legal@ungouge.ai" className="text-primary-600 hover:underline">legal@ungouge.ai</a>.
            </p>
          </section>

          <section>
            <h2 className="text-2xl font-bold text-gray-900 mb-3">International Users</h2>
            <p className="text-gray-700">
              Our service is operated in the United States. If you're accessing from outside the US, your data will be transferred to and processed in the United States. By using our service, you consent to this transfer. We comply with applicable data protection regulations including GDPR for EU users.
            </p>
          </section>

          <section>
            <h2 className="text-2xl font-bold text-gray-900 mb-3">Changes to This Policy</h2>
            <p className="text-gray-700">
              We may update this privacy policy occasionally. We'll notify you of significant changes via email and update the "Last updated" date at the top. Your continued use of the service after changes constitutes acceptance of the updated policy.
            </p>
          </section>

          <section>
            <h2 className="text-2xl font-bold text-gray-900 mb-3">Contact Us</h2>
            <div className="text-gray-700">
              <p className="mb-2">Questions about privacy? We're here to help:</p>
              <p><strong>Email:</strong> <a href="mailto:legal@ungouge.ai" className="text-primary-600 hover:underline">legal@ungouge.ai</a></p>
              <p><strong>General support:</strong> <a href="mailto:support@ungouge.ai" className="text-primary-600 hover:underline">support@ungouge.ai</a></p>
            </div>
          </section>
        </div>

        {/* Bottom CTA */}
        <div className="mt-12 p-6 bg-gray-50 rounded-xl border border-gray-200">
          <p className="text-center text-gray-700">
            <strong>Remember:</strong> We're on your side. Our business model is protecting you from getting gouged, not selling your data. If you have any concerns about how we handle your information, please reach out. We're happy to explain our practices in detail.
          </p>
        </div>
      </div>
    </div>
  );
}
