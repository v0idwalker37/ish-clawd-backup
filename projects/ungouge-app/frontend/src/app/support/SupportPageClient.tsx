'use client';

import { MessageCircle } from 'lucide-react';

export default function SupportPageClient() {
  const openChat = () => {
    // Trigger the ChatWidget to open — dispatch a custom event
    window.dispatchEvent(new CustomEvent('open-scout-chat'));
  };

  return (
    <button
      onClick={openChat}
      className="flex items-center gap-3 w-full px-5 py-3.5 bg-primary-600 text-white rounded-xl font-semibold hover:bg-primary-700 active:scale-[0.98] transition-all shadow-sm"
    >
      <MessageCircle className="w-5 h-5" />
      Chat with Scout
    </button>
  );
}
