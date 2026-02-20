import type { Metadata } from 'next';
import { Scale, FileText, Shield, AlertTriangle, CheckCircle } from 'lucide-react';

export const metadata: Metadata = {
  title: 'Terms of Service',
  description:
    'UnGouge.ai terms of service. Read our terms for using our contractor quote analysis service, explained in plain English.',
  alternates: {
    canonical: 'https://ungouge.ai/terms',
  },
};

export default function TermsPage() {
  return (
    <div className="py-12 bg-white">
      <div className="container mx-auto px-4 max-w-4xl">
        {/* Hero */}
        <div className="text-center mb-12">
          <div className="w-16 h-16 bg-primary-100 rounded-full flex items-center justify-center mx-auto mb-4">
            <Scale className="w-8 h-8 text-primary-600" />
          </div>
          <h1 className="text-4xl font-bold text-gray-900 mb-4">Terms of Service</h1>
          <p className="text-xl text-gray-600">
            The legal stuff, explained in plain English
          </p>
          <p className="text-sm text-gray-500 mt-2">Last updated: February 3, 2024</p>
        </div>

        {/* Plain English Summary */}
        <div className="bg-blue-50 border-2 border-blue-600 rounded-xl p-6 mb-12">
          <h2 className="text-2xl font-bold text-gray-900 mb-4 flex items-center gap-2">
            <FileText className="w-6 h-6 text-blue-600" />
            Plain English Summary
          </h2>
          <div className="space-y-2 text-gray-700">
            <p><strong>• You pay $9.99 per report.</strong> No subscriptions, no hidden fees.</p>
            <p><strong>• We analyze your quote honestly</strong> using real BLS data and material costs.</p>
            <p><strong>• Our reports are for your information,</strong> not legal or professional advice.</p>
            <p><strong>• We never guarantee specific outcomes</strong> in contractor negotiations.</p>
            <p><strong>• You can get a full refund within 7 days,</strong> no questions asked.</p>
            <p><strong>• We protect your data</strong> and never sell it to contractors (see our Privacy Policy).</p>
          </div>
          <p className="text-sm text-gray-600 mt-4">The legal version is below, but that's the gist.</p>
        </div>

        {/* Content Sections */}
        <div className="space-y-8">
          <section>
            <h2 className="text-2xl font-bold text-gray-900 mb-3">1. Acceptance of Terms</h2>
            <div className="space-y-3 text-gray-700">
              <p>By accessing or using Ungouge.ai ("Service"), you agree to be bound by these Terms of Service ("Terms"). If you disagree with any part of these terms, you may not access the Service.</p>
              
              <p>These Terms apply to all visitors, users, and others who access or use the Service.</p>
            </div>
          </section>

          <section>
            <h2 className="text-2xl font-bold text-gray-900 mb-3">2. Description of Service</h2>
            <div className="space-y-3 text-gray-700">
              <p>Ungouge.ai provides contractor quote analysis services. Specifically, we:</p>
              <ul className="list-disc list-inside space-y-2 ml-4">
                <li>Analyze contractor quotes you submit</li>
                <li>Compare quote line items against Bureau of Labor Statistics (BLS) wage data and material cost databases</li>
                <li>Provide reports indicating whether pricing appears fair, high, or significantly overpriced</li>
                <li>Offer negotiation suggestions and alternative pricing insights</li>
              </ul>
              
              <p className="font-semibold mt-4">What we are NOT:</p>
              <ul className="list-disc list-inside space-y-2 ml-4">
                <li>We are not a contractor referral service</li>
                <li>We are not a lead generation platform</li>
                <li>We do not provide legal, financial, or professional contracting advice</li>
                <li>We do not guarantee specific negotiation outcomes</li>
              </ul>
            </div>
          </section>

          <section>
            <h2 className="text-2xl font-bold text-gray-900 mb-3">3. Account Registration</h2>
            <div className="space-y-3 text-gray-700">
              <p>To use our Service, you must:</p>
              <ul className="list-disc list-inside space-y-2 ml-4">
                <li>Be at least 18 years old</li>
                <li>Provide accurate, current, and complete information during registration</li>
                <li>Maintain the security of your password and account</li>
                <li>Promptly notify us of any unauthorized use of your account</li>
                <li>Accept responsibility for all activities that occur under your account</li>
              </ul>
              
              <p>You may not use another person's account without permission. We reserve the right to refuse service, terminate accounts, or remove content at our discretion.</p>
            </div>
          </section>

          <section>
            <h2 className="text-2xl font-bold text-gray-900 mb-3">4. Pricing & Payment</h2>
            <div className="space-y-3 text-gray-700">
              <p><strong>Service Fee:</strong> Our quote analysis service costs $9.99 per report. This is a one-time fee per quote analyzed. There are no subscriptions, recurring charges, or hidden fees.</p>
              
              <p><strong>Payment Processing:</strong> Payments are processed securely through Stripe. By providing a payment method, you authorize us to charge you for the Service. All fees are in US dollars.</p>
              
              <p><strong>Taxes:</strong> Prices do not include applicable sales tax, which will be added where required by law.</p>
              
              <p><strong>No Automatic Renewal:</strong> We do not store your payment information for future charges. Each report is a separate transaction.</p>
            </div>
          </section>

          <section>
            <div className="flex items-start gap-3 mb-4">
              <CheckCircle className="w-6 h-6 text-green-600 flex-shrink-0 mt-1" />
              <div>
                <h2 className="text-2xl font-bold text-gray-900 mb-3">5. Refund Policy</h2>
                <div className="space-y-3 text-gray-700">
                  <p className="font-semibold">We offer a 100% money-back guarantee within 7 days of purchase.</p>
                  
                  <p>If you're not satisfied with your report for any reason, email us at <a href="mailto:support@ungouge.ai" className="text-primary-600 hover:underline">support@ungouge.ai</a> with your report ID within 7 days of purchase, and we'll issue a full refund.</p>
                  
                  <p>After 7 days, all sales are final. We believe 7 days is ample time to review your report and determine if it meets your needs.</p>
                  
                  <p><strong>Refund processing:</strong> Refunds are processed back to your original payment method within 5-10 business days.</p>
                </div>
              </div>
            </div>
          </section>

          <section>
            <div className="flex items-start gap-3 mb-4">
              <AlertTriangle className="w-6 h-6 text-yellow-600 flex-shrink-0 mt-1" />
              <div>
                <h2 className="text-2xl font-bold text-gray-900 mb-3">6. Disclaimers & Limitations</h2>
                <div className="space-y-3 text-gray-700">
                  <p className="font-semibold">IMPORTANT: Please read this section carefully.</p>
                  
                  <p><strong>Informational Purposes Only:</strong> Our reports are for informational purposes only. They do not constitute professional advice, legal advice, financial advice, or any form of professional consultation. You should consult with qualified professionals before making significant financial decisions.</p>
                  
                  <p><strong>No Guarantees:</strong> While we use real BLS data and material cost databases, contractor pricing can vary based on many factors including:</p>
                  <ul className="list-disc list-inside space-y-2 ml-4">
                    <li>Contractor experience and reputation</li>
                    <li>Regional market conditions and competition</li>
                    <li>Project complexity and custom requirements</li>
                    <li>Material quality variations</li>
                    <li>Seasonal demand fluctuations</li>
                    <li>Overhead and business model differences</li>
                  </ul>
                  
                  <p><strong>No Warranty:</strong> We provide our Service "AS IS" and "AS AVAILABLE" without warranties of any kind, either express or implied. We do not warrant that:</p>
                  <ul className="list-disc list-inside space-y-2 ml-4">
                    <li>The Service will be uninterrupted or error-free</li>
                    <li>Our analysis will result in lower contractor prices</li>
                    <li>Contractors will negotiate based on our reports</li>
                    <li>Our data is completely comprehensive or perfectly accurate</li>
                  </ul>
                  
                  <p><strong>Data Sources:</strong> We rely on third-party data sources including BLS wage data and material cost databases. While we strive for accuracy, these sources may have delays, errors, or regional variations. We update our data quarterly.</p>
                  
                  <p><strong>Your Judgment:</strong> Our reports are tools to help you make informed decisions. The final decision about whether to accept a quote, negotiate, or hire a contractor is entirely yours. You are responsible for your own due diligence.</p>
                </div>
              </div>
            </div>
          </section>

          <section>
            <h2 className="text-2xl font-bold text-gray-900 mb-3">7. Limitation of Liability</h2>
            <div className="space-y-3 text-gray-700">
              <p>TO THE MAXIMUM EXTENT PERMITTED BY LAW:</p>
              
              <p>Ungouge.ai, its officers, directors, employees, and agents shall not be liable for any indirect, incidental, special, consequential, or punitive damages, including but not limited to:</p>
              <ul className="list-disc list-inside space-y-2 ml-4">
                <li>Loss of profits or savings</li>
                <li>Costs of obtaining substitute services</li>
                <li>Contractor disputes or failed negotiations</li>
                <li>Project delays or complications</li>
                <li>Any damages arising from your use of or inability to use the Service</li>
              </ul>
              
              <p className="mt-4"><strong>Maximum Liability:</strong> In no event shall our total liability to you for all damages exceed the amount you paid us for the specific report in question (i.e., $9.99).</p>
              
              <p>Some jurisdictions do not allow the exclusion or limitation of liability for consequential or incidental damages, so the above limitations may not apply to you.</p>
            </div>
          </section>

          <section>
            <h2 className="text-2xl font-bold text-gray-900 mb-3">8. User Conduct & Prohibited Uses</h2>
            <div className="space-y-3 text-gray-700">
              <p>You agree not to:</p>
              <ul className="list-disc list-inside space-y-2 ml-4">
                <li>Violate any laws or regulations</li>
                <li>Submit false, fraudulent, or misleading information</li>
                <li>Attempt to reverse engineer, decompile, or hack our Service</li>
                <li>Use automated systems (bots, scrapers) to access the Service</li>
                <li>Resell, redistribute, or share your reports commercially without permission</li>
                <li>Abuse our refund policy through repeated frivolous refund requests</li>
                <li>Harass, threaten, or abuse our staff or other users</li>
                <li>Upload malicious code, viruses, or harmful content</li>
                <li>Impersonate another person or entity</li>
              </ul>
              
              <p className="mt-4">Violation of these terms may result in immediate termination of your account and legal action if necessary.</p>
            </div>
          </section>

          <section>
            <h2 className="text-2xl font-bold text-gray-900 mb-3">9. Intellectual Property</h2>
            <div className="space-y-3 text-gray-700">
              <p><strong>Our Content:</strong> The Service and its original content, features, and functionality are owned by Ungouge.ai and are protected by copyright, trademark, and other intellectual property laws.</p>
              
              <p><strong>Your Content:</strong> You retain ownership of any content you submit (quotes, project details). By submitting content, you grant us a license to use it solely for providing the Service and generating your report.</p>
              
              <p><strong>Reports:</strong> The reports we generate for you are for your personal, non-commercial use. You may share them with contractors, lenders, or others as needed for your project, but you may not resell or republish them commercially.</p>
              
              <p><strong>Trademarks:</strong> "Ungouge.ai" and related logos are trademarks of our company. You may not use them without prior written permission.</p>
            </div>
          </section>

          <section>
            <div className="flex items-start gap-3 mb-4">
              <Shield className="w-6 h-6 text-primary-600 flex-shrink-0 mt-1" />
              <div>
                <h2 className="text-2xl font-bold text-gray-900 mb-3">10. Privacy & Data Protection</h2>
                <div className="space-y-3 text-gray-700">
                  <p>Your privacy is critically important to us. Our collection and use of personal information is described in our <a href="/privacy" className="text-primary-600 hover:underline font-semibold">Privacy Policy</a>.</p>
                  
                  <p className="font-semibold">Core Privacy Commitment:</p>
                  <p>We will NEVER sell your data to contractors, lead generation companies, or third-party marketers. This is fundamental to our mission. See our Privacy Policy for complete details.</p>
                </div>
              </div>
            </div>
          </section>

          <section>
            <h2 className="text-2xl font-bold text-gray-900 mb-3">11. Termination</h2>
            <div className="space-y-3 text-gray-700">
              <p>We may terminate or suspend your account and access to the Service immediately, without prior notice, for conduct that we believe:</p>
              <ul className="list-disc list-inside space-y-2 ml-4">
                <li>Violates these Terms</li>
                <li>Is harmful to other users, us, or third parties</li>
                <li>Violates applicable law</li>
              </ul>
              
              <p className="mt-4">You may terminate your account at any time from your account settings or by emailing <a href="mailto:support@ungouge.ai" className="text-primary-600 hover:underline">support@ungouge.ai</a>. Upon termination, your right to use the Service will immediately cease.</p>
            </div>
          </section>

          <section>
            <h2 className="text-2xl font-bold text-gray-900 mb-3">12. Changes to Terms</h2>
            <div className="space-y-3 text-gray-700">
              <p>We reserve the right to modify these Terms at any time. If we make material changes, we will notify you by:</p>
              <ul className="list-disc list-inside space-y-2 ml-4">
                <li>Sending an email to your registered email address</li>
                <li>Posting a prominent notice on our Service</li>
                <li>Updating the "Last updated" date at the top of this page</li>
              </ul>
              
              <p className="mt-4">Your continued use of the Service after such modifications constitutes your acceptance of the updated Terms. If you disagree with the changes, you must stop using the Service.</p>
            </div>
          </section>

          <section>
            <h2 className="text-2xl font-bold text-gray-900 mb-3">13. Governing Law & Disputes</h2>
            <div className="space-y-3 text-gray-700">
              <p>These Terms shall be governed by and construed in accordance with the laws of the State of [Your State], United States, without regard to its conflict of law provisions.</p>
              
              <p><strong>Dispute Resolution:</strong> We prefer to resolve disputes amicably. If you have a concern, please contact us at <a href="mailto:support@ungouge.ai" className="text-primary-600 hover:underline">support@ungouge.ai</a> and we'll work with you to resolve it.</p>
              
              <p><strong>Arbitration:</strong> For disputes that cannot be resolved informally, both parties agree to submit to binding arbitration under the rules of the American Arbitration Association. Arbitration will take place in [Your City, State].</p>
              
              <p><strong>Class Action Waiver:</strong> You agree to bring claims against us only in your individual capacity and not as part of any class or representative action.</p>
            </div>
          </section>

          <section>
            <h2 className="text-2xl font-bold text-gray-900 mb-3">14. Miscellaneous</h2>
            <div className="space-y-3 text-gray-700">
              <p><strong>Entire Agreement:</strong> These Terms, together with our Privacy Policy, constitute the entire agreement between you and Ungouge.ai.</p>
              
              <p><strong>Severability:</strong> If any provision of these Terms is found to be unenforceable, the remaining provisions will remain in full effect.</p>
              
              <p><strong>Waiver:</strong> Our failure to enforce any right or provision of these Terms will not be considered a waiver of those rights.</p>
              
              <p><strong>Assignment:</strong> You may not assign or transfer these Terms. We may assign our rights and obligations without restriction.</p>
            </div>
          </section>

          <section>
            <h2 className="text-2xl font-bold text-gray-900 mb-3">15. Contact Information</h2>
            <div className="text-gray-700">
              <p className="mb-4">Questions about these Terms? Contact us:</p>
              <p><strong>Email:</strong> <a href="mailto:legal@ungouge.ai" className="text-primary-600 hover:underline">legal@ungouge.ai</a></p>
              <p><strong>Support:</strong> <a href="mailto:support@ungouge.ai" className="text-primary-600 hover:underline">support@ungouge.ai</a></p>
            </div>
          </section>
        </div>

        {/* Bottom CTA */}
        <div className="mt-12 p-6 bg-gray-50 rounded-xl border border-gray-200">
          <p className="text-center text-gray-700">
            <strong>The bottom line:</strong> We're here to help you avoid getting gouged by contractors. Use our reports wisely, make informed decisions, and don't hesitate to reach out if you have questions. We're on your side.
          </p>
        </div>
      </div>
    </div>
  );
}
