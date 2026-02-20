#!/bin/bash
# Batch update all $19.99 references to $9.99 with Early Adopter messaging

cd /home/ungouge/clawd/projects/ungouge-app/frontend/src

# Update Chat Widget
sed -i "s/\$19\.99/\$9.99 (Early Adopter Pricing)/g" components/ChatWidget.tsx
sed -i "s/'price', 'cost', '\$19\.99'/'price', 'cost', '\$9.99'/g" components/ChatWidget.tsx
sed -i "s/What does \$19\.99 get me?/What does \$9.99 get me?/g" components/ChatWidget.tsx
sed -i "s/For \$19\.99/For \$9.99 (Early Adopter Pricing, normally \$19.99)/g" components/ChatWidget.tsx

# Update SEO metadata
sed -i "s/\$19\.99/\$9.99 Early Adopter Pricing (normally \$19.99)/g" lib/seo.ts
sed -i "s/price: '19\.99'/price: '9.99'/g" lib/seo.ts
sed -i "s/description: '\$19\.99/description: '\$9.99/g" lib/seo.ts

# Update pricing page
sed -i "s/Pricing — \$19\.99/Pricing — \$9.99 Early Adopter Pricing/g" app/pricing/page.tsx
sed -i "s/\$19\.99/\$9.99/g" app/pricing/page.tsx
sed -i "s/<div className=\"text-5xl font-bold text-primary-600 mb-2\">\$9\.99<\/div>/<div className=\"text-5xl font-bold text-primary-600 mb-2\">\$9.99<\/div>\n              <div className=\"text-lg text-gray-500 line-through\">Normally \$19.99<\/div>\n              <div className=\"text-sm text-primary-600 font-semibold mt-1\">Early Adopter Pricing<\/div>/g" app/pricing/page.tsx

# Update homepage
sed -i "s/\$19\.99/\$9.99 (Early Adopter Pricing)/g" app/page.tsx
sed -i "s/price: '19\.99'/price: '9.99'/g" app/page.tsx

# Update HomePageContent
sed -i "s/\$19\.99/\$9.99/g" app/HomePageContent.tsx

# Update layout metadata
sed -i "s/\$19\.99/\$9.99 Early Adopter Pricing/g" app/layout.tsx

# Update terms
sed -i "s/\$19\.99/\$9.99 (Early Adopter Pricing, normally \$19.99)/g" app/terms/page.tsx

# Update OG image
sed -i "s/\$19\.99/\$9.99 Early Adopter Pricing/g" app/opengraph-image.tsx

# Update support page
sed-i "s/\$19\.99/\$9.99 (Early Adopter Pricing)/g" app/support/page.tsx

echo "✅ All pricing updated to \$9.99 with Early Adopter messaging"
