# Ungouge.ai Frontend

Next.js 14 application with TypeScript and Tailwind CSS.

## Getting Started

```bash
# Install dependencies
npm install

# Run development server
npm run dev

# Build for production
npm run build

# Start production server
npm start
```

Open [http://localhost:3000](http://localhost:3000) with your browser.

## Environment Variables

Create a `.env.local` file:

```bash
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_STRIPE_PUBLISHABLE_KEY=pk_test_...
```

## Project Structure

```
src/
├── app/              # App Router pages
│   ├── page.tsx      # Landing page
│   ├── analyze/      # Quote upload form
│   ├── report/[id]/  # Report results
│   ├── about/        # About page
│   ├── pricing/      # Pricing page
│   └── layout.tsx    # Root layout
├── components/       # Reusable components
│   ├── Header.tsx
│   ├── Footer.tsx
│   ├── QuoteForm.tsx
│   ├── ReportCard.tsx
│   └── PriceGauge.tsx
└── styles/
    └── globals.css   # Global styles + Tailwind
```

## Key Features

- **Responsive Design:** Mobile-first with Tailwind CSS
- **Type Safety:** Full TypeScript coverage
- **Form Validation:** React Hook Form + Zod schemas
- **API Integration:** Axios for backend communication
- **SEO Optimized:** Next.js metadata API
- **Performance:** App Router with server components where possible

## Learn More

- [Next.js Documentation](https://nextjs.org/docs)
- [Tailwind CSS](https://tailwindcss.com/docs)
- [TypeScript](https://www.typescriptlang.org/docs)
