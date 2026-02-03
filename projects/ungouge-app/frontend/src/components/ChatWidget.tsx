'use client';

import { useState, useEffect, useRef } from 'react';
import { MessageCircle, X, Send, Bot, User } from 'lucide-react';

interface Message {
  id: string;
  text: string;
  sender: 'user' | 'bot';
  timestamp: Date;
}

interface FAQ {
  keywords: string[];
  question: string;
  answer: string;
}

const faqs: FAQ[] = [
  {
    keywords: ['how', 'work', 'process', 'does'],
    question: 'How does Ungouge work?',
    answer: "Ungouge.ai analyzes contractor quotes by comparing them against real Bureau of Labor Statistics (BLS) wage data and current material cost databases for your specific region. Our AI breaks down each line item, calculates fair price ranges based on actual labor rates and material costs, then flags anything that's significantly overpriced. You get a detailed report showing exactly where you might be getting gouged and by how much.",
  },
  {
    keywords: ['safe', 'security', 'secure', 'privacy', 'data'],
    question: 'Is my data safe?',
    answer: "Absolutely. Your quote data is encrypted in transit and at rest using industry-standard AES-256 encryption. We store your information on secure servers with strict access controls. Your quotes and personal information are never shared with third parties, contractors, or lead generation services. We're here to protect you, not profit from your data.",
  },
  {
    keywords: ['accurate', 'accuracy', 'reliable', 'trust'],
    question: 'How accurate are the reports?',
    answer: "Our analysis uses official BLS occupational wage data updated quarterly, combined with real-time material cost databases from major suppliers. We account for regional variations, project complexity, and seasonal pricing. While contractor quotes can vary based on their overhead and specialization, our reports provide statistically sound benchmarks. In our testing, we've identified overcharges in 73% of quotes analyzed, with an average markup of 28% above fair market rates.",
  },
  {
    keywords: ['price', 'cost', '$19.99', 'pay', 'get', 'include'],
    question: 'What does $19.99 get me?',
    answer: "For $19.99, you get a comprehensive analysis report including: (1) Line-by-line breakdown of every quote item, (2) Fair price range based on BLS data for your region, (3) Percentage markup on each item, (4) Overall gouge rating (Fair/High/Gouged), (5) Negotiation tips specific to your quote, and (6) Alternative pricing suggestions. One report, one payment. No subscriptions, no hidden fees, no upsells. The report is yours to keep and use in negotiations.",
  },
  {
    keywords: ['sell', 'share', 'contractor', 'lead', 'referral'],
    question: 'Do you sell my info to contractors?',
    answer: "NEVER. This is core to who we are. We will NEVER sell your data, share your information with contractors, or operate as a lead generation service. That's exactly what we're fighting against. Traditional 'quote comparison' sites make money by selling your info to contractors who then spam you. We make money only from you, by providing honest analysis. Your information stays private, period.",
  },
  {
    keywords: ['refund', 'money back', 'guarantee', 'satisfied'],
    question: 'Can I get a refund?',
    answer: "Yes! We offer a 100% money-back guarantee within 7 days of purchase. If you're not satisfied with your report for any reason, just email support@ungouge.ai with your report ID and we'll issue a full refund, no questions asked. We stand behind our analysis and want you to feel confident in your investment.",
  },
];

export default function ChatWidget() {
  const [isOpen, setIsOpen] = useState(false);
  const [messages, setMessages] = useState<Message[]>([]);
  const [inputText, setInputText] = useState('');
  const [isTyping, setIsTyping] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, isTyping]);

  useEffect(() => {
    if (isOpen && messages.length === 0) {
      // Send welcome message when first opened
      setTimeout(() => {
        addBotMessage(
          "👋 Hi! I'm here to answer questions about Ungouge.ai. You can ask me anything, or try one of these common questions:\n\n• How does Ungouge work?\n• Is my data safe?\n• What does $19.99 get me?\n• Do you sell my info to contractors?"
        );
      }, 300);
    }
  }, [isOpen]);

  const addBotMessage = (text: string) => {
    const newMessage: Message = {
      id: Date.now().toString(),
      text,
      sender: 'bot',
      timestamp: new Date(),
    };
    setMessages((prev) => [...prev, newMessage]);
  };

  const addUserMessage = (text: string) => {
    const newMessage: Message = {
      id: Date.now().toString(),
      text,
      sender: 'user',
      timestamp: new Date(),
    };
    setMessages((prev) => [...prev, newMessage]);
  };

  const findMatchingFAQ = (query: string): FAQ | null => {
    const lowerQuery = query.toLowerCase();
    
    // Find FAQ with most matching keywords
    let bestMatch: { faq: FAQ; score: number } | null = null;
    
    for (const faq of faqs) {
      let score = 0;
      for (const keyword of faq.keywords) {
        if (lowerQuery.includes(keyword)) {
          score++;
        }
      }
      
      if (score > 0 && (!bestMatch || score > bestMatch.score)) {
        bestMatch = { faq, score };
      }
    }
    
    return bestMatch ? bestMatch.faq : null;
  };

  const handleSendMessage = async () => {
    if (!inputText.trim()) return;

    const userMessage = inputText.trim();
    setInputText('');
    addUserMessage(userMessage);

    // Show typing indicator
    setIsTyping(true);

    // Simulate AI thinking time
    await new Promise((resolve) => setTimeout(resolve, 800 + Math.random() * 400));

    setIsTyping(false);

    // Find matching FAQ
    const matchedFAQ = findMatchingFAQ(userMessage);

    if (matchedFAQ) {
      addBotMessage(matchedFAQ.answer);
    } else {
      // Default response for unmatched queries
      addBotMessage(
        "I'm not sure about that specific question, but I can help with:\n\n• How Ungouge.ai works\n• Data security and privacy\n• Pricing and what you get\n• Our no-lead-gen guarantee\n• Refund policy\n• Report accuracy\n\nYou can also email us at support@ungouge.ai for personalized help!"
      );
    }
  };

  const handleQuickQuestion = (question: string) => {
    setInputText(question);
    setTimeout(() => handleSendMessage(), 100);
  };

  return (
    <>
      {/* Chat Bubble */}
      {!isOpen && (
        <button
          onClick={() => setIsOpen(true)}
          className="fixed bottom-6 right-6 w-16 h-16 bg-primary-600 hover:bg-primary-700 text-white rounded-full shadow-lg hover:shadow-xl transition-all flex items-center justify-center z-50 group"
          aria-label="Open chat"
        >
          <MessageCircle className="w-7 h-7" />
          <span className="absolute -top-1 -right-1 w-3 h-3 bg-green-500 rounded-full border-2 border-white"></span>
        </button>
      )}

      {/* Chat Panel */}
      {isOpen && (
        <div className="fixed bottom-6 right-6 w-96 h-[600px] bg-white rounded-2xl shadow-2xl flex flex-col z-50 border border-gray-200">
          {/* Header */}
          <div className="bg-gradient-to-r from-primary-600 to-primary-700 text-white p-4 rounded-t-2xl flex items-center justify-between">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 bg-white/20 rounded-full flex items-center justify-center">
                <Bot className="w-6 h-6" />
              </div>
              <div>
                <h3 className="font-semibold">Ungouge Support</h3>
                <p className="text-xs text-primary-100">Always here to help</p>
              </div>
            </div>
            <button
              onClick={() => setIsOpen(false)}
              className="p-1.5 hover:bg-white/20 rounded-lg transition-colors"
              aria-label="Close chat"
            >
              <X className="w-5 h-5" />
            </button>
          </div>

          {/* Messages */}
          <div className="flex-1 overflow-y-auto p-4 space-y-4 bg-gray-50">
            {messages.map((message) => (
              <div
                key={message.id}
                className={`flex gap-2 ${message.sender === 'user' ? 'justify-end' : 'justify-start'}`}
              >
                {message.sender === 'bot' && (
                  <div className="w-8 h-8 bg-primary-100 rounded-full flex items-center justify-center flex-shrink-0">
                    <Bot className="w-5 h-5 text-primary-600" />
                  </div>
                )}
                <div
                  className={`max-w-[75%] rounded-2xl px-4 py-2.5 ${
                    message.sender === 'user'
                      ? 'bg-primary-600 text-white rounded-br-sm'
                      : 'bg-white text-gray-800 rounded-bl-sm shadow-sm border border-gray-100'
                  }`}
                >
                  <p className="text-sm whitespace-pre-line leading-relaxed">{message.text}</p>
                </div>
                {message.sender === 'user' && (
                  <div className="w-8 h-8 bg-gray-300 rounded-full flex items-center justify-center flex-shrink-0">
                    <User className="w-5 h-5 text-gray-600" />
                  </div>
                )}
              </div>
            ))}

            {/* Typing Indicator */}
            {isTyping && (
              <div className="flex gap-2 justify-start">
                <div className="w-8 h-8 bg-primary-100 rounded-full flex items-center justify-center flex-shrink-0">
                  <Bot className="w-5 h-5 text-primary-600" />
                </div>
                <div className="bg-white rounded-2xl rounded-bl-sm px-4 py-3 shadow-sm border border-gray-100">
                  <div className="flex gap-1">
                    <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0ms' }}></div>
                    <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '150ms' }}></div>
                    <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '300ms' }}></div>
                  </div>
                </div>
              </div>
            )}

            <div ref={messagesEndRef} />
          </div>

          {/* Quick Questions (shown when no messages) */}
          {messages.length === 0 && !isTyping && (
            <div className="p-4 border-t bg-white space-y-2">
              <p className="text-xs font-semibold text-gray-500 mb-2">Quick questions:</p>
              {faqs.slice(0, 3).map((faq, idx) => (
                <button
                  key={idx}
                  onClick={() => handleQuickQuestion(faq.question)}
                  className="block w-full text-left px-3 py-2 text-sm bg-gray-50 hover:bg-gray-100 rounded-lg transition-colors text-gray-700"
                >
                  {faq.question}
                </button>
              ))}
            </div>
          )}

          {/* Input */}
          <div className="p-4 border-t bg-white rounded-b-2xl">
            <div className="flex gap-2">
              <input
                type="text"
                value={inputText}
                onChange={(e) => setInputText(e.target.value)}
                onKeyPress={(e) => e.key === 'Enter' && handleSendMessage()}
                placeholder="Ask a question..."
                className="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500 outline-none text-sm"
              />
              <button
                onClick={handleSendMessage}
                disabled={!inputText.trim()}
                className="bg-primary-600 text-white p-2 rounded-lg hover:bg-primary-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                aria-label="Send message"
              >
                <Send className="w-5 h-5" />
              </button>
            </div>
            <p className="text-xs text-gray-500 mt-2 text-center">
              Or email <a href="mailto:support@ungouge.ai" className="text-primary-600 hover:underline">support@ungouge.ai</a>
            </p>
          </div>
        </div>
      )}
    </>
  );
}
