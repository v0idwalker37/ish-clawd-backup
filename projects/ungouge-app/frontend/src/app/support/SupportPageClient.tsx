'use client';

import { MessageCircle } from 'lucide-react';

export default function SupportPageClient({ variant = 'primary' }: { variant?: 'primary' | 'secondary' }) {
  const openChat = () => {
    window.dispatchEvent(new CustomEvent('open-scout-chat'));
  };

  const styles = variant === 'secondary'
    ? 'btn-secondary flex items-center justify-center gap-2'
    : 'flex items-center gap-3 w-full px-5 py-3.5 bg-primary-600 text-white rounded-xl font-semibold hover:bg-primary-700 active:scale-[0.98] transition-all shadow-sm';

  return (
    <button onClick={openChat} className={styles}>
      <MessageCircle className="w-5 h-5" />
      Ask Zedd
    </button>
  );
}
