'use client';

import { useState, useRef, useCallback } from 'react';
import { useRouter } from 'next/navigation';
import { useForm, useFieldArray } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { Plus, Trash2, ArrowRight, ArrowLeft, FileText, AlertCircle, LogIn } from 'lucide-react';
import FileUpload, { ParsedQuoteData } from './FileUpload';
import { useAuth } from '@/providers/AuthProvider';
import Link from 'next/link';

const lineItemSchema = z.object({
  item_name: z.string().min(1, 'Item name is required'),
  description: z.string().optional().default(''),
  quoted_price: z.number().min(0, 'Price must be positive'),
  quantity: z.number().min(1, 'Quantity must be at least 1').default(1),
  unit: z.string().min(1, 'Please select a unit type'),
});

const quoteFormSchema = z.object({
  project_type: z.string().min(1, 'Project type is required'),
  location: z.string().min(1, 'Location is required'),
  contractor_name: z.string().optional(),
  line_items: z.array(lineItemSchema).min(1, 'Add at least one line item'),
});

type QuoteFormData = z.infer<typeof quoteFormSchema>;

const unitOptions = [
  { value: 'item', label: 'Item (lump sum)' },
  { value: 'sqft', label: 'Square Feet' },
  { value: 'lnft', label: 'Linear Feet' },
  { value: 'each', label: 'Each' },
  { value: 'hour', label: 'Hours' },
  { value: 'day', label: 'Days' },
  { value: 'sqyd', label: 'Square Yards' },
  { value: 'cuyd', label: 'Cubic Yards' },
  { value: 'ton', label: 'Tons' },
  { value: 'bundle', label: 'Bundles' },
  { value: 'sheet', label: 'Sheets' },
  { value: 'room', label: 'Rooms' },
  { value: 'fixture', label: 'Fixtures' },
  { value: 'other', label: 'Other' },
];

const projectTypes = [
  'Kitchen Remodel',
  'Bathroom Remodel',
  'Roof Replacement',
  'HVAC Installation',
  'Plumbing Work',
  'Electrical Work',
  'Flooring Installation',
  'Painting (Interior)',
  'Painting (Exterior)',
  'Deck Construction',
  'Basement Finishing',
  'Other',
];

export default function QuoteForm() {
  const [step, setStepRaw] = useState(0); // Start at 0 (upload step)
  const formRef = useRef<HTMLDivElement>(null);
  const setStep = useCallback((newStep: number) => {
    setStepRaw(newStep);
    // Scroll form into view so user sees the new step
    setTimeout(() => {
      formRef.current?.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }, 50);
  }, []);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [uploadError, setUploadError] = useState<string | null>(null);
  const [showAuthPrompt, setShowAuthPrompt] = useState(false);
  const [estimationData, setEstimationData] = useState<{
    is_estimated: boolean;
    estimation_confidence?: string;
    estimation_methodology?: string;
  } | null>(null);
  const router = useRouter();
  const { user, loading: authLoading } = useAuth();

  const {
    register,
    handleSubmit,
    control,
    formState: { errors },
    watch,
    reset,
    setValue,
  } = useForm<QuoteFormData>({
    resolver: zodResolver(quoteFormSchema),
    defaultValues: {
      line_items: [{ item_name: '', description: '', quoted_price: 0, quantity: 1, unit: 'item' }],
    },
  });

  const { fields, append, remove } = useFieldArray({
    control,
    name: 'line_items',
  });

  const handleFileProcessed = (data: ParsedQuoteData) => {
    // Check auth before allowing user to proceed
    if (!user && !authLoading) {
      setShowAuthPrompt(true);
      return;
    }
    
    // Pre-fill form with parsed data
    if (data.project_type) {
      setValue('project_type', data.project_type);
    }
    if (data.location) {
      setValue('location', data.location);
    }
    if (data.contractor_name) {
      setValue('contractor_name', data.contractor_name);
    }
    if (data.line_items && data.line_items.length > 0) {
      setValue('line_items', data.line_items.map(item => ({
        ...item,
        description: item.description || '',
      })));
    }
    
    // Store estimation data if present
    if (data.is_estimated) {
      setEstimationData({
        is_estimated: true,
        estimation_confidence: data.estimation_confidence,
        estimation_methodology: data.estimation_methodology,
      });
    } else {
      setEstimationData(null);
    }
    
    // Move to next step
    setStep(1);
    setUploadError(null);
  };

  const handleUploadError = (error: string) => {
    setUploadError(error);
  };

  const skipUpload = () => {
    // Check auth before allowing user to start filling form
    if (!user && !authLoading) {
      setShowAuthPrompt(true);
      return;
    }
    setStep(1);
  };

  const [promoCode, setPromoCode] = useState('');
  const [promoApplied, setPromoApplied] = useState(false);

  const onSubmit = async (data: QuoteFormData) => {
    // Gate: require account before checkout (so users have historical reports)
    if (!user) {
      setShowAuthPrompt(true);
      return;
    }

    setLoading(true);
    setError(null);

    try {
      // Step 1: Save the quote as a draft (no analysis yet — that happens after payment)
      const quoteRes = await fetch('/api/quotes', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        credentials: 'include',
        body: JSON.stringify({
          ...data,
          // Include estimation metadata if present
          is_estimated: estimationData?.is_estimated || false,
          estimation_confidence: estimationData?.estimation_confidence,
          estimation_methodology: estimationData?.estimation_methodology,
        }),
      });

      if (!quoteRes.ok) {
        const errData = await quoteRes.json().catch(() => ({}));
        const detail = errData.detail;
        if (typeof detail === 'object' && detail?.error) {
          throw new Error(detail.error + (detail.suggestion ? ` ${detail.suggestion}` : ''));
        } else if (typeof detail === 'string') {
          throw new Error(detail);
        }
        throw new Error('Failed to save your quote.');
      }

      const quoteData = await quoteRes.json();
      const quoteId = quoteData.id;

      // Step 2: If promo code entered, try applying it first
      if (promoCode.trim()) {
        const promoRes = await fetch('/api/payments/apply-promo', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          credentials: 'include',
          body: JSON.stringify({ quote_id: quoteId, promo_code: promoCode.trim() }),
        });

        if (promoRes.ok) {
          const promoData = await promoRes.json();
          // Promo applied — redirect to report
          window.location.href = promoData.report_url || `/report/${quoteId}?payment=success`;
          return;
        } else {
          const promoErr = await promoRes.json().catch(() => ({}));
          const errMsg = promoErr.detail?.error || promoErr.detail || 'Invalid promo code.';
          // Don't fail — just warn and fall through to Stripe
          setError(`Promo code error: ${errMsg} Proceeding to payment...`);
          await new Promise(r => setTimeout(r, 2000));
          setError(null);
        }
      }
      
      // Step 3: Create a Stripe Checkout Session
      const checkoutRes = await fetch('/api/payments/create-checkout', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        credentials: 'include',
        body: JSON.stringify({ quote_id: quoteId }),
      });

      if (!checkoutRes.ok) {
        const errData = await checkoutRes.json().catch(() => ({}));
        throw new Error(errData.detail || 'Failed to create checkout session.');
      }

      const checkoutData = await checkoutRes.json();
      
      // Step 4: Redirect to Stripe Checkout (external hosted page)
      // Stripe handles payment collection; on success it redirects to /report/{quoteId}?payment=success
      const checkoutUrl = checkoutData.checkout_url;
      if (checkoutUrl) {
        window.location.href = checkoutUrl;
      } else {
        throw new Error('No checkout URL returned');
      }
    } catch (err: unknown) {
      console.error('Error submitting quote:', err);
      if (err instanceof Error) {
        setError(err.message);
      } else {
        setError('Failed to process your quote. Please try again.');
      }
      setLoading(false);
    }
  };

  const projectType = watch('project_type');
  const lineItems = watch('line_items');
  const totalQuoted = lineItems.reduce((sum, item) => {
    const price = item.quoted_price || 0;
    const qty = item.quantity || 1;
    return sum + (price * qty);
  }, 0);

  return (
    <div className="card" ref={formRef}>
      {/* Auth Prompt Modal */}
      {showAuthPrompt && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
          <div className="bg-white rounded-2xl max-w-md w-full p-8 shadow-2xl">
            <div className="text-center mb-6">
              <div className="w-16 h-16 bg-primary-100 rounded-full flex items-center justify-center mx-auto mb-4">
                <LogIn className="w-8 h-8 text-primary-600" />
              </div>
              <h3 className="text-2xl font-bold text-gray-900 mb-2">Create Your Account</h3>
              <p className="text-gray-600">
                Sign up to save your quote and access your report anytime. Your data stays private — we never sell it.
              </p>
            </div>
            <div className="space-y-3">
              <Link
                href="/register?redirect=/analyze"
                className="block w-full text-center bg-primary-600 text-white px-6 py-3 rounded-lg font-semibold hover:bg-primary-700 transition-colors"
              >
                Create Free Account
              </Link>
              <Link
                href="/login?redirect=/analyze"
                className="block w-full text-center bg-gray-100 text-gray-700 px-6 py-3 rounded-lg font-semibold hover:bg-gray-200 transition-colors"
              >
                Already have an account? Sign In
              </Link>
            </div>
            <button
              onClick={() => setShowAuthPrompt(false)}
              className="mt-4 w-full text-center text-sm text-gray-500 hover:text-gray-700"
            >
              Go back to editing
            </button>
          </div>
        </div>
      )}

      {/* Progress Indicator */}
      <div className="mb-8">
        <div className="flex justify-between items-center mb-2">
          <span className={`text-sm font-medium ${step >= 0 ? 'text-primary-600' : 'text-gray-400'}`}>
            1. Upload Quote
          </span>
          <span className={`text-sm font-medium ${step >= 1 ? 'text-primary-600' : 'text-gray-400'}`}>
            2. Project Info
          </span>
          <span className={`text-sm font-medium ${step >= 2 ? 'text-primary-600' : 'text-gray-400'}`}>
            3. Quote Details & Pay
          </span>
        </div>
        <div className="h-2 bg-gray-200 rounded-full">
          <div
            className="h-2 bg-primary-600 rounded-full transition-all duration-300"
            style={{ width: `${((step + 1) / 3) * 100}%` }}
          />
        </div>
      </div>

      {/* Auth Status Banner */}
      {!authLoading && !user && step > 0 && (
        <div className="mb-6 bg-amber-50 border-l-4 border-amber-500 p-4 rounded-r-lg">
          <div className="flex items-start gap-3">
            <AlertCircle className="w-5 h-5 text-amber-600 flex-shrink-0 mt-0.5" />
            <div className="flex-1">
              <p className="text-amber-900 font-semibold mb-1">Account Required</p>
              <p className="text-amber-800 text-sm mb-3">
                You'll need to sign in before checkout to save your quote and access your report.
              </p>
              <div className="flex gap-3">
                <Link
                  href="/login?redirect=/analyze"
                  className="text-sm font-semibold text-amber-900 hover:text-amber-950 underline"
                >
                  Sign In
                </Link>
                <Link
                  href="/register?redirect=/analyze"
                  className="text-sm font-semibold text-amber-900 hover:text-amber-950 underline"
                >
                  Create Account
                </Link>
              </div>
            </div>
          </div>
        </div>
      )}

      <form onSubmit={handleSubmit(onSubmit)}>
        {/* Step 0: Upload Quote */}
        {step === 0 && (
          <div className="space-y-6">
            <div className="text-center mb-8">
              <FileText className="w-16 h-16 mx-auto mb-4 text-blue-600" />
              <h2 className="text-2xl font-bold mb-2">Upload Your Quote</h2>
              <p className="text-gray-600">
                Skip the manual entry! Upload your contractor quote and we'll extract all the details automatically.
              </p>
            </div>

            {uploadError && (
              <div className="bg-red-50 border-l-4 border-red-500 rounded-lg p-4 mb-6 animate-shake">
                <div className="flex items-start gap-3">
                  <AlertCircle className="w-5 h-5 text-red-600 flex-shrink-0 mt-0.5" />
                  <div>
                    <h4 className="font-semibold text-red-900 mb-1">Upload Failed</h4>
                    <p className="text-red-700 text-sm">{uploadError}</p>
                  </div>
                </div>
              </div>
            )}

            <FileUpload 
              onFileProcessed={handleFileProcessed}
              onError={handleUploadError}
            />

            <div className="mt-8 pt-6 border-t border-gray-200">
              <div className="text-center">
                <p className="text-gray-600 mb-4">
                  Don't have a digital quote? No problem!
                </p>
                <button
                  type="button"
                  onClick={skipUpload}
                  className="btn-secondary hover:shadow-lg active:scale-95 transition-all"
                >
                  Enter Details Manually
                </button>
              </div>
            </div>
          </div>
        )}

        {/* Step 1: Project Information */}
        {step === 1 && (
          <div className="space-y-6">
            <h2 className="text-2xl font-bold mb-6">Project Information</h2>

            {/* Total-Only Quote — honest expectations banner */}
            {estimationData?.is_estimated && (
              <div className="bg-blue-50 border border-blue-200 rounded-xl p-5 space-y-4">
                <div className="flex items-start gap-3">
                  <span className="text-2xl flex-shrink-0">📋</span>
                  <div>
                    <h4 className="font-bold text-blue-900 text-base">
                      Total-Only Quote Detected
                    </h4>
                    <p className="text-blue-800 text-sm mt-1">
                      Your quote includes a total price but no per-item cost breakdown. 
                      Here&apos;s what that means for your report:
                    </p>
                  </div>
                </div>

                <div className="space-y-2.5 pl-1">
                  <div className="flex items-start gap-2.5">
                    <span className="text-emerald-500 font-bold text-sm mt-px">✅</span>
                    <p className="text-sm text-gray-800">
                      <strong>What you&apos;ll get:</strong> Total price fairness analysis against 
                      current market rates, plus typical cost ranges for each work item in your area
                    </p>
                  </div>
                  <div className="flex items-start gap-2.5">
                    <span className="text-amber-500 font-bold text-sm mt-px">⚠️</span>
                    <p className="text-sm text-gray-800">
                      <strong>What we can&apos;t do:</strong> Rate individual line items as 
                      fair or overpriced — without your contractor&apos;s per-item pricing, there&apos;s 
                      no way to know what they&apos;re charging for each piece
                    </p>
                  </div>
                  <div className="flex items-start gap-2.5">
                    <span className="text-blue-500 font-bold text-sm mt-px">💡</span>
                    <p className="text-sm text-gray-800">
                      <strong>Want the full analysis?</strong> Ask your contractor for an 
                      itemized breakdown and re-submit for detailed fair-price ratings on every line item
                    </p>
                  </div>
                </div>
              </div>
            )}

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Project Type *
              </label>
              <select
                {...register('project_type')}
                className={`input-field ${errors.project_type ? 'border-red-500 ring-2 ring-red-200' : ''}`}
              >
                <option value="">Select project type...</option>
                {projectTypes.map((type) => (
                  <option key={type} value={type}>
                    {type}
                  </option>
                ))}
              </select>
              {errors.project_type && (
                <div className="flex items-center gap-2 mt-2 text-red-600">
                  <AlertCircle className="w-4 h-4 flex-shrink-0" />
                  <p className="text-sm">{errors.project_type.message}</p>
                </div>
              )}
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Location (City, State) *
              </label>
              <input
                type="text"
                {...register('location')}
                placeholder="e.g., Denver, CO"
                className={`input-field ${errors.location ? 'border-red-500 ring-2 ring-red-200' : ''}`}
              />
              {errors.location && (
                <div className="flex items-center gap-2 mt-2 text-red-600">
                  <AlertCircle className="w-4 h-4 flex-shrink-0" />
                  <p className="text-sm">{errors.location.message}</p>
                </div>
              )}
              <p className="text-gray-500 text-sm mt-1">
                We use this to match regional labor rates and material costs
              </p>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                Contractor Name (Optional)
              </label>
              <input
                type="text"
                {...register('contractor_name')}
                placeholder="ABC Contracting"
                className="input-field"
              />
              <p className="text-gray-500 text-sm mt-1">
                For your records only — never shared
              </p>
            </div>

            <div className="flex justify-end">
              <button
                type="button"
                onClick={() => setStep(2)}
                disabled={!projectType || !watch('location')}
                className="btn-primary flex items-center disabled:opacity-50 disabled:cursor-not-allowed transition-all hover:shadow-lg active:scale-95"
              >
                Next: Quote Details
                <ArrowRight className="w-4 h-4 ml-2" />
              </button>
            </div>
          </div>
        )}

        {/* Step 2: Line Items */}
        {step === 2 && (
          <div className="space-y-6">
            {estimationData?.is_estimated ? (
              /* ── Total-Only Quote: Simplified View (no fake per-item prices) ── */
              <>
                <h2 className="text-2xl font-bold mb-2">Work Items From Your Quote</h2>
                <p className="text-gray-600 mb-4">
                  Your contractor provided a total price without per-item costs.
                  We identified {fields.length} work item{fields.length !== 1 ? 's' : ''} from your quote.
                  We&apos;ll analyze the <strong>total price</strong> against market rates and provide
                  typical cost ranges for each item in your area.
                </p>

                <div className="space-y-3">
                  {fields.map((field, index) => (
                    <div key={field.id} className="p-4 border border-gray-200 rounded-lg bg-gray-50">
                      <div className="flex items-start gap-3">
                        <span className="flex-shrink-0 w-7 h-7 bg-primary-100 text-primary-700 rounded-full flex items-center justify-center text-sm font-bold mt-0.5">
                          {index + 1}
                        </span>
                        <div className="flex-1">
                          <h3 className="font-semibold text-gray-900">
                            {watch(`line_items.${index}.item_name`) || `Item ${index + 1}`}
                          </h3>
                          {watch(`line_items.${index}.description`) && (
                            <p className="text-sm text-gray-600 mt-1">
                              {watch(`line_items.${index}.description`)}
                            </p>
                          )}
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </>
            ) : (
              /* ── Itemized Quote: Full Editable View ── */
              <>
                <h2 className="text-2xl font-bold mb-6">Quote Line Items</h2>
                <p className="text-gray-600 mb-4">
                  Break down your contractor's quote into individual line items for detailed analysis.
                </p>

                {fields.map((field, index) => (
                  <div key={field.id} className="p-4 border border-gray-200 rounded-lg">
                    <div className="flex justify-between items-start mb-4">
                      <h3 className="font-semibold text-gray-700">Item {index + 1}</h3>
                      {fields.length > 1 && (
                        <button
                          type="button"
                          onClick={() => remove(index)}
                          className="p-2 rounded-lg text-red-500 hover:text-red-700 hover:bg-red-50 active:scale-95 transition-all"
                          aria-label="Remove line item"
                        >
                          <Trash2 className="w-4 h-4" />
                        </button>
                      )}
                    </div>

                    <div className="grid md:grid-cols-2 gap-4">
                      <div className="md:col-span-2">
                        <label className="block text-sm font-medium text-gray-700 mb-2">
                          Item Name *
                        </label>
                        <input
                          type="text"
                          {...register(`line_items.${index}.item_name`)}
                          placeholder="e.g., Cabinet Installation"
                          className={`input-field ${errors.line_items?.[index]?.item_name ? 'border-red-500 ring-2 ring-red-200' : ''}`}
                        />
                        {errors.line_items?.[index]?.item_name && (
                          <div className="flex items-center gap-2 mt-2 text-red-600">
                            <AlertCircle className="w-4 h-4 flex-shrink-0" />
                            <p className="text-sm">
                              {errors.line_items[index]?.item_name?.message}
                            </p>
                          </div>
                        )}
                      </div>

                      <div className="md:col-span-2">
                        <label className="block text-sm font-medium text-gray-700 mb-2">
                          Description <span className="text-gray-400 font-normal">(Optional)</span>
                        </label>
                        <input
                          type="text"
                          {...register(`line_items.${index}.description`)}
                          placeholder="Optional - additional details about this item..."
                          className="input-field"
                        />
                      </div>

                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-2">
                          Price per Unit *
                        </label>
                        <div className="relative">
                          <span className="absolute left-3 top-2 text-gray-500">$</span>
                          <input
                            type="number"
                            step="0.01"
                            {...register(`line_items.${index}.quoted_price`, {
                              valueAsNumber: true,
                            })}
                            placeholder="0.00"
                            className={`input-field pl-7 ${errors.line_items?.[index]?.quoted_price ? 'border-red-500 ring-2 ring-red-200' : ''}`}
                          />
                        </div>
                        {errors.line_items?.[index]?.quoted_price && (
                          <div className="flex items-center gap-2 mt-2 text-red-600">
                            <AlertCircle className="w-4 h-4 flex-shrink-0" />
                            <p className="text-sm">
                              {errors.line_items[index]?.quoted_price?.message}
                            </p>
                          </div>
                        )}
                        <p className="text-xs text-gray-500 mt-1">
                          Unit price (e.g., $50/hour, $1.50/sqft)
                        </p>
                      </div>

                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-2">
                          Quantity *
                        </label>
                        <input
                          type="number"
                          {...register(`line_items.${index}.quantity`, {
                            valueAsNumber: true,
                          })}
                          placeholder="1"
                          className="input-field"
                        />
                        <p className="text-xs text-gray-500 mt-1">
                          Number of units
                        </p>
                      </div>

                      <div>
                        <label className="block text-sm font-medium text-gray-700 mb-2">
                          Unit *
                        </label>
                        <select
                          {...register(`line_items.${index}.unit`)}
                          className={`input-field ${errors.line_items?.[index]?.unit ? 'border-red-500 ring-2 ring-red-200' : ''}`}
                        >
                          {unitOptions.map((u) => (
                            <option key={u.value} value={u.value}>{u.label}</option>
                          ))}
                        </select>
                        {errors.line_items?.[index]?.unit && (
                          <div className="flex items-center gap-2 mt-2 text-red-600">
                            <AlertCircle className="w-4 h-4 flex-shrink-0" />
                            <p className="text-sm">
                              {errors.line_items[index]?.unit?.message}
                            </p>
                          </div>
                        )}
                        <p className="text-xs text-gray-500 mt-1">
                          Required for accurate analysis
                        </p>
                      </div>
                    </div>

                    {/* Line Total Calculator */}
                    {(() => {
                      const price = watch(`line_items.${index}.quoted_price`) || 0;
                      const qty = watch(`line_items.${index}.quantity`) || 1;
                      const lineTotal = price * qty;
                      return lineTotal > 0 ? (
                        <div className="mt-3 pt-3 border-t border-gray-200">
                          <div className="flex justify-between items-center">
                            <span className="text-sm font-medium text-gray-600">Line Total:</span>
                            <span className="text-lg font-bold text-primary-600">
                              ${lineTotal.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
                            </span>
                          </div>
                          <p className="text-xs text-gray-500 mt-1">
                            ${price.toFixed(2)} × {qty} {watch(`line_items.${index}.unit`) || 'unit'}{qty !== 1 ? 's' : ''}
                          </p>
                        </div>
                      ) : null;
                    })()}
                  </div>
                ))}

                <button
                  type="button"
                  onClick={() => append({ item_name: '', description: '', quoted_price: 0, quantity: 1, unit: 'item' })}
                  className="btn-secondary flex items-center w-full justify-center hover:shadow-lg active:scale-[0.98] transition-all"
                >
                  <Plus className="w-4 h-4 mr-2" />
                  Add Another Line Item
                </button>

                {/* Warn about $0 line items */}
                {lineItems.some(item => item.quoted_price === 0) && (
                  <div className="bg-amber-50 border border-amber-300 rounded-lg p-4 flex items-start gap-3">
                    <AlertCircle className="w-5 h-5 text-amber-600 flex-shrink-0 mt-0.5" />
                    <div>
                      <h4 className="font-semibold text-amber-800 text-sm">Some items have $0 prices</h4>
                      <p className="text-amber-700 text-sm mt-1">
                        Please check: {lineItems.filter(i => i.quoted_price === 0).map(i => i.item_name || 'Unnamed').join(', ')}.
                        If these have real costs, update the prices above for accurate analysis.
                      </p>
                    </div>
                  </div>
                )}
              </>
            )}

            {totalQuoted > 0 && (
              <div className="bg-gray-50 p-4 rounded-lg">
                <div className="flex justify-between items-center">
                  <span className="font-semibold">Total Quoted:</span>
                  <span className="text-2xl font-bold text-primary-600">
                    ${totalQuoted.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
                  </span>
                </div>
              </div>
            )}

            {/* Promo Code — shown before advancing to checkout */}
            <div className={`rounded-lg p-4 border ${promoApplied ? 'bg-emerald-50 border-emerald-300' : 'bg-amber-50 border-amber-200'}`}>
              <label className="block text-sm font-semibold mb-2" style={{ color: promoApplied ? '#065f46' : '#92400e' }}>
                🎟️ Have a promo code?
              </label>
              <div className="flex items-center gap-3">
                <input
                  type="text"
                  value={promoCode}
                  onChange={(e) => { setPromoCode(e.target.value.toUpperCase()); setPromoApplied(false); }}
                  placeholder="Enter promo code"
                  disabled={promoApplied}
                  className="input-field flex-1 text-base font-mono tracking-wider uppercase disabled:bg-gray-100"
                />
                {promoCode && !promoApplied && (
                  <button
                    type="button"
                    onClick={() => setPromoApplied(true)}
                    className="px-5 py-2.5 bg-amber-600 text-white text-sm font-bold rounded-lg hover:bg-amber-700 active:scale-95 transition-all shadow-sm whitespace-nowrap"
                  >
                    Apply
                  </button>
                )}
                {promoApplied && (
                  <button
                    type="button"
                    onClick={() => { setPromoCode(''); setPromoApplied(false); }}
                    className="px-4 py-2.5 bg-gray-200 text-gray-700 text-sm font-medium rounded-lg hover:bg-gray-300 transition-all whitespace-nowrap"
                  >
                    Remove
                  </button>
                )}
              </div>
              {promoApplied && (
                <p className="text-sm text-emerald-700 font-semibold mt-2">✅ Code &quot;{promoCode}&quot; applied — discount will be applied at checkout</p>
              )}
            </div>

            {/* Payment summary */}
            <div className="bg-primary-50 border border-primary-200 p-5 rounded-lg">
              <div className="flex justify-between items-center mb-3">
                <div>
                  <h3 className="text-lg font-bold">AI Analysis Report</h3>
                  <p className="text-sm text-gray-600">One-time payment · <span className="text-primary-600 font-semibold">Early Adopter Pricing</span></p>
                </div>
                <div className="flex flex-col items-end">
                  <div className="text-2xl font-bold text-primary-600">$9.99</div>
                  <div className="text-xs text-gray-500 line-through">$19.99</div>
                </div>
              </div>
              <ul className="text-sm space-y-1 text-gray-700">
                <li>✓ AI-powered line-item analysis</li>
                <li>✓ Real-time market price verification</li>
                <li>✓ Regional labor &amp; material cost comparison</li>
                <li>✓ Instant PDF report with recommendations</li>
              </ul>
            </div>

            {error && (
              <div className="bg-red-50 border-l-4 border-red-500 rounded-lg p-4 animate-shake">
                <div className="flex items-start gap-3">
                  <AlertCircle className="w-5 h-5 text-red-600 flex-shrink-0 mt-0.5" />
                  <div>
                    <h4 className="font-semibold text-red-900 mb-1">Something went wrong</h4>
                    <p className="text-red-700 text-sm">{error}</p>
                    <p className="text-red-600 text-xs mt-2">Please try again or contact support if the problem persists.</p>
                  </div>
                </div>
              </div>
            )}

            <div className="flex flex-col sm:flex-row justify-between gap-4">
              <button
                type="button"
                onClick={() => setStep(1)}
                disabled={loading}
                className="btn-secondary flex items-center justify-center disabled:opacity-50 disabled:cursor-not-allowed hover:shadow-lg active:scale-95 transition-all"
              >
                <ArrowLeft className="w-4 h-4 mr-2" />
                Back
              </button>
              <button
                type="submit"
                disabled={loading || fields.length === 0}
                className="btn-primary flex items-center justify-center disabled:opacity-70 disabled:cursor-not-allowed hover:shadow-xl active:scale-95 transition-all"
              >
                {loading ? (
                  <>
                    <div className="animate-spin rounded-full h-5 w-5 border-2 border-white border-t-transparent mr-2"></div>
                    Processing...
                  </>
                ) : (
                  <>
                    Pay $9.99 & Get Report
                    <ArrowRight className="w-4 h-4 ml-2" />
                  </>
                )}
              </button>
            </div>

            <p className="text-xs text-gray-500 text-center">
              By submitting, you agree to our Terms of Service and Privacy Policy.
              Payment processing is secured by Stripe.
            </p>
          </div>
        )}
      </form>
    </div>
  );
}
